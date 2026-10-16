"""Prove del disegno dell'interfaccia su un blocco finto.

Il disegno non decide nulla: riceve un piano già pronto. Qui si verifica che
ogni elemento del piano diventi la chiamata giusta e, soprattutto, che il
pannello non fallisca mai: se un dato non è più disponibile, al suo posto deve
comparire una riga disattivata.
"""

from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
for _percorso in (ROOT / "tests", ROOT / "addon"):
    if str(_percorso) not in sys.path:
        sys.path.insert(0, str(_percorso))

import supporto_finto  # noqa: E402

supporto_finto.prepara_import_puro()

from formafacile_3d import comandi, configuration  # noqa: E402
from formafacile_3d.localization import TESTI  # noqa: E402
from formafacile_3d.ui import modello, piano, renderer  # noqa: E402
from formafacile_3d.ui.modello import Azione, Campo, Etichetta, Gruppo, Pannello, Riga  # noqa: E402


def scena_finta(**valori: object) -> object:
    """Scena finta con lo stato `formafacile` annidato, come in Blender."""
    stato = types.SimpleNamespace(
        modalita=valori.pop("modalita", configuration.MODALITA_SEMPLICE),
        filtro=valori.pop("filtro", ""),
        passo=valori.pop("passo", configuration.PASSO_PREDEFINITO),
    )
    return types.SimpleNamespace(formafacile=stato, **valori)


def oggetto_finto(nome: str = "Cubo", **valori: object) -> object:
    """Oggetto finto con i dati separati, come in Blender.

    Include le proprietà usate dai campi numerici del pannello Oggetto scelto
    (posizione, rotazione e dimensione), così le prove verificano che quei campi
    vengano disegnati davvero e non sostituiti da righe disattivate.
    """
    dati = valori.pop("dati", None)
    if dati is None:
        dati = types.SimpleNamespace(name=f"Geometria di {nome}", energy=1000.0)
    valori.setdefault("location", (0.0, 0.0, 0.0))
    valori.setdefault("rotation_mode", "XYZ")
    valori.setdefault("rotation_euler", (0.0, 0.0, 0.0))
    valori.setdefault("dimensions", (2.0, 2.0, 2.0))
    valori.setdefault("scale", (1.0, 1.0, 1.0))
    return types.SimpleNamespace(name=nome, data=dati, **valori)


class TestDisegnoDelPannello(unittest.TestCase):
    def setUp(self) -> None:
        self.registro: list[dict] = []
        self.blocco = supporto_finto.BloccoFinto(self.registro)

    def disegna(self, pannello_ui: Pannello, risolutore: dict | None = None) -> list[dict]:
        renderer.disegna_pannello(self.blocco, pannello_ui, risolutore or {})
        return self.registro

    def test_ogni_gruppo_diventa_un_riquadro_con_titolo(self):
        pannello_ui = Pannello(
            "prova",
            (
                Gruppo("Costruisci", (Riga((Azione(comandi.ID_AGGIUNGI_CUBO, "Cubo"),)),)),
                Gruppo("", (Riga((Etichetta("Senza titolo"),)),)),
            ),
        )
        self.disegna(pannello_ui)
        self.assertEqual(len(supporto_finto.riquadri(self.registro)), 2)
        self.assertEqual(supporto_finto.etichette(self.registro), ["Costruisci", "Senza titolo"])

    def test_riga_distanziata_non_allinea_i_pulsanti(self):
        pannello_ui = Pannello(
            "prova",
            (
                Gruppo(
                    "Prova",
                    (
                        Riga((Azione(comandi.ID_AGGIUNGI_CUBO, "Cubo"),)),
                        Riga((Azione(comandi.ID_AGGIUNGI_SFERA, "Sfera"),), distanziata=True),
                    ),
                ),
            ),
        )
        self.disegna(pannello_ui)
        allineamenti = [voce["parametri"]["align"] for voce in supporto_finto.righe(self.registro)]
        self.assertEqual(allineamenti, [True, False])

    def test_riga_disabilitata_disattiva_il_blocco(self):
        pannello_ui = Pannello(
            "prova",
            (
                Gruppo(
                    "Costruisci",
                    (Riga((Azione(comandi.ID_AGGIUNGI_CUBO, "Cubo"),), disabilitata=True),),
                ),
            ),
        )
        self.disegna(pannello_ui)
        self.assertIn(False, supporto_finto.proprieta_assegnate(self.registro, "enabled"))

    def test_il_pulsante_porta_testo_icona_e_stato(self):
        pannello_ui = Pannello(
            "prova",
            (
                Gruppo(
                    "Prova",
                    (
                        Riga(
                            (
                                Azione(comandi.ID_AGGIUNGI_CUBO, "Cubo", "MESH_CUBE"),
                                Azione(comandi.ID_ALTERNA_SCELTA, "Scelta", "CHECKBOX_HLT", premuto=True),
                                Azione(comandi.ID_PULISCI_FILTRO, "Pulisci", "X", solo_icona=True),
                            )
                        ),
                    ),
                ),
            ),
        )
        self.disegna(pannello_ui)
        comandi_disegnati = supporto_finto.comandi(self.registro)
        self.assertEqual(
            comandi_disegnati,
            [comandi.ID_AGGIUNGI_CUBO, comandi.ID_ALTERNA_SCELTA, comandi.ID_PULISCI_FILTRO],
        )
        primo, secondo, terzo = [
            voce for voce in self.registro if voce["tipo"] == "comando"
        ]
        self.assertEqual(primo["parametri"]["text"], "Cubo")
        self.assertEqual(primo["parametri"]["icon"], "MESH_CUBE")
        self.assertTrue(secondo["parametri"]["depress"])
        self.assertEqual(terzo["parametri"], {"text": "", "icon": "X"})
        self.assertEqual(secondo["parametri"]["text"], "Scelta")

    def test_i_parametri_del_pulsante_diventano_valori_del_comando(self):
        pannello_ui = Pannello(
            "prova",
            (
                Gruppo(
                    "Prova",
                    (
                        Riga(
                            (
                                Azione(
                                    comandi.ID_SPOSTA_PASSO,
                                    "Destra",
                                    parametri=(("direzione", "destra"),),
                                ),
                            )
                        ),
                    ),
                ),
            ),
        )
        self.disegna(pannello_ui)
        self.assertEqual(
            supporto_finto.valori(self.registro, comandi.ID_SPOSTA_PASSO),
            [{"direzione": "destra"}],
        )

    def test_un_avviso_viene_evidenziato(self):
        pannello_ui = Pannello(
            "prova", (Gruppo("", (Riga((Etichetta("Attenzione", icona="ERROR", avviso=True),)),)),)
        )
        self.disegna(pannello_ui)
        self.assertIn(True, supporto_finto.proprieta_assegnate(self.registro, "alert"))
        self.assertEqual(supporto_finto.etichette(self.registro), ["Attenzione"])


class TestCampiCollegatiAiDati(unittest.TestCase):
    def setUp(self) -> None:
        self.registro: list[dict] = []
        self.blocco = supporto_finto.BloccoFinto(self.registro)

    def pannello_con(self, campo: Campo) -> Pannello:
        return Pannello("prova", (Gruppo("Prova", (Riga((campo,)),)),))

    def test_campo_dello_stato_della_scena(self):
        scena = scena_finta()
        campo = Campo(
            riferimento=configuration.RIFERIMENTO_SCENA,
            chiave=configuration.CHIAVE_SCENA,
            proprieta=configuration.CAMPO_MODALITA,
            testo="Modalità",
            espanso=True,
        )
        renderer.disegna_pannello(
            self.blocco,
            self.pannello_con(campo),
            {configuration.CHIAVE_SCENA: scena},
        )
        voci = [voce for voce in self.registro if voce["tipo"] == "campo"]
        self.assertEqual(len(voci), 1)
        self.assertIs(voci[0]["dati"], scena)
        self.assertEqual(voci[0]["proprieta"], configuration.CAMPO_MODALITA)
        self.assertTrue(voci[0]["parametri"]["expand"])
        self.assertEqual(voci[0]["parametri"]["text"], "Modalità")

    def test_campo_dei_dati_dell_oggetto(self):
        oggetto = oggetto_finto("Luce")
        campo = Campo(
            riferimento=configuration.RIFERIMENTO_DATI,
            chiave="Luce",
            proprieta="energy",
            testo="Potenza",
        )
        renderer.disegna_pannello(self.blocco, self.pannello_con(campo), {"Luce": oggetto})
        voci = [voce for voce in self.registro if voce["tipo"] == "campo"]
        self.assertEqual(len(voci), 1)
        self.assertIs(voci[0]["dati"], oggetto.data)
        self.assertEqual(voci[0]["proprieta"], "energy")

    def test_campo_interruttore(self):
        oggetto = oggetto_finto(hide_select=False)
        campo = Campo(
            riferimento=configuration.RIFERIMENTO_OGGETTO,
            chiave="Cubo",
            proprieta="hide_select",
            interruttore=True,
        )
        renderer.disegna_pannello(self.blocco, self.pannello_con(campo), {"Cubo": oggetto})
        voci = [voce for voce in self.registro if voce["tipo"] == "campo"]
        self.assertTrue(voci[0]["parametri"]["toggle"])

    def test_dato_mancante_diventa_riga_disattivata(self):
        campo = Campo(
            riferimento=configuration.RIFERIMENTO_SCENA,
            chiave=configuration.CHIAVE_SCENA,
            proprieta=configuration.CAMPO_MODALITA,
            testo="Modalità",
        )
        renderer.disegna_pannello(self.blocco, self.pannello_con(campo), {})
        self.assertEqual([voce for voce in self.registro if voce["tipo"] == "campo"], [])
        self.assertIn("Modalità", supporto_finto.etichette(self.registro))
        self.assertIn(False, supporto_finto.proprieta_assegnate(self.registro, "enabled"))

    def test_percorso_annidato_non_disponibile(self):
        scena_senza_stato = types.SimpleNamespace()
        campo = Campo(
            riferimento=configuration.RIFERIMENTO_SCENA,
            chiave=configuration.CHIAVE_SCENA,
            proprieta=configuration.CAMPO_MODALITA,
            testo="Modalità",
        )
        renderer.disegna_pannello(
            self.blocco,
            self.pannello_con(campo),
            {configuration.CHIAVE_SCENA: scena_senza_stato},
        )
        self.assertEqual([voce for voce in self.registro if voce["tipo"] == "campo"], [])
        self.assertIn("Modalità", supporto_finto.etichette(self.registro))

    def test_un_campo_senza_dati_mostra_il_suo_nome(self):
        campo = Campo(
            riferimento=configuration.RIFERIMENTO_OGGETTO,
            chiave="Cubo",
            proprieta="scale",
        )
        renderer.disegna_pannello(self.blocco, self.pannello_con(campo), {})
        self.assertIn("scale", supporto_finto.etichette(self.registro))

    def test_risolutore_completamente_guasto_non_ferma_il_pannello(self):
        campo = Campo(
            riferimento=configuration.RIFERIMENTO_OGGETTO,
            chiave="Cubo",
            proprieta="location",
            testo="Posizione",
        )
        renderer.disegna_pannello(self.blocco, self.pannello_con(campo), {"Cubo": object()})
        self.assertIn("Posizione", supporto_finto.etichette(self.registro))


class TestDisegnoARobustezza(unittest.TestCase):
    """Blender può rifiutare una chiamata: il pannello deve restare in piedi."""

    def test_pulsante_rifiutato_diventa_etichetta_di_errore(self):
        registro: list[dict] = []
        blocco = supporto_finto.BloccoCheFallisce(registro, nome_metodo="operator")
        pannello_ui = Pannello(
            "prova",
            (Gruppo("Prova", (Riga((Azione(comandi.ID_AGGIUNGI_CUBO, "Cubo"),)),)),),
        )
        renderer.disegna_pannello(blocco, pannello_ui, {})
        etichette = supporto_finto.etichette(registro)
        self.assertIn("Cubo", etichette)
        self.assertEqual(supporto_finto.icone_usate(registro), ["ERROR"])

    def test_campo_rifiutato_diventa_etichetta_di_errore(self):
        registro: list[dict] = []
        blocco = supporto_finto.BloccoCheFallisce(registro, nome_metodo="prop")
        campo = Campo(
            riferimento=configuration.RIFERIMENTO_SCENA,
            chiave=configuration.CHIAVE_SCENA,
            proprieta=configuration.CAMPO_FILTRO,
            testo="Cerca",
        )
        pannello_ui = Pannello("prova", (Gruppo("Prova", (Riga((campo,)),)),))
        renderer.disegna_pannello(blocco, pannello_ui, {configuration.CHIAVE_SCENA: scena_finta()})
        self.assertIn(TESTI["ETICHETTA_CAMPO_NON_DISPONIBILE"], supporto_finto.etichette(registro))

    def test_un_pannello_vuoto_non_disegna_nulla(self):
        registro: list[dict] = []
        blocco = supporto_finto.BloccoFinto(registro)
        renderer.disegna_pannello(blocco, Pannello("prova", ()), {})
        self.assertEqual(registro, [])


class TestAnteprimaDelMateriale(unittest.TestCase):
    """L'anteprima di un dato di Blender si disegna solo quando il dato c'è."""

    def _disegna(self, risolutore, elemento=None):
        registro: list[dict] = []
        blocco = supporto_finto.BloccoFinto(registro)
        elemento = elemento or modello.Anteprima(
            chiave="materiale", testo="Anteprima assente"
        )
        renderer.disegna_anteprima(blocco, elemento, risolutore)
        return registro

    def test_senza_dato_resta_il_testo(self):
        registro = self._disegna({})
        self.assertEqual([voce["tipo"] for voce in registro], ["etichetta"])
        self.assertIn("Anteprima assente", supporto_finto.etichette(registro))

    def test_con_il_dato_si_disegna_l_anteprima(self):
        materiale = object()
        registro = self._disegna({"materiale": materiale})
        self.assertEqual([voce["tipo"] for voce in registro], ["anteprima"])
        self.assertIs(registro[0]["dati"], materiale)
        self.assertIn("id", registro[0]["parametri"])

    def test_se_il_disegno_fallisce_resta_il_testo(self):
        class BloccoSenzaAnteprima(supporto_finto.BloccoFinto):
            def template_preview(self, id, **parametri):  # noqa: A002
                raise TypeError("Anteprima non disponibile")

        registro: list[dict] = []
        blocco = BloccoSenzaAnteprima(registro)
        renderer.disegna_anteprima(
            blocco,
            modello.Anteprima(chiave="materiale", testo="Anteprima assente"),
            {"materiale": object()},
        )
        self.assertEqual([voce["tipo"] for voce in registro], ["etichetta"])
        self.assertIn("Anteprima assente", supporto_finto.etichette(registro))


class TestPianoRealeSulDisegno(unittest.TestCase):
    """Il piano di una scena tipica deve diventare un disegno completo."""

    def contesto(self, **valori: object):
        valori.setdefault("modalita", configuration.MODALITA_COMPLETA)
        valori.setdefault(
            "oggetti",
            (
                modello.Oggetto(
                    chiave="Albero",
                    nome="Albero",
                    tipo="MESH",
                    tipo_parola="Forma",
                    icona="MESH_DATA",
                    scelto=True,
                    attivo=True,
                    nome_dati="Geometria di Albero",
                    vertici=8,
                    facce=6,
                ),
            ),
        )
        return modello.crea_contesto(**valori)  # type: ignore[arg-type]

    def test_ogni_pannello_si_disegna_e_usa_solo_icone_verificate(self):
        from formafacile_3d.ui import icone

        contesto = self.contesto()
        risolutore = {"scena": scena_finta(), "Albero": oggetto_finto("Albero")}
        for pannello_ui in piano.costruisci_piano(contesto):
            with self.subTest(pannello=pannello_ui.chiave):
                registro: list[dict] = []
                renderer.disegna_pannello(
                    supporto_finto.BloccoFinto(registro), pannello_ui, risolutore
                )
                self.assertTrue(registro)
                for nome in supporto_finto.icone_usate(registro):
                    self.assertIn(nome, icone.ICONE_USATE)
                for comando in supporto_finto.comandi(registro):
                    self.assertIn(comando, _IDENTIFICATORI_DICHIARATI)

    def test_nessun_pulsante_invisibile(self):
        """Un pulsante senza testo deve almeno avere un'icona."""
        contesto = self.contesto()
        risolutore = {"scena": scena_finta(), "Albero": oggetto_finto("Albero")}
        for pannello_ui in piano.costruisci_piano(contesto):
            registro: list[dict] = []
            renderer.disegna_pannello(
                supporto_finto.BloccoFinto(registro), pannello_ui, risolutore
            )
            for voce in registro:
                if voce["tipo"] != "comando":
                    continue
                with self.subTest(pannello=pannello_ui.chiave, comando=voce["idname"]):
                    self.assertTrue(
                        voce["parametri"]["text"] or voce["parametri"].get("icon"),
                        "Pulsante senza testo e senza icona",
                    )

    def test_il_pannello_della_modalita_semplice_non_mostra_campi_tecnici(self):
        contesto = self.contesto(modalita=configuration.MODALITA_SEMPLICE)
        risolutore = {"scena": scena_finta(), "Albero": oggetto_finto("Albero")}
        chiavi = [pannello_ui.chiave for pannello_ui in piano.costruisci_piano(contesto)]
        self.assertNotIn("completo", chiavi)

        # I campi numerici (posizione, rotazione, dimensione) sono previsti anche
        # nella modalità Semplice: sono i numeri che chi inizia chiede. Restano
        # invece fuori i campi tecnici veri, quelli della modalità Completa.
        tecnici = {
            "name",
            "scale",
            "display_type",
            "rotation_mode",
            "hide_render",
            "hide_select",
        }
        disegnate: list[str] = []
        for pannello_ui in piano.costruisci_piano(contesto):
            registro: list[dict] = []
            renderer.disegna_pannello(
                supporto_finto.BloccoFinto(registro), pannello_ui, risolutore
            )
            disegnate.extend(proprieta for _tipo, proprieta in supporto_finto.campi(registro))
        self.assertEqual([nome for nome in disegnate if nome in tecnici], [])
        for previsto in ("location", "rotation_euler", "dimensions"):
            self.assertIn(previsto, disegnate)

    def test_i_campi_numerici_usano_uno_asse_per_volta(self):
        """Posizione e dimensione si disegnano come tre campi brevi, uno per asse."""
        contesto = self.contesto()
        risolutore = {"scena": scena_finta(), "Albero": oggetto_finto("Albero")}
        registro: list[dict] = []
        for pannello_ui in piano.costruisci_piano(contesto):
            renderer.disegna_pannello(
                supporto_finto.BloccoFinto(registro), pannello_ui, risolutore
            )
        per_indice: dict[tuple[str, int], int] = {}
        for voce in registro:
            if voce["tipo"] != "campo":
                continue
            indice = voce["parametri"].get("index")
            if indice is None:
                continue
            chiave = (str(voce["proprieta"]), int(indice))
            per_indice[chiave] = per_indice.get(chiave, 0) + 1
        for proprieta in ("location", "dimensions"):
            for indice in range(3):
                self.assertIn((proprieta, indice), per_indice)


_IDENTIFICATORI_DICHIARATI = {
    valore
    for nome, valore in vars(comandi).items()
    if nome.startswith("ID_") and isinstance(valore, str)
} | {"transform.translate", "transform.rotate", "transform.resize"}


if __name__ == "__main__":
    unittest.main()
