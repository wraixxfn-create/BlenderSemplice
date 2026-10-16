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
    # Componente aggiuntivo: tutti i moduli della prima versione utilizzabile.
    CARTELLA_ADDON / "blender_manifest.toml",
    CARTELLA_ADDON / "__init__.py",
    CARTELLA_ADDON / "comandi.py",
    CARTELLA_ADDON / "configuration.py",
    CARTELLA_ADDON / "localization.py",
    CARTELLA_ADDON / "logging_service.py",
    CARTELLA_ADDON / "operators" / "__init__.py",
    CARTELLA_ADDON / "operators" / "base.py",
    CARTELLA_ADDON / "operators" / "assets.py",
    CARTELLA_ADDON / "operators" / "oggetti.py",
    CARTELLA_ADDON / "operators" / "scene.py",
    CARTELLA_ADDON / "operators" / "selezione.py",
    CARTELLA_ADDON / "operators" / "trasformazioni.py",
    CARTELLA_ADDON / "operators" / "vista.py",
    CARTELLA_ADDON / "operators" / "modellazione.py",
    CARTELLA_ADDON / "operators" / "insiemi.py",
    CARTELLA_ADDON / "operators" / "guide.py",
    CARTELLA_ADDON / "scene" / "__init__.py",
    CARTELLA_ADDON / "scene" / "messaggi.py",
    CARTELLA_ADDON / "scene" / "misure.py",
    CARTELLA_ADDON / "scene" / "nomi.py",
    CARTELLA_ADDON / "scene" / "primitives.py",
    CARTELLA_ADDON / "scene" / "libreria.py",
    CARTELLA_ADDON / "scene" / "stato.py",
    CARTELLA_ADDON / "scene" / "regole_modellazione.py",
    CARTELLA_ADDON / "scene" / "guide.py",
    CARTELLA_ADDON / "scene" / "testi.py",
    CARTELLA_ADDON / "blender" / "__init__.py",
    CARTELLA_ADDON / "blender" / "adapter.py",
    CARTELLA_ADDON / "blender" / "asset_library.py",
    CARTELLA_ADDON / "blender" / "oggetti.py",
    CARTELLA_ADDON / "blender" / "selezione.py",
    CARTELLA_ADDON / "blender" / "trasformazioni.py",
    CARTELLA_ADDON / "blender" / "vista.py",
    CARTELLA_ADDON / "blender" / "modificatori.py",
    CARTELLA_ADDON / "blender" / "allineamento.py",
    CARTELLA_ADDON / "blender" / "raccolte.py",
    CARTELLA_ADDON / "ui" / "__init__.py",
    CARTELLA_ADDON / "ui" / "icone.py",
    CARTELLA_ADDON / "ui" / "modello.py",
    CARTELLA_ADDON / "ui" / "panel.py",
    CARTELLA_ADDON / "ui" / "piano.py",
    CARTELLA_ADDON / "ui" / "renderer.py",
    CARTELLA_ADDON / "ui" / "vista.py",
    # Programmi di avvio e controllo.
    ROOT / "scripts" / "ambiente_bpy_locale.py",
    ROOT / "scripts" / "avvia_formafacile.py",
    ROOT / "scripts" / "bootstrap_blender.py",
    ROOT / "scripts" / "cli_italiano.py",
    ROOT / "scripts" / "controlla.py",
    ROOT / "scripts" / "crea_pacchetto.py",
    # Prove automatiche.
    ROOT / "tests" / "supporto_finto.py",
    ROOT / "tests" / "blender" / "test_addon.py",
    ROOT / "tests" / "unit" / "test_configuration.py",
    ROOT / "tests" / "unit" / "test_asset_library.py",
    ROOT / "tests" / "unit" / "test_misure.py",
    ROOT / "tests" / "unit" / "test_regole_modellazione.py",
    ROOT / "tests" / "unit" / "test_launcher.py",
    ROOT / "tests" / "unit" / "test_localization.py",
    ROOT / "tests" / "unit" / "test_packaging.py",
    ROOT / "tests" / "unit" / "test_piano.py",
    ROOT / "tests" / "unit" / "test_renderer.py",
    ROOT / "tests" / "unit" / "test_selezione.py",
    # Documentazione.
    ROOT / "docs" / "ARCHITETTURA.md",
    ROOT / "docs" / "LIMITAZIONI.md",
    ROOT / "docs" / "LICENZE.md",
    ROOT / "docs" / "REVISIONE_UX.md",
    ROOT / "docs" / "VERIFICA_MANUALE.md",
    ROOT / "docs" / "SVILUPPO.md",
    ROOT / "docs" / "VERIFICA_LINGUISTICA.md",
)

# Riga stampata dalle prove dentro Blender quando tutto è andato bene.
RIGA_SUCCESSO_TEST = "Test Blender superato:"

# Segnali con cui l'ambiente dice che il modulo bpy non c'è: in quel caso le prove
# con il modulo non si possono eseguire e il controllo lo dice, senza fingere di
# averle superate.
SEGNALI_BPY_ASSENTE = (
    "BPY_NON_DISPONIBILE",
    "AMBIENTE_BPY_ERRORE_LIBRERIE",
    "ModuleNotFoundError: No module named 'bpy'",
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


def _uscita_test(risultato: subprocess.CompletedProcess) -> tuple[bool, str]:
    """Giudica l'esito di un test eseguito in un altro processo.

    Non basta il codice di uscita: le prove stampano una riga di riepilogo e una
    traccia di errore Python significa che qualcosa è andato storto anche se il
    processo è terminato senza codice di errore.
    """
    uscita = f"{risultato.stdout or ''}\n{risultato.stderr or ''}"
    if risultato.returncode != 0:
        return False, uscita
    if RIGA_SUCCESSO_TEST not in uscita:
        return False, uscita
    if "Traceback (most recent call last)" in uscita:
        return False, uscita
    return True, uscita


def _mostra_coda(uscita: str, righe: int = 20) -> None:
    for riga in uscita.strip().splitlines()[-righe:]:
        print(f"  {riga}", file=sys.stderr)


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
        capture_output=True,
        text=True,
    )
    superato, uscita = _uscita_test(risultato)
    if not superato:
        print(
            TESTI["ERRORE_TEST_BLENDER"].format(versione=".".join(map(str, versione))),
            file=sys.stderr,
        )
        _mostra_coda(uscita)
        return False
    print(TESTI["TEST_BLENDER_RIUSCITO"])
    return True


def esegui_test_bpy(percorso_python: str | None) -> bool:
    """Esegue le prove del componente aggiuntivo con il modulo bpy, senza schermo."""
    print(TESTI["AVVIO_TEST_BPY"])
    comando = [sys.executable, str(ROOT / "scripts" / "ambiente_bpy_locale.py")]
    if percorso_python:
        comando += ["--python", percorso_python]
    risultato = subprocess.run(comando, cwd=ROOT, check=False, capture_output=True, text=True)
    uscita = f"{risultato.stdout or ''}\n{risultato.stderr or ''}"
    if any(segnale in uscita for segnale in SEGNALI_BPY_ASSENTE):
        print(TESTI["TEST_BPY_SALTATO"], file=sys.stderr)
        return True
    superato, uscita = _uscita_test(risultato)
    if not superato:
        print(TESTI["ERRORE_TEST_BPY"], file=sys.stderr)
        _mostra_coda(uscita)
        return False
    print(TESTI["TEST_BPY_RIUSCITO"])
    return True


def crea_parser() -> argparse.ArgumentParser:
    parser = ParserItaliano(description=TESTI["DESCRIZIONE_CONTROLLI"])
    parser.add_argument("--test-blender", action="store_true", help=TESTI["AIUTO_TEST_BLENDER"])
    parser.add_argument("--blender", help=TESTI["AIUTO_PERCORSO_TEST_BLENDER"])
    parser.add_argument("--test-bpy", action="store_true", help=TESTI["AIUTO_TEST_BPY"])
    parser.add_argument("--bpy-python", help=TESTI["AIUTO_PERCORSO_BPY"])
    return parser


def main(argomenti: list[str] | None = None) -> int:
    opzioni = crea_parser().parse_args(argomenti)
    esiti = [controlla_file_richiesti(), controlla_sintassi(), controlla_manifest()]
    esiti.append(esegui_test_unita())
    if opzioni.test_blender:
        esiti.append(esegui_test_blender(opzioni.blender))
    if opzioni.test_bpy:
        esiti.append(esegui_test_bpy(opzioni.bpy_python))
    return 0 if all(esiti) else 1


if __name__ == "__main__":
    raise SystemExit(main())
