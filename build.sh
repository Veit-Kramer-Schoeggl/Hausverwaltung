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
#   ./build.sh --force ...                    auch unveränderte neu bauen
#
# Inkrementell: bereits aktuelle PDFs/DOCX werden übersprungen (es sei denn die
# Quelle, Vorlagen/reference.docx oder build.sh sind neuer). Mit --force erzwingen.
#
# Die Ausgaben landen unter  Export/<gleicher Pfad>/  und werden nicht versioniert.
# Design kommt aus  Vorlagen/reference.docx .
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REF="$ROOT/Vorlagen/reference.docx"
SELF="$ROOT/build.sh"
OUTROOT="$ROOT/Export"

WANT_DOCX=1; WANT_PDF=1; FORCE=0
ARGS=()
for a in "$@"; do
  case "$a" in
    --docx)  WANT_PDF=0 ;;
    --pdf)   WANT_DOCX=0 ;;
    --force) FORCE=1 ;;
    *)       ARGS+=("$a") ;;
  esac
done

command -v pandoc      >/dev/null || { echo "FEHLT: pandoc";      exit 1; }
[[ $WANT_PDF -eq 1 ]] && ! command -v soffice >/dev/null && ! command -v libreoffice >/dev/null \
  && { echo "FEHLT: libreoffice/soffice (für PDF)"; exit 1; }
SOFFICE="$(command -v soffice || command -v libreoffice || true)"
[[ -f "$REF" ]] || { echo "FEHLT: $REF"; exit 1; }

# Liste der zu bauenden .md-Dateien ermitteln
collect() {
  if [[ ${#ARGS[@]} -eq 0 ]]; then
    find "$ROOT" -name '*.md' -not -path "$ROOT/Vorlagen/*" -not -path "$ROOT/Export/*" \
                 -not -path "$ROOT/.git/*" -not -iname 'README.md' -not -iname 'MEMORY.md'
  else
    for t in "${ARGS[@]}"; do
      if   [[ -d "$t" ]]; then find "$t" -name '*.md'
      elif [[ -f "$t" ]]; then echo "$t"
      else echo "WARN: nicht gefunden: $t" >&2
      fi
    done
  fi
}

# Muss die Datei (neu) gebaut werden?
needs_build() {
  local md="$1" docx="$2" pdf="$3"
  [[ $FORCE -eq 1 ]] && return 0
  [[ $WANT_DOCX -eq 1 && ! -f "$docx" ]] && return 0
  [[ $WANT_PDF  -eq 1 && ! -f "$pdf"  ]] && return 0
  local outs=()
  [[ $WANT_DOCX -eq 1 ]] && outs+=("$docx")
  [[ $WANT_PDF  -eq 1 ]] && outs+=("$pdf")
  local out
  for out in "${outs[@]}"; do
    [[ "$md"   -nt "$out" ]] && return 0   # Quelle neuer
    [[ "$REF"  -nt "$out" ]] && return 0   # Design-Vorlage neuer
    [[ "$SELF" -nt "$out" ]] && return 0   # Build-Skript neuer
  done
  return 1
}

build_one() {
  local md="$1"
  local abs; abs="$(cd "$(dirname "$md")" && pwd)/$(basename "$md")"
  local rel="${abs#"$ROOT"/}"
  local outdir="$OUTROOT/$(dirname "$rel")"
  local base; base="$(basename "$md" .md)"
  local docx="$outdir/$base.docx"
  local pdf="$outdir/$base.pdf"

  if ! needs_build "$md" "$docx" "$pdf"; then
    echo "= aktuell: $rel"; SKIPPED=$((SKIPPED+1)); return 0
  fi

  mkdir -p "$outdir"
  # 'markdown-smart' statt 'gfm': nur so werden die Spaltenbreiten der
  # Tabellen (aus den Strichen der Trennzeile) übernommen; -smart lässt
  # die deutschen Anführungszeichen unangetastet.
  pandoc "$md" --reference-doc="$REF" --from markdown-smart -o "$docx"

  if [[ $WANT_PDF -eq 1 ]]; then
    # PDF aus dem DOCX -> identisches Aussehen wie die DOCX
    "$SOFFICE" --headless --convert-to pdf --outdir "$outdir" "$docx" >/dev/null 2>&1
  fi
  [[ $WANT_DOCX -eq 0 ]] && rm -f "$docx"
  echo "✓ gebaut:  $rel"; BUILT=$((BUILT+1))
}

BUILT=0; SKIPPED=0
while IFS= read -r md; do
  [[ -z "$md" ]] && continue
  build_one "$md"
done < <(collect)
echo "Fertig: $BUILT gebaut, $SKIPPED übersprungen -> $OUTROOT/"
