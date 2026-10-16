#!/usr/bin/env python3
"""Esegue i test di FormaFacile con il modulo `bpy`, anche senza Blender grafico.

Serve agli ambienti di sviluppo e di integrazione continua che non hanno uno
schermo. Il modulo `bpy` di PyPI richiede alcune librerie grafiche di sistema:
se mancano, questo programma ne prepara di fittizie nella cartella `.cache`
(usando il compilatore di sistema) e le usa solo per far partire i test in
modalità senza finestre. Non vengono installate nel sistema e non servono a
disegnare nulla: la grafica vera va provata con Blender completo.

Esempi:

    python3 scripts/ambiente_bpy_locale.py
    python3 scripts/ambiente_bpy_locale.py --file tests/blender/test_addon.py
    python3 scripts/ambiente_bpy_locale.py --prepara --python .venv/bin/python
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CARTELLA_ADDON = ROOT / "addon" / "formafacile_3d"
CARTELLA_LIBRERIE = ROOT / ".cache" / "librerie_bpy"
CARTELLA_SORGENTI = CARTELLA_LIBRERIE / "sorgenti"
FILE_PREDEFINITO = ROOT / "tests" / "blender" / "test_addon.py"

if str(CARTELLA_ADDON) not in sys.path:
    sys.path.insert(0, str(CARTELLA_ADDON))

from localization import TESTI  # noqa: E402
from cli_italiano import ParserItaliano  # noqa: E402

# Librerie grafiche che il modulo bpy cerca e che spesso non ci sono su un server.
LIBERE_FINTE = (
    "libXrender.so.1",
    "libXfixes.so.3",
    "libXi.so.6",
    "libxkbcommon.so.0",
    "libSM.so.6",
    "libICE.so.6",
    "libGL.so.1",
)

# Prefissi usati per capire a quale libreria appartiene un simbolo mancante.
PREFISSI_LIBRERIA = (
    ("XRender", "libXrender.so.1"),
    ("XFixes", "libXfixes.so.3"),
    ("XInput", "libXi.so.6"),
    ("XI", "libXi.so.6"),
    ("XOpenDevice", "libXi.so.6"),
    ("XCloseDevice", "libXi.so.6"),
    ("XListInputDevices", "libXi.so.6"),
    ("XFreeDeviceList", "libXi.so.6"),
    ("XQueryDeviceState", "libXi.so.6"),
    ("XFreeDeviceState", "libXi.so.6"),
    ("XSelectExtensionEvent", "libXi.so.6"),
    ("XGetExtensionVersion", "libXi.so.6"),
    ("_Xi", "libXi.so.6"),
    ("xkb", "libxkbcommon.so.0"),
    ("Smc", "libSM.so.6"),
    ("Sms", "libSM.so.6"),
    ("Ice", "libICE.so.6"),
    ("gl", "libGL.so.1"),
)

# Simboli forniti dal sistema o dall'interprete Python: non vanno ricreati.
SIMBOLI_DI_SISTEMA = re.compile(
    r"^(?:GLIBC_|GLIBCXX_|CXXABI_|GCC_|Py|_Py|__cxa_|__gxx_|_Unwind_|_ITM_|__tls_|__libc_|_dl_|__stack_chk)"
)


def ambiente_python(percorso: str | None) -> str:
    """Interprete da usare: quello indicato oppure quello corrente."""
    if percorso:
        return percorso
    candidato = ROOT / ".venv" / "bin" / "python"
    if candidato.is_file():
        return str(candidato)
    return sys.executable


def cartella_bpy(interprete: str) -> Path:
    """Cartella del pacchetto bpy installato, chiesta all'interprete indicato."""
    codice = (
        "import importlib.util, pathlib; "
        "spec = importlib.util.find_spec('bpy'); "
        "print(pathlib.Path(spec.submodule_search_locations[0]) if spec else '')"
    )
    esito = subprocess.run([interprete, "-c", codice], capture_output=True, text=True, check=False)
    percorso = esito.stdout.strip()
    if not percorso or not Path(percorso).is_dir():
        raise RuntimeError(TESTI["BPY_NON_DISPONIBILE"])
    return Path(percorso)


def _simboli_esterni(percorso: Path) -> tuple[set[str], dict[str, tuple[str, str]]]:
    """Restituisce i simboli definiti e quelli richiesti da una libreria."""
    definiti = subprocess.run(
        ["nm", "-D", "--defined-only", str(percorso)], capture_output=True, text=True, check=False
    )
    nomi = {riga.split()[-1].split("@")[0] for riga in definiti.stdout.splitlines() if riga.split()}

    tabella = subprocess.run(
        ["objdump", "-T", str(percorso)], capture_output=True, text=True, check=False
    )
    richiesti: dict[str, tuple[str, str]] = {}
    for riga in tabella.stdout.splitlines():
        if "*UND*" not in riga:
            continue
        pezzi = riga.split()
        if len(pezzi) < 3:
            continue
        nome = pezzi[-1]
        versione = ""
        for pezzo in pezzi:
            if pezzo.startswith("(") and pezzo.endswith(")"):
                versione = pezzo.strip("()")
        if not nome or versione.startswith(("GLIBC", "GLIBCXX", "CXXABI", "GCC")):
            continue
        richiesti.setdefault(nome, ("DO" if pezzi[-2] == "DO" else "DF", versione))
    return nomi, richiesti


def _libreria_per(simbolo: str) -> str:
    for prefisso, libreria in PREFISSI_LIBRERIA:
        if simbolo.startswith(prefisso):
            return libreria
    return "libGL.so.1"


def prepara_librerie(interprete: str, destinazione: Path = CARTELLA_LIBRERIE) -> Path:
    """Costruisce librerie fittizie con i simboli che il modulo bpy cerca."""
    libro = cartella_bpy(interprete)
    destinazione.mkdir(parents=True, exist_ok=True)
    CARTELLA_SORGENTI.mkdir(parents=True, exist_ok=True)

    librerie = [libro / "__init__.so"]
    librerie.extend(sorted((libro / "lib").glob("*.so*")))
    librerie = [percorso for percorso in librerie if percorso.is_file()]

    definiti: set[str] = set()
    richiesti: dict[str, tuple[str, str]] = {}
    for percorso in librerie:
        nomi, tabella = _simboli_esterni(percorso)
        definiti |= nomi
        for nome, valore in tabella.items():
            richiesti.setdefault(nome, valore)

    per_libreria: dict[str, dict[str, tuple[str, str]]] = {nome: {} for nome in LIBERE_FINTE}
    for nome, valore in sorted(richiesti.items()):
        if nome in definiti or SIMBOLI_DI_SISTEMA.match(nome):
            continue
        per_libreria[_libreria_per(nome)][nome] = valore

    for libreria, simboli in per_libreria.items():
        righe = ["/* Libreria fittizia generata da scripts/ambiente_bpy_locale.py */", "#include <stdlib.h>"]
        versioni: dict[str, list[str]] = {}
        for nome, (tipo, versione) in sorted(simboli.items()):
            if tipo == "DO":
                righe.append(f"char {nome}[512];")
            else:
                righe.append(f"int {nome}(void) {{ return 0; }}")
            if versione:
                versioni.setdefault(versione, []).append(nome)

        sorgente = CARTELLA_SORGENTI / f"{libreria}.c"
        sorgente.write_text("\n".join(righe) + "\n", encoding="utf-8")
        comando = ["gcc", "-shared", "-fPIC", "-o", str(destinazione / libreria), str(sorgente)]
        if versioni:
            mappa = CARTELLA_SORGENTI / f"{libreria}.map"
            mappa.write_text(
                "\n".join(
                    f"{versione} {{\n  global: {'; '.join(nomi)};\n}};"
                    for versione, nomi in sorted(versioni.items())
                )
                + "\n",
                encoding="utf-8",
            )
            comando += ["-Wl,--version-script", str(mappa)]
        subprocess.run(comando, check=True)

    print(TESTI["AMBIENTE_BPY_LIBRERIE_FINTE"].format(percorso=destinazione))
    return destinazione


def librerie_disponibili(destinazione: Path = CARTELLA_LIBRERIE) -> bool:
    """Indica se le librerie fittizie sono già state preparate."""
    return all((destinazione / nome).is_file() for nome in LIBERE_FINTE)


def esegui(percorso_file: Path, interprete: str, librerie: Path) -> int:
    """Esegue un file di test con il modulo bpy e le librerie fittizie."""
    ambiente = dict(os.environ)
    ambiente["LD_LIBRARY_PATH"] = os.pathsep.join(
        [str(librerie), ambiente.get("LD_LIBRARY_PATH", "")]
    ).rstrip(os.pathsep)
    print(TESTI["AMBIENTE_BPY_AVVIO"])
    esito = subprocess.run([interprete, str(percorso_file)], cwd=ROOT, env=ambiente, check=False)
    if esito.returncode != 0:
        print(TESTI["AMBIENTE_BPY_NON_RIUSCITO"], file=sys.stderr)
        return esito.returncode
    print(TESTI["AMBIENTE_BPY_FINITO"])
    return 0


def crea_parser() -> argparse.ArgumentParser:
    parser = ParserItaliano(description=TESTI["DESCRIZIONE_AMBIENTE_BPY"])
    parser.add_argument("--file", help=TESTI["AIUTO_FILE_AMBIENTE_BPY"], default=str(FILE_PREDEFINITO))
    parser.add_argument("--python", help=TESTI["AIUTO_PERCORSO_PYTHON"])
    parser.add_argument("--prepara", action="store_true", help=TESTI["AIUTO_PREPARA_LIBRERIE"])
    return parser


def main(argomenti: list[str] | None = None) -> int:
    opzioni = crea_parser().parse_args(argomenti)
    interprete = ambiente_python(opzioni.python)

    if opzioni.prepara or not librerie_disponibili():
        try:
            prepara_librerie(interprete)
        except (OSError, RuntimeError, subprocess.CalledProcessError) as errore:
            print(f"{TESTI['AMBIENTE_BPY_ERRORE_LIBRERIE']} {errore}", file=sys.stderr)
            return 2

    print(TESTI["AMBIENTE_BPY_PRONTO"])
    return esegui(Path(opzioni.file), interprete, CARTELLA_LIBRERIE)


if __name__ == "__main__":
    raise SystemExit(main())
