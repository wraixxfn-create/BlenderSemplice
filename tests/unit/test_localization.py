from __future__ import annotations

import re
import sys
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACCHETTO = ROOT / "addon" / "formafacile_3d"
if str(PACCHETTO) not in sys.path:
    sys.path.insert(0, str(PACCHETTO))

from localization import TESTI


SEGNAPOSTO_INGLESE = re.compile(
    r"\b(?:TODO|Click here|Save|Cancel|Render|Error|Welcome)\b",
    re.IGNORECASE,
)


class TestLocalizzazioneItaliana(unittest.TestCase):
    def test_tutti_i_testi_centrali_sono_presenti(self):
        self.assertGreaterEqual(len(TESTI), 20)
        for chiave, valore in TESTI.items():
            with self.subTest(chiave=chiave):
                self.assertTrue(valore.strip(), f"Testo vuoto: {chiave}")
                self.assertIsNone(SEGNAPOSTO_INGLESE.search(valore), f"Testo inglese non localizzato: {chiave}")

    def test_interfaccia_usa_la_risorsa_centrale(self):
        file_interfaccia = (PACCHETTO / "ui" / "panel.py").read_text(encoding="utf-8")
        file_operatore = (PACCHETTO / "operators" / "scene.py").read_text(encoding="utf-8")
        sorgenti = file_interfaccia + "\n" + file_operatore

        # Le etichette visibili sono recuperate dalla mappa italiana, non scritte
        # direttamente come stringhe nel codice dell'interfaccia.
        self.assertNotRegex(sorgenti, r"\bbl_label\s*=\s*[\"']")
        self.assertNotRegex(sorgenti, r"\bbl_description\s*=\s*[\"']")
        self.assertNotRegex(sorgenti, r"layout\.label\(\s*text\s*=\s*[\"']")
        self.assertNotRegex(sorgenti, r"layout\.operator\([^\n]*text\s*=\s*[\"']")

    def test_metadati_visibili_usano_testi_italiani(self):
        inizializzatore = (PACCHETTO / "__init__.py").read_text(encoding="utf-8")
        for campo in ("name", "author", "location", "description", "category"):
            with self.subTest(campo=campo):
                self.assertRegex(inizializzatore, rf'"{campo}"\s*:\s*TESTI\[')

        with (PACCHETTO / "blender_manifest.toml").open("rb") as manifesto:
            metadati = tomllib.load(manifesto)
        for campo in ("name", "tagline", "maintainer"):
            with self.subTest(campo=campo):
                self.assertIsNone(SEGNAPOSTO_INGLESE.search(metadati[campo]))

    def test_documentazione_iniziale_non_contiene_segnaposto_ui_inglesi(self):
        documenti = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
        for documento in documenti:
            testo = documento.read_text(encoding="utf-8")
            with self.subTest(file=documento.name):
                self.assertIsNone(SEGNAPOSTO_INGLESE.search(testo))


if __name__ == "__main__":
    unittest.main()
