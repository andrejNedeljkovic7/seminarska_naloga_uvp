"""Prenos podatkov Formule 1 prek API-ja Jolpica in lokalno predpomnjenje."""

import json
import os
import time

import requests

OSNOVNI_URL = "https://api.jolpi.ca/ergast/f1"
MAPA_PREDPOMNILNIKA = os.path.join(os.path.dirname(__file__), "podatki", "predpomnilnik")

# API vrne največ 100 zapisov na zahtevek, zato je treba daljše sezname brati po straneh.
VELIKOST_STRANI = 100

# Podatke o postankih prenašamo le za pet vzorčnih dirk v sezoni (1., 5., 10., 15. in 20.
# krog koledarja), ker bi bilo branje vseh 24 dirk za vsako sezono prepočasno.
VZORCNI_KROGI = [1, 5, 10, 15, 20]

_seja = requests.Session()


class NapakaPriPrenosu(Exception):
    """Sporočilo, da podatkov ni bilo mogoče prebrati ne iz predpomnilnika ne iz API-ja."""


def _preberi_predpomnilnik(pot_datoteke):
    if not os.path.exists(pot_datoteke):
        return None
    try:
        with open(pot_datoteke, "r", encoding="utf-8") as dat:
            podatki = json.load(dat)
    except (json.JSONDecodeError, OSError):
        return None
    return podatki if podatki.get("MRData") else None


def pridobi_ali_prenesi(koncna_tocka, parametri=None, ime_datoteke=None):
    """Vrne JSON s končne točke, pri čemer najprej poskusi lokalni predpomnilnik."""
    os.makedirs(MAPA_PREDPOMNILNIKA, exist_ok=True)
    if ime_datoteke is None:
        ime_datoteke = koncna_tocka.strip("/").replace("/", "_") + ".json"

    pot_datoteke = os.path.join(MAPA_PREDPOMNILNIKA, ime_datoteke)
    podatki = _preberi_predpomnilnik(pot_datoteke)
    if podatki is not None:
        return podatki

    url = f"{OSNOVNI_URL}/{koncna_tocka.lstrip('/')}"
    for poskus in range(3):
        try:
            odgovor = _seja.get(url, params=parametri, timeout=20)
            odgovor.raise_for_status()
            podatki = odgovor.json()
        except (requests.RequestException, ValueError) as napaka:
            if poskus == 2:
                raise NapakaPriPrenosu(f"prenos {url} ni uspel: {napaka}") from napaka
            time.sleep(2 * (poskus + 1))
            continue

        with open(pot_datoteke, "w", encoding="utf-8") as dat:
            json.dump(podatki, dat, ensure_ascii=False, indent=2)
        time.sleep(0.2)
        return podatki

    raise NapakaPriPrenosu(f"prenos {url} ni uspel")


def prenesi_vse_strani(koncna_tocka, predpona):
    """Prebere vse strani ene končne točke in vrne seznam odgovorov MRData."""
    strani = []
    odmik = 0
    while True:
        podatki = pridobi_ali_prenesi(
            koncna_tocka,
            parametri={"limit": VELIKOST_STRANI, "offset": odmik},
            ime_datoteke=f"{predpona}_offset_{odmik}.json",
        )
        strani.append(podatki)
        skupaj = int(podatki["MRData"].get("total", 0))
        if not podatki["MRData"].get("RaceTable", {}).get("Races"):
            break
        odmik += VELIKOST_STRANI
        if odmik >= skupaj:
            break
    return strani


def prenesi_lestvice(sezone):
    """Prenese končni lestvici dirkačev in konstruktorjev za vsako sezono."""
    lestvice = {"dirkaci": {}, "konstruktorji": {}}
    for sezona in sezone:
        lestvice["dirkaci"][sezona] = pridobi_ali_prenesi(
            f"{sezona}/driverStandings.json",
            parametri={"limit": VELIKOST_STRANI},
            ime_datoteke=f"driver_standings_{sezona}.json",
        )
        lestvice["konstruktorji"][sezona] = pridobi_ali_prenesi(
            f"{sezona}/constructorStandings.json",
            parametri={"limit": VELIKOST_STRANI},
            ime_datoteke=f"constructor_standings_{sezona}.json",
        )
    return lestvice


def prenesi_rezultate_in_koledar(sezone):
    """Prenese rezultate vseh dirk v sezoni skupaj s podatki o dirkališčih."""
    return {
        sezona: prenesi_vse_strani(f"{sezona}/results.json", f"results_{sezona}")
        for sezona in sezone
    }


def prenesi_kvalifikacije(sezone):
    """Prenese uvrstitve in čase kvalifikacij."""
    return {
        sezona: prenesi_vse_strani(f"{sezona}/qualifying.json", f"qualifying_{sezona}")
        for sezona in sezone
    }


def prenesi_sprinte(sezone):
    """Prenese rezultate sprint dirk; format se uporablja od sezone 2021 naprej."""
    return {
        sezona: prenesi_vse_strani(f"{sezona}/sprint.json", f"sprints_{sezona}")
        for sezona in sezone
        if sezona >= 2021
    }


def prenesi_postanke(sezone, vzorcne_dirke=None):
    """Prenese postanke v boksih za vzorčne dirke izbranih sezon."""
    if vzorcne_dirke is None:
        vzorcne_dirke = VZORCNI_KROGI

    podatki_postankov = {}
    for sezona in sezone:
        podatki_postankov[sezona] = {}
        for krog in vzorcne_dirke:
            podatki = pridobi_ali_prenesi(
                f"{sezona}/{krog}/pitstops.json",
                parametri={"limit": VELIKOST_STRANI},
                ime_datoteke=f"pitstops_{sezona}_round_{krog}.json",
            )
            dirke = podatki["MRData"].get("RaceTable", {}).get("Races") or []
            if not dirke or not dirke[0].get("PitStops"):
                # npr. sezona 2020 je imela le 17 dirk, zato 20. krog ne obstaja
                print(f"  opozorilo: {sezona}, {krog}. dirka - ni podatkov o postankih")
                prazna = os.path.join(MAPA_PREDPOMNILNIKA, f"pitstops_{sezona}_round_{krog}.json")
                if os.path.exists(prazna):
                    os.remove(prazna)
                continue
            podatki_postankov[sezona][krog] = podatki
    return podatki_postankov
