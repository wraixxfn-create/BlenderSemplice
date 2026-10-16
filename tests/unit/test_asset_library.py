"""Prove del catalogo italiano e dei campi della libreria di modelli."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
for _percorso in (ROOT / "tests", ROOT / "addon"):
    if str(_percorso) not in sys.path:
        sys.path.insert(0, str(_percorso))

import supporto_finto  # noqa: E402

supporto_finto.prepara_import_puro()

from formafacile_3d.localization import TESTI  # noqa: E402
from formafacile_3d.scene import libreria  # noqa: E402


SEGNAPOSTO_INGLESE = re.compile(r"\b(?:TODO|Click here|Save|Cancel|Render|Error|Welcome)\b", re.IGNORECASE)


class TestCatalogoLibreria(unittest.TestCase):
    def test_catalogo_iniziale_contiene_dieci_modelli_con_id_unici(self):
        identificatori = [voce.identificatore for voce in libreria.SCHEDE]
        self.assertEqual(len(identificatori), 10)
        self.assertEqual(len(set(identificatori)), len(identificatori))
        self.assertEqual(len(libreria.voci_elenco()), len(libreria.SCHEDE))

    def test_tutti_i_modelli_hanno_descrizioni_italiane_senza_falsa_promessa_parametrica(self):
        for voce in libreria.SCHEDE:
            with self.subTest(modello=voce.identificatore):
                self.assertTrue(voce.nome)
                self.assertTrue(voce.descrizione)
                self.assertIsNone(SEGNAPOSTO_INGLESE.search(voce.nome))
                self.assertIsNone(SEGNAPOSTO_INGLESE.search(voce.descrizione))
                self.assertRegex(voce.descrizione.casefold(), r"mesh|testo")
                self.assertRegex(voce.descrizione.casefold(), r"statica|statiche")
                self.assertRegex(voce.descrizione.casefold(), r"modifica|regolabili")

    def test_voci_dell_elenco_usano_nome_descrizione_e_identificatore_della_scheda(self):
        for voce, (identificatore, nome, descrizione) in zip(libreria.SCHEDE, libreria.voci_elenco()):
            with self.subTest(modello=voce.identificatore):
                self.assertEqual(identificatore, voce.identificatore)
                self.assertEqual(nome, TESTI[voce.chiave_nome])
                self.assertEqual(descrizione, TESTI[voce.chiave_descrizione])

    def test_campi_di_ogni_modello_esistono_e_hanno_etichetta_italiana(self):
        for voce in libreria.SCHEDE:
            with self.subTest(modello=voce.identificatore):
                self.assertTrue(voce.campi)
                for campo in voce.campi:
                    self.assertIn(campo, libreria.CAMPI)
                    self.assertTrue(libreria.nome_campo(campo))

    def test_scheda_sconosciuta_ripiega_sul_tavolino_e_non_viene_accettata_dal_creatore(self):
        self.assertEqual(libreria.scheda("sconosciuto").identificatore, libreria.ID_PREDEFINITO)
        self.assertFalse(libreria.identificatore_valido("sconosciuto"))
        self.assertTrue(libreria.identificatore_valido(libreria.ID_PREDEFINITO))


if __name__ == "__main__":
    unittest.main()
