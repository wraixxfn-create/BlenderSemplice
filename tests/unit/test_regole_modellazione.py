"""Regole pure degli strumenti guidati: numeri e giudizi, senza Blender.

Queste prove non aprono Blender: chiamano le stesse funzioni che usano i
comandi veri e controllano i valori al limite, quelli che in Blender si vedono
solo quando qualcosa va storto (una forma troppo piccola, un giro senza centro,
un allineamento già a posto).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "tests") not in sys.path:
    sys.path.insert(0, str(ROOT / "tests"))

import supporto_finto  # noqa: E402

supporto_finto.prepara_import_puro()

from formafacile_3d.scene import regole_modellazione as regole  # noqa: E402


# Facce e normali di un cubo, come le legge il servizio dai dati di Blender:
# le facce sono elenchi di indici, le normali terne di numeri.
FACCE_CUBO = (
    (0, 3, 2, 1),
    (4, 5, 6, 7),
    (0, 1, 5, 4),
    (1, 2, 6, 5),
    (2, 3, 7, 6),
    (3, 0, 4, 7),
)
NORMALI_CUBO = (
    (0.0, 0.0, -1.0),
    (0.0, 0.0, 1.0),
    (0.0, -1.0, 0.0),
    (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (-1.0, 0.0, 0.0),
)
FACCE_PIANO = ((0, 1, 2, 3),)
VERTICI_CUBO = (
    (0.0, 0.0, 0.0),
    (1.0, 0.0, 0.0),
    (1.0, 1.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, 1.0),
    (1.0, 0.0, 1.0),
    (1.0, 1.0, 1.0),
    (0.0, 1.0, 1.0),
)
NORMALI_PIANO = ((0.0, 0.0, 1.0),)


class TestSmusso(unittest.TestCase):
    def test_la_forza_resta_nell_intervallo(self):
        self.assertEqual(regole.forza_valida(0, 1, 3), 1)
        self.assertEqual(regole.forza_valida(9, 1, 3), 3)
        self.assertEqual(regole.forza_valida("2", 1, 3), 2)
        self.assertEqual(regole.forza_valida("boh", 1, 3), 1)

    def test_il_raggio_cresce_con_la_forza_ma_non_mangia_la_forma(self):
        piccolo = regole.raggio_smusso(
            2.0, 1, rapporto_per_forza=0.06, rapporto_massimo=0.2, raggio_minimo=0.001
        )
        forte = regole.raggio_smusso(
            2.0, 3, rapporto_per_forza=0.06, rapporto_massimo=0.2, raggio_minimo=0.001
        )
        self.assertLess(piccolo, forte)
        self.assertLessEqual(forte, 2.0 * 0.2 + 1e-9)

    def test_un_raggio_minimo_vale_anche_per_una_forma_piatta(self):
        raggio = regole.raggio_smusso(
            0.0, 3, rapporto_per_forza=0.06, rapporto_massimo=0.2, raggio_minimo=0.001
        )
        self.assertEqual(raggio, 0.001)

    def test_i_segmenti_non_scendono_sotto_due(self):
        self.assertEqual(regole.segmenti_smusso(1, 4), 2)
        self.assertEqual(regole.segmenti_smusso(9, 4), 4)


class TestSpigoliEBordi(unittest.TestCase):
    def test_il_cubo_ha_dodici_spigoli_vivi(self):
        self.assertEqual(regole.spigoli_vivi(FACCE_CUBO, NORMALI_CUBO, 30.0), 12)

    def test_alzando_la_soglia_gli_spigoli_scompaiono(self):
        # Oltre 90° nessuna coppia di facce del cubo forma più un angolo vivo:
        # è la stessa risposta di Blender con un limite di angolo alto.
        self.assertEqual(regole.spigoli_vivi(FACCE_CUBO, NORMALI_CUBO, 95.0), 0)

    def test_una_superficie_aperta_non_ha_spigoli_vivi(self):
        # Un piano è tutto bordo: non c'è nessuno spigolo da ammorbidire.
        self.assertEqual(regole.spigoli_vivi(FACCE_PIANO, NORMALI_PIANO, 30.0), 0)
        self.assertEqual(regole.bordi_aperti(FACCE_PIANO), 4)

    def test_la_forma_chiusa_non_ha_bordi_aperti(self):
        self.assertEqual(regole.bordi_aperti(FACCE_CUBO), 0)


class TestSimmetria(unittest.TestCase):
    def test_il_cubo_e_simmetrico_rispetto_al_proprio_centro(self):
        self.assertTrue(regole.simmetrica(VERTICI_CUBO, "x", 0.001, 0.5))
        self.assertTrue(regole.simmetrica(VERTICI_CUBO, "z", 0.001, 0.5))

    def test_rispetto_al_piano_del_mondo_il_cubo_sta_tutto_da_una_parte(self):
        # Il cubo occupa x da 0 a 1: il suo specchio rispetto al piano x=0
        # cadrebbe da -1 a 0, cioè in un altro posto.
        self.assertFalse(regole.simmetrica(VERTICI_CUBO, "x", 0.001, 0.0))

    def test_un_cubo_a_cavallo_del_piano_e_simmetrico(self):
        vertici = tuple(
            (x - 0.5, y, z) for x, y, z in VERTICI_CUBO
        )
        self.assertTrue(regole.simmetrica(vertici, "x", 0.001, 0.0))

    def test_senza_punti_non_e_simmetrica(self):
        self.assertFalse(regole.simmetrica((), "x", 0.001))

    def test_un_asse_che_non_esiste_non_e_simmetrico(self):
        self.assertFalse(regole.simmetrica(VERTICI_CUBO, "w", 0.001))


class TestSuddivisione(unittest.TestCase):
    def test_ogni_livello_quadruplica_le_facce(self):
        self.assertEqual(regole.facce_dopo_suddivisione(6, 1), 24)
        self.assertEqual(regole.facce_dopo_suddivisione(6, 2), 96)
        self.assertEqual(regole.facce_dopo_suddivisione(6, 0), 6)

    def test_i_livelli_scendono_finche_la_forma_resta_leggera(self):
        self.assertEqual(regole.livelli_consentiti(6, 3, 100), 2)
        self.assertEqual(regole.livelli_consentiti(6, 3, 100000), 3)

    def test_anche_una_forma_pesantissima_tiene_un_livello(self):
        self.assertEqual(regole.livelli_consentiti(100000, 3, 100), 1)


class TestRipetizione(unittest.TestCase):
    def test_le_copie_aggiuntive_escludono_l_originale(self):
        self.assertEqual(regole.copie_aggiuntive(4), 3)
        self.assertEqual(regole.copie_aggiuntive(1), 0)

    def test_la_fila_finisce_dopo_l_ultima_copia(self):
        self.assertEqual(regole.fine_fila(1.5, 4, "y"), (0.0, 4.5, 0.0))
        self.assertEqual(regole.fine_fila(1.5, 4, "z"), (0.0, 0.0, 4.5))

    def test_la_direzione_da_un_punto_e_distanza_e_angolo(self):
        distanza, angolo = regole.direzione_da_punto((0.0, 0.0, 0.0), (2.0, 0.0, 0.0))
        self.assertAlmostEqual(distanza, 2.0)
        self.assertAlmostEqual(angolo, 0.0)
        distanza, angolo = regole.direzione_da_punto((0.0, 0.0, 0.0), (0.0, 2.0, 0.0))
        self.assertAlmostEqual(distanza, 2.0)
        self.assertAlmostEqual(angolo, 90.0)

    def test_sul_centro_non_c_e_direzione(self):
        self.assertEqual(regole.direzione_da_punto((1.0, 1.0, 0.0), (1.0, 1.0, 0.0)), (0.0, 0.0))

    def test_il_punto_sul_cerchio_rispetta_distanza_e_angolo(self):
        punto = regole.punto_su_cerchio((0.0, 0.0, 3.0), 2.0, 180.0)
        self.assertAlmostEqual(punto[0], -2.0)
        self.assertAlmostEqual(punto[1], 0.0)
        self.assertAlmostEqual(punto[2], 3.0)

    def test_le_copie_si_distribuiscono_a_passi_uguali(self):
        copie = regole.posizioni_cerchio((0.0, 0.0, 0.0), 4, 2.0, 0.0)
        self.assertEqual(len(copie), 3)
        angoli = [round(rotazione) for _posizione, rotazione in copie]
        self.assertEqual(angoli, [90, 180, 270])
        for posizione, _rotazione in copie:
            self.assertAlmostEqual(
                (posizione[0] ** 2 + posizione[1] ** 2) ** 0.5, 2.0, places=6
            )

    def test_una_sola_forma_non_ha_copie(self):
        self.assertEqual(regole.posizioni_cerchio((0.0, 0.0, 0.0), 1, 2.0, 0.0), ())


class TestSpessore(unittest.TestCase):
    def test_lo_spessore_resta_una_frazione_della_forma(self):
        spessore = regole.spessore_consentito(
            1.0, 5.0, rapporto_massimo=0.5, spessore_minimo=0.001
        )
        self.assertAlmostEqual(spessore, 0.5)

    def test_lo_spessore_richiesto_piu_piccolo_viene_rispettato(self):
        spessore = regole.spessore_consentito(
            2.0, 0.2, rapporto_massimo=0.5, spessore_minimo=0.001
        )
        self.assertAlmostEqual(spessore, 0.2)

    def test_non_si_scende_sotto_lo_spessore_minimo(self):
        spessore = regole.spessore_consentito(
            1.0, 0.0, rapporto_massimo=0.5, spessore_minimo=0.01
        )
        self.assertAlmostEqual(spessore, 0.01)


class TestAllineamento(unittest.TestCase):
    def test_il_bordo_iniziale_e_quello_finale(self):
        self.assertEqual(
            regole.spostamento_allineamento(2.0, 4.0, 0.0, 6.0, "inizio"), -2.0
        )
        self.assertEqual(
            regole.spostamento_allineamento(2.0, 4.0, 0.0, 6.0, "fine"), 2.0
        )

    def test_il_centro_combacia_con_il_centro(self):
        self.assertEqual(
            regole.spostamento_allineamento(0.0, 2.0, 0.0, 4.0, "centro"), 1.0
        )

    def test_in_modo_sconosciuto_si_usa_l_inizio(self):
        self.assertEqual(
            regole.spostamento_allineamento(1.0, 2.0, 0.0, 5.0, "boh"), -1.0
        )

    def test_la_spaziatura_lascia_fermi_il_primo_e_l_ultimo(self):
        intervalli = ((0.0, 2.0), (0.0, 2.0), (10.0, 12.0))
        posizioni = regole.posizioni_spaziate(intervalli)
        self.assertAlmostEqual(posizioni[0], 0.0)
        # L'ultimo oggetto tiene il suo bordo finale: 10 + 2 = 12.
        self.assertAlmostEqual(posizioni[-1] + 2.0, 12.0)
        # Lo spazio fra un oggetto e il successivo è sempre lo stesso.
        self.assertAlmostEqual(regole.spazio_fra_oggetti(intervalli), 3.0)
        self.assertAlmostEqual(posizioni[1] - (posizioni[0] + 2.0), 3.0)

    def test_con_meno_di_tre_oggetti_non_si_spazia(self):
        intervalli = ((0.0, 2.0), (5.0, 7.0))
        self.assertEqual(regole.posizioni_spaziate(intervalli), (0.0, 5.0))
        self.assertEqual(regole.spazio_fra_oggetti(intervalli), 0.0)

    def test_oggetti_sovrapposti_danno_spazio_negativo(self):
        self.assertLess(regole.spazio_fra_oggetti(((0.0, 2.0), (0.0, 2.0), (0.0, 2.0))), 0.0)


class TestNomiDeiGruppi(unittest.TestCase):
    def test_il_primo_nome_libero_della_serie(self):
        self.assertEqual(regole.nome_gruppo_libero(("Gruppo 1",), "Gruppo"), "Gruppo 2")
        self.assertEqual(regole.nome_gruppo_libero((), "Gruppo"), "Gruppo 1")

    def test_il_confronto_ignora_le_maiuscole(self):
        self.assertEqual(regole.nome_gruppo_libero(("gruppo 1",), "Gruppo"), "Gruppo 2")

    def test_dopo_mille_nomi_si_continua_comunque(self):
        esistenti = tuple(f"Gruppo {numero}" for numero in range(1, 1000))
        self.assertEqual(regole.nome_gruppo_libero(esistenti, "Gruppo"), "Gruppo 1000")


class TestTipiConvertibili(unittest.TestCase):
    def test_testi_e_curve_diventano_forme(self):
        for tipo in ("FONT", "CURVE", "SURFACE", "META"):
            with self.subTest(tipo=tipo):
                self.assertIn(tipo, regole.TIPI_CONVERTIBILI)

    def test_una_forma_non_si_trasforma_in_se_stessa(self):
        self.assertNotIn("MESH", regole.TIPI_CONVERTIBILI)


if __name__ == "__main__":
    unittest.main()
