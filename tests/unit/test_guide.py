"""Prove della guida passo passo: comandi veri, testi veri, avanzamento giusto.

La guida promette di costruire una casetta usando **solo** comandi che esistono
in questa versione. Qui si controlla esattamente questo, senza aprire Blender:

* ogni comando citato dai passi esiste davvero (è uno degli identificatori
  dichiarati in `comandi.py`, con un operatore che lo implementa);
* ogni parametro passato a un comando è una proprietà di quell'operatore:
  altrimenti Blender rifiuterebbe la chiamata e il passo fallirebbe;
* ogni testo citato esiste nella mappa centrale, nomi degli oggetti compresi;
* l'avanzamento non esce mai dai passi e "Avanti" può arrivare in fondo
  (l'ultimo passo non si ripete all'infinito).
"""

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACCHETTO = ROOT / "addon" / "formafacile_3d"
if str(ROOT / "tests") not in sys.path:
    sys.path.insert(0, str(ROOT / "tests"))

import supporto_finto  # noqa: E402

supporto_finto.prepara_import_puro()

from formafacile_3d import comandi  # noqa: E402
from formafacile_3d.localization import TESTI  # noqa: E402
from formafacile_3d.scene import guide  # noqa: E402


def _identificatori_dichiarati() -> dict[str, str]:
    """Nomi delle costanti `ID_*` di `comandi.py` e loro valore."""
    albero = ast.parse((PACCHETTO / "comandi.py").read_text(encoding="utf-8"))
    valori: dict[str, str] = {}
    for nodo in albero.body:
        if not isinstance(nodo, ast.Assign):
            continue
        if not isinstance(nodo.value, ast.Constant) or not isinstance(nodo.value.value, str):
            continue
        for bersaglio in nodo.targets:
            if isinstance(bersaglio, ast.Name) and bersaglio.id.startswith("ID_"):
                valori[bersaglio.id] = nodo.value.value
    return valori


def _proprieta_degli_operatori() -> dict[str, set[str]]:
    """Per ogni comando, i nomi delle proprietà dichiarate dal suo operatore.

    Si legge il sorgente: serve a sapere che cosa Blender accetterebbe come
    parametro, senza eseguire i moduli (che importano `bpy`).
    """
    valori = _identificatori_dichiarati()
    proprieta: dict[str, set[str]] = {}
    for percorso in sorted((PACCHETTO / "operators").glob("*.py")):
        albero = ast.parse(percorso.read_text(encoding="utf-8"))
        for classe in [nodo for nodo in ast.walk(albero) if isinstance(nodo, ast.ClassDef)]:
            idname = None
            nomi: set[str] = set()
            for nodo in classe.body:
                if (
                    isinstance(nodo, ast.Assign)
                    and isinstance(nodo.value, ast.Attribute)
                    and nodo.value.attr.startswith("ID_")
                ):
                    for bersaglio in nodo.targets:
                        if isinstance(bersaglio, ast.Name) and bersaglio.id == "bl_idname":
                            idname = valori.get(nodo.value.attr)
                if isinstance(nodo, ast.AnnAssign) and isinstance(nodo.target, ast.Name):
                    nomi.add(nodo.target.id)
            if idname:
                proprieta.setdefault(idname, set()).update(nomi)
    return proprieta


def _valore_testo(valore: object) -> object:
    """Valore di un parametro come lo risolve la guida a Blender aperto."""
    if isinstance(valore, guide.Testo):
        assert valore.chiave in TESTI, f"Testo inesistente: {valore.chiave}"
        return TESTI[valore.chiave]
    return valore


class TestComandiDellaGuida(unittest.TestCase):
    def guide(self):
        return [guide.guida(chiave) for chiave in guide.chiavi_guide()]

    def test_c_e_almeno_una_guida_e_ha_dei_passi(self):
        self.assertTrue(guide.chiavi_guide())
        for corrente in self.guide():
            with self.subTest(guida=corrente.chiave):
                self.assertTrue(corrente.passi)
                self.assertIn(corrente.titolo, TESTI)
                self.assertIn(corrente.descrizione, TESTI)

    def test_ogni_passo_si_spiega(self):
        for corrente in self.guide():
            for passo in corrente.passi:
                with self.subTest(passo=passo.chiave):
                    self.assertTrue(passo.azioni, "un passo senza comandi non fa nulla")
                    self.assertIn(passo.titolo, TESTI)
                    self.assertIn(passo.spiegazione, TESTI)

    def test_le_chiavi_dei_passi_non_si_ripetono(self):
        for corrente in self.guide():
            chiavi = [passo.chiave for passo in corrente.passi]
            with self.subTest(guida=corrente.chiave):
                self.assertEqual(len(chiavi), len(set(chiavi)))

    def test_ogni_comando_citato_esiste_davvero(self):
        dichiarati = set(_identificatori_dichiarati().values())
        for corrente in self.guide():
            for passo in corrente.passi:
                for azione in passo.azioni:
                    with self.subTest(comando=azione.comando):
                        self.assertIn(azione.comando, dichiarati)

    def test_ogni_comando_ha_un_operatore_che_lo_implementa(self):
        proprieta = _proprieta_degli_operatori()
        for corrente in self.guide():
            for passo in corrente.passi:
                for azione in passo.azioni:
                    with self.subTest(comando=azione.comando):
                        self.assertIn(azione.comando, proprieta)

    def test_ogni_parametro_e_una_proprieta_dell_operatore(self):
        proprieta = _proprieta_degli_operatori()
        for corrente in self.guide():
            for passo in corrente.passi:
                for azione in passo.azioni:
                    nomi = {chiave for chiave, _valore in azione.parametri}
                    with self.subTest(comando=azione.comando, parametri=sorted(nomi)):
                        self.assertTrue(
                            nomi <= proprieta[azione.comando],
                            f"{azione.comando} non accetta {sorted(nomi - proprieta[azione.comando])}",
                        )

    def test_i_valori_dei_parametri_sono_testi_o_valori_semplici(self):
        for corrente in self.guide():
            for passo in corrente.passi:
                for azione in passo.azioni:
                    for chiave, valore in azione.parametri:
                        with self.subTest(comando=azione.comando, parametro=chiave):
                            risolto = _valore_testo(valore)
                            self.assertIn(type(risolto), (str, int, float, bool))

    def test_i_nomi_degli_oggetti_sono_testi_centrali(self):
        for corrente in self.guide():
            for passo in corrente.passi:
                for testo in passo.selezione:
                    with self.subTest(nome=testo.chiave):
                        self.assertIn(testo.chiave, TESTI)

    def test_le_impostazioni_dei_passi_sono_valori_di_scena_conosciuti(self):
        for corrente in self.guide():
            for passo in corrente.passi:
                for campo, valore in passo.impostazioni:
                    with self.subTest(passo=passo.chiave, campo=campo):
                        self.assertIn(campo, (guide.STATO_GRANDEZZA_FORMA, guide.STATO_PASSO))
                        self.assertIsInstance(valore, (int, float))

    def test_la_guida_principale_e_quella_della_casetta(self):
        self.assertIn(guide.chiavi_guide(), [("casetta",)])


class TestAvanzamento(unittest.TestCase):
    def test_l_indice_resta_fra_i_passi(self):
        self.assertEqual(guide.indice_valido(-5, 5), 0)
        self.assertEqual(guide.indice_valido(2, 5), 2)
        self.assertEqual(guide.indice_valido(99, 5), 5)
        self.assertEqual(guide.indice_valido("boh", 5), 0)

    def test_avanti_arriva_in_fondo_e_non_oltre(self):
        totale = 3
        self.assertEqual(guide.prossimo_indice(0, totale, comandi.MODO_GUIDA_AVANTI), 1)
        self.assertEqual(guide.prossimo_indice(2, totale, comandi.MODO_GUIDA_AVANTI), 3)
        self.assertEqual(guide.prossimo_indice(3, totale, comandi.MODO_GUIDA_AVANTI), 3)

    def test_indietro_non_scende_sotto_zero(self):
        self.assertEqual(guide.prossimo_indice(1, 3, comandi.MODO_GUIDA_INDIETRO), 0)
        self.assertEqual(guide.prossimo_indice(0, 3, comandi.MODO_GUIDA_INDIETRO), 0)
        self.assertEqual(guide.prossimo_indice(3, 3, comandi.MODO_GUIDA_INDIETRO), 2)

    def test_la_guida_e_finita_solo_in_fondo(self):
        self.assertFalse(guide.completata(0, 3))
        self.assertFalse(guide.completata(2, 3))
        self.assertTrue(guide.completata(3, 3))
        self.assertFalse(guide.completata(0, 0))

    def test_il_passo_mostrato_resta_dentro_l_elenco(self):
        corrente = guide.guida("casetta")
        ultimo = guide.passo_corrente("casetta", len(corrente.passi))
        self.assertIs(ultimo, corrente.passi[-1])
        self.assertIsNone(guide.passo_corrente("non-esiste", 0))

    def test_ogni_passo_si_puo_eseguire_una_volta_sola(self):
        # Percorso completo: si parte da zero e si arriva a "finita" senza mai
        # ripetere un passo.
        corrente = guide.guida("casetta")
        indice = 0
        eseguiti = []
        while not guide.completata(indice, len(corrente.passi)):
            passo = guide.passo_corrente("casetta", indice)
            eseguiti.append(passo.chiave)
            indice = guide.prossimo_indice(indice, len(corrente.passi), comandi.MODO_GUIDA_AVANTI)
        self.assertEqual(len(eseguiti), len(corrente.passi))
        self.assertEqual(len(set(eseguiti)), len(corrente.passi))


if __name__ == "__main__":
    unittest.main()
