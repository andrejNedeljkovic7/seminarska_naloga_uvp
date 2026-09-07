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


def _vrstice_iz_strani(sezonski_podatki):
    """Sprehodi se po vseh straneh in vrne pare (sezona, dirka)."""
    for sezona, strani in sezonski_podatki.items():
        for stran in strani:
            dirke = stran.get("MRData", {}).get("RaceTable", {}).get("Races", [])
            for dirka in dirke:
                yield sezona, dirka


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


def obdelaj_rezultate_dirk(rezultati_sezon):
    """Rezultati dirk z najhitrejšimi krogi in hitrostmi."""
    zapisi = []
    for sezona, dirka in _vrstice_iz_strani(rezultati_sezon):
        dirkalisce = dirka.get("Circuit", {})
        for rez in dirka.get("Results", []):
            najhitrejsi = rez.get("FastestLap", {})
            cas_kroga = najhitrejsi.get("Time", {}).get("time")
            hitrost = najhitrejsi.get("AverageSpeed", {}).get("speed")
            mesto = str(rez.get("position", ""))
            uvrstitev_kroga = str(najhitrejsi.get("rank", ""))
            zapisi.append({
                "sezona": int(sezona),
                "stevilka_dirke": int(dirka.get("round", 0)),
                "ime_dirke": dirka.get("raceName", ""),
                "id_dirkalisca": dirkalisce.get("circuitId", ""),
                "ime_dirkalisca": dirkalisce.get("circuitName", ""),
                "datum": dirka.get("date", ""),
                "id_dirkaca": rez.get("Driver", {}).get("driverId", ""),
                "koda_dirkaca": rez.get("Driver", {}).get("code", ""),
                "ime_dirkaca": sestavi_polno_ime(rez.get("Driver", {})),
                "id_konstruktorja": rez.get("Constructor", {}).get("constructorId", ""),
                "ime_konstruktorja": rez.get("Constructor", {}).get("name", ""),
                "startno_mesto": int(rez.get("grid", 0)),
                "koncno_mesto": int(mesto) if mesto.isdigit() else None,
                "tocke": float(rez.get("points", 0.0)),
                "status": rez.get("status", ""),
                "prevozeni_krogi": int(rez.get("laps", 0)),
                "uvrstitev_najhitrejsega_kroga": (
                    int(uvrstitev_kroga) if uvrstitev_kroga.isdigit() else None
                ),
                "cas_najhitrejsega_kroga": cas_kroga,
                "sekunde_najhitrejsega_kroga": cas_v_sekunde(cas_kroga),
                "hitrost_najhitrejsega_kroga_kmh": float(hitrost) if hitrost else None,
            })
    df = pd.DataFrame(zapisi)
    if not df.empty:
        df = df.drop_duplicates(subset=["sezona", "stevilka_dirke", "id_dirkaca"])
    return df
