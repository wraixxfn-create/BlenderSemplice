"""Supporto italiano per le guide e gli errori dei comandi di sviluppo."""

from __future__ import annotations

import argparse
import sys

from localization import TESTI


class FormattatoreItaliano(argparse.HelpFormatter):
    def _format_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = TESTI["ARGPARSE_USO"]
        return super()._format_usage(usage, actions, groups, prefix)

    def start_section(self, heading):
        intestazioni = {
            "options": TESTI["ARGPARSE_OPZIONI"],
            "positional arguments": TESTI["ARGPARSE_POSIZIONALI"],
        }
        super().start_section(intestazioni.get(heading, heading))


class ParserItaliano(argparse.ArgumentParser):
    def __init__(self, *argomenti, **opzioni):
        opzioni.setdefault("formatter_class", FormattatoreItaliano)
        opzioni.setdefault("add_help", False)
        super().__init__(*argomenti, **opzioni)
        self.add_argument("-h", "--help", action="help", help=TESTI["ARGPARSE_AIUTO"])

    def error(self, messaggio):
        sostituzioni = (
            ("argument ", TESTI["ARGPARSE_PARAMETRO_PREFISSO"]),
            ("unrecognized arguments: ", TESTI["ARGPARSE_NON_RICONOSCIUTI_PREFISSO"]),
            (
                "the following arguments are required: ",
                TESTI["ARGPARSE_OBBLIGATORI_PREFISSO"],
            ),
            ("expected one argument", TESTI["ARGPARSE_UN_VALORE"]),
            ("expected at least one argument", TESTI["ARGPARSE_UNO_MINIMO"]),
            ("expected at most one argument", TESTI["ARGPARSE_UNO_MASSIMO"]),
            ("invalid choice: ", TESTI["ARGPARSE_SCELTA_PREFISSO"]),
            (" (choose from ", TESTI["ARGPARSE_VALORI_AMMESSI_PREFISSO"]),
        )
        for originale, tradotto in sostituzioni:
            messaggio = messaggio.replace(originale, tradotto)
        self.print_usage(sys.stderr)
        self.exit(2, TESTI["ARGPARSE_ERRORE"].format(messaggio=messaggio))
