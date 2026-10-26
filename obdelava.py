"""Pretvorba surovih odgovorov API-ja v urejene tabele pandas."""

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
    return f"{slovar_dirkaca.get('givenName', '')} {slovar_dirkaca.get('familyName', '')}".strip()


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


def obdelaj_kvalifikacije(podatki_kvalifikacij):
    """Uvrstitve v kvalifikacijah; stolpec Q3 manjka, če dirkač ni prišel v tretji del."""
    zapisi = []
    for sezona, dirka in _vrstice_iz_strani(podatki_kvalifikacij):
        for q in dirka.get("QualifyingResults", []):
            mesto = str(q.get("position", ""))
            zapisi.append({
                "sezona": int(sezona),
                "stevilka_dirke": int(dirka.get("round", 0)),
                "ime_dirke": dirka.get("raceName", ""),
                "id_dirkaca": q.get("Driver", {}).get("driverId", ""),
                "ime_dirkaca": sestavi_polno_ime(q.get("Driver", {})),
                "id_konstruktorja": q.get("Constructor", {}).get("constructorId", ""),
                "uvrstitev_kvalifikacij": int(mesto) if mesto.isdigit() else None,
                "q1": q.get("Q1"),
                "q2": q.get("Q2"),
                "q3": q.get("Q3"),
                "najboljsi_cas_sekunde": cas_v_sekunde(q.get("Q3") or q.get("Q2") or q.get("Q1")),
            })
    df = pd.DataFrame(zapisi)
    if not df.empty:
        df = df.drop_duplicates(subset=["sezona", "stevilka_dirke", "id_dirkaca"])
    return df


def obdelaj_postanke_v_boksih(podatki_postankov):
    """Trajanje posameznih postankov za vzorčne dirke."""
    zapisi = []
    for sezona, krogi in podatki_postankov.items():
        for st_kroga, podatki in krogi.items():
            dirke = podatki.get("MRData", {}).get("RaceTable", {}).get("Races", [])
            if not dirke:
                continue
            for postanek in dirke[0].get("PitStops", []):
                zapisi.append({
                    "sezona": int(sezona),
                    "stevilka_dirke": int(st_kroga),
                    "ime_dirke": dirke[0].get("raceName", ""),
                    "id_dirkaca": postanek.get("driverId", ""),
                    "stevilka_postanka": int(postanek.get("stop", 0)),
                    "krog_postanka": int(postanek.get("lap", 0)),
                    "trajanje_sekunde": cas_v_sekunde(postanek.get("duration", "")),
                })
    return pd.DataFrame(zapisi)


def obdelaj_sprint_rezultate(podatki_sprintov):
    """Uvrstitve in točke s sprint dirk."""
    zapisi = []
    for sezona, dirka in _vrstice_iz_strani(podatki_sprintov):
        for s in dirka.get("SprintResults", []):
            mesto = str(s.get("position", ""))
            zapisi.append({
                "sezona": int(sezona),
                "stevilka_dirke": int(dirka.get("round", 0)),
                "ime_dirke": dirka.get("raceName", ""),
                "id_dirkaca": s.get("Driver", {}).get("driverId", ""),
                "ime_dirkaca": sestavi_polno_ime(s.get("Driver", {})),
                "id_konstruktorja": s.get("Constructor", {}).get("constructorId", ""),
                "ime_konstruktorja": s.get("Constructor", {}).get("name", ""),
                "startno_mesto": int(s.get("grid", 0)),
                "koncno_mesto": int(mesto) if mesto.isdigit() else None,
                "tocke": float(s.get("points", 0.0)),
                "prevozeni_krogi": int(s.get("laps", 0)),
                "status": s.get("status", ""),
            })
    return pd.DataFrame(zapisi)
