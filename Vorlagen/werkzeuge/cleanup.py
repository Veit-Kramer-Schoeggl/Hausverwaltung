#!/usr/bin/env python3
"""Entfernt typische pandoc-ODT->md Artefakte aus den konvertierten Dateien."""
import re, sys
from pathlib import Path

for fp in sys.argv[1:]:
    p = Path(fp)
    t = p.read_text(encoding="utf-8")

    # 1) span-Anker, eingebettete Bild-Platzhalter, leere Kommentare
    t = re.sub(r'<span id="anchor[^"]*"></span>\s*', '', t)
    t = re.sub(r'^\s*<img src="\./ObjectReplacements/[^>]*/>\s*$', '', t, flags=re.M)
    t = re.sub(r'^\s*<!-- -->\s*$', '', t, flags=re.M)

    # 2) 3+ Sternchen -> 2 (****fett**** -> **fett**)
    t = re.sub(r'\*{3,}', '**', t)

    # 3) leere Fett-Paare wiederholt entfernen ( ** **  /  **** )
    prev = None
    while prev != t:
        prev = t
        t = re.sub(r'\*\*(\s*)\*\*', r'\1', t)

    # 4) Fett-Umschalter mitten im Wort entfernen (Mit**t**lerweile -> Mittlerweile)
    prev = None
    while prev != t:
        prev = t
        t = re.sub(r'(\w)\*\*(\w)', r'\1\2', t)

    # 4b) Leerzeichen aus dem rechten Fett-Rand loesen (**Label: ** -> **Label:** )
    prev = None
    while prev != t:
        prev = t
        t = re.sub(r'\*\*([^\s*][^*\n]*?)[^\S\n]+\*\*', r'**\1** ', t)

    # 4b2) Fett um vereinzelte Satzzeichen entfernen (**)** -> ) , **.** -> . )
    t = re.sub(r'\*\*([^\w\s]{1,2})\*\*', r'\1', t)

    # 4c) ungerade (uebrige) Fett-Marker pro Zeile entfernen -> letztes ** weg
    def fix_odd(line):
        if line.count('**') % 2 == 1:
            i = line.rfind('**')
            line = line[:i] + line[i+2:]
        return line
    t = "\n".join(fix_odd(l) for l in t.split("\n"))

    # 5) Zeilen, die nur noch aus Sternchen/Whitespace bestehen
    t = re.sub(r'^[ \t]*\*\*[ \t]*$', '', t, flags=re.M)

    # 6) von pandoc escapte Aufzaehlungs-/Satzzeichen entschaerfen
    t = re.sub(r'(?<=\d)\\([.)])', r'\1', t)      # 2\)  9\.  -> 2) 9.
    t = t.replace(r'\>', '>')

    # 7) mehrfache Leerzeilen zusammenfassen
    t = re.sub(r'\n{3,}', '\n\n', t)
    t = t.strip() + "\n"

    p.write_text(t, encoding="utf-8")
    print("bereinigt:", fp)
