#!/usr/bin/env python3
"""Carica il componente aggiuntivo dal repository nella sessione corrente di Blender."""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CARTELLA_ADDON = ROOT / "addon"
PACCHETTO = CARTELLA_ADDON / "formafacile_3d"
if str(CARTELLA_ADDON) not in sys.path:
    sys.path.insert(0, str(CARTELLA_ADDON))

SPEC_TESTI = importlib.util.spec_from_file_location(
    "_formafacile_testi",
    PACCHETTO / "localization.py",
)
if SPEC_TESTI is None or SPEC_TESTI.loader is None:
    raise RuntimeError("Risorsa linguistica non disponibile.")
MODULO_TESTI = importlib.util.module_from_spec(SPEC_TESTI)
SPEC_TESTI.loader.exec_module(MODULO_TESTI)
TESTI = MODULO_TESTI.TESTI

try:
    import bpy

    estensione = importlib.import_module("formafacile_3d")
    estensione.register()
    print(TESTI["AVVIO_COMPONENTE_RIUSCITO"])
except Exception:
    # Non vengono stampati percorsi o dati del progetto.
    print(TESTI["AVVIO_COMPONENTE_FALLITO"], file=sys.stderr)
