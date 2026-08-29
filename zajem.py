"""Prenos podatkov Formule 1 prek API-ja Jolpica."""

import json
import os

import requests

OSNOVNI_URL = "https://api.jolpi.ca/ergast/f1"
MAPA_PREDPOMNILNIKA = os.path.join(os.path.dirname(__file__), "podatki", "predpomnilnik")


def prenesi(koncna_tocka, parametri=None, ime_datoteke=None):
    os.makedirs(MAPA_PREDPOMNILNIKA, exist_ok=True)
    if ime_datoteke is None:
        ime_datoteke = koncna_tocka.strip("/").replace("/", "_") + ".json"

    pot_datoteke = os.path.join(MAPA_PREDPOMNILNIKA, ime_datoteke)
    if os.path.exists(pot_datoteke):
        with open(pot_datoteke, "r", encoding="utf-8") as dat:
            return json.load(dat)

    url = f"{OSNOVNI_URL}/{koncna_tocka.lstrip('/')}"
    odgovor = requests.get(url, params=parametri, timeout=15)
    odgovor.raise_for_status()
    podatki = odgovor.json()
    with open(pot_datoteke, "w", encoding="utf-8") as dat:
        json.dump(podatki, dat, ensure_ascii=False, indent=2)
    return podatki


def prenesi_lestvice(sezone):
    lestvice = {"dirkaci": {}, "konstruktorji": {}}
    for sezona in sezone:
        lestvice["dirkaci"][sezona] = prenesi(
            f"{sezona}/driverStandings.json",
            parametri={"limit": 100},
            ime_datoteke=f"driver_standings_{sezona}.json",
        )
        lestvice["konstruktorji"][sezona] = prenesi(
            f"{sezona}/constructorStandings.json",
            parametri={"limit": 100},
            ime_datoteke=f"constructor_standings_{sezona}.json",
        )
    return lestvice


def prenesi_rezultate(sezone):
    rezultati = {}
    for sezona in sezone:
        rezultati[sezona] = prenesi(
            f"{sezona}/results.json",
            parametri={"limit": 100},
            ime_datoteke=f"results_{sezona}.json",
        )
    return rezultati
