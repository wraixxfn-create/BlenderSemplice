from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts"
if str(SCRIPT) not in sys.path:
    sys.path.insert(0, str(SCRIPT))

import avvia_formafacile as avvio


class TestVersioneBlender(unittest.TestCase):
    def test_legge_la_versione_completa(self):
        self.assertEqual(avvio.analizza_versione_blender("Blender 4.5.14\n"), (4, 5, 14))

    def test_legge_la_versione_senza_revisione(self):
        self.assertEqual(avvio.analizza_versione_blender("Blender 4.5\n"), (4, 5, 0))

    def test_rifiuta_una_risposta_senza_versione(self):
        self.assertIsNone(avvio.analizza_versione_blender("versione non disponibile"))

    def test_guida_del_launcher_in_italiano(self):
        guida = avvio.crea_parser().format_help()
        self.assertIn("Uso:", guida)
        self.assertIn("opzioni", guida)
        self.assertNotIn("usage:", guida)
        self.assertNotIn("options", guida)

    def test_verifica_la_serie_supportata(self):
        with tempfile.TemporaryDirectory() as directory:
            eseguibile = Path(directory) / "blender"
            eseguibile.write_text("programma di prova", encoding="utf-8")
            eseguibile.chmod(eseguibile.stat().st_mode | 0o111)
            risposta = type("Risposta", (), {"returncode": 0, "stdout": "Blender 4.5.14", "stderr": ""})()
            with patch.object(avvio.subprocess, "run", return_value=risposta):
                self.assertEqual(avvio.verifica_versione_blender(eseguibile), (4, 5, 14))

    def test_rifiuta_una_serie_non_supportata(self):
        with tempfile.TemporaryDirectory() as directory:
            eseguibile = Path(directory) / "blender"
            risposta = type("Risposta", (), {"returncode": 0, "stdout": "Blender 5.2.2", "stderr": ""})()
            with patch.object(avvio.subprocess, "run", return_value=risposta):
                with self.assertRaises(avvio.ErroreAvvio):
                    avvio.verifica_versione_blender(eseguibile)


class TestRicercaBlender(unittest.TestCase):
    def test_preferisce_la_variabile_esplicita(self):
        with tempfile.TemporaryDirectory() as directory:
            eseguibile = Path(directory) / "blender-test"
            eseguibile.write_text("programma di prova", encoding="utf-8")
            eseguibile.chmod(eseguibile.stat().st_mode | 0o111)
            risultato = avvio.trova_eseguibile_blender(
                ambiente={"FORMAFACILE_BLENDER": str(eseguibile)},
                file_configurazione=Path(directory) / "inesistente.ini",
                sistema="linux",
                casa=Path(directory),
                cerca_nel_path=lambda _nome: None,
            )
            self.assertEqual(risultato, eseguibile.resolve())

    def test_legge_la_configurazione_utente(self):
        with tempfile.TemporaryDirectory() as directory:
            cartella = Path(directory)
            eseguibile = cartella / "blender-test"
            eseguibile.write_text("programma di prova", encoding="utf-8")
            eseguibile.chmod(eseguibile.stat().st_mode | 0o111)
            file_config = cartella / "config.ini"
            file_config.write_text(f"[blender]\nexecutable={eseguibile}\n", encoding="utf-8")
            risultato = avvio.trova_eseguibile_blender(
                ambiente={},
                file_configurazione=file_config,
                sistema="linux",
                casa=cartella,
                cerca_nel_path=lambda _nome: None,
            )
            self.assertEqual(risultato, eseguibile.resolve())

    def test_rifiuta_un_percorso_esplicito_mancante(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(avvio.ErroreAvvio):
                avvio.trova_eseguibile_blender(
                    percorso_esplicito=str(Path(directory) / "assente"),
                    ambiente={},
                    file_configurazione=Path(directory) / "config.ini",
                    sistema="linux",
                    casa=Path(directory),
                )

    def test_cartella_configurazione_rispetta_xdg(self):
        percorso = avvio.percorso_configurazione(
            ambiente={"XDG_CONFIG_HOME": "/tmp/config-test"},
            sistema="linux",
            casa=Path("/casa"),
        )
        self.assertEqual(percorso, Path("/tmp/config-test/formafacile3d/config.ini"))


if __name__ == "__main__":
    unittest.main()
