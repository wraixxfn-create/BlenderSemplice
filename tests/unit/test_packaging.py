from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts"
if str(SCRIPT) not in sys.path:
    sys.path.insert(0, str(SCRIPT))

import crea_pacchetto


class TestPacchettoEstensione(unittest.TestCase):
    def test_archivio_contiene_manifesto_codice_e_licenze(self):
        with tempfile.TemporaryDirectory() as directory:
            destinazione_precedente = crea_pacchetto.DESTINAZIONE
            crea_pacchetto.DESTINAZIONE = Path(directory)
            try:
                archivio = crea_pacchetto.crea_pacchetto()
            finally:
                crea_pacchetto.DESTINAZIONE = destinazione_precedente

            with ZipFile(archivio) as contenuto:
                nomi = set(contenuto.namelist())

        self.assertIn("formafacile_3d/blender_manifest.toml", nomi)
        self.assertIn("formafacile_3d/__init__.py", nomi)
        self.assertIn("formafacile_3d/LICENSE", nomi)
        self.assertIn("formafacile_3d/LICENZE.md", nomi)
        self.assertFalse(any("__pycache__" in nome or nome.endswith(".pyc") for nome in nomi))


if __name__ == "__main__":
    unittest.main()
