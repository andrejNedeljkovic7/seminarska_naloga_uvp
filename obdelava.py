"""Modul za pretvorbo in strukturiranje surovih podatkov Formule 1 v tabele."""

import pandas as pd


def cas_v_sekunde(niz_casa):
    """Pretvori čas kroga ali trajanja (npr. '1:27.452') v sekunde kot float."""
    if not niz_casa or not isinstance(niz_casa, str):
        return None
    try:
        if ":" in niz_casa:
            minute, sekunde = niz_casa.split(":", 1)
            return float(minute) * 60 + float(sekunde)
        return float(niz_casa)
    except (ValueError, TypeError):
        return None


def sestavi_polno_ime(slovar_dirkaca):
    """Združi ime in priimek dirkača v enoten niz."""
    ime = slovar_dirkaca.get("givenName", "")
    priimek = slovar_dirkaca.get("familyName", "")
    return f"{ime} {priimek}".strip()


def obdelaj_lestvico_dirkacev(neobdelani_podatki):
    """Pretvori neobdelano lestvico dirkačev v pandas DataFrame."""
    zapisi = []
    for sezona, podatki in neobdelani_podatki.items():
        tabela = podatki.get("MRData", {}).get("StandingsTable", {})
        seznami = tabela.get("StandingsLists", [])
        if not seznami:
            continue
        for vrstica in seznami[0].get("DriverStandings", []):
            dirkac = vrstica.get("Driver", {})
            konstruktorji = vrstica.get("Constructors", [{}])
            ekipa = konstruktorji[0].get("name", "") if konstruktorji else ""
            zapisi.append({
                "sezona": int(sezona),
                "uvrstitev": int(vrstica.get("position", 0)),
                "tocke": float(vrstica.get("points", 0.0)),
                "zmage": int(vrstica.get("wins", 0)),
                "id_dirkaca": dirkac.get("driverId", ""),
                "ime_dirkaca": sestavi_polno_ime(dirkac),
                "drzavljanstvo": dirkac.get("nationality", ""),
                "ekipa": ekipa,
            })
    return pd.DataFrame(zapisi)


def obdelaj_lestvico_konstruktorjev(neobdelani_podatki):
    """Pretvori neobdelano lestvico konstruktorjev v pandas DataFrame."""
    zapisi = []
    for sezona, podatki in neobdelani_podatki.items():
        tabela = podatki.get("MRData", {}).get("StandingsTable", {})
        seznami = tabela.get("StandingsLists", [])
        if not seznami:
            continue
        for vrstica in seznami[0].get("ConstructorStandings", []):
            konstruktor = vrstica.get("Constructor", {})
            zapisi.append({
                "sezona": int(sezona),
                "uvrstitev": int(vrstica.get("position", 0)),
                "tocke": float(vrstica.get("points", 0.0)),
                "zmage": int(vrstica.get("wins", 0)),
                "id_konstruktorja": konstruktor.get("constructorId", ""),
                "ime_konstruktorja": konstruktor.get("name", ""),
                "drzavljanstvo": konstruktor.get("nationality", ""),
            })
    return pd.DataFrame(zapisi)


def obdelaj_rezultate_dirk(rezultati_sezon):
    """Pretvori rezultate posameznih dirk v strukturiran pandas DataFrame."""
    zapisi = []
    for sezona, strani in rezultati_sezon.items():
        for stran in strani:
            dirke = stran.get("MRData", {}).get("RaceTable", {}).get("Races", [])
            for dirka in dirke:
                st_dirke = int(dirka.get("round", 0))
                ime_dirke = dirka.get("raceName", "")
                dirkalisce = dirka.get("Circuit", {})
                id_dirkalisca = dirkalisce.get("circuitId", "")
                ime_dirkalisca = dirkalisce.get("circuitName", "")
                datum = dirka.get("date", "")

                for rez in dirka.get("Results", []):
                    dirkac = rez.get("Driver", {})
                    konstruktor = rez.get("Constructor", {})
                    najhitrejsi = rez.get("FastestLap", {})
                    cas_najhitrejsega = najhitrejsi.get("Time", {}).get("time")

                    mesto_niz = rez.get("position", "")
                    mesto_int = int(mesto_niz) if mesto_niz.isdigit() else None

                    r_niz = najhitrejsi.get("rank", "")
                    uvrstitev_kroga = int(r_niz) if r_niz.isdigit() else None

                    hitrost_niz = najhitrejsi.get(
                        "AverageSpeed", {}
                    ).get("speed")
                    hitrost_float = (
                        float(hitrost_niz) if hitrost_niz else None
                    )

                    zapisi.append({
                        "sezona": int(sezona),
                        "stevilka_dirke": st_dirke,
                        "ime_dirke": ime_dirke,
                        "id_dirkalisca": id_dirkalisca,
                        "ime_dirkalisca": ime_dirkalisca,
                        "datum": datum,
                        "id_dirkaca": dirkac.get("driverId", ""),
                        "koda_dirkaca": dirkac.get("code", ""),
                        "ime_dirkaca": sestavi_polno_ime(dirkac),
                        "id_konstruktorja": konstruktor.get("constructorId", ""),
                        "ime_konstruktorja": konstruktor.get("name", ""),
                        "startno_mesto": int(rez.get("grid", 0)),
                        "koncno_mesto": mesto_int,
                        "tocke": float(rez.get("points", 0.0)),
                        "status": rez.get("status", ""),
                        "prevozeni_krogi": int(rez.get("laps", 0)),
                        "uvrstitev_najhitrejsega_kroga": uvrstitev_kroga,
                        "cas_najhitrejsega_kroga": cas_najhitrejsega,
                        "sekunde_najhitrejsega_kroga": cas_v_sekunde(
                            cas_najhitrejsega
                        ),
                        "hitrost_najhitrejsega_kroga_kmh": hitrost_float,
                    })
    df = pd.DataFrame(zapisi)
    if not df.empty:
        df = df.drop_duplicates(
            subset=["sezona", "stevilka_dirke", "id_dirkaca"]
        )
    return df


def obdelaj_kvalifikacije(podatki_kvalifikacij):
    """Pretvori rezultate kvalifikacij v pregleden pandas DataFrame."""
    zapisi = []
    for sezona, strani in podatki_kvalifikacij.items():
        for stran in strani:
            dirke = stran.get("MRData", {}).get("RaceTable", {}).get("Races", [])
            for dirka in dirke:
                st_dirke = int(dirka.get("round", 0))
                ime_dirke = dirka.get("raceName", "")
                for q in dirka.get("QualifyingResults", []):
                    dirkac = q.get("Driver", {})
                    konstruktor = q.get("Constructor", {})
                    q1 = q.get("Q1")
                    q2 = q.get("Q2")
                    q3 = q.get("Q3")
                    najboljsi = q3 or q2 or q1

                    q_mesto_niz = str(q.get("position", ""))
                    q_mesto = (
                        int(q_mesto_niz) if q_mesto_niz.isdigit() else None
                    )

                    zapisi.append({
                        "sezona": int(sezona),
                        "stevilka_dirke": st_dirke,
                        "ime_dirke": ime_dirke,
                        "id_dirkaca": dirkac.get("driverId", ""),
                        "ime_dirkaca": sestavi_polno_ime(dirkac),
                        "id_konstruktorja": konstruktor.get("constructorId", ""),
                        "uvrstitev_kvalifikacij": q_mesto,
                        "q1": q1,
                        "q2": q2,
                        "q3": q3,
                        "najboljsi_cas_sekunde": cas_v_sekunde(najboljsi),
                    })
    df = pd.DataFrame(zapisi)
    if not df.empty:
        df = df.drop_duplicates(
            subset=["sezona", "stevilka_dirke", "id_dirkaca"]
        )
    return df


def obdelaj_postanke_v_boksih(podatki_postankov):
    """Pretvori podatke o postankih v boksih v pandas DataFrame."""
    zapisi = []
    for sezona, krogi in podatki_postankov.items():
        for st_kroga, podatki in krogi.items():
            dirke = podatki.get("MRData", {}).get("RaceTable", {}).get("Races", [])
            if not dirke:
                continue
            ime_dirke = dirke[0].get("raceName", "")
            for postanek in dirke[0].get("PitStops", []):
                trajanje_niz = postanek.get("duration", "")
                zapisi.append({
                    "sezona": int(sezona),
                    "stevilka_dirke": int(st_kroga),
                    "ime_dirke": ime_dirke,
                    "id_dirkaca": postanek.get("driverId", ""),
                    "stevilka_postanka": int(postanek.get("stop", 0)),
                    "krog_postanka": int(postanek.get("lap", 0)),
                    "trajanje_sekunde": cas_v_sekunde(trajanje_niz),
                })
    return pd.DataFrame(zapisi)


def obdelaj_sprint_rezultate(podatki_sprintov):
    """Pretvori rezultate sprint dirk v pandas DataFrame."""
    zapisi = []
    for sezona, podatki in podatki_sprintov.items():
        dirke = podatki.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        for dirka in dirke:
            st_dirke = int(dirka.get("round", 0))
            ime_dirke = dirka.get("raceName", "")
            for s in dirka.get("SprintResults", []):
                dirkac = s.get("Driver", {})
                konstruktor = s.get("Constructor", {})
                mesto_niz = str(s.get("position", ""))
                mesto_int = (
                    int(mesto_niz) if mesto_niz.isdigit() else None
                )

                zapisi.append({
                    "sezona": int(sezona),
                    "stevilka_dirke": st_dirke,
                    "ime_dirke": ime_dirke,
                    "id_dirkaca": dirkac.get("driverId", ""),
                    "ime_dirkaca": sestavi_polno_ime(dirkac),
                    "id_konstruktorja": konstruktor.get("constructorId", ""),
                    "ime_konstruktorja": konstruktor.get("name", ""),
                    "startno_mesto": int(s.get("grid", 0)),
                    "koncno_mesto": mesto_int,
                    "tocke": float(s.get("points", 0.0)),
                    "prevozeni_krogi": int(s.get("laps", 0)),
                    "status": s.get("status", ""),
                })
    return pd.DataFrame(zapisi)
