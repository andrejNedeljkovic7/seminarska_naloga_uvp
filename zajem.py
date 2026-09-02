"""Modul za prenos in lokalno shranjevanje podatkov Formule 1 prek API-ja."""

import json
import os
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

OSNOVNI_URL = "https://api.jolpi.ca/ergast/f1"
MAPA_PREDPOMNILNIKA = os.path.join(
    os.path.dirname(__file__), "podatki", "predpomnilnik"
)

_seja = requests.Session()
_ponovitve = Retry(
    total=4,
    backoff_factor=1.5,
    status_forcelist=[429, 500, 502, 503, 504],
)
_seja.mount("https://", HTTPAdapter(max_retries=_ponovitve))


def pridobi_ali_prenesi(koncna_tocka, parametri=None, ime_datoteke=None):
    """Pridobi JSON iz lokalnega predpomnilnika ali spletnega vira."""
    os.makedirs(MAPA_PREDPOMNILNIKA, exist_ok=True)
    if ime_datoteke is None:
        ime_datoteke = koncna_tocka.strip("/").replace("/", "_") + ".json"

    pot_datoteke = os.path.join(MAPA_PREDPOMNILNIKA, ime_datoteke)
    if os.path.exists(pot_datoteke):
        try:
            with open(pot_datoteke, "r", encoding="utf-8") as dat:
                podatki = json.load(dat)
                if podatki and "MRData" in podatki:
                    return podatki
        except json.JSONDecodeError:
            pass

    url = f"{OSNOVNI_URL}/{koncna_tocka.lstrip('/')}"
    for poskus in range(3):
        try:
            odgovor = _seja.get(url, params=parametri, timeout=15)
            odgovor.raise_for_status()
            podatki = odgovor.json()
            with open(pot_datoteke, "w", encoding="utf-8") as dat:
                json.dump(podatki, dat, ensure_ascii=False, indent=2)
            time.sleep(0.25)
            return podatki
        except requests.RequestException as napaka:
            if poskus == 2:
                print(f"Opozorilo: Napaka pri prenosu {url}: {napaka}")
            time.sleep(1.0 + poskus)
    return None


def prenesi_lestvice(sezone):
    """Prenese točkovne lestvice dirkačev in konstruktorjev za dane sezone."""
    lestvice = {"dirkaci": {}, "konstruktorji": {}}
    for sezona in sezone:
        podatki_d = pridobi_ali_prenesi(
            f"{sezona}/driverStandings.json",
            parametri={"limit": 100},
            ime_datoteke=f"driver_standings_{sezona}.json",
        )
        if podatki_d:
            lestvice["dirkaci"][sezona] = podatki_d

        podatki_k = pridobi_ali_prenesi(
            f"{sezona}/constructorStandings.json",
            parametri={"limit": 100},
            ime_datoteke=f"constructor_standings_{sezona}.json",
        )
        if podatki_k:
            lestvice["konstruktorji"][sezona] = podatki_k
    return lestvice


def prenesi_rezultate_in_koledar(sezone):
    """Prenese koledar in uradne rezultate dirk za dane sezone."""
    rezultati_sezon = {}
    for sezona in sezone:
        strani = []
        odmik = 0
        omejitev = 100
        while True:
            ime_datoteke = f"results_{sezona}_offset_{odmik}.json"
            podatki = pridobi_ali_prenesi(
                f"{sezona}/results.json",
                parametri={"limit": omejitev, "offset": odmik},
                ime_datoteke=ime_datoteke,
            )
            if not podatki or "MRData" not in podatki:
                break
            strani.append(podatki)
            skupaj = int(podatki["MRData"].get("total", 0))
            odmik += omejitev
            if odmik >= skupaj:
                break
        rezultati_sezon[sezona] = strani
    return rezultati_sezon


def prenesi_kvalifikacije(sezone):
    """Prenese rezultate kvalifikacijskih voženj za dane sezone."""
    podatki_kvalifikacij = {}
    for sezona in sezone:
        strani = []
        odmik = 0
        omejitev = 100
        while True:
            ime_datoteke = f"qualifying_{sezona}_offset_{odmik}.json"
            podatki = pridobi_ali_prenesi(
                f"{sezona}/qualifying.json",
                parametri={"limit": omejitev, "offset": odmik},
                ime_datoteke=ime_datoteke,
            )
            if not podatki or "MRData" not in podatki:
                break
            strani.append(podatki)
            skupaj = int(podatki["MRData"].get("total", 0))
            odmik += omejitev
            if odmik >= skupaj:
                break
        podatki_kvalifikacij[sezona] = strani
    return podatki_kvalifikacij


def prenesi_sprinte(sezone):
    """Prenese rezultate sobotnih sprint dirk (od uvedbe leta 2021 naprej)."""
    podatki_sprintov = {}
    for sezona in sezone:
        if sezona < 2021:
            continue
        podatki = pridobi_ali_prenesi(
            f"{sezona}/sprint.json",
            parametri={"limit": 100},
            ime_datoteke=f"sprints_{sezona}.json",
        )
        if podatki:
            podatki_sprintov[sezona] = podatki
    return podatki_sprintov


def prenesi_postanke(sezone, vzorcne_dirke=None):
    """Prenese podatke o postankih v boksih za izbrane sezone in kroge."""
    if vzorcne_dirke is None:
        vzorcne_dirke = [1, 5, 10, 15, 20]

    podatki_postankov = {}
    for sezona in sezone:
        podatki_postankov[sezona] = {}
        for krog in vzorcne_dirke:
            ime_datoteke = f"pitstops_{sezona}_round_{krog}.json"
            podatki = pridobi_ali_prenesi(
                f"{sezona}/{krog}/pitstops.json",
                parametri={"limit": 100},
                ime_datoteke=ime_datoteke,
            )
            if podatki:
                podatki_postankov[sezona][krog] = podatki
    return podatki_postankov
