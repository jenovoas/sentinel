#!/usr/bin/env python3
# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
"""
translate_md_batch.py
---------------------
Traduce en lote todos los archivos Markdown que en ENGLISH_MD_LIST.md
están marcados como **Inglés**, generando un archivo hermano *_es.md*.

* Respeta bloques de código, tablas, fórmulas, front‑matter, etc.
* Usa Argos‑Translate (offline) – cambia `translate_text()` si quieres
  LibreTranslate o DeepL.
* Actualiza ENGLISH_MD_LIST.md añadiendo las nuevas filas en español.
"""

from __future__ import annotations

import re
import sys
import pathlib
import argparse
from typing import List, Tuple

# ------------------------------------------------------------
# 1️⃣  Backend de traducción  (Argos‑Translate – offline)
# ------------------------------------------------------------
try:
    import argostranslate.package
    import argostranslate.translate
except ImportError:
    sys.exit("❌  argostranslate no instalado → `pip install argostranslate`")

# Asegura que el modelo en→es esté instalado (primera ejecución descarga ~70 MB)
argostranslate.package.update_package_index()
available = argostranslate.package.get_available_packages()
en_es = next(
    (p for p in available if p.from_code == "en" and p.to_code == "es"), None
)
if en_es:
    en_es.download()
    en_es.install()


def translate_text(txt: str) -> str:
    """
    Traduce un párrafo plano (sin markdown). Argos funciona mejor con
    trozos < 500 caracteres; separamos por oraciones.
    """
    sentences = re.split(r"(?<=[.!?])\s+", txt.strip())
    out = []
    for s in sentences:
        if not s:
            continue
        out.append(argostranslate.translate.translate(s, "en", "es"))
    return " ".join(out)


# ------------------------------------------------------------
# 2️⃣  Protección de bloques que NO deben traducirse
# ------------------------------------------------------------
CODE_FENCE = re.compile(r"(^```.*?^```)", re.MULTILINE | re.DOTALL)
MATH_BLOCK = re.compile(r"(^\$\$.*?^\$\$)", re.MULTILINE | re.DOTALL)
INLINE_MATH = re.compile(r"(\$[^$]+\$)")
TABLE_ROW = re.compile(r"^\|.*\|$", re.MULTILINE)
FRONT_MATTER = re.compile(r"^---.*?^---", re.MULTILINE | re.DOTALL)

PH = "⟪TRANSLATE_BLOCK_{}⟫"   # token que nunca aparecerá en el markdown real


def protect_blocks(md: str) -> Tuple[str, List[str]]:
    """Sustituye bloques protegidos por tokens y devuelve (md_enmascarado, lista_bloques)."""
    blocks: List[str] = []

    def _repl(m):
        blocks.append(m.group(0))
        return PH.format(len(blocks) - 1)

    md = CODE_FENCE.sub(_repl, md)
    md = MATH_BLOCK.sub(_repl, md)
    md = INLINE_MATH.sub(_repl, md)
    md = TABLE_ROW.sub(_repl, md)
    md = FRONT_MATTER.sub(_repl, md)
    return md, blocks


def restore_blocks(md: str, blocks: List[str]) -> str:
    """Restaura los bloques originales sustituyendo los tokens."""
    def _repl(m):
        idx = int(m.group(1))
        return blocks[idx]

    return re.sub(PH.replace("{}", r"(\d+)"), _repl, md)


def translate_markdown(md: str) -> str:
    """Traduce solo la prosa del markdown, dejando intactos código, tablas, fórmulas…"""
    masked, blocks = protect_blocks(md)

    # Divide en párrafos (línea en blanco)
    paragraphs = re.split(r"\n\s*\n", masked)
    translated = []
    for para in paragraphs:
        if not para.strip():
            translated.append("")
            continue
        if para.strip().startswith("⟪TRANSLATE_BLOCK_"):
            translated.append(para)               # token → no tocar
        else:
            translated.append(translate_text(para))

    masked_translated = "\n\n".join(translated)
    return restore_blocks(masked_translated, blocks)


# ------------------------------------------------------------
# 3️⃣  Parsear ENGLISH_MD_LIST.md  (tabla pipe simple)
# ------------------------------------------------------------
LIST_PATH = pathlib.Path("ENGLISH_MD_LIST.md")


def parse_english_list() -> List[Tuple[int, pathlib.Path]]:
    """
    Devuelve lista de (número_de_línea_en_tabla, Path) para filas cuyo
    idioma = 'Inglés'.
    """
    if not LIST_PATH.exists():
        sys.exit(f"❌  No se encuentra {LIST_PATH}")

    content = LIST_PATH.read_text(encoding="utf-8")
    lines = content.splitlines()
    in_table = False
    results = []

    for i, line in enumerate(lines):
        if line.strip().startswith("| # |"):
            in_table = True
            continue
        if in_table:
            if not line.startswith("|"):
                break                     # fin de la tabla
            cols = [c.strip() for c in line.split("|")[1:-1]]  # quita bordes vacíos
            if len(cols) >= 3 and cols[2].lower().startswith("inglés"):
                rel_path = pathlib.Path(cols[1].strip("`"))
                results.append((i, rel_path))
    return results


# ------------------------------------------------------------
# 4️⃣  Driver principal
# ------------------------------------------------------------
def main(dry_run: bool = False):
    entries = parse_english_list()
    print(f"🔎  Encontrados {len(entries)} archivos markdown marcados como **Inglés**.")

    for line_no, rel_path in entries:
        src = pathlib.Path(rel_path)
        if not src.exists():
            print(f"⚠️  Archivo no existe (línea {line_no}): {src}")
            continue

        dst = src.with_name(src.stem + "_es" + src.suffix)
        print(f"📄  Traduciendo {src} → {dst}")

        md = src.read_text(encoding="utf-8")
        translated = translate_markdown(md)

        if not dry_run:
            dst.write_text(translated, encoding="utf-8")
            # Añade la nueva fila al final de la tabla maestra
            with LIST_PATH.open("a", encoding="utf-8") as f:
                f.write(f"| {len(entries)+1} | `{dst}` | Español (auto‑traducido) |\n")
        else:
            print("   (dry‑run – no se escribe)")

    print("✅  Traducción por lotes finalizada.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Traduce en lote markdowns ingleses → es‑ES los .md marcados en ENGLISH_MD_LIST.md (Argos‑Translate)."
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Muestra lo que haría sin escribir archivos."
    )
    args = parser.parse_args()
    main(dry_run=args.dry_run)