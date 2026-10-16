"""Prove della scelta degli oggetti, senza aprire Blender.

`blender/selezione.py` lavora solo con i metodi pubblici degli oggetti di
Blender (`select_get`, `select_set`, `visible_get`, `hide_viewport`,
`hide_select`, `type`, `name`): con oggetti finti si possono quindi verificare
tutte le regole della scelta — visibili o nascosti, bloccati o no, uno o molti
— in una prova veloce che non richiede il modulo bpy.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACCHETTO = ROOT / "addon" / "formafacile_3d"
if str(PACCHETTO) not in sys.path:
    sys.path.insert(0, str(PACCHETTO))

from blender import selezione  # noqa: E402
from localization import TESTI  # noqa: E402


class OggettoFinto:
    """Oggetto con la sola parte di API usata dal servizio di scelta."""

    def __init__(
        self,
        nome: str,
        *,
        tipo: str = "MESH",
        scelto: bool = False,
        nascosto: bool = False,
        bloccato: bool = False,
    ) -> None:
        self.name = nome
        self.type = tipo
        self.hide_viewport = nascosto
        self.hide_select = bloccato
        self._scelto = scelto

    def select_get(self) -> bool:
        return self._scelto

    def select_set(self, valore: bool) -> None:
        self._scelto = bool(valore)

    def visible_get(self) -> bool:
        return not self.hide_viewport


class ElencoFinto(list):
    """Elenco di oggetti con la proprietà `active`, come `view_layer.objects`."""

    def __init__(self, *oggetti: OggettoFinto) -> None:
        super().__init__(oggetti)
        self.active: OggettoFinto | None = None


class VettoreFinto:
    """Vettore di scena finto: contiene gli oggetti e l'oggetto attivo."""

    def __init__(self, *oggetti: OggettoFinto) -> None:
        self.objects = ElencoFinto(*oggetti)

    @property
    def attivi(self) -> list[str]:
        return [oggetto.name for oggetto in self.objects if oggetto.select_get()]


def vettore(*oggetti: OggettoFinto) -> VettoreFinto:
    contenitore = VettoreFinto(*oggetti)
    for oggetto in oggetti:
        if oggetto.select_get():
            contenitore.objects.active = oggetto
            break
    return contenitore


class TestRegolaDiScelta(unittest.TestCase):
    def test_un_oggetto_nascosto_si_sceglie_da_solo(self):
        """Dall'elenco si può scegliere anche un oggetto nascosto, per ritrovarlo."""
        nascosto = OggettoFinto("Nascosto", nascosto=True)
        self.assertTrue(selezione.scegliibile(nascosto))
        self.assertFalse(selezione.scegliibile_in_gruppo(nascosto))
        self.assertEqual(selezione.motivo_rifiuto(nascosto), "nascosto")

    def test_un_oggetto_bloccato_non_si_sceglie(self):
        bloccato = OggettoFinto("Bloccato", bloccato=True)
        self.assertFalse(selezione.scegliibile(bloccato))
        self.assertFalse(selezione.scegliibile_in_gruppo(bloccato))
        self.assertEqual(selezione.motivo_rifiuto(bloccato), "bloccato")

    def test_un_oggetto_visibile_si_sceglie(self):
        libero = OggettoFinto("Libero")
        self.assertTrue(selezione.scegliibile(libero))
        self.assertTrue(selezione.scegliibile_in_gruppo(libero))
        self.assertEqual(selezione.motivo_rifiuto(libero), "")


class TestScelteDiGruppo(unittest.TestCase):
    def test_scegli_tutto_prende_solo_i_visibili(self):
        libero = OggettoFinto("Libero")
        nascosto = OggettoFinto("Nascosto", nascosto=True)
        bloccato = OggettoFinto("Bloccato", bloccato=True)
        scena = vettore(libero, nascosto, bloccato)

        esito = selezione.scegli_tutto(scena)

        self.assertEqual(esito.scelti, 1)
        self.assertEqual(esito.saltati, 2)
        self.assertEqual(scena.attivi, ["Libero"])
        self.assertIs(scena.objects.active, libero)

    def test_scegli_tutto_non_cambia_l_attivo_esistente(self):
        libero = OggettoFinto("Libero")
        altro = OggettoFinto("Altro")
        scena = vettore(libero, altro)
        scena.objects.active = altro

        selezione.scegli_tutto(scena)

        self.assertIs(scena.objects.active, altro)

    def test_scegli_tutto_restituisce_un_esito(self):
        """Regressione: l'esito della scelta deve essere il tipo dichiarato."""
        esito = selezione.scegli_tutto(vettore())
        self.assertEqual((esito.scelti, esito.saltati), (0, 0))
        self.assertIsInstance(esito, selezione.EsitoSelezione)

    def test_scegli_tutto_toglie_la_scelta_a_chi_non_si_vede_piu(self):
        libero = OggettoFinto("Libero", scelto=True)
        nascosto = OggettoFinto("Nascosto", nascosto=True, scelto=True)
        scena = vettore(libero, nascosto)

        selezione.scegli_tutto(scena)

        self.assertFalse(nascosto.select_get())
        self.assertTrue(libero.select_get())

    def test_descegli_tutto_toglie_tutto_e_l_attivo(self):
        libero = OggettoFinto("Libero", scelto=True)
        scena = vettore(libero)

        esito = selezione.descegli_tutto(scena)

        self.assertEqual((esito.scelti, esito.saltati), (0, 0))
        self.assertEqual(scena.attivi, [])
        self.assertIsNone(scena.objects.active)

    def test_inverti_scelta_ribalta_la_scelta(self):
        primo = OggettoFinto("Primo", scelto=True)
        secondo = OggettoFinto("Secondo")
        scena = vettore(primo, secondo)

        esito = selezione.inverti_scelta(scena)

        self.assertEqual(esito.scelti, 1)
        self.assertEqual(scena.attivi, ["Secondo"])

    def test_inverti_scelta_lascia_fuori_i_non_scegliibili(self):
        nascosto = OggettoFinto("Nascosto", nascosto=True)
        bloccato = OggettoFinto("Bloccato", bloccato=True, scelto=True)
        libero = OggettoFinto("Libero")
        scena = vettore(nascosto, bloccato, libero)

        esito = selezione.inverti_scelta(scena)

        self.assertEqual(esito.scelti, 1)
        self.assertEqual(esito.saltati, 2)
        self.assertEqual(scena.attivi, ["Libero"])

    def test_scegli_stesso_tipo_prende_solo_il_tipo(self):
        cubo = OggettoFinto("Cubo")
        sfera = OggettoFinto("Sfera")
        luce = OggettoFinto("Luce", tipo="LIGHT")
        scena = vettore(cubo, sfera, luce)

        esito = selezione.scegli_stesso_tipo(scena, sfera)

        self.assertEqual(esito.scelti, 2)
        self.assertEqual(scena.attivi, ["Cubo", "Sfera"])
        self.assertIs(scena.objects.active, sfera)

    def test_scegli_stesso_tipo_senza_riferimento_non_fa_nulla(self):
        scena = vettore(OggettoFinto("Cubo"))
        self.assertEqual(selezione.scegli_stesso_tipo(scena, None).scelti, 0)


class TestSceltaSingola(unittest.TestCase):
    def test_sostituisci_lascia_scelto_un_solo_oggetto(self):
        cubo = OggettoFinto("Cubo", scelto=True)
        sfera = OggettoFinto("Sfera")
        scena = vettore(cubo, sfera)

        esito = selezione.scegli_oggetto(scena, sfera, "sostituisci")

        self.assertEqual((esito.scelti, esito.saltati), (1, 0))
        self.assertEqual(scena.attivi, ["Sfera"])
        self.assertIs(scena.objects.active, sfera)

    def test_aggiungi_lascia_gli_altri(self):
        cubo = OggettoFinto("Cubo", scelto=True)
        sfera = OggettoFinto("Sfera")
        scena = vettore(cubo, sfera)

        selezione.scegli_oggetto(scena, sfera, "aggiungi")

        self.assertEqual(scena.attivi, ["Cubo", "Sfera"])

    def test_rimuovi_toglie_solo_l_oggetto_indicato(self):
        cubo = OggettoFinto("Cubo", scelto=True)
        sfera = OggettoFinto("Sfera", scelto=True)
        scena = vettore(cubo, sfera)
        scena.objects.active = sfera

        esito = selezione.scegli_oggetto(scena, sfera, "rimuovi")

        self.assertEqual(esito.scelti, 0)
        self.assertEqual(scena.attivi, ["Cubo"])
        self.assertIs(scena.objects.active, cubo)

    def test_rimuovi_toglie_l_attivo_quando_resta_vuoto(self):
        cubo = OggettoFinto("Cubo", scelto=True)
        scena = vettore(cubo)

        selezione.scegli_oggetto(scena, cubo, "rimuovi")

        self.assertIsNone(scena.objects.active)

    def test_un_oggetto_rifiutato_non_cambia_la_scelta(self):
        cubo = OggettoFinto("Cubo", scelto=True)
        bloccato = OggettoFinto("Bloccato", bloccato=True)
        scena = vettore(cubo, bloccato)

        esito = selezione.scegli_oggetto(scena, bloccato, "sostituisci")

        self.assertEqual((esito.scelti, esito.saltati), (0, 1))
        self.assertEqual(scena.attivi, ["Cubo"])

    def test_alterna_scelta_aggiunge_e_toglie(self):
        cubo = OggettoFinto("Cubo")
        scena = vettore(cubo)

        selezione.alterna_scelta(scena, cubo)
        self.assertTrue(cubo.select_get())

        selezione.alterna_scelta(scena, cubo)
        self.assertFalse(cubo.select_get())

    def test_alterna_scelta_funziona_anche_su_uno_nascosto(self):
        """La casella dell'elenco serve anche a ritrovare un oggetto nascosto."""
        nascosto = OggettoFinto("Nascosto", nascosto=True)
        scena = vettore(nascosto)

        esito = selezione.alterna_scelta(scena, nascosto)

        self.assertEqual((esito.scelti, esito.saltati), (1, 0))
        self.assertTrue(nascosto.select_get())

    def test_la_scelta_di_un_singolo_oggetto_bloccato_fallisce(self):
        bloccato = OggettoFinto("Bloccato", bloccato=True)
        scena = vettore(bloccato)

        esito = selezione.scegli_oggetto(scena, bloccato, "sostituisci")

        self.assertEqual(esito.saltati, 1)
        self.assertFalse(bloccato.select_get())


class TestElenco(unittest.TestCase):
    def test_elenco_in_ordine_alfabetico_senza_maiuscole(self):
        scena = vettore(OggettoFinto("Zaino"), OggettoFinto("albero"), OggettoFinto("Casa"))

        nomi = [oggetto.name for oggetto in selezione.oggetti_della_scena(scena)]

        self.assertEqual(nomi, ["albero", "Casa", "Zaino"])

    def test_elenco_di_una_scena_vuota(self):
        self.assertEqual(selezione.oggetti_della_scena(vettore()), [])


class TestTestiDeiRifiuti(unittest.TestCase):
    def test_i_messaggi_dei_rifiuti_esistono_e_hanno_il_nome(self):
        for chiave in ("ERRORE_OGGETTO_NON_SELEZIONABILE", "ERRORE_OGGETTO_NASCOSTO"):
            with self.subTest(chiave=chiave):
                testo = TESTI[chiave].format(nome="Cubo")
                self.assertIn("Cubo", testo)


if __name__ == "__main__":
    unittest.main()
