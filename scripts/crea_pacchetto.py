#!/usr/bin/env python3
"""Crea un archivio installabile dell'estensione usando solo la libreria standard."""

from __future__ import annotations

import tomllib
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CARTELLA_ADDON = ROOT / "addon" / "formafacile_3d"
DESTINAZIONE = ROOT / "dist"
if str(CARTELLA_ADDON) not in sys.path:
    sys.path.insert(0, str(CARTELLA_ADDON))

from localization import TESTI  # noqa: E402


def crea_pacchetto() -> Path:
    with (CARTELLA_ADDON / "blender_manifest.toml").open("rb") as file_manifest:
        manifest = tomllib.load(file_manifest)

    nome_archivio = f"{manifest['id']}-{manifest['version']}.zip"
    DESTINAZIONE.mkdir(parents=True, exist_ok=True)
    archivio = DESTINAZIONE / nome_archivio

    with zipfile.ZipFile(archivio, "w", compression=zipfile.ZIP_DEFLATED) as pacchetto:
        for file in sorted(CARTELLA_ADDON.rglob("*")):
            if not file.is_file() or "__pycache__" in file.parts:
                continue
            nome_interno = Path(manifest["id"]) / file.relative_to(CARTELLA_ADDON)
            pacchetto.write(file, nome_interno.as_posix())

        for file in (ROOT / "LICENSE", ROOT / "docs" / "LICENZE.md"):
            if file.is_file():
                pacchetto.write(file, (Path(manifest["id"]) / file.name).as_posix())

    return archivio


if __name__ == "__main__":
    print(TESTI["PACCHETTO_CREATO"].format(percorso=crea_pacchetto()))
