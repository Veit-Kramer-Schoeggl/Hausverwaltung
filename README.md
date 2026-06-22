# Hausverwaltung Paracelsusgasse 2

Versioniertes Ablage- und Dokumentensystem für die Hausverwaltertätigkeit.
Die **Quelle der Wahrheit sind Markdown-Dateien** (`.md`); daraus werden bei
Bedarf hübsche **PDF** und **DOCX** erzeugt. So bleibt alles diff- und
versionierbar, sieht aber gedruckt professionell aus.

## Ordnerstruktur

```
.
├── Vorlagen/                     Design-Schablone & Blueprints
│   ├── reference.docx            Layout (Schrift, Farben, Tabellen) für PDF/DOCX
│   ├── Protokoll_Vorlage.md      Blanko-Blueprint für Versammlungsprotokolle
│   └── werkzeuge/                Skripte zum Neu-Erzeugen der Schablone
├── build.sh                      Markdown → DOCX + PDF
├── Export/                       erzeugte PDF/DOCX (nicht versioniert)
├── App/                          (Platzhalter für eine spätere Eigentümer-App)
└── Objekt_Paracelsusgasse_2/     das Objekt
    ├── 2025/ 2026/ …             Versammlungen, Anlagen je Jahr
    ├── Korrespondenz/            Schriftverkehr
    └── …
```

## Voraussetzungen

- **pandoc** (installiert unter `~/.local/bin/pandoc`)
- **LibreOffice** (`soffice`) — wandelt das DOCX ins PDF, damit beide identisch aussehen

## PDF/DOCX erzeugen

```bash
./build.sh datei.md                # eine Datei → DOCX + PDF
./build.sh Objekt_Paracelsusgasse_2/2026/   # ein Ordner (rekursiv)
./build.sh                         # ALLE .md im Projekt
./build.sh --pdf datei.md          # nur PDF   (--docx = nur DOCX)
```

Ergebnisse landen unter `Export/<gleicher Pfad>/`. `Export/` wird bewusst **nicht**
versioniert — die Dateien lassen sich jederzeit neu bauen.

## Namensschema

Dateien werden nach `<Typ>_<MM>_<JJJJ>` benannt, z. B.
`Hauseigentümerversammlung_06_2026.md`, `Tagesordnung_03_2026.odt`,
`Anwesenheitsliste_06_2026.xlsx`. Gleiche Sitzung = gleicher Dateiname,
nur andere Endung (`.md` = finale Fassung, `.odt`/`.pdf` = Originale/Export).

## Neues Protokoll anlegen

1. `Vorlagen/Protokoll_Vorlage.md` in den Jahresordner kopieren, z. B.
   `Objekt_Paracelsusgasse_2/2026/Hauseigentümerversammlung_06_2026.md`
2. Platzhalter in `[eckigen Klammern]` ausfüllen.
3. `./build.sh <datei.md>` → fertiges PDF/DOCX im `Export/`.

## Design anpassen

Das Aussehen steckt in `Vorlagen/reference.docx` (Schrift **Carlito**, Akzentfarbe
dezentes Blaugrau). Zum Ändern entweder die DOCX direkt in LibreOffice bearbeiten
(Formatvorlagen *Überschrift 1–3*, *Standard*, *Tabelle* …) **oder** die Werte in
`Vorlagen/werkzeuge/build_reference.py` anpassen und neu erzeugen:

```bash
cd /tmp && rm -rf ref && mkdir ref \
  && (cd ref && unzip -q ~/IdeaProjects/Hausverwaltung/Vorlagen/werkzeuge/default-reference.docx) \
  && python3 ~/IdeaProjects/Hausverwaltung/Vorlagen/werkzeuge/build_reference.py ref \
       ~/IdeaProjects/Hausverwaltung/Vorlagen/reference.docx
```

## Konvertierung der Alt-Dokumente

Die ursprünglichen `.odt`-Dateien wurden mit pandoc nach `.md` konvertiert und von
typischen Konvertierungs-Artefakten bereinigt (`Vorlagen/werkzeuge/cleanup.py`).
Die Originale bleiben vorerst zur Sicherheit liegen.
