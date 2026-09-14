"""Glavna zagonska datoteka za analizo podatkov Formule 1 (2018 – 2025)."""

import os
import zajem
import obdelava

SEZONE = list(range(2018, 2026))
MAPA_OBDELANIH = os.path.join(os.path.dirname(__file__), "podatki", "obdelani")


def zazen():
    """Izvede celoten postopek pridobivanja, obdelave in shranjevanja podatkov."""
    os.makedirs(MAPA_OBDELANIH, exist_ok=True)
    print("=" * 60)
    print("Projektna naloga: Analiza podatkov Formule 1 (2018 - 2025)")
    print("=" * 60)

    # 1. Zajem podatkov
    print("\n[1/4] Zajem in predpomnjenje podatkov iz Jolpica API...")
    lestvice_surovo = zajem.prenesi_lestvice(SEZONE)
    rezultati_surovo = zajem.prenesi_rezultate_in_koledar(SEZONE)
    kvalifikacije_surovo = zajem.prenesi_kvalifikacije(SEZONE)
    sprinti_surovo = zajem.prenesi_sprinte(SEZONE)
    postanki_surovo = zajem.prenesi_postanke(SEZONE)

    # 2. Obdelava podatkov
    print("\n[2/4] Pretvorba surovih podatkov v urejene tabele (DataFrame)...")
    df_dirkaci = obdelava.obdelaj_lestvico_dirkacev(lestvice_surovo["dirkaci"])
    df_konstruktorji = obdelava.obdelaj_lestvico_konstruktorjev(
        lestvice_surovo["konstruktorji"]
    )
    df_rezultati = obdelava.obdelaj_rezultate_dirk(rezultati_surovo)
    df_kvalifikacije = obdelava.obdelaj_kvalifikacije(kvalifikacije_surovo)
    df_sprinti = obdelava.obdelaj_sprint_rezultate(sprinti_surovo)
    df_postanki = obdelava.obdelaj_postanke_v_boksih(postanki_surovo)

    zbirke = {
        "lestvica_dirkaci.csv": df_dirkaci,
        "lestvica_konstruktorji.csv": df_konstruktorji,
        "rezultati_dirk.csv": df_rezultati,
        "kvalifikacije.csv": df_kvalifikacije,
        "sprint_dirke.csv": df_sprinti,
        "postanki_v_boksih.csv": df_postanki,
    }

    # 3. Shranjevanje v CSV
    print("\n[3/4] Izvoz obdelanih podatkov v datoteke CSV...")
    for ime_datoteke, df in zbirke.items():
        pot = os.path.join(MAPA_OBDELANIH, ime_datoteke)
        df.to_csv(pot, index=False, encoding="utf-8")
        print(f"  -> Shranjeno {ime_datoteke:<26} ({len(df):>5} vrstic)")

    # 4. Zaključek
    print("\n[4/4] Obdelava uspešno zaključena!")
    print(f"Podatki so shranjeni v: {os.path.abspath(MAPA_OBDELANIH)}")
    print("Za ogled analize odprite zvezek: jupyter notebook analiza.ipynb")
    print("=" * 60)


if __name__ == "__main__":
    zazen()
