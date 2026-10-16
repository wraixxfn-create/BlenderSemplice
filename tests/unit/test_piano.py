"""Prove del piano dell'interfaccia: che cosa vede l'utente in ogni situazione.

Girano senza Blender: il piano è una descrizione di dati puri, quindi le
regole su scelta singola, scelta multipla, nessuna scelta, elenco lungo,
ricerca, oggetti nascosti e modalità semplice o completa si possono verificare
qui, velocemente e senza aprire finestre.
"""

from __future__ import annotations

import sys
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
from formafacile_3d.ui import icone, modello, piano  # noqa: E402
from formafacile_3d.ui.modello import Azione, Campo, Contesto, Etichetta, Oggetto  # noqa: E402


def oggetto(
    nome: str,
    tipo: str = "MESH",
    *,
    scelto: bool = False,
    attivo: bool = False,
    nascosto: bool = False,
    nascosto_direttamente: bool = False,
    bloccato: bool = False,
    modo_rotazione: str = "XYZ",
) -> Oggetto:
    return Oggetto(
        chiave=nome,
        nome=nome,
        tipo=tipo,
        tipo_parola=icone.parola_tipo(tipo),
        icona=icone.icona_tipo(tipo),
        scelto=scelto,
        attivo=attivo,
        nascosto=nascosto,
        nascosto_direttamente=nascosto_direttamente,
        bloccato=bloccato,
        modo_rotazione=modo_rotazione,
        nome_dati=f"Geometria di {nome}" if tipo == "MESH" else "",
        vertici=8 if tipo == "MESH" else 0,
        facce=6 if tipo == "MESH" else 0,
    )


def contesto(*oggetti: Oggetto, **valori: object) -> Contesto:
    valori.setdefault("oggetti", oggetti)
    return modello.crea_contesto(**valori)  # type: ignore[arg-type]


def pannello(contesto_ui: Contesto, chiave: str) -> piano.Pannello:
    for candidato in piano.costruisci_piano(contesto_ui):
        if candidato.chiave == chiave:
            return candidato
    raise AssertionError(f"Pannello assente: {chiave}")


def testi(contesto_ui: Contesto, chiave: str) -> list[str]:
    """Tutti i testi di un pannello: titoli, etichette e pulsanti."""
    risultato: list[str] = []
    for gruppo in pannello(contesto_ui, chiave).gruppi:
        risultato.append(gruppo.titolo)
        for riga in gruppo.righe:
            for elemento in riga.elementi:
                if isinstance(elemento, Etichetta):
                    risultato.append(elemento.testo)
                elif isinstance(elemento, Azione):
                    risultato.append(elemento.testo)
                elif isinstance(elemento, Campo):
                    risultato.append(elemento.testo or elemento.proprieta)
    return [testo for testo in risultato if testo]


def elementi(contesto_ui: Contesto, chiave: str, tipo: type) -> list:
    """Tutti gli elementi di un certo tipo presenti in un pannello."""
    raccolti: list = []
    for gruppo in pannello(contesto_ui, chiave).gruppi:
        for riga in gruppo.righe:
            raccolti.extend(
                elemento for elemento in riga.elementi if isinstance(elemento, tipo)
            )
    return raccolti


def identificatori(contesto_ui: Contesto, chiave: str) -> list[str]:
    return [azione.idname for azione in elementi(contesto_ui, chiave, Azione)]


class TestStrutturaDelPiano(unittest.TestCase):
    def test_modalita_semplice_mostra_tre_pannelli(self):
        chiavi = [p.chiave for p in piano.costruisci_piano(contesto())]
        self.assertEqual(chiavi, ["principale", "scena", "oggetto"])

    def test_modalita_completa_aggiunge_il_pannello_tecnico(self):
        chiavi = [
            p.chiave
            for p in piano.costruisci_piano(contesto(modalita=configuration.MODALITA_COMPLETA))
        ]
        self.assertEqual(chiavi, ["principale", "scena", "oggetto", "completo"])

    def test_l_interfaccia_usa_solo_i_comandi_dichiarati(self):
        """La tabella dei comandi è l'unica fonte: niente nomi inventati."""
        dichiarati = {
            valore
            for nome, valore in vars(comandi).items()
            if nome.startswith("ID_") and isinstance(valore, str)
        }
        contesto_ui = contesto(
            oggetto("Cubo", scelto=True, attivo=True),
            oggetto("Luce", "LIGHT", scelto=True),
            oggetto("Telecamera", "CAMERA", attivo=True),
            modalita=configuration.MODALITA_COMPLETA,
        )
        usati = set()
        for chiave in ("principale", "scena", "oggetto", "completo"):
            usati.update(identificatori(contesto_ui, chiave))
        estranei = {nome for nome in usati if nome.startswith("formafacile.")} - dichiarati
        self.assertEqual(estranei, set())

    def test_le_chiavi_del_piano_sono_univoche(self):
        for modalita in (configuration.MODALITA_SEMPLICE, configuration.MODALITA_COMPLETA):
            with self.subTest(modalita=modalita):
                chiavi = [
                    p.chiave for p in piano.costruisci_piano(contesto(modalita=modalita))
                ]
                self.assertEqual(len(chiavi), len(set(chiavi)))

    def test_il_piano_non_cambia_fra_due_letture(self):
        contesto_ui = contesto(oggetto("Cubo", scelto=True, attivo=True))
        self.assertEqual(
            piano.costruisci_piano(contesto_ui), piano.costruisci_piano(contesto_ui)
        )

    def test_icone_usate_dall_interfaccia_sono_verificate(self):
        contesto_ui = contesto(
            oggetto("Cubo", scelto=True, attivo=True),
            oggetto("Luce", "LIGHT", scelto=True),
            modalita=configuration.MODALITA_COMPLETA,
        )
        for chiave in ("principale", "scena", "oggetto", "completo"):
            for azione in elementi(contesto_ui, chiave, Azione):
                with self.subTest(chiave=chiave, comando=azione.idname):
                    if azione.idname.startswith("formafacile."):
                        self.assertTrue(azione.testo or azione.solo_icona)
                    self.assertIn(azione.icona, icone.ICONE_USATE | {""})

    def test_chiavi_azione_elenca_tutti_i_comandi_del_piano(self):
        contesto_ui = contesto(
            oggetto("Cubo", scelto=True, attivo=True), modalita=configuration.MODALITA_COMPLETA
        )
        attesi = [
            azione.idname
            for pannello_ui in piano.costruisci_piano(contesto_ui)
            for gruppo in pannello_ui.gruppi
            for riga in gruppo.righe
            for azione in riga.elementi
            if isinstance(azione, Azione)
        ]
        self.assertEqual(list(piano.chiavi_azione(contesto_ui)), attesi)
        self.assertIn(comandi.ID_VISTA_INIZIALE, attesi)
        self.assertIn(comandi.ID_ANNULLA, attesi)


class TestCostruisci(unittest.TestCase):
    def test_azioni_principali_sono_in_italiano_e_in_ordine(self):
        testo = testi(contesto(), "principale")
        for chiave in (
            "GRUPPO_COSTRUISCI",
            "GRUPPO_STORIA",
            "GRUPPO_GUARDA",
            "GRUPPO_AIUTO",
        ):
            with self.subTest(gruppo=chiave):
                self.assertIn(TESTI[chiave], testo)
        self.assertIn(TESTI["AZIONE_AGGIUNGI_CUBO"], testo)
        self.assertIn(TESTI["AZIONE_AGGIUNGI_LUCE"], testo)

    def test_annulla_e_ripeti_sono_sempre_visibili(self):
        """Anche nella scena vuota i due pulsanti più cercati restano a portata."""
        comandi_visibili = identificatori(contesto(), "principale")
        self.assertIn(comandi.ID_ANNULLA, comandi_visibili)
        self.assertIn(comandi.ID_RIPETI, comandi_visibili)
        testo = testi(contesto(), "principale")
        self.assertIn(TESTI["AZIONE_ANNULLA"], testo)
        self.assertIn(TESTI["AZIONE_RIPETI"], testo)

    def test_vista_iniziale_sempre_visibile_inquadra_solo_se_c_e_una_vista(self):
        senza_vista = identificatori(contesto(vista_disponibile=False), "principale")
        self.assertIn(comandi.ID_VISTA_INIZIALE, senza_vista)
        self.assertNotIn(comandi.ID_INQUADRA_TUTTO, senza_vista)

        con_vista = identificatori(contesto(vista_disponibile=True), "principale")
        self.assertIn(comandi.ID_INQUADRA_TUTTO, con_vista)

    def test_in_modalita_modifica_la_creazione_e_disattivata(self):
        contesto_ui = contesto(in_modalita_oggetto=False)
        self.assertIn(TESTI["ETICHETTA_MODALITA_MODIFICA"], testi(contesto_ui, "principale"))
        creazione = [
            riga
            for gruppo in pannello(contesto_ui, "principale").gruppi
            if gruppo.titolo == TESTI["GRUPPO_COSTRUISCI"]
            for riga in gruppo.righe
        ]
        self.assertTrue(creazione)
        self.assertTrue(all(riga.disabilitata for riga in creazione))

    def test_il_messaggio_recente_compare_in_cima(self):
        contesto_ui = contesto(messaggio="Aggiunto: Cubo", messaggio_recente=True)
        primo = pannello(contesto_ui, "principale").gruppi[0]
        self.assertEqual(primo.righe[0].elementi[0].testo, "Aggiunto: Cubo")
        self.assertEqual(primo.righe[0].elementi[0].icona, "INFO")

    def test_il_messaggio_scaduto_non_compare(self):
        contesto_ui = contesto(messaggio="Aggiunto: Cubo", messaggio_recente=False)
        self.assertNotIn("Aggiunto: Cubo", testi(contesto_ui, "principale"))

    def test_in_modalita_completa_compare_il_promemoria(self):
        contesto_ui = contesto(modalita=configuration.MODALITA_COMPLETA)
        self.assertIn(TESTI["ETICHETTA_AVANZATO_ATTIVO"], testi(contesto_ui, "principale"))


class TestElencoDellaScena(unittest.TestCase):
    def test_scena_vuota_spiega_cosa_fare(self):
        testo = testi(contesto(), "scena")
        self.assertIn(TESTI["ETICHETTA_NESSUN_OGGETTO"], testo)
        self.assertIn(TESTI["AIUTO_NESSUN_OGGETTO"], testo)

    def test_conteggio_in_parole_semplici(self):
        uno = testi(contesto(oggetto("Cubo", scelto=True)), "scena")
        self.assertIn(
            TESTI["ETICHETTA_CONTEGGIO"].format(
                oggetti=TESTI["ETICHETTA_OGGETTO_UNO"], scelti=TESTI["ETICHETTA_SCELTI_UNO"]
            ),
            uno,
        )

        molti = testi(
            contesto(oggetto("Cubo", scelto=True), oggetto("Sfera"), oggetto("Piano")), "scena"
        )
        self.assertIn(
            TESTI["ETICHETTA_CONTEGGIO"].format(
                oggetti=TESTI["ETICHETTA_OGGETTI"].format(numero=3),
                scelti=TESTI["ETICHETTA_SCELTI_UNO"],
            ),
            molti,
        )

    def test_il_conteggio_ricorda_quanti_oggetti_sono_nascosti(self):
        contesto_ui = contesto(
            oggetto("Cubo", scelto=True),
            oggetto("Sfera", nascosto=True, nascosto_direttamente=True),
        )
        self.assertIn(
            TESTI["ETICHETTA_OGGETTI_NASCOSTI"].format(numero=1),
            " ".join(testi(contesto_ui, "scena")),
        )

    def test_ogni_riga_ha_scegli_scelta_visibilita_lucchetto(self):
        contesto_ui = contesto(oggetto("Cubo"))
        identificatori_elenco = identificatori(contesto_ui, "scena")
        for chiave in (
            comandi.ID_SCEGLI_OGGETTO,
            comandi.ID_ALTERNA_SCELTA,
            comandi.ID_ALTERNA_VISIBILITA,
            comandi.ID_BLOCCA_SCELTA,
        ):
            with self.subTest(comando=chiave):
                self.assertIn(chiave, identificatori_elenco)
        self.assertNotIn(comandi.ID_RINOMINA, identificatori_elenco)

    def test_il_lucchetto_dell_elenco_dice_cosa_farà(self):
        """Anche dall'elenco si può sbloccare un oggetto non scegliibile."""
        righe_blocca = [
            azione
            for azione in elementi(contesto(oggetto("Cubo")), "scena", Azione)
            if azione.idname == comandi.ID_BLOCCA_SCELTA
        ]
        self.assertEqual(len(righe_blocca), 1)
        self.assertEqual(dict(righe_blocca[0].parametri), {"oggetto": "Cubo", "blocca": True})

        righe_sblocca = [
            azione
            for azione in elementi(contesto(oggetto("Cubo", bloccato=True)), "scena", Azione)
            if azione.idname == comandi.ID_BLOCCA_SCELTA
        ]
        self.assertEqual(dict(righe_sblocca[0].parametri), {"oggetto": "Cubo", "blocca": False})

    def test_rinomina_compare_solo_sull_oggetto_attivo(self):
        contesto_ui = contesto(oggetto("Cubo", attivo=True), oggetto("Sfera"))
        rinomine = [
            azione
            for azione in elementi(contesto_ui, "scena", Azione)
            if azione.idname == comandi.ID_RINOMINA
        ]
        self.assertEqual(len(rinomine), 1)
        self.assertEqual(dict(rinomine[0].parametri)["oggetto"], "Cubo")

    def test_elenco_lungo_si_ferma_al_limite_e_lo_dice(self):
        molti = tuple(oggetto(f"Oggetto {numero}") for numero in range(30))
        contesto_ui = contesto(*molti)
        testo = testi(contesto_ui, "scena")
        self.assertIn(
            TESTI["ETICHETTA_MANCANO_OGGETTI"].format(
                mostrati=configuration.LIMITE_ELENCO_SEMPLICE, totali=30
            ),
            testo,
        )
        testi_nomi = [
            azione.testo
            for azione in elementi(contesto_ui, "scena", Azione)
            if azione.idname == comandi.ID_SCEGLI_OGGETTO
        ]
        self.assertEqual(len(testi_nomi), configuration.LIMITE_ELENCO_SEMPLICE)

    def test_la_ricerca_compare_solo_con_molti_oggetti(self):
        pochi = elementi(contesto(oggetto("Cubo")), "scena", Campo)
        self.assertNotIn(configuration.CAMPO_FILTRO, [campo.proprieta for campo in pochi])

        molti = elementi(
            contesto(*tuple(oggetto(f"O{numero}") for numero in range(12))), "scena", Campo
        )
        self.assertIn(configuration.CAMPO_FILTRO, [campo.proprieta for campo in molti])

    def test_ricerca_senza_risultati_lo_dice_e_propone_pulisci(self):
        contesto_ui = contesto(oggetto("Cubo"), filtro="zzz")
        testo = testi(contesto_ui, "scena")
        self.assertIn(TESTI["ETICHETTA_FILTRO_VUOTO"], testo)
        self.assertIn(comandi.ID_PULISCI_FILTRO, identificatori(contesto_ui, "scena"))

    def test_oggetti_nascosti_mostrano_il_comando_mostra_tutti(self):
        nascosto = contesto(oggetto("Cubo", nascosto=True, nascosto_direttamente=True))
        self.assertIn(comandi.ID_MOSTRA_TUTTI, identificatori(nascosto, "scena"))

        visibile = contesto(oggetto("Cubo"))
        self.assertNotIn(comandi.ID_MOSTRA_TUTTI, identificatori(visibile, "scena"))

    def test_filtro_per_nome(self):
        contesto_ui = contesto(oggetto("Albero"), oggetto("Sfera"), filtro="sfe")
        self.assertEqual([o.nome for o in contesto_ui.filtrati()], ["Sfera"])


class TestNessunaScelta(unittest.TestCase):
    def test_spiega_come_scegliere_e_propone_tutti(self):
        contesto_ui = contesto(oggetto("Cubo"))
        testo = testi(contesto_ui, "oggetto")
        self.assertIn(TESTI["ETICHETTA_NESSUNA_SELEZIONE"], testo)
        self.assertIn(TESTI["AIUTO_NESSUNA_SELEZIONE"], testo)
        self.assertIn(comandi.ID_SCEGLI_TUTTO, identificatori(contesto_ui, "oggetto"))

    def test_non_mostra_i_comandi_di_trasformazione(self):
        contesto_ui = contesto(oggetto("Cubo"))
        for chiave in ("GRUPPO_SPOSTA", "GRUPPO_RUOTA", "GRUPPO_INGRANDISCI"):
            with self.subTest(gruppo=chiave):
                self.assertNotIn(TESTI[chiave], testi(contesto_ui, "oggetto"))


class TestSceltaSingola(unittest.TestCase):
    def test_mostra_nome_tipo_e_trasformazioni_a_passi(self):
        contesto_ui = contesto(oggetto("Albero", scelto=True, attivo=True))
        testo = testi(contesto_ui, "oggetto")
        self.assertIn("Albero", testo)
        self.assertIn(TESTI["TIPO_FORMA"], testo)
        for chiave in (
            "GRUPPO_SPOSTA",
            "GRUPPO_RUOTA",
            "GRUPPO_INGRANDISCI",
            "GRUPPO_MOUSE",
            "GRUPPO_ALTRO",
        ):
            with self.subTest(gruppo=chiave):
                self.assertIn(TESTI[chiave], testo)

        identificatori_oggetto = identificatori(contesto_ui, "oggetto")
        self.assertEqual(
            len([i for i in identificatori_oggetto if i == comandi.ID_SPOSTA_PASSO]), 6
        )
        for chiave in (comandi.ID_RUOTA_PASSO, comandi.ID_SCALA_PASSO, comandi.ID_DUPLICA, comandi.ID_ELIMINA):
            with self.subTest(comando=chiave):
                self.assertIn(chiave, identificatori_oggetto)

    def test_il_passo_si_puo_cambiare(self):
        contesto_ui = contesto(oggetto("Albero", scelto=True, attivo=True), passo=2.0)
        passi = [
            campo
            for campo in elementi(contesto_ui, "oggetto", Campo)
            if campo.proprieta == configuration.CAMPO_PASSO
        ]
        self.assertEqual(len(passi), 1)
        self.assertEqual(passi[0].riferimento, configuration.RIFERIMENTO_SCENA)

    def test_la_luce_ha_i_suoi_comandi(self):
        contesto_ui = contesto(oggetto("Luce", "LIGHT", scelto=True, attivo=True))
        testo = testi(contesto_ui, "oggetto")
        self.assertIn(TESTI["GRUPPO_LUCE"], testo)
        self.assertIn(TESTI["AZIONE_PIU_LUMINOSA"], testo)
        self.assertIn(TESTI["AZIONE_MENO_LUMINOSA"], testo)
        self.assertNotIn(TESTI["GRUPPO_TELECAMERA"], testo)

    def test_la_telecamera_ha_i_suoi_comandi(self):
        semplice = contesto(oggetto("Telecamera", "CAMERA", scelto=True, attivo=True))
        testo = testi(semplice, "oggetto")
        self.assertIn(TESTI["GRUPPO_TELECAMERA"], testo)
        self.assertIn(TESTI["AZIONE_GUARDA_DA_CAMERA"], testo)
        self.assertNotIn(
            TESTI["AZIONE_TELECAMERA_PRINCIPALE"],
            testo,
            "In modalità Semplice basta il comando che mostra la vista della telecamera",
        )

        completa = contesto(
            oggetto("Telecamera", "CAMERA", scelto=True, attivo=True),
            modalita=configuration.MODALITA_COMPLETA,
        )
        self.assertIn(TESTI["AZIONE_TELECAMERA_PRINCIPALE"], testi(completa, "oggetto"))

    def test_un_oggetto_vuoto_non_ha_gruppi_speciali(self):
        contesto_ui = contesto(oggetto("Segnaposto", "EMPTY", scelto=True, attivo=True))
        testo = testi(contesto_ui, "oggetto")
        self.assertIn(TESTI["TIPO_SEGNAPOSTO"], testo)
        self.assertNotIn(TESTI["GRUPPO_LUCE"], testo)
        self.assertNotIn(TESTI["GRUPPO_TELECAMERA"], testo)

    def test_un_oggetto_nascosto_scelto_dall_elenco_si_puo_mostrare(self):
        """Dall'elenco si sceglie anche un oggetto nascosto: il pannello lo spiega."""
        contesto_ui = contesto(
            oggetto("Cubo", scelto=True, attivo=True, nascosto=True, nascosto_direttamente=True)
        )
        pannello = testi(contesto_ui, "oggetto")
        self.assertIn(TESTI["ETICHETTA_NASCOSTO"], pannello)
        self.assertIn(TESTI["AZIONE_MOSTRA"], pannello)

    def test_un_oggetto_nascosto_dalla_sua_raccolta_non_promette_mostra(self):
        """Se è la raccolta a nasconderlo, il comando Mostra non avrebbe effetto."""
        contesto_ui = contesto(
            oggetto("Cubo", scelto=True, attivo=True, nascosto=True, nascosto_direttamente=False)
        )
        pannello = testi(contesto_ui, "oggetto")
        self.assertIn(TESTI["ETICHETTA_NASCOSTO_CON_GRUPPO"], pannello)
        self.assertNotIn(TESTI["AZIONE_MOSTRA"], pannello)
        self.assertNotIn(TESTI["AZIONE_NASCONDI"], pannello)

    def test_un_oggetto_visibile_si_puo_nascondere(self):
        contesto_ui = contesto(oggetto("Cubo", scelto=True, attivo=True))
        self.assertIn(TESTI["AZIONE_NASCONDI"], testi(contesto_ui, "oggetto"))


class TestSceltaMultipla(unittest.TestCase):
    def crea(self) -> Contesto:
        return contesto(
            oggetto("Cubo", scelto=True, attivo=True),
            oggetto("Sfera", scelto=True),
            oggetto("Luce", "LIGHT", scelto=True),
            oggetto("Piano"),
        )

    def test_riassume_quanti_sono_e_quali_tipi(self):
        contesto_ui = self.crea()
        testo = testi(contesto_ui, "oggetto")
        self.assertIn(TESTI["ETICHETTA_MULTI_SELEZIONE"].format(numero=3), testo)
        self.assertIn(TESTI["AIUTO_MULTI_SELEZIONE"], testo)
        self.assertIn(
            TESTI["TIPO_FORMA_PLURALE"].format(numero=2)
            + ", "
            + TESTI["TIPO_LUCE"],
            testo,
        )

    def test_indica_l_oggetto_attivo(self):
        contesto_ui = self.crea()
        self.assertIn(
            TESTI["ETICHETTA_OGGETTO_ATTIVO"].format(nome="Cubo"), testi(contesto_ui, "oggetto")
        )

    def test_le_azioni_valgono_per_tutti_gli_scelti(self):
        contesto_ui = self.crea()
        identificatori_oggetto = identificatori(contesto_ui, "oggetto")
        for chiave in (comandi.ID_SPOSTA_PASSO, comandi.ID_DUPLICA, comandi.ID_ELIMINA):
            with self.subTest(comando=chiave):
                self.assertIn(chiave, identificatori_oggetto)
        testi_pulsanti = testi(contesto_ui, "oggetto")
        self.assertIn(TESTI["AZIONE_ELIMINA_SCELTI"].format(numero=3), testi_pulsanti)
        self.assertIn(TESTI["AZIONE_DESCEGLI_SCELTI"], testi_pulsanti)
        self.assertIn(TESTI["AZIONE_INQUADRA_SCELTI"], testi_pulsanti)

    def test_nessun_comando_per_tipo_in_scelta_multipla(self):
        testo = testi(self.crea(), "oggetto")
        self.assertNotIn(TESTI["GRUPPO_LUCE"], testo)


class TestModalitaCompleta(unittest.TestCase):
    def crea(self) -> Contesto:
        return contesto(
            oggetto("Cubo", scelto=True, attivo=True),
            modalita=configuration.MODALITA_COMPLETA,
        )

    def test_campi_tecnici_collegati_ai_dati_veri(self):
        campi = {campo.proprieta: campo for campo in elementi(self.crea(), "completo", Campo)}
        for proprieta in (
            "location",
            "rotation_mode",
            "rotation_euler",
            "scale",
            "display_type",
            "hide_select",
            "hide_render",
        ):
            with self.subTest(proprieta=proprieta):
                self.assertIn(proprieta, campi)
                self.assertEqual(campi[proprieta].riferimento, configuration.RIFERIMENTO_OGGETTO)

    def test_il_campo_di_rotazione_segue_il_modo(self):
        quaternioni = contesto(
            oggetto("Cubo", scelto=True, attivo=True, modo_rotazione="QUATERNION"),
            modalita=configuration.MODALITA_COMPLETA,
        )
        self.assertIn(
            "rotation_quaternion",
            [campo.proprieta for campo in elementi(quaternioni, "completo", Campo)],
        )

        asse_angolo = contesto(
            oggetto("Cubo", scelto=True, attivo=True, modo_rotazione="AXIS_ANGLE"),
            modalita=configuration.MODALITA_COMPLETA,
        )
        self.assertIn(
            "rotation_axis_angle",
            [campo.proprieta for campo in elementi(asse_angolo, "completo", Campo)],
        )

    def test_i_dati_dell_oggetto_sono_indicati_una_volta(self):
        testo = testi(self.crea(), "completo")
        self.assertIn(TESTI["GRUPPO_DATI"], testo)
        self.assertIn(TESTI["ETICHETTA_TIPO_TECNICO"].format(tipo="MESH"), testo)
        self.assertIn(TESTI["ETICHETTA_DATI_MESH"].format(vertici=8, facce=6), testo)

    def test_in_modalita_completa_si_puo_cambiare_il_nome_con_il_campo(self):
        campi = [
            campo
            for campo in elementi(self.crea(), "oggetto", Campo)
            if campo.proprieta == "name"
        ]
        self.assertEqual(len(campi), 1)

    def test_in_modalita_semplice_nessun_campo_tecnico_nel_pannello_oggetto(self):
        contesto_ui = contesto(oggetto("Cubo", scelto=True, attivo=True))
        self.assertEqual(
            elementi(contesto_ui, "oggetto", Campo)[0].proprieta, configuration.CAMPO_PASSO
        )

    def test_senza_scelta_il_pannello_tecnico_invita_a_scegliere(self):
        contesto_ui = contesto(oggetto("Cubo"), modalita=configuration.MODALITA_COMPLETA)
        testo = testi(contesto_ui, "completo")
        self.assertIn(TESTI["ETICHETTA_NESSUNA_SELEZIONE"], testo)
        self.assertEqual(elementi(contesto_ui, "completo", Campo), [])


class TestLunghezzaDeiTesti(unittest.TestCase):
    """I testi devono stare nella barra laterale, che è stretta."""

    def contesto_ricco(self) -> Contesto:
        return contesto(
            oggetto("Albero", scelto=True, attivo=True),
            oggetto("Luce", "LIGHT", scelto=True),
            oggetto("Telecamera", "CAMERA"),
            oggetto("Segnaposto", "EMPTY"),
            modalita=configuration.MODALITA_COMPLETA,
        )

    def test_etichette_brevi(self):
        for chiave in ("principale", "scena", "oggetto", "completo"):
            for elemento in elementi(self.contesto_ricco(), chiave, Etichetta):
                with self.subTest(chiave=chiave, testo=elemento.testo):
                    self.assertLessEqual(
                        len(elemento.testo), configuration.LUNGHEZZA_MASSIMA_ETICHETTA
                    )

    def test_pulsanti_brevi_secondo_la_riga(self):
        contesto_ui = self.contesto_ricco()
        nomi = {o.nome for o in contesto_ui.oggetti}
        for chiave in ("principale", "scena", "oggetto", "completo"):
            for gruppo in pannello(contesto_ui, chiave).gruppi:
                for riga in gruppo.righe:
                    azioni = [e for e in riga.elementi if isinstance(e, Azione)]
                    limite = (
                        configuration.LUNGHEZZA_MASSIMA_AZIONE
                        if len(riga.elementi) > 1
                        else configuration.LUNGHEZZA_MASSIMA_AZIONE_SINGOLA
                    )
                    for azione in azioni:
                        if azione.testo in nomi:
                            continue
                        with self.subTest(chiave=chiave, testo=azione.testo):
                            self.assertLessEqual(len(azione.testo), limite)

    def test_i_nomi_tecnici_restano_solo_nella_modalita_completa(self):
        semplice = self.contesto_ricco()
        semplice = modello.crea_contesto(
            modalita=configuration.MODALITA_SEMPLICE, oggetti=semplice.oggetti
        )
        testo_semplice = " ".join(testi(semplice, "oggetto"))
        for parola in ("MESH", "LIGHT", "CAMERA", "location", "scale"):
            with self.subTest(parola=parola):
                self.assertNotIn(parola, testo_semplice)

        completo = self.contesto_ricco()
        testo_completo = " ".join(testi(completo, "oggetto") + testi(completo, "completo"))
        self.assertIn("MESH", testo_completo)


class TestFormeENumeri(unittest.TestCase):
    """Le novità del piano: forme aggiuntive, grandezza, numeri e maniglie."""

    def test_le_forme_aggiuntive_compiono_nel_gruppo_costruisci(self):
        contesto_ui = contesto()
        comandi_visibili = identificatori(contesto_ui, "principale")
        for chiave in comandi.ID_FORME:
            with self.subTest(comando=chiave):
                self.assertIn(chiave, comandi_visibili)
        testo = testi(contesto_ui, "principale")
        self.assertIn(TESTI["AZIONE_AGGIUNGI_CONO"], testo)
        self.assertIn(TESTI["AZIONE_AGGIUNGI_TORO"], testo)
        self.assertIn(TESTI["AZIONE_AGGIUNGI_TESTO"], testo)

    def test_la_grandezza_delle_nuove_forme_si_puo_cambiare(self):
        campi = [
            campo
            for campo in elementi(contesto(), "principale", Campo)
            if campo.proprieta == configuration.CAMPO_GRANDEZZA_FORMA
        ]
        self.assertEqual(len(campi), 1)
        self.assertEqual(campi[0].riferimento, configuration.RIFERIMENTO_SCENA)

    def test_con_un_oggetto_scelto_compiono_i_campi_numerici(self):
        contesto_ui = contesto(oggetto("Albero", scelto=True, attivo=True))
        campi = [campo.proprieta for campo in elementi(contesto_ui, "oggetto", Campo)]
        for previsto in ("location", "rotation_euler", "dimensions", configuration.CAMPO_PASSO):
            with self.subTest(proprieta=previsto):
                self.assertIn(previsto, campi)
        # Ogni misura ha tre campi, uno per asse.
        self.assertEqual(campi.count("location"), 3)
        self.assertEqual(campi.count("dimensions"), 3)
        # Le etichette portano l'unità della scena.
        testo = " ".join(testi(contesto_ui, "oggetto"))
        self.assertIn(f"{TESTI['ETICHETTA_POSIZIONE']} (m)", testo)
        self.assertIn(f"{TESTI['ETICHETTA_ROTAZIONE']} (°)", testo)
        self.assertIn(f"{TESTI['ETICHETTA_DIMENSIONE']} (m)", testo)

    def test_la_rotazione_segue_il_modo_dell_oggetto(self):
        """Un quaternione non ha tre angoli: il piano lo dice invece di mentire."""
        per_quaternione = contesto(
            oggetto("Albero", scelto=True, attivo=True, modo_rotazione="QUATERNION")
        )
        campi = [campo.proprieta for campo in elementi(per_quaternione, "oggetto", Campo)]
        self.assertNotIn("rotation_euler", campi)
        self.assertIn("rotation_quaternion", campi)
        self.assertIn(TESTI["ETICHETTA_ROTAZIONE_QUATERNIONE"], testi(per_quaternione, "oggetto"))

    def test_le_maniglie_del_mouse_compiono_sulla_scelta(self):
        contesto_ui = contesto(oggetto("Albero", scelto=True, attivo=True))
        comandi_oggetto = identificatori(contesto_ui, "oggetto")
        for chiave in (
            comandi.ID_STRUMENTO_SPOSTA,
            comandi.ID_STRUMENTO_RUOTA,
            comandi.ID_STRUMENTO_SCALA,
        ):
            with self.subTest(comando=chiave):
                self.assertIn(chiave, comandi_oggetto)

    def test_le_posizioni_precise_compiono_sulla_scelta(self):
        contesto_ui = contesto(oggetto("Albero", scelto=True, attivo=True))
        comandi_oggetto = identificatori(contesto_ui, "oggetto")
        for chiave in (
            comandi.ID_CENTRA,
            comandi.ID_APPOGGIA_SUL_PIANO,
            comandi.ID_COPIA,
            comandi.ID_INCOLLA,
            comandi.ID_BLOCCA_SCELTA,
        ):
            with self.subTest(comando=chiave):
                self.assertIn(chiave, comandi_oggetto)

    def test_con_più_oggetti_scelti_nessun_campo_numerico(self):
        """Con più oggetti i numeri di uno solo sarebbero fuorvianti."""
        contesto_ui = contesto(
            oggetto("Cubo", scelto=True, attivo=True),
            oggetto("Sfera", scelto=True),
        )
        campi = [campo.proprieta for campo in elementi(contesto_ui, "oggetto", Campo)]
        self.assertNotIn("location", campi)
        self.assertNotIn("dimensions", campi)
        # I comandi che valgono per tutti restano.
        comandi_oggetto = identificatori(contesto_ui, "oggetto")
        for chiave in (comandi.ID_CENTRA, comandi.ID_APPOGGIA_SUL_PIANO, comandi.ID_COPIA):
            with self.subTest(comando=chiave):
                self.assertIn(chiave, comandi_oggetto)

    def test_la_scritta_ha_i_suoi_campi(self):
        contesto_ui = contesto(oggetto("Scritta", "FONT", scelto=True, attivo=True))
        testo = testi(contesto_ui, "oggetto")
        self.assertIn(TESTI["GRUPPO_TESTO"], testo)
        campi = [campo.proprieta for campo in elementi(contesto_ui, "oggetto", Campo)]
        self.assertIn("body", campi)
        self.assertIn("size", campi)

    def test_il_pulsante_di_blocco_dice_cosa_farà(self):
        libero = contesto(oggetto("Albero", scelto=True, attivo=True))
        self.assertIn(TESTI["AZIONE_BLOCCA_SCELTA"], testi(libero, "oggetto"))

        bloccato = contesto(oggetto("Albero", scelto=True, attivo=True, bloccato=True))
        self.assertIn(TESTI["AZIONE_SBLOCCA_SCELTA"], testi(bloccato, "oggetto"))
        self.assertNotIn(TESTI["AZIONE_BLOCCA_SCELTA"], testi(bloccato, "oggetto"))

    def test_le_unita_della_scena_compaiono_nelle_etichette(self):
        """Con i centimetri l'etichetta lo dice: nessuna unità inventata."""
        contesto_ui = contesto(
            oggetto("Albero", scelto=True, attivo=True), unita_lunghezza="cm"
        )
        testo = " ".join(testi(contesto_ui, "oggetto"))
        self.assertIn(f"{TESTI['ETICHETTA_POSIZIONE']} (cm)", testo)
        self.assertNotIn("(m)", testo)

    def test_con_radianti_cambia_anche_l_unita_degli_angoli(self):
        contesto_ui = contesto(
            oggetto("Albero", scelto=True, attivo=True), unita_angolo="rad"
        )
        testo = " ".join(testi(contesto_ui, "oggetto"))
        self.assertIn(f"{TESTI['ETICHETTA_ROTAZIONE']} (rad)", testo)


if __name__ == "__main__":
    unittest.main()
