#!/usr/bin/env python3
"""Baut die Design-Schablone reference.docx fuer pandoc.
Stil: Modern Sans (Carlito), Akzentfarbe dezentes Blaugrau.
Ausgangsbasis: pandoc --print-default-data-file reference.docx
"""
import re, sys, shutil, subprocess, zipfile, os
from pathlib import Path

SRC = Path(sys.argv[1])   # extracted default reference dir
OUT = Path(sys.argv[2])   # output .docx path

ACCENT      = "34657F"   # Blaugrau (Linien, Tabellenkopf, H2/H3)
ACCENT_DARK = "2F4858"   # dunkles Blaugrau (Titel/H1)
ACCENT_SOFT = "49687C"   # weicheres Blaugrau (H3)
GREY_TXT    = "7A8893"   # Fusszeile
ROW_BORDER  = "DCE2E6"   # feine Zeilenlinie
BAND        = "F2F5F7"   # zarte Zebra-/Callout-Fuellung
RULE        = "BFC9D0"   # Tabellen-Rahmen aussen

def repl_style(xml, style_id, new_block):
    pat = re.compile(r'<w:style [^>]*w:styleId="%s".*?</w:style>' % re.escape(style_id), re.S)
    new, n = pat.subn(new_block.strip(), xml)
    assert n == 1, f"style {style_id}: {n} Treffer (erwartet 1)"
    return new

# ---------- theme1.xml : Carlito + Akzentfarbe ----------
theme = (SRC/"word/theme/theme1.xml").read_text(encoding="utf-8")
theme = theme.replace('typeface="Aptos Display"', 'typeface="Carlito"')
theme = theme.replace('typeface="Aptos"', 'typeface="Carlito"')
theme2, n = re.subn(r'(<a:accent1>\s*<a:srgbClr val=")[0-9A-Fa-f]{6}("\s*/>)',
                    r'\g<1>'+ACCENT+r'\2', theme)
assert n == 1, "accent1 nicht ersetzt"
(SRC/"word/theme/theme1.xml").write_text(theme2, encoding="utf-8")

# ---------- styles.xml ----------
st = (SRC/"word/styles.xml").read_text(encoding="utf-8")

# docDefaults: 11pt, Sprache de-AT, Zeilenabstand
st = st.replace('<w:sz w:val="24" />\n        <w:szCs w:val="24" />',
                '<w:sz w:val="22" />\n        <w:szCs w:val="22" />')
st = st.replace('w:val="en-US" w:eastAsia="zh-CN" w:bidi="ar-SA"',
                'w:val="de-AT" w:eastAsia="de-AT" w:bidi="ar-SA"')
st = st.replace('<w:pPrDefault>\n      <w:pPr>\n        <w:spacing w:after="200" />\n      </w:pPr>\n    </w:pPrDefault>',
                '<w:pPrDefault>\n      <w:pPr>\n        <w:spacing w:after="120" w:line="264" w:lineRule="auto" />\n      </w:pPr>\n    </w:pPrDefault>')

st = repl_style(st, "Title", f'''
<w:style w:type="paragraph" w:styleId="Title">
  <w:name w:val="Title" /><w:basedOn w:val="Normal" /><w:next w:val="BodyText" />
  <w:link w:val="TitleChar" /><w:uiPriority w:val="10" /><w:qFormat />
  <w:pPr><w:spacing w:after="60" w:line="240" w:lineRule="auto" /><w:contextualSpacing /></w:pPr>
  <w:rPr><w:rFonts w:asciiTheme="majorHAnsi" w:eastAsiaTheme="majorEastAsia" w:hAnsiTheme="majorHAnsi" w:cstheme="majorBidi" />
    <w:b /><w:color w:val="{ACCENT_DARK}" /><w:sz w:val="48" /><w:szCs w:val="48" /></w:rPr>
</w:style>''')

st = repl_style(st, "Heading1", f'''
<w:style w:type="paragraph" w:styleId="Heading1">
  <w:name w:val="heading 1" /><w:basedOn w:val="Normal" /><w:next w:val="BodyText" />
  <w:link w:val="Heading1Char" /><w:uiPriority w:val="9" /><w:qFormat />
  <w:pPr><w:keepNext /><w:keepLines /><w:spacing w:before="60" w:after="200" />
    <w:pBdr><w:bottom w:val="single" w:sz="8" w:space="6" w:color="{ACCENT}" /></w:pBdr>
    <w:outlineLvl w:val="0" /></w:pPr>
  <w:rPr><w:rFonts w:asciiTheme="majorHAnsi" w:eastAsiaTheme="majorEastAsia" w:hAnsiTheme="majorHAnsi" w:cstheme="majorBidi" />
    <w:b /><w:color w:val="{ACCENT_DARK}" /><w:sz w:val="44" /><w:szCs w:val="44" /></w:rPr>
</w:style>''')

st = repl_style(st, "Heading2", f'''
<w:style w:type="paragraph" w:styleId="Heading2">
  <w:name w:val="heading 2" /><w:basedOn w:val="Normal" /><w:next w:val="BodyText" />
  <w:link w:val="Heading2Char" /><w:uiPriority w:val="9" /><w:qFormat />
  <w:pPr><w:keepNext /><w:keepLines /><w:spacing w:before="320" w:after="80" /><w:outlineLvl w:val="1" /></w:pPr>
  <w:rPr><w:rFonts w:asciiTheme="majorHAnsi" w:eastAsiaTheme="majorEastAsia" w:hAnsiTheme="majorHAnsi" w:cstheme="majorBidi" />
    <w:b /><w:color w:val="{ACCENT}" /><w:sz w:val="30" /><w:szCs w:val="30" /></w:rPr>
</w:style>''')

st = repl_style(st, "Heading3", f'''
<w:style w:type="paragraph" w:styleId="Heading3">
  <w:name w:val="heading 3" /><w:basedOn w:val="Normal" /><w:next w:val="BodyText" />
  <w:link w:val="Heading3Char" /><w:uiPriority w:val="9" /><w:qFormat />
  <w:pPr><w:keepNext /><w:keepLines /><w:spacing w:before="220" w:after="60" /><w:outlineLvl w:val="2" /></w:pPr>
  <w:rPr><w:rFonts w:asciiTheme="majorHAnsi" w:eastAsiaTheme="majorEastAsia" w:hAnsiTheme="majorHAnsi" w:cstheme="majorBidi" />
    <w:b /><w:color w:val="{ACCENT_SOFT}" /><w:sz w:val="25" /><w:szCs w:val="25" /></w:rPr>
</w:style>''')

st = repl_style(st, "BodyText", '''
<w:style w:type="paragraph" w:styleId="BodyText">
  <w:name w:val="Body Text" /><w:basedOn w:val="Normal" /><w:link w:val="BodyTextChar" /><w:qFormat />
  <w:pPr><w:spacing w:before="0" w:after="140" /></w:pPr>
</w:style>''')

st = repl_style(st, "BlockText", f'''
<w:style w:type="paragraph" w:styleId="BlockText">
  <w:name w:val="Block Text" /><w:basedOn w:val="BodyText" /><w:next w:val="BodyText" />
  <w:uiPriority w:val="9" /><w:qFormat />
  <w:pPr><w:spacing w:before="60" w:after="60" /><w:ind w:left="284" w:right="142" />
    <w:pBdr><w:left w:val="single" w:sz="24" w:space="10" w:color="{ACCENT}" /></w:pBdr>
    <w:shd w:val="clear" w:color="auto" w:fill="{BAND}" /></w:pPr>
</w:style>''')

st = repl_style(st, "Table", f'''
<w:style w:type="table" w:default="1" w:styleId="Table">
  <w:name w:val="Table" /><w:basedOn w:val="TableNormal" /><w:qFormat />
  <w:pPr><w:spacing w:before="20" w:after="20" /></w:pPr>
  <w:tblPr><w:tblInd w:w="0" w:type="dxa" />
    <w:tblBorders>
      <w:top w:val="single" w:sz="4" w:space="0" w:color="{RULE}" />
      <w:bottom w:val="single" w:sz="4" w:space="0" w:color="{RULE}" />
      <w:insideH w:val="single" w:sz="2" w:space="0" w:color="{ROW_BORDER}" />
    </w:tblBorders>
    <w:tblCellMar><w:top w:w="40" w:type="dxa" /><w:left w:w="108" w:type="dxa" />
      <w:bottom w:w="40" w:type="dxa" /><w:right w:w="108" w:type="dxa" /></w:tblCellMar>
  </w:tblPr>
  <w:tblStylePr w:type="firstRow">
    <w:rPr><w:b /><w:color w:val="FFFFFF" /></w:rPr>
    <w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="{ACCENT}" />
      <w:tcBorders><w:bottom w:val="single" w:sz="4" w:space="0" w:color="{ACCENT}" /></w:tcBorders>
      <w:vAlign w:val="center" /></w:tcPr>
  </w:tblStylePr>
  <w:tblStylePr w:type="band2Horz">
    <w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="{BAND}" /></w:tcPr>
  </w:tblStylePr>
</w:style>''')

(SRC/"word/styles.xml").write_text(st, encoding="utf-8")

# ---------- footer1.xml ----------
NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"')
def run(txt, fld=None):
    rpr = f'<w:rPr><w:color w:val="{GREY_TXT}" /><w:sz w:val="16" /><w:szCs w:val="16" /></w:rPr>'
    if fld:
        return (f'<w:r>{rpr}<w:fldChar w:fldCharType="begin" /></w:r>'
                f'<w:r>{rpr}<w:instrText xml:space="preserve"> {fld} </w:instrText></w:r>'
                f'<w:r>{rpr}<w:fldChar w:fldCharType="end" /></w:r>')
    return f'<w:r>{rpr}<w:t xml:space="preserve">{txt}</w:t></w:r>'

footer = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
  f'<w:ftr {NS}>'
  f'<w:p><w:pPr>'
  f'<w:pBdr><w:top w:val="single" w:sz="4" w:space="6" w:color="{RULE}" /></w:pBdr>'
  f'<w:tabs><w:tab w:val="center" w:pos="4536" /><w:tab w:val="right" w:pos="9072" /></w:tabs>'
  f'<w:spacing w:after="0" /><w:rPr><w:color w:val="{GREY_TXT}" /><w:sz w:val="16" /></w:rPr></w:pPr>'
  + run("Paracelsusgasse 2 · Hausverwaltung")
  + f'<w:r><w:rPr><w:color w:val="{GREY_TXT}" /><w:sz w:val="16" /></w:rPr><w:tab /></w:r>'
  + run("Seite ") + run(None, "PAGE") + run(" / ") + run(None, "NUMPAGES")
  + f'<w:r><w:rPr><w:color w:val="{GREY_TXT}" /><w:sz w:val="16" /></w:rPr><w:tab /></w:r>'
  + '</w:p></w:ftr>')
(SRC/"word/footer1.xml").write_text(footer, encoding="utf-8")

# ---------- document.xml : sectPr (A4, Raender, Footer) ----------
doc = (SRC/"word/document.xml").read_text(encoding="utf-8")
new_sect = ('<w:sectPr>'
  '<w:footerReference w:type="default" r:id="rId900" />'
  '<w:footnotePr><w:numRestart w:val="eachSect" /></w:footnotePr>'
  '<w:pgSz w:w="11906" w:h="16838" />'
  '<w:pgMar w:top="1418" w:right="1418" w:bottom="1418" w:left="1418" w:header="709" w:footer="567" w:gutter="0" />'
  '<w:cols w:space="708" /><w:docGrid w:linePitch="360" />'
  '</w:sectPr>')
doc, n = re.subn(r'<w:sectPr>.*?</w:sectPr>', new_sect, doc, flags=re.S)
assert n == 1, "sectPr nicht ersetzt"
(SRC/"word/document.xml").write_text(doc, encoding="utf-8")

# ---------- relationships + content types ----------
rels = (SRC/"word/_rels/document.xml.rels").read_text(encoding="utf-8")
assert 'rId900' not in rels
rel = ('<Relationship Id="rId900" '
       'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" '
       'Target="footer1.xml" />')
rels = rels.replace('</Relationships>', rel + '</Relationships>')
(SRC/"word/_rels/document.xml.rels").write_text(rels, encoding="utf-8")

ct = (SRC/"[Content_Types].xml").read_text(encoding="utf-8")
ov = ('<Override PartName="/word/footer1.xml" '
      'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml" />')
ct = ct.replace('</Types>', ov + '</Types>')
(SRC/"[Content_Types].xml").write_text(ct, encoding="utf-8")

# ---------- re-zip ----------
if OUT.exists(): OUT.unlink()
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    # [Content_Types].xml zuerst (Konvention)
    z.write(SRC/"[Content_Types].xml", "[Content_Types].xml")
    for p in sorted(SRC.rglob("*")):
        if p.is_file() and p.name != "[Content_Types].xml":
            z.write(p, str(p.relative_to(SRC)))
print("OK ->", OUT)
