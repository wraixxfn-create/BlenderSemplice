"""Prove delle regole dell'aspetto: materiali, luci, qualità e file creati.

Girano senza Blender: le regole sono dati puri, quindi i valori dei materiali,
i limiti fisici, i nomi dei file, i percorsi e le stime di memoria si possono
verificare qui, velocemente. Le prove che creano davvero materiali, luci e
immagini stanno in `tests/blender/test_addon.py`, perché hanno bisogno di
Blender.
"""

from __future__ import annotations

import datetime
import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
for _percorso in (ROOT / "tests", ROOT / "addon"):
    if str(_percorso) not in sys.path:
        sys.path.insert(0, str(_percorso))

import supporto_finto  # noqa: E402

supporto_finto.prepara_import_puro()

from formafacile_3d import configuration  # noqa: E402
from formafacile_3d.localization import TESTI  # noqa: E402
from formafacile_3d.scene import aspetto  # noqa: E402


class TestMaterialiPronti(unittest.TestCase):
    def test_ogni_materiale_ha_nome_e_descrizione(self):
        for chiave in aspetto.ORDINE_MATERIALI:
            with self.subTest(chiave=chiave):
                valori = aspetto.MATERIALI[chiave]
                self.assertEqual(valori.chiave, chiave)
                self.assertTrue(valori.nome.strip())
                self.assertTrue(valori.descrizione.strip())

    def test_gli_ordini_comprendono_tutti_i_materiali(self):
        self.assertEqual(set(aspetto.ORDINE_MATERIALI), set(aspetto.MATERIALI))
        self.assertEqual(len(aspetto.ORDINE_MATERIALI), len(set(aspetto.ORDINE_MATERIALI)))

    def test_i_materiali_richiesti_ci_sono(self):
        """I materiali promessi dal pannello esistono tutti."""
        self.assertEqual(
            set(aspetto.MATERIALI),
            {
                aspetto.MATERIALE_PLASTICA_OPACA,
                aspetto.MATERIALE_METALLO,
                aspetto.MATERIALE_LEGNO_STILIZZATO,
                aspetto.MATERIALE_VETRO,
                aspetto.MATERIALE_CERAMICA,
                aspetto.MATERIALE_GOMMA,
            },
        )

    def test_i_valori_stanno_nei_limiti_di_blender(self):
        """Colore, ruvidità, metallico e trasparenza sono valori fisici validi."""
        for chiave, valori in aspetto.MATERIALI.items():
            with self.subTest(chiave=chiave):
                self.assertEqual(len(valori.colore), 3)
                for canale in valori.colore:
                    self.assertGreaterEqual(canale, 0.0)
                    self.assertLessEqual(canale, 1.0)
                self.assertGreaterEqual(valori.ruvidita, 0.0)
                self.assertLessEqual(valori.ruvidita, 1.0)
                self.assertGreaterEqual(valori.metallico, 0.0)
                self.assertLessEqual(valori.metallico, 1.0)
                self.assertGreaterEqual(valori.trasparenza, 0.0)
                self.assertLessEqual(valori.trasparenza, 1.0)

    def test_la_trasparenza_e_configurata_solo_dove_serve(self):
        """Un materiale opaco non può essere dichiarato trasparente per errore."""
        for chiave, valori in aspetto.MATERIALI.items():
            with self.subTest(chiave=chiave):
                if not valori.trasparenza_disponibile:
                    self.assertEqual(valori.trasparenza, 0.0)
                else:
                    self.assertGreaterEqual(valori.trasparenza, 0.5)

    def test_il_metallo_riflette_e_la_gomma_no(self):
        """I due estremi dell'aspetto: se fossero uguali non servirebbero a nulla."""
        self.assertEqual(aspetto.MATERIALI[aspetto.MATERIALE_METALLO].metallico, 1.0)
        self.assertEqual(aspetto.MATERIALI[aspetto.MATERIALE_GOMMA].metallico, 0.0)
        self.assertGreater(
            aspetto.MATERIALI[aspetto.MATERIALE_GOMMA].ruvidita,
            aspetto.MATERIALI[aspetto.MATERIALE_CERAMICA].ruvidita,
        )
        self.assertLess(
            aspetto.MATERIALI[aspetto.MATERIALE_VETRO].ruvidita,
            aspetto.MATERIALI[aspetto.MATERIALE_LEGNO_STILIZZATO].ruvidita,
        )

    def test_materiale_sconosciuto_ricade_sul_predefinito(self):
        self.assertEqual(
            aspetto.materiale("non-esiste").chiave, aspetto.MATERIALE_PREDEFINITO
        )

    def test_i_materiali_hanno_un_nome_inglese_per_il_file(self):
        """Il nome inglese serve solo ai nomi dei dati: deve esserci e essere corto."""
        for chiave, valori in aspetto.MATERIALI.items():
            with self.subTest(chiave=chiave):
                self.assertTrue(valori.parola_inglese)
                self.assertRegex(valori.parola_inglese, r"^[a-z]+$")


class TestTavolozza(unittest.TestCase):
    def test_ogni_colore_ha_un_nome_italiano(self):
        for chiave in aspetto.ORDINE_TAVOLOZZA:
            with self.subTest(chiave=chiave):
                colore = aspetto.TAVOLOZZA[chiave]
                self.assertEqual(colore.chiave, chiave)
                self.assertTrue(colore.nome.strip())
                self.assertTrue(colore.aiuto.strip())

    def test_i_colori_sono_distinti_fra_loro(self):
        """Due colori troppo simili non servirebbero a nulla."""
        for indice, chiave in enumerate(aspetto.ORDINE_TAVOLOZZA):
            for altra in aspetto.ORDINE_TAVOLOZZA[indice + 1 :]:
                with self.subTest(colori=(chiave, altra)):
                    primo = aspetto.TAVOLOZZA[chiave].rgb
                    secondo = aspetto.TAVOLOZZA[altra].rgb
                    distanza = sum((a - b) ** 2 for a, b in zip(primo, secondo)) ** 0.5
                    self.assertGreater(distanza, 0.08)

    def test_i_nomi_dei_colori_sono_diversi(self):
        nomi = [aspetto.TAVOLOZZA[chiave].nome for chiave in aspetto.ORDINE_TAVOLOZZA]
        self.assertEqual(len(nomi), len(set(nomi)))

    def test_colore_sconosciuto_non_esiste(self):
        self.assertIsNone(aspetto.colore("turchese-inventato"))


class TestComposizioneDelMateriale(unittest.TestCase):
    def test_senza_correzioni_i_valori_sono_quelli_della_ricetta(self):
        valori = aspetto.componi(aspetto.MATERIALE_CERAMICA)
        self.assertEqual(valori, aspetto.MATERIALI[aspetto.MATERIALE_CERAMICA])

    def test_il_colore_scelto_sostituisce_quello_della_ricetta(self):
        rosso = aspetto.TAVOLOZZA["rosso"].rgb
        valori = aspetto.componi(aspetto.MATERIALE_METALLO, rosso)
        self.assertEqual(valori.colore, rosso)
        self.assertEqual(valori.ruvidita, aspetto.MATERIALI[aspetto.MATERIALE_METALLO].ruvidita)

    def test_i_valori_fuori_limite_vengono_riportati_dentro(self):
        """Un campo numerico non deve poter creare un materiale impossibile."""
        valori = aspetto.componi(
            aspetto.MATERIALE_PLASTICA_OPACA, None, ruvidita=5.0, metallico=-3.0, trasparenza=7.0
        )
        self.assertEqual(valori.ruvidita, configuration.MATERIALE_RUVIDITA_MASSIMA)
        self.assertEqual(valori.metallico, configuration.MATERIALE_METALLICO_MINIMO)
        # La plastica non prevede la trasparenza: resta a zero anche se richiesta.
        self.assertEqual(valori.trasparenza, 0.0)

    def test_la_trasparenza_si_applica_al_vetro(self):
        valori = aspetto.componi(aspetto.MATERIALE_VETRO, None, trasparenza=0.3)
        self.assertAlmostEqual(valori.trasparenza, 0.3)

    def test_valori_non_numerici_non_fanno_fallire_la_composizione(self):
        self.assertEqual(aspetto.limita("non-un-numero", 0.2, 0.8), 0.2)
        self.assertEqual(aspetto.limita(None, 0.2, 0.8), 0.2)
        self.assertEqual(aspetto.limita(0.5, 0.2, 0.8), 0.5)

    def test_composizione_con_colore_corto_o_lungo(self):
        for colore in ((0.1, 0.2), (0.1,), (0.1, 0.2, 0.3, 0.4)):
            with self.subTest(colore=colore):
                valori = aspetto.componi(aspetto.MATERIALE_GOMMA, colore)
                self.assertEqual(len(valori.colore), 3)
                for canale in valori.colore:
                    self.assertGreaterEqual(canale, 0.0)
                    self.assertLessEqual(canale, 1.0)

    def test_un_colore_fuori_limite_viene_riportato_dentro(self):
        valori = aspetto.componi(aspetto.MATERIALE_GOMMA, (5.0, -2.0, 0.5))
        self.assertEqual(valori.colore, (1.0, 0.0, 0.5))


class TestIlluminazionePronta(unittest.TestCase):
    def test_le_illuminazioni_richieste_ci_sono(self):
        self.assertEqual(
            set(aspetto.ILLUMINAZIONI),
            {
                aspetto.ILLUMINAZIONE_AUTOMATICA,
                aspetto.ILLUMINAZIONE_PRODOTTO,
                aspetto.ILLUMINAZIONE_INTERNO_SEMPLICE,
                aspetto.ILLUMINAZIONE_ESTERNO_SEMPLICE,
                aspetto.ILLUMINAZIONE_STUDIO_NEUTRO,
            },
        )

    def test_ogni_illuminazione_ha_nome_descrizione_e_luci(self):
        for chiave in aspetto.ORDINE_ILLUMINAZIONI:
            with self.subTest(chiave=chiave):
                preset = aspetto.ILLUMINAZIONI[chiave]
                self.assertTrue(preset.nome.strip())
                self.assertTrue(preset.descrizione.strip())
                self.assertGreaterEqual(len(preset.luci), 1)

    def test_ogni_luce_e_configurata_davvero(self):
        for chiave, preset in aspetto.ILLUMINAZIONI.items():
            for luce in preset.luci:
                with self.subTest(illuminazione=chiave, luce=luce.nome_chiave):
                    self.assertIn(luce.nome_chiave, TESTI)
                    self.assertIn(luce.tipo, {"AREA", "SUN", "POINT"})
                    self.assertGreater(luce.energia, 0.0)
                    self.assertEqual(len(luce.posizione), 3)
                    self.assertEqual(len(luce.colore), 3)
                    for canale in luce.colore:
                        self.assertGreater(canale, 0.0)
                        self.assertLessEqual(canale, 1.0)
                    if luce.tipo == "AREA":
                        self.assertGreater(luce.dimensione, 0.0)

    def test_le_luci_non_stanno_tutte_nello_stesso_punto(self):
        """Tre luci sovrapposte sarebbero una luce sola con il triplo della potenza."""
        for chiave, preset in aspetto.ILLUMINAZIONI.items():
            if len(preset.luci) < 2:
                continue
            with self.subTest(chiave=chiave):
                posizioni = {tuple(round(v, 3) for v in luce.posizione) for luce in preset.luci}
                self.assertEqual(len(posizioni), len(preset.luci))

    def test_lo_sfondo_e_dichiarato_con_valori_utilizzabili(self):
        for chiave, preset in aspetto.ILLUMINAZIONI.items():
            with self.subTest(chiave=chiave):
                self.assertEqual(len(preset.sfondo), 3)
                for canale in preset.sfondo:
                    self.assertGreaterEqual(canale, 0.0)
                    self.assertLessEqual(canale, 1.0)
                self.assertGreater(preset.sfondo_intensita, 0.0)
                self.assertLessEqual(preset.sfondo_intensita, 2.0)

    def test_l_illuminazione_automatica_si_adatta_alla_scena(self):
        """La sola illuminazione che dichiara di adattarsi è quella automatica."""
        adattabili = [
            chiave
            for chiave, preset in aspetto.ILLUMINAZIONI.items()
            if preset.adatta_alla_scena
        ]
        self.assertEqual(adattabili, [aspetto.ILLUMINAZIONE_AUTOMATICA])

    def test_illuminazione_sconosciuta_ricade_sul_predefinito(self):
        self.assertEqual(
            aspetto.illuminazione("non-esiste").chiave, aspetto.ILLUMINAZIONE_PREDEFINITA
        )


class TestQualitaDellImmagine(unittest.TestCase):
    def test_le_qualita_richieste_ci_sono(self):
        self.assertEqual(
            set(aspetto.QUALITA),
            {aspetto.QUALITA_ANTEPRIMA, aspetto.QUALITA_STANDARD, aspetto.QUALITA_ALTA},
        )

    def test_i_valori_crescono_con_la_qualita(self):
        anteprima = aspetto.QUALITA[aspetto.QUALITA_ANTEPRIMA]
        standard = aspetto.QUALITA[aspetto.QUALITA_STANDARD]
        alta = aspetto.QUALITA[aspetto.QUALITA_ALTA]
        self.assertLess(anteprima.campioni_cycles, standard.campioni_cycles)
        self.assertLess(standard.campioni_cycles, alta.campioni_cycles)
        self.assertLess(anteprima.percentuale, standard.percentuale)

    def test_i_valori_sono_prudenti(self):
        """Nessuna qualità chiede valori da computer potente."""
        for chiave, qualita in aspetto.QUALITA.items():
            with self.subTest(chiave=chiave):
                self.assertLessEqual(qualita.percentuale, configuration.QUALITA_PERCENTUALE_MASSIMA)
                self.assertGreaterEqual(
                    qualita.percentuale, configuration.QUALITA_PERCENTUALE_MINIMA
                )
                # Il valore predefinito di Blender per Cycles è 4096 campioni:
                # nessuna qualità di FormaFacile si avvicina a quella cifra.
                self.assertLess(qualita.campioni_cycles, 1024)
                self.assertLess(qualita.campioni_eevee, 1024)
                self.assertGreaterEqual(qualita.campioni_eevee, 1)

    def test_i_campioni_dipendono_dal_motore(self):
        qualita = aspetto.QUALITA[aspetto.QUALITA_STANDARD]
        self.assertEqual(qualita.campioni("CYCLES"), qualita.campioni_cycles)
        self.assertEqual(qualita.campioni("BLENDER_EEVEE_NEXT"), qualita.campioni_eevee)

    def test_qualita_sconosciuta_ricade_sul_predefinito(self):
        self.assertEqual(aspetto.qualita("non-esiste").chiave, aspetto.QUALITA_PREDEFINITA)

    def test_motori_e_formati_hanno_testi_e_nomi_di_blender(self):
        for chiave in aspetto.ORDINE_MOTORI:
            with self.subTest(motore=chiave):
                self.assertIn(aspetto.NOMI_MOTORI[chiave], TESTI)
                self.assertIn(aspetto.DESCRIZIONI_MOTORI[chiave], TESTI)
        for motore, identificatore in aspetto.MOTORI_BLENDER.items():
            with self.subTest(motore=motore):
                self.assertIn(motore, aspetto.ORDINE_MOTORI)
                self.assertRegex(identificatore, r"^[A-Z_]+$")
        for chiave in aspetto.ORDINE_FORMATI:
            with self.subTest(formato=chiave):
                self.assertIn(chiave, aspetto.FORMATI_BLENDER)
                self.assertTrue(aspetto.ESTENSIONI_FORMATI[chiave].startswith("."))
                self.assertIn(aspetto.NOMI_FORMATI[chiave], TESTI)
                self.assertIn(aspetto.DESCRIZIONI_FORMATI[chiave], TESTI)
        self.assertNotIn(aspetto.MOTORE_COME_IN_BLENDER, aspetto.MOTORI_BLENDER)


class TestNomi(unittest.TestCase):
    def test_nome_libero_quando_il_nome_e_occupato(self):
        self.assertEqual(aspetto.nome_libero("Vetro", ["Ceramica"]), "Vetro")
        self.assertEqual(aspetto.nome_libero("Vetro", ["Vetro"]), "Vetro 2")
        self.assertEqual(aspetto.nome_libero("Vetro", ["Vetro", "Vetro 2"]), "Vetro 3")

    def test_il_nome_non_supera_il_limite_di_blender(self):
        lunghissimo = "M" * 200
        for occupati in ([], [lunghissimo], [lunghissimo, f"{lunghissimo[:61]} 2"]):
            with self.subTest(occupati=len(occupati)):
                nome = aspetto.nome_libero(lunghissimo, occupati)
                self.assertLessEqual(len(nome), configuration.LUNGHEZZA_MASSIMA_NOME)

    def test_un_nome_vuoto_non_produce_un_nome_vuoto(self):
        self.assertTrue(aspetto.nome_libero("   ", []).strip())

    def test_il_nome_del_materiale_e_quello_del_materiale_pronto(self):
        nome = aspetto.nome_materiale(aspetto.MATERIALI[aspetto.MATERIALE_GOMMA], [])
        self.assertEqual(nome, aspetto.MATERIALI[aspetto.MATERIALE_GOMMA].nome)
        nome_doppio = aspetto.nome_materiale(
            aspetto.MATERIALI[aspetto.MATERIALE_GOMMA], [nome]
        )
        self.assertEqual(nome_doppio, f"{nome} 2")

    def test_il_nome_della_variazione_ricorda_il_materiale(self):
        nome = aspetto.nome_variazione("Vetro", [])
        self.assertIn("Vetro", nome)
        self.assertEqual(nome, TESTI["MATERIALE_NOME_VARIAZIONE"].format(nome="Vetro"))
        self.assertNotEqual(aspetto.nome_variazione("Vetro", [nome]), nome)

    def test_il_nome_del_file_ha_data_ora_e_estensione(self):
        quando = datetime.datetime(2026, 10, 16, 9, 8, 7)
        nome = aspetto.nome_file_immagine(quando, aspetto.FORMATO_PNG)
        self.assertTrue(nome.startswith(TESTI["IMMAGINE_PREFISSO_FILE"]))
        self.assertTrue(nome.endswith(".png"))
        self.assertIn("20261016", nome)
        self.assertIn("090807", nome)

    def test_formati_diversi_danno_estensioni_diverse(self):
        quando = datetime.datetime(2026, 10, 16, 9, 8, 7)
        self.assertTrue(
            aspetto.nome_file_immagine(quando, aspetto.FORMATO_JPEG).endswith(".jpg")
        )
        self.assertNotEqual(
            aspetto.nome_file_immagine(quando, aspetto.FORMATO_PNG),
            aspetto.nome_file_immagine(quando, aspetto.FORMATO_JPEG),
        )

    def test_formato_sconosciuto_usa_l_estensione_predefinita(self):
        nome = aspetto.nome_file_immagine(datetime.datetime(2026, 1, 1), "tiff-inventato")
        self.assertTrue(nome.endswith(aspetto.ESTENSIONI_FORMATI[aspetto.FORMATO_PREDEFINITO]))


class TestPercorsoDellImmagine(unittest.TestCase):
    def test_cartella_vuota_non_va_bene(self):
        self.assertEqual(aspetto.cartella_problema(""), "ERRORE_CARTELLA_MANCANTE")
        self.assertEqual(aspetto.cartella_problema("   "), "ERRORE_CARTELLA_MANCANTE")
        self.assertEqual(aspetto.cartella_problema(None), "ERRORE_CARTELLA_MANCANTE")

    def test_cartella_inesistente_non_va_bene(self):
        with tempfile.TemporaryDirectory() as cartella:
            mancante = str(Path(cartella) / "non-esiste")
            self.assertEqual(aspetto.cartella_problema(mancante), "ERRORE_CARTELLA_INESISTENTE")
            # Un file non è una cartella.
            file_prova = Path(cartella) / "file.txt"
            file_prova.write_text("prova", encoding="utf-8")
            self.assertEqual(
                aspetto.cartella_problema(str(file_prova)), "ERRORE_CARTELLA_INESISTENTE"
            )

    def test_cartella_scrivibile_va_bene(self):
        with tempfile.TemporaryDirectory() as cartella:
            self.assertEqual(aspetto.cartella_problema(cartella), "")

    def test_cartella_senza_permessi_non_va_bene(self):
        if os.geteuid() == 0:
            self.skipTest("l'utente di sistema può scrivere ovunque")
        with tempfile.TemporaryDirectory() as cartella:
            chiusa = Path(cartella) / "chiusa"
            chiusa.mkdir()
            chiusa.chmod(0o500)
            try:
                self.assertEqual(
                    aspetto.cartella_problema(str(chiusa)), "ERRORE_CARTELLA_NON_SCRIVIBILE"
                )
            finally:
                chiusa.chmod(0o700)

    def test_il_percorso_uniscce_cartella_e_nome(self):
        percorso = aspetto.percorso_immagine("/tmp/prova", "immagine.png")
        self.assertEqual(percorso, os.path.join("/tmp/prova", "immagine.png"))
        self.assertTrue(percorso.endswith("immagine.png"))


class TestStimaDellaMemoria(unittest.TestCase):
    def test_i_pixel_seguono_risoluzione_e_percentuale(self):
        self.assertEqual(aspetto.pixel_immagine(1920, 1080, 100), 1920 * 1080)
        self.assertEqual(aspetto.pixel_immagine(1920, 1080, 50), 960 * 540)
        # Valori senza senso non devono portare a zero pixel né a numeri negativi.
        self.assertGreater(aspetto.pixel_immagine(0, 1080, 100), 0)
        self.assertGreater(aspetto.pixel_immagine(1920, 1080, 0), 0)
        self.assertGreater(aspetto.pixel_immagine(-5, -5, -5), 0)

    def test_la_stima_cresce_con_i_pixel(self):
        piccola = aspetto.stima_memoria_mb(aspetto.pixel_immagine(640, 480, 100))
        media = aspetto.stima_memoria_mb(aspetto.pixel_immagine(1920, 1080, 100))
        grande = aspetto.stima_memoria_mb(aspetto.pixel_immagine(3840, 2160, 100))
        self.assertLess(piccola, media)
        self.assertLess(media, grande)

    def test_la_stima_e_prudente_ma_non_assurda(self):
        """Un'immagine normale deve stare in poche centinaia di megabyte."""
        media = aspetto.stima_memoria_mb(aspetto.pixel_immagine(1920, 1080, 100))
        self.assertGreater(media, 50.0)
        self.assertLess(media, 1000.0)

    def test_un_immagine_enorme_supera_il_limite_di_sicurezza(self):
        pixel = aspetto.pixel_immagine(10000, 10000, 100)
        self.assertGreater(pixel, configuration.PIXEL_MASSIMI_IMMAGINE)


class TestVociPerInterfaccia(unittest.TestCase):
    def test_le_voci_dei_materiali_seguono_l_ordine(self):
        voci = aspetto.voci_materiali()
        self.assertEqual([chiave for chiave, _nome, _aiuto in voci], list(aspetto.ORDINE_MATERIALI))
        for chiave, nome, aiuto in voci:
            with self.subTest(chiave=chiave):
                self.assertEqual(nome, aspetto.MATERIALI[chiave].nome)
                self.assertEqual(aiuto, aspetto.MATERIALI[chiave].descrizione)

    def test_le_voci_della_tavolozza_hanno_tre_colonne(self):
        for chiave, nome, aiuto in aspetto.voci_tavolozza():
            with self.subTest(chiave=chiave):
                self.assertEqual(nome, aspetto.TAVOLOZZA[chiave].nome)
                self.assertTrue(aiuto)

    def test_le_voci_delle_qualita_e_dei_motori_sono_in_italiano(self):
        for voci in (aspetto.voci_qualita(), aspetto.voci_motori(), aspetto.voci_formati()):
            for chiave, nome, aiuto in voci:
                with self.subTest(chiave=chiave):
                    self.assertTrue(nome.strip())
                    self.assertTrue(aiuto.strip())
                    self.assertNotRegex(nome, r"\b(?:TODO|Click here|Save|Cancel)\b")


if __name__ == "__main__":
    unittest.main()
