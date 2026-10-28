# Analiza podatkov Formule 1 (2018 – 2025)

Orodje za prenos, predpomnjenje, obdelavo in analizo podatkov dirk Formule 1 za sezone 2018–2025.

Podatke prenesem prek odprtega API-ja Jolpica (Ergast), surove odgovore shranim v lokalni predpomnilnik, jih pretvorim v tabele CSV in analiziram v Jupyter zvezku.

---

## Struktura repozitorija

```
seminarska_naloga_uvp/
├── .gitignore                  # prezrte začasne datoteke
├── README.md                   # navodila za uporabo
├── requirements.txt            # seznam potrebnih knjižnic
├── glavna_datoteka.py          # edina vstopna točka programa
├── zajem.py                    # prenos podatkov in predpomnjenje
├── obdelava.py                 # pretvorba JSON v tabele pandas
├── analiza.ipynb               # zvezek z izračuni in grafi
└── podatki/
    ├── predpomnilnik/          # shranjeni surovi JSON odgovori
    └── obdelani/               # končne tabele CSV
        ├── lestvica_dirkaci.csv
        ├── lestvica_konstruktorji.csv
        ├── rezultati_dirk.csv
        ├── kvalifikacije.csv
        ├── sprint_dirke.csv
        └── postanki_v_boksih.csv
```

---

## Kaj dela koda

- **`zajem.py`** – prenaša podatke s končnih točk API-ja. API vrača največ 100 zapisov na zahtevek, zato funkcija `prenesi_vse_strani()` prebere vse strani (rezultati, kvalifikacije in sprint dirke). Vsak odgovor se shrani v `podatki/predpomnilnik/`, tako da naslednji zagon ne potrebuje omrežja. Če prenos po treh poskusih ne uspe, program javi napako in se ustavi, namesto da bi shranil nepopolne podatke.
- **`obdelava.py`** – pretvori gnezdene odgovore JSON v tabele pandas (lestvici, rezultati dirk, kvalifikacije, sprint dirke, postanki).
- **`glavna_datoteka.py`** – poveže obe zgornji datoteki in shrani šest tabel CSV v `podatki/obdelani/`.
- **`analiza.ipynb`** – izračuni, grafi in razlage.

---

## Namestitev in zagon

```bash
git clone https://github.com/andrejNedeljkovic7/seminarska_naloga_uvp.git
cd seminarska_naloga_uvp
pip install -r requirements.txt
python glavna_datoteka.py
```

Zagon traja nekaj minut, ker program ob prvem zagonu prenese podatke za osem sezon. Ob ponovnem zagonu se uporabi predpomnilnik.

Za ogled analize odprite zvezek:

```bash
jupyter notebook analiza.ipynb
```

---

## Opis tabel

| Datoteka | Vsebina | Ključni stolpci |
|---|---|---|
| `lestvica_dirkaci.csv` | končne uvrstitve dirkačev po sezonah | `sezona`, `uvrstitev`, `tocke`, `zmage`, `ime_dirkaca`, `ekipa` |
| `lestvica_konstruktorji.csv` | uvrstitve ekip v konstruktorskem prvenstvu | `sezona`, `uvrstitev`, `tocke`, `zmage`, `ime_konstruktorja` |
| `rezultati_dirk.csv` | rezultati dirk z najhitrejšimi krogi in hitrostmi | `sezona`, `stevilka_dirke`, `ime_dirke`, `ime_dirkaca`, `startno_mesto`, `koncno_mesto`, `hitrost_najhitrejsega_kroga_kmh` |
| `kvalifikacije.csv` | uvrstitve in časi iz kvalifikacij | `sezona`, `stevilka_dirke`, `ime_dirkaca`, `uvrstitev_kvalifikacij`, `q1`, `q2`, `q3` |
| `sprint_dirke.csv` | uvrstitve in točke s sprint dirk (2021–2025) | `sezona`, `stevilka_dirke`, `ime_dirkaca`, `startno_mesto`, `koncno_mesto`, `tocke` |
| `postanki_v_boksih.csv` | trajanje postankov v boksih | `sezona`, `stevilka_dirke`, `id_dirkaca`, `stevilka_postanka`, `krog_postanka`, `trajanje_sekunde` |

---

## Omejitve podatkov

- **Postanki v boksih**: API ponuja postanke le po posamezni dirki, zato jih prenašam za pet vzorčnih dirk v sezoni (1., 5., 10., 15. in 20. krog koledarja). Tabela `postanki_v_boksih.csv` je zato vzorec in ne zajema vseh dirk. Za sezono 2020 20. dirka ne obstaja (sezona je imela 17 dirk), zato je pri tej sezoni petih dirk manj; to je pri zagonu izpisano kot opozorilo.
- **Hitrosti najhitrejših krogov**: v viru za leto 2025 ni podatka o hitrosti najhitrejšega kroga, zato se grafi hitrosti končajo z letom 2024. Manjkajo tudi posamezne dirke (Monako 2020 je bil odpovedan, za Monako 2024 in Spa 2021 pa v viru ni podatka).
- **Sprint točke**: leta 2021 so točke dobili trije najboljši (3-2-1), od leta 2022 naprej prvih osem (8-7-…-1). Skupne vsote po dirkačih zato mešajo dva različna sistema.
- **Najboljši štartni položaj**: za "pole" v analizi vzamem prvo mesto v kvalifikacijah (`kvalifikacije.csv`), ne prvega štartnega mesta iz rezultatov, ker se zaradi kazni lahko razlikujeta.
