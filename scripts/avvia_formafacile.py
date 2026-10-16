#!/usr/bin/env python3
"""Trova Blender 4.5 LTS e avvia la copia di sviluppo di FormaFacile 3D."""

from __future__ import annotations

import argparse
import configparser
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
PACCHETTO = ROOT / "addon" / "formafacile_3d"
if str(PACCHETTO) not in sys.path:
    sys.path.insert(0, str(PACCHETTO))

from localization import TESTI  # noqa: E402
from cli_italiano import ParserItaliano  # noqa: E402

SERIE_BLENDER_SUPPORTATA = (4, 5)
_PATTERN_VERSIONE = re.compile(r"\bBlender\s+(\d+)\.(\d+)(?:\.(\d+))?\b", re.IGNORECASE)


class ErroreAvvio(RuntimeError):
    """Errore gestibile di individuazione o avvio di Blender."""


def percorso_configurazione(
    ambiente: Mapping[str, str] | None = None,
    sistema: str | None = None,
    casa: Path | None = None,
) -> Path:
    """Restituisce la posizione di configurazione secondo le convenzioni del sistema."""
    ambiente = os.environ if ambiente is None else ambiente
    sistema = sys.platform if sistema is None else sistema
    casa = Path.home() if casa is None else Path(casa)

    if sistema.startswith("win"):
        base = Path(ambiente.get("APPDATA", casa / "AppData" / "Roaming"))
        return base / "FormaFacile3D" / "config.ini"
    if sistema == "darwin":
        return casa / "Library" / "Application Support" / "FormaFacile3D" / "config.ini"

    base = Path(ambiente.get("XDG_CONFIG_HOME", casa / ".config"))
    return base / "formafacile3d" / "config.ini"


def _eseguibile_configurato(file_configurazione: Path) -> str | None:
    configurazione = configparser.ConfigParser(interpolation=None)
    try:
        configurazione.read(file_configurazione, encoding="utf-8")
        valore = configurazione.get("blender", "executable", fallback="").strip()
        return valore or None
    except (OSError, configparser.Error):
        return None


def _percorsi_standard(
    sistema: str,
    ambiente: Mapping[str, str],
    casa: Path,
) -> list[Path]:
    """Aggiunge solo posizioni di installazione convenzionali, mai percorsi personali fissi."""
    risultati: list[Path] = []
    if sistema.startswith("win"):
        radici = [
            Path(ambiente[chiave])
            for chiave in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA")
            if ambiente.get(chiave)
        ]
        for radice in radici:
            if radice.name.lower() == "local":
                radice = radice / "Programs"
            risultati.extend((radice / "Blender Foundation").glob("Blender */blender.exe"))
    elif sistema == "darwin":
        risultati.extend(
            [
                Path("/Applications/Blender.app/Contents/MacOS/Blender"),
                casa / "Applications" / "Blender.app" / "Contents" / "MacOS" / "Blender",
            ]
        )
    else:
        risultati.extend(
            [
                Path("/usr/bin/blender"),
                Path("/usr/local/bin/blender"),
                Path("/snap/bin/blender"),
                casa / ".local" / "bin" / "blender",
            ]
        )
        for radice in (Path("/opt"), casa / "Applications"):
            if radice.is_dir():
                risultati.extend(radice.glob("blender*/blender"))
    return risultati


def trova_eseguibile_blender(
    percorso_esplicito: str | None = None,
    ambiente: Mapping[str, str] | None = None,
    file_configurazione: Path | None = None,
    sistema: str | None = None,
    casa: Path | None = None,
    cerca_nel_path=shutil.which,
) -> Path:
    """Trova un eseguibile tramite opzione, variabile, configurazione, PATH o posizioni standard."""
    ambiente = os.environ if ambiente is None else ambiente
    sistema = sys.platform if sistema is None else sistema
    casa = Path.home() if casa is None else Path(casa)
    file_configurazione = file_configurazione or percorso_configurazione(ambiente, sistema, casa)

    forzato = percorso_esplicito or ambiente.get("FORMAFACILE_BLENDER")
    if forzato:
        candidato = Path(os.path.expandvars(forzato)).expanduser()
        if candidato.is_file() and (sistema.startswith("win") or os.access(candidato, os.X_OK)):
            return candidato.resolve()
        raise ErroreAvvio(TESTI["PERCORSO_BLENDER_NON_VALIDO"])

    valore_configurato = _eseguibile_configurato(file_configurazione)
    candidati: list[Path] = []
    if valore_configurato:
        candidati.append(Path(os.path.expandvars(valore_configurato)).expanduser())

    trovato_nel_path = cerca_nel_path("blender")
    if trovato_nel_path:
        candidati.append(Path(trovato_nel_path))
    if sistema.startswith("win"):
        trovato_nel_path = cerca_nel_path("blender.exe")
        if trovato_nel_path:
            candidati.append(Path(trovato_nel_path))

    candidati.extend(_percorsi_standard(sistema, ambiente, casa))
    visitati: set[str] = set()
    for candidato in candidati:
        chiave = os.path.normcase(str(candidato.expanduser()))
        if chiave in visitati:
            continue
        visitati.add(chiave)
        candidato = candidato.expanduser()
        if candidato.is_file() and (sistema.startswith("win") or os.access(candidato, os.X_OK)):
            return candidato.resolve()

    raise ErroreAvvio(TESTI["BLENDER_NON_TROVATO"])


def analizza_versione_blender(risposta: str) -> tuple[int, int, int] | None:
    corrispondenza = _PATTERN_VERSIONE.search(risposta)
    if corrispondenza is None:
        return None
    principale, secondaria, revisione = corrispondenza.groups()
    return int(principale), int(secondaria), int(revisione or 0)


def verifica_versione_blender(eseguibile: Path) -> tuple[int, int, int]:
    try:
        risultato = subprocess.run(
            [str(eseguibile), "--version"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as errore:
        raise ErroreAvvio(TESTI["VERSIONE_BLENDER_NON_LEGGIBILE"]) from errore

    versione = analizza_versione_blender(risultato.stdout + "\n" + risultato.stderr)
    if risultato.returncode != 0 or versione is None:
        raise ErroreAvvio(TESTI["VERSIONE_BLENDER_NON_LEGGIBILE"])
    if versione[:2] != SERIE_BLENDER_SUPPORTATA:
        descrizione = ".".join(str(parte) for parte in versione)
        raise ErroreAvvio(TESTI["VERSIONE_BLENDER_NON_SUPPORTATA"].format(versione=descrizione))
    return versione


def crea_parser() -> argparse.ArgumentParser:
    parser = ParserItaliano(
        description=TESTI["DESCRIZIONE_AVVIO"],
        usage=TESTI["USO_LAUNCHER"],
    )
    parser.add_argument("--blender", help=TESTI["AIUTO_PERCORSO_BLENDER"])
    parser.add_argument(
        "argomenti_blender",
        nargs=argparse.REMAINDER,
        help=TESTI["AIUTO_ARGOMENTI_BLENDER"],
    )
    return parser


def main(argomenti: Sequence[str] | None = None) -> int:
    argomenti = list(sys.argv[1:] if argomenti is None else argomenti)
    parser = crea_parser()
    opzioni = parser.parse_args(argomenti)

    try:
        eseguibile = trova_eseguibile_blender(opzioni.blender)
        verifica_versione_blender(eseguibile)
    except ErroreAvvio as errore:
        print(str(errore), file=sys.stderr)
        return 2

    passati = list(opzioni.argomenti_blender)
    if passati and passati[0] == "--":
        passati.pop(0)

    comando = [str(eseguibile), "--python", str(ROOT / "scripts" / "bootstrap_blender.py"), *passati]
    print(TESTI["AVVIO_BLENDER"])
    try:
        return subprocess.run(comando, check=False).returncode
    except OSError:
        print(TESTI["ERRORE_AVVIO_BLENDER"], file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
