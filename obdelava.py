"""Pretvorba surovih odgovorov API-ja v tabele pandas."""

import pandas as pd


def cas_v_sekunde(niz_casa):
    """Pretvori zapis časa ('1:27.452') v sekunde."""
    if not niz_casa or not isinstance(niz_casa, str):
        return None
    try:
        if ":" in niz_casa:
            minute, sekunde = niz_casa.split(":", 1)
            return float(minute) * 60 + float(sekunde)
        return float(niz_casa)
    except ValueError:
        return None


def sestavi_polno_ime(slovar_dirkaca):
    """Združi ime in priimek dirkača."""
    ime = slovar_dirkaca.get("givenName", "")
    priimek = slovar_dirkaca.get("familyName", "")
    return f"{ime} {priimek}".strip()


def _vrstice_lestvice(neobdelani_podatki, kljuc):
    for sezona, podatki in neobdelani_podatki.items():
        seznami = podatki.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
        for vrstica in (seznami[0].get(kljuc, []) if seznami else []):
            yield sezona, vrstica


def obdelaj_lestvico_dirkacev(neobdelani_podatki):
    """Končne uvrstitve dirkačev po sezonah."""
    zapisi = []
    for sezona, vrstica in _vrstice_lestvice(neobdelani_podatki, "DriverStandings"):
        dirkac = vrstica.get("Driver", {})
        ekipe = vrstica.get("Constructors") or [{}]
        zapisi.append({
            "sezona": int(sezona),
            "uvrstitev": int(vrstica.get("position", 0)),
            "tocke": float(vrstica.get("points", 0.0)),
            "zmage": int(vrstica.get("wins", 0)),
            "id_dirkaca": dirkac.get("driverId", ""),
            "ime_dirkaca": sestavi_polno_ime(dirkac),
            "drzavljanstvo": dirkac.get("nationality", ""),
            "ekipa": ekipe[0].get("name", ""),
        })
    return pd.DataFrame(zapisi)


def obdelaj_lestvico_konstruktorjev(neobdelani_podatki):
    """Končne uvrstitve konstruktorjev po sezonah."""
    zapisi = []
    for sezona, vrstica in _vrstice_lestvice(neobdelani_podatki, "ConstructorStandings"):
        ekipa = vrstica.get("Constructor", {})
        zapisi.append({
            "sezona": int(sezona),
            "uvrstitev": int(vrstica.get("position", 0)),
            "tocke": float(vrstica.get("points", 0.0)),
            "zmage": int(vrstica.get("wins", 0)),
            "id_konstruktorja": ekipa.get("constructorId", ""),
            "ime_konstruktorja": ekipa.get("name", ""),
            "drzavljanstvo": ekipa.get("nationality", ""),
        })
    return pd.DataFrame(zapisi)
