# Analiza podatkov Formule 1 (2018 – 2025)

Avtomatizirano orodje za zajem, predpomnjenje, obdelavo in vizualno analizo podatkov dirk Formule 1 za sezone od 2018 do vključno 2025.

Projekt pridobiva dirkaške podatke prek odprtokodnega vmesnika Jolpica Ergast API, shranjuje surove odgovore v lokalni predpomnilnik (za hitro izvajanje brez ponovnega obremenjevanja omrežja), pretvarja gnezdeno strukturo JSON v urejene tabele CSV ter ponuja poglobljeno analizo v interaktivnem Jupyter zvezku.

---

## Kazalo vsebine
- [Arhitektura programa](#arhitektura-programa)
- [Struktura repozitorija](#struktura-repozitorija)
- [Zahteve in namestitev](#zahteve-in-namestitev)
- [Zagon programa](#zagon-programa)
- [Ogled rezultatov analize](#ogled-rezultatov-analize)
- [Opis podatkovnih zbirk](#opis-podatkovnih-zbirk)
- [Ključna raziskovalna vprašanja](#ključna-raziskovalna-vprašanja)

---

## Arhitektura programa

Projekt je zasnovan modularno z jasno ločenimi nalogami:

```
[Jolpica Ergast API]
         │
         ▼
     zajem.py           ───> Lokalni predpomnilnik (podatki/predpomnilnik/*.json)
         │
         ▼
    obdelava.py         ───> Pretvorba v pandas DataFrame
         │
         ▼
 glavna_datoteka.py     ───> Izvoz v tabele CSV (podatki/obdelani/*.csv)
         │
         ▼
    analiza.ipynb       ───> Grafični prikazi in ugotovitve analize
```

1. **`zajem.py`**: Skrbi za poizvedbe na API z uporabo varne seje, ponovnih poskusov ob izpadih ter shranjevanja surovih odgovorov v mapo `podatki/predpomnilnik/`.
2. **`obdelava.py`**: Vsebuje namenske funkcije za pretvorbo surovih podatkov v urejene tabele (rezultati dirk, točke, kvalifikacije, sprint dirke, postanki v boksih in hitrosti krogov).
3. **`glavna_datoteka.py`**: Edina glavna zagonska datoteka, ki poveže zajem, obdelavo in izvoz podatkov v CSV.
4. **`analiza.ipynb`**: Interaktivni Jupyter zvezek z grafičnimi prikazi, tabelami in vsebinskimi razlagami.

---

## Struktura repozitorija

```
seminarska_naloga_uvp/
├── .gitignore                    # Prezrte začasne datoteke
├── README.md                     # Dokumentacija in navodila za uporabo
├── zahteve.txt                   # Seznam potrebnih knjižnic
├── requirements.txt              # Standardni indeks knjižnic
├── glavna_datoteka.py            # Edina glavna zagonska datoteka
├── zajem.py                      # Modul za zajem podatkov
├── obdelava.py                   # Modul za obdelavo podatkov
├── analiza.ipynb                 # Jupyter zvezek z vizualizacijami
└── podatki/
    ├── predpomnilnik/            # Shranjeni surovi JSON odgovori
    └── obdelani/                 # Končne tabele CSV za analizo
        ├── lestvica_konstruktorji.csv
        ├── lestvica_dirkaci.csv
        ├── postanki_v_boksih.csv
        ├── kvalifikacije.csv
        ├── rezultati_dirk.csv
        └── sprint_dirke.csv
```

---

## Zahteve in namestitev

### Predpogoji
- Nameščen Python (različica 3.10 ali novejša)
- Nameščen Git

### Namestitev knjižnic
Klonirajte repozitorij in namestite potrebne pakete:

```bash
git clone <povezava-do-repozitorija>
cd seminarska_naloga_uvp
pip install -r zahteve.txt
```

---

## Zagon programa

Celoten postopek zajema in osvežitve podatkov zaženete z zagonom edine glavne datoteke:

```bash
python glavna_datoteka.py
```

Program bo:
1. Preveril lokalni predpomnilnik oziroma prenesel manjkajoče podatke za sezone 2018–2025.
2. Pretvoril podatke v urejene tabele.
3. Shranil šest CSV tabel v mapo `podatki/obdelani/`.
4. V terminalu izpisal število obdelanih vrstic in povzetek izvajanja.

---

## Ogled rezultatov analize

Za interaktivni ogled grafov in statističnih ugotovitev zaženite Jupyter:

```bash
jupyter notebook analiza.ipynb
```

Zvezek lahko odprete tudi neposredno v Visual Studio Code, PyCharmu ali prek spletnega vmesnika na GitHubu, saj so vsi grafi in tabele vnaprej izrisani in shranjeni.

---

## Opis podatkovnih zbirk

| Ime datoteke | Vsebina | Ključni stolpci |
|---|---|---|
| `lestvica_dirkaci.csv` | Končne uvrstitve dirkačev po sezonah (2018–2025) | `sezona`, `uvrstitev`, `tocke`, `zmage`, `ime_dirkaca`, `ekipa` |
| `lestvica_konstruktorji.csv` | Uvrstitve ekip v konstruktorskem prvenstvu | `sezona`, `uvrstitev`, `tocke`, `zmage`, `ime_konstruktorja` |
| `rezultati_dirk.csv` | Podrobni rezultati posameznih dirk in najhitrejši krogi | `sezona`, `stevilka_dirke`, `ime_dirke`, `ime_dirkaca`, `startno_mesto`, `koncno_mesto`, `tocke`, `hitrost_najhitrejsega_kroga_kmh` |
| `kvalifikacije.csv` | Doseženi časi in uvrstitve na kvalifikacijah | `sezona`, `stevilka_dirke`, `ime_dirke`, `ime_dirkaca`, `uvrstitev_kvalifikacij`, `q1`, `q2`, `q3`, `najboljsi_cas_sekunde` |
| `postanki_v_boksih.csv` | Podatki o postankih in času menjave pnevmatik | `sezona`, `stevilka_dirke`, `ime_dirke`, `id_dirkaca`, `stevilka_postanka`, `trajanje_sekunde` |
| `sprint_dirke.csv` | Uvrstitve na sobotnih sprint dirkah (2021–2025) | `sezona`, `stevilka_dirke`, `ime_dirke`, `ime_dirkaca`, `startno_mesto`, `koncno_mesto`, `tocke` |

---

## Ključna raziskovalna vprašanja

1. **Obdobja prevlade**: Kako se je premoč gibala med Mercedesom (2018–2020), Red Bullom (2022–2023) in vzponom McLarna ter Ferrarija (2024–2025)?
2. **Učinek najboljšega štartnega položaja**: Kolikšen je delež zmag iz prvega štartnega mesta (Pole position) ter kakšna je korelacija med štartnim mestom in ciljem?
3. **Učinkovitost postankov v boksih**: Kakšna je mediana trajanja postanka v boksih in katera strategija menjave pnevmatik (1 ali 2 postanka) prevladuje?
4. **Hitrost na stezah**: Kako so pravila talnega učinka leta 2022 vplivala na povprečne hitrosti na dirkališčih Monza, Silverstone, Spa in Monako?
5. **Doprinos sprint dirk**: Kolikšen točkovni doprinos prinašajo sobotne sprint dirke in kdo so njihovi največji dobitniki?
