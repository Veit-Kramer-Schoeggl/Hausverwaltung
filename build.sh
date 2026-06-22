#!/usr/bin/env bash
#
# build.sh – wandelt Markdown-Dateien in hübsche DOCX und PDF um.
#
# Verwendung:
#   ./build.sh datei.md                      eine Datei -> DOCX + PDF
#   ./build.sh ordner/                       alle .md in einem Ordner (rekursiv)
#   ./build.sh                               ALLE .md im Projekt (außer Vorlagen/, Export/)
#   ./build.sh --docx datei.md               nur DOCX
#   ./build.sh --pdf  datei.md               nur PDF
#
# Die Ausgaben landen unter  Export/<gleicher Pfad>/  und werden nicht versioniert.
# Design kommt aus  Vorlagen/reference.docx .
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REF="$ROOT/Vorlagen/reference.docx"
OUTROOT="$ROOT/Export"

WANT_DOCX=1; WANT_PDF=1
ARGS=()
for a in "$@"; do
  case "$a" in
    --docx) WANT_PDF=0 ;;
    --pdf)  WANT_DOCX=0 ;;
    *)      ARGS+=("$a") ;;
  esac
done

command -v pandoc      >/dev/null || { echo "FEHLT: pandoc";      exit 1; }
[[ $WANT_PDF -eq 1 ]] && ! command -v soffice >/dev/null && ! command -v libreoffice >/dev/null \
  && { echo "FEHLT: libreoffice/soffice (für PDF)"; exit 1; }
SOFFICE="$(command -v soffice || command -v libreoffice)"
[[ -f "$REF" ]] || { echo "FEHLT: $REF"; exit 1; }

# Liste der zu bauenden .md-Dateien ermitteln
collect() {
  if [[ ${#ARGS[@]} -eq 0 ]]; then
    find "$ROOT" -name '*.md' -not -path "$ROOT/Vorlagen/*" -not -path "$ROOT/Export/*" \
                 -not -iname 'README.md' -not -iname 'MEMORY.md'
  else
    for t in "${ARGS[@]}"; do
      if   [[ -d "$t" ]]; then find "$t" -name '*.md'
      elif [[ -f "$t" ]]; then echo "$t"
      else echo "WARN: nicht gefunden: $t" >&2
      fi
    done
  fi
}

build_one() {
  local md="$1"
  local abs; abs="$(cd "$(dirname "$md")" && pwd)/$(basename "$md")"
  local rel="${abs#"$ROOT"/}"
  local outdir="$OUTROOT/$(dirname "$rel")"
  local base; base="$(basename "$md" .md)"
  mkdir -p "$outdir"

  local docx="$outdir/$base.docx"
  # 'markdown-smart' statt 'gfm': nur so werden die Spaltenbreiten der
  # Tabellen (aus den Strichen der Trennzeile) übernommen; -smart lässt
  # die deutschen Anführungszeichen unangetastet.
  pandoc "$md" --reference-doc="$REF" --from markdown-smart -o "$docx"

  if [[ $WANT_PDF -eq 1 ]]; then
    # PDF aus dem DOCX -> identisches Aussehen wie die DOCX
    "$SOFFICE" --headless --convert-to pdf --outdir "$outdir" "$docx" >/dev/null 2>&1
  fi
  [[ $WANT_DOCX -eq 0 ]] && rm -f "$docx"
  echo "✓ $rel"
}

n=0
while IFS= read -r md; do
  [[ -z "$md" ]] && continue
  build_one "$md"; n=$((n+1))
done < <(collect)
echo "Fertig: $n Datei(en) -> $OUTROOT/"
