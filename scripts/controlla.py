#!/usr/bin/env python3
"""Controlla struttura, sintassi, localizzazione e test di FormaFacile 3D."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CARTELLA_ADDON = ROOT / "addon" / "formafacile_3d"
if str(CARTELLA_ADDON) not in sys.path:
    sys.path.insert(0, str(CARTELLA_ADDON))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from localization import TESTI  # noqa: E402
from cli_italiano import ParserItaliano  # noqa: E402
from avvia_formafacile import ErroreAvvio, trova_eseguibile_blender, verifica_versione_blender  # noqa: E402


FILE_RICHIESTI = (
    ROOT / "README.md",
    ROOT / "LICENSE",
    CARTELLA_ADDON / "blender_manifest.toml",
    CARTELLA_ADDON / "__init__.py",
    CARTELLA_ADDON / "localization.py",
    CARTELLA_ADDON / "operators" / "scene.py",
    CARTELLA_ADDON / "scene" / "primitives.py",
    CARTELLA_ADDON / "blender" / "adapter.py",
    CARTELLA_ADDON / "ui" / "panel.py",
    ROOT / "scripts" / "bootstrap_blender.py",
    ROOT / "scripts" / "cli_italiano.py",
    ROOT / "tests" / "blender" / "test_addon.py",
    ROOT / "docs" / "ARCHITETTURA.md",
    ROOT / "docs" / "LIMITAZIONI.md",
    ROOT / "docs" / "LICENZE.md",
)


def controlla_file_richiesti() -> bool:
    mancanti = [percorso.relative_to(ROOT) for percorso in FILE_RICHIESTI if not percorso.is_file()]
    if mancanti:
        print(TESTI["FILE_RICHIESTI_ASSENTI"], file=sys.stderr)
        for percorso in mancanti:
            print(f"  - {percorso}", file=sys.stderr)
        return False
    print(TESTI["CONTROLLO_FILE_RIUSCITO"])
    return True


def controlla_sintassi() -> bool:
    file_python = sorted(
        percorso
        for cartella in (ROOT / "addon", ROOT / "scripts", ROOT / "tests")
        for percorso in cartella.rglob("*.py")
        if "__pycache__" not in percorso.parts
    )
    try:
        for percorso in file_python:
            sorgente = percorso.read_text(encoding="utf-8")
            compile(sorgente, str(percorso), "exec")
    except (OSError, SyntaxError) as errore:
        relativo = percorso.relative_to(ROOT) if 'percorso' in locals() else Path("sorgente sconosciuta")
        numero_riga = getattr(errore, "lineno", 1) or 1
        print(
            TESTI["ERRORE_SINTASSI"].format(file=relativo, riga=numero_riga),
            file=sys.stderr,
        )
        return False
    print(TESTI["CONTROLLO_SINTASSI_RIUSCITO"])
    return True


def controlla_manifest() -> bool:
    percorso = CARTELLA_ADDON / "blender_manifest.toml"
    try:
        with percorso.open("rb") as file_manifest:
            manifest = tomllib.load(file_manifest)
        versione_minima = tuple(int(parte) for parte in manifest["blender_version_min"].split("."))
        valido = (
            manifest.get("id") == "formafacile_3d"
            and manifest.get("type") == "add-on"
            and versione_minima[:2] == (4, 5)
            and manifest.get("blender_version_max") == "4.6.0"
            and bool(manifest.get("license"))
        )
    except (OSError, KeyError, TypeError, ValueError, tomllib.TOMLDecodeError):
        valido = False

    if not valido:
        print(TESTI["ERRORE_MANIFEST"], file=sys.stderr)
        return False
    print(TESTI["CONTROLLO_MANIFEST_RIUSCITO"])
    return True


def esegui_test_unita() -> bool:
    risultato = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests" / "unit"), "-v"],
        cwd=ROOT,
        check=False,
    )
    if risultato.returncode != 0:
        return False
    print(TESTI["TEST_UNITA_RIUSCITI"])
    return True


def esegui_test_blender(percorso_blender: str | None) -> bool:
    try:
        eseguibile = trova_eseguibile_blender(percorso_blender)
        versione = verifica_versione_blender(eseguibile)
    except ErroreAvvio as errore:
        print(str(errore), file=sys.stderr)
        return False

    print(TESTI["AVVIO_TEST_BLENDER"])
    test = ROOT / "tests" / "blender" / "test_addon.py"
    risultato = subprocess.run(
        [str(eseguibile), "--background", "--factory-startup", "--python", str(test)],
        cwd=ROOT,
        check=False,
    )
    if risultato.returncode != 0:
        print(
            TESTI["ERRORE_TEST_BLENDER"].format(versione=".".join(map(str, versione))),
            file=sys.stderr,
        )
        return False
    print(TESTI["TEST_BLENDER_RIUSCITO"])
    return True


def crea_parser() -> argparse.ArgumentParser:
    parser = ParserItaliano(description=TESTI["DESCRIZIONE_CONTROLLI"])
    parser.add_argument("--test-blender", action="store_true", help=TESTI["AIUTO_TEST_BLENDER"])
    parser.add_argument("--blender", help=TESTI["AIUTO_PERCORSO_TEST_BLENDER"])
    return parser


def main(argomenti: list[str] | None = None) -> int:
    opzioni = crea_parser().parse_args(argomenti)
    esiti = [controlla_file_richiesti(), controlla_sintassi(), controlla_manifest()]
    esiti.append(esegui_test_unita())
    if opzioni.test_blender:
        esiti.append(esegui_test_blender(opzioni.blender))
    return 0 if all(esiti) else 1


if __name__ == "__main__":
    raise SystemExit(main())
