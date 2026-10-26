"""Zagon celotnega postopka: prenos podatkov, obdelava in izvoz v CSV."""

import os
import sys

import obdelava
import zajem

SEZONE = list(range(2018, 2026))
MAPA_OBDELANIH = os.path.join(os.path.dirname(__file__), "podatki", "obdelani")


def zazen():
    os.makedirs(MAPA_OBDELANIH, exist_ok=True)

    try:
        lestvice = zajem.prenesi_lestvice(SEZONE)
        rezultati = zajem.prenesi_rezultate_in_koledar(SEZONE)
        kvalifikacije = zajem.prenesi_kvalifikacije(SEZONE)
        sprinti = zajem.prenesi_sprinte(SEZONE)
        postanki = zajem.prenesi_postanke(SEZONE)
    except zajem.NapakaPriPrenosu as napaka:
        sys.exit(f"Prekinjam, podatki niso popolni: {napaka}")

    zbirke = {
        "lestvica_dirkaci.csv": obdelava.obdelaj_lestvico_dirkacev(lestvice["dirkaci"]),
        "lestvica_konstruktorji.csv": obdelava.obdelaj_lestvico_konstruktorjev(
            lestvice["konstruktorji"]
        ),
        "rezultati_dirk.csv": obdelava.obdelaj_rezultate_dirk(rezultati),
        "kvalifikacije.csv": obdelava.obdelaj_kvalifikacije(kvalifikacije),
        "sprint_dirke.csv": obdelava.obdelaj_sprint_rezultate(sprinti),
        "postanki_v_boksih.csv": obdelava.obdelaj_postanke_v_boksih(postanki),
    }

    for ime_datoteke, df in zbirke.items():
        df.to_csv(os.path.join(MAPA_OBDELANIH, ime_datoteke), index=False, encoding="utf-8")
        print(f"{ime_datoteke:<26} {len(df):>5} vrstic")

    print(f"Tabele so shranjene v {MAPA_OBDELANIH}")


if __name__ == "__main__":
    zazen()
