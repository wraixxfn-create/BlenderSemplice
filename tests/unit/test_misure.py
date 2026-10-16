"""Prove delle regole di misure, unità e blocchi, senza aprire Blender.

`scene/misure.py` è un modulo puro: riceve numeri e terna di numeri. Qui si
verificano le regole che proteggono il lavoro dell'utente:

* i blocchi di Blender ("asse bloccato") vengono rispettati: uno spostamento
  su un asse bloccato si azzera, una dimensione bloccata non cambia;
* un asse libero resta libero anche quando gli altri sono bloccati;
* le unità si scrivono solo quando la scena le usa davvero.
"""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACCHETTO = ROOT / "addon" / "formafacile_3d"
if str(ROOT / "tests") not in sys.path:
    sys.path.insert(0, str(ROOT / "tests"))

import supporto_finto  # noqa: E402

supporto_finto.prepara_import_puro()

from formafacile_3d.scene import misure  # noqa: E402


class TestUnita(unittest.TestCase):
    def test_le_unita_della_scena_diventano_abbreviazioni(self):
        self.assertEqual(misure.unita_lunghezza("METRIC", "METERS"), "m")
        self.assertEqual(misure.unita_lunghezza("METRIC", "CENTIMETERS"), "cm")
        self.assertEqual(misure.unita_lunghezza("IMPERIAL", "FEET"), "ft")

    def test_senza_sistema_di_unita_non_si_scrive_nulla(self):
        self.assertEqual(misure.unita_lunghezza("NONE", "METERS"), "")

    def test_gli_angoli_sono_gradi_o_radianti(self):
        self.assertEqual(misure.unita_angolo("DEGREES"), "°")
        self.assertEqual(misure.unita_angolo("RADIANS"), "rad")

    def test_l_unita_va_fra_parentesi_solo_se_c_e(self):
        self.assertEqual(misure.etichetta_con_unita("Posizione", "m"), "Posizione (m)")
        self.assertEqual(misure.etichetta_con_unita("Posizione", ""), "Posizione")

    def test_conversioni_di_angoli(self):
        self.assertAlmostEqual(misure.gradi_in_radianti(180.0), math.pi)
        self.assertAlmostEqual(misure.radianti_in_gradi(math.pi / 2.0), 90.0)

    def test_numeri_brevi(self):
        self.assertEqual(misure.numero_breve(15.0), "15")
        self.assertEqual(misure.numero_breve(7.5), "7,5")
        self.assertEqual(misure.numero_breve(0.123456), "0,123")


class TestBlocchi(unittest.TestCase):
    def test_un_asse_bloccato_azzera_solo_il_suo_spostamento(self):
        delta = misure.delta_consentito((1.0, 2.0, 3.0), (True, False, False))
        self.assertEqual(delta, (0.0, 2.0, 3.0))

    def test_tutti_gli_assi_bloccati_azzera_tutto(self):
        self.assertEqual(misure.delta_consentito((1.0, 2.0, 3.0), (True, True, True)), (0.0, 0.0, 0.0))
        self.assertTrue(misure.tutti_bloccati((True, True, True)))
        self.assertFalse(misure.tutti_bloccati((True, False, True)))

    def test_gli_indici_degli_assi_bloccati_sono_in_ordine(self):
        self.assertEqual(misure.assi_bloccati((False, True, True)), (1, 2))
        self.assertEqual(misure.assi_bloccati(None), ())

    def test_una_dimesione_bloccata_non_cambia(self):
        self.assertEqual(misure.fattori_consentiti(2.0, (False, True, False)), (2.0, 1.0, 2.0))

    def test_la_posizione_assoluta_rispetta_i_blocchi(self):
        nuova = misure.posizione_consentita((5.0, 6.0, 7.0), (0.0, 0.0, 0.0), (True, False, False))
        self.assertEqual(nuova, (5.0, 0.0, 0.0))

    def test_uno_spostamento_nullo_non_e_valutabile(self):
        self.assertFalse(misure.spostamento_valutabile((0.0, 0.0, 0.0)))
        self.assertFalse(misure.spostamento_valutabile((1e-13, 0.0, 0.0)))
        self.assertTrue(misure.spostamento_valutabile((0.0, 0.01, 0.0)))


if __name__ == "__main__":
    unittest.main()
