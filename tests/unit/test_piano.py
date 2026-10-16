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
from formafacile_3d.scene import testi as testi_lunghi  # noqa: E402
from formafacile_3d.ui import icone, modello, piano  # noqa: E402
from formafacile_3d.ui.modello import (  # noqa: E402
    Azione,
    Campo,
    Contesto,
    Etichetta,
    Oggetto,
    Riga,
)


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


def raccolta(nome: str, *, quanti: int = 3, scelti: int = 0, nascosto: bool = False):
    return modello.Raccolta(
        chiave=nome, nome=nome, quanti=quanti, scelti=scelti, nascosto=nascosto
    )


def modifica(nome: str, tipo: str = "BEVEL", problema: str = ""):
    """Modifica non applicata, con le stesse parole che usa il pannello."""
    return modello.Modificatore(
        chiave=nome,
        nome=nome,
        parola=icone.parola_modificatore(tipo),
        icona=icone.icona_modificatore(tipo),
        problema=problema,
    )


def contesto(*oggetti: Oggetto, **valori: object) -> Contesto:
    valori.setdefault("oggetti", oggetti)
    return modello.crea_contesto(**valori)  # type: ignore[arg-type]


# Strumenti guidati sempre presenti: i pulsanti dei gruppi e delle modifiche
# compaiono solo quando ci sono gruppi o modifiche da mostrare.
STRUMENTI_SENZA_ELENCHI = tuple(
    idname
    for idname in comandi.ID_STRUMENTI_GUIDATI
    if idname
    not in (comandi.ID_SCEGLI_GRUPPO, comandi.ID_ALTERNA_GRUPPO, comandi.ID_TOGLI_MODIFICHE)
)

# Chiavi dei pannelli nell'ordine in cui compaiono, secondo la modalità.
PANNELLI_SEMPLICE = ("principale", "scena", "libreria", "oggetto", "modella")
PANNELLI = (*PANNELLI_SEMPLICE, "completo")


def riga_di(contesto_ui: Contesto, chiave: str, idname: str) -> Riga:
    """Prima riga di un pannello che contiene il comando indicato."""
    for gruppo in pannello(contesto_ui, chiave).gruppi:
        for riga in gruppo.righe:
            if any(
                isinstance(elemento, Azione) and elemento.idname == idname
                for elemento in riga.elementi
            ):
                return riga
    raise AssertionError(f"Riga assente: {idname}")


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
    def test_modalita_semplice_mostra_i_pannelli_dei_principianti(self):
        chiavi = [p.chiave for p in piano.costruisci_piano(contesto())]
        self.assertEqual(chiavi, list(PANNELLI_SEMPLICE))

    def test_modalita_completa_aggiunge_il_pannello_tecnico(self):
        chiavi = [
            p.chiave
            for p in piano.costruisci_piano(contesto(modalita=configuration.MODALITA_COMPLETA))
        ]
        self.assertEqual(chiavi, list(PANNELLI))

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
        for chiave in ("principale", "scena", "libreria", "oggetto", "completo"):
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
        for chiave in PANNELLI:
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

    def test_libreria_mostra_descrizione_parametri_e_inserimento(self):
        contesto_ui = contesto(asset_selezionato="scaffale")
        testo = testi(contesto_ui, "libreria")
        self.assertIn(TESTI["ASSET_NOME_SCAFFALE"], " ".join(testo))
        self.assertIn(TESTI["ASSET_DESCRIZIONE_SCAFFALE"].split()[0], " ".join(testo))
        self.assertIn(TESTI["ASSET_CAMPO_NUMERO_RIPIANI"], testo)
        self.assertIn(TESTI["ASSET_AZIONE_AGGIUNGI"], testo)
        campi = elementi(contesto_ui, "libreria", Campo)
        self.assertEqual(
            [campo.proprieta for campo in campi],
            [
                "asset_selezionato",
                "asset_larghezza",
                "asset_profondita",
                "asset_altezza",
                "asset_numero_ripiani",
                "asset_spessore",
                "asset_colore",
            ],
        )
        self.assertIn(comandi.ID_AGGIUNGI_ASSET, identificatori(contesto_ui, "libreria"))

    def test_libreria_disabilita_solo_l_inserimento_in_modalita_modifica(self):
        contesto_ui = contesto(in_modalita_oggetto=False)
        pannello_ui = pannello(contesto_ui, "libreria")
        self.assertTrue(any(riga.disabilitata for gruppo in pannello_ui.gruppi for riga in gruppo.righe))
        self.assertIn(TESTI["ASSET_SELEZIONA"], testi(contesto_ui, "libreria"))

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
        for chiave in PANNELLI:
            for elemento in elementi(self.contesto_ricco(), chiave, Etichetta):
                with self.subTest(chiave=chiave, testo=elemento.testo):
                    self.assertLessEqual(
                        len(elemento.testo), configuration.LUNGHEZZA_MASSIMA_ETICHETTA
                    )

    def test_pulsanti_brevi_secondo_la_riga(self):
        contesto_ui = modello.crea_contesto(
            oggetti=self.contesto_ricco().oggetti,
            raccolte=(raccolta("Casetta"),),
            modificatori=(modifica("Arrotondamento"),),
            guida="casetta",
            passo_guida=0,
            modalita=configuration.MODALITA_COMPLETA,
        )
        # I nomi scritti dall'utente (oggetti e gruppi) non sono testi
        # dell'interfaccia: possono essere lunghi quanto vuole l'utente.
        nomi = {o.nome for o in contesto_ui.oggetti} | {r.nome for r in contesto_ui.raccolte}
        for chiave in PANNELLI:
            for gruppo in pannello(contesto_ui, chiave).gruppi:
                for riga in gruppo.righe:
                    azioni = [e for e in riga.elementi if isinstance(e, Azione)]
                    limite = (
                        configuration.LUNGHEZZA_MASSIMA_AZIONE
                        if len(riga.elementi) > 1
                        else configuration.LUNGHEZZA_MASSIMA_AZIONE_SINGOLA
                    )
                    for azione in azioni:
                        # I nomi scritti dall'utente non sono testi
                        # dell'interfaccia, e i pulsanti con la sola icona non
                        # scrivono nulla: il testo resta come spiegazione.
                        if azione.testo in nomi or azione.solo_icona:
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




class TestPannelloDaiForma(unittest.TestCase):
    """Il pannello "Dai forma": strumenti guidati, gruppi, modifiche e guida."""

    def completo(self, *oggetti: Oggetto, **valori: object) -> Contesto:
        valori.setdefault("modalita", configuration.MODALITA_COMPLETA)
        return contesto(*oggetti, **valori)

    def test_senza_scelta_spiega_cosa_fare(self):
        contesto_ui = contesto()
        testo = testi(contesto_ui, "modella")
        self.assertIn(TESTI["ETICHETTA_MODELLA_NIENTE"], testo)
        self.assertNotIn(TESTI["ETICHETTA_MODELLA_SCELTA"], testo)
        # Gli strumenti restano visibili ma spenti: si vede che esistono.
        visibili = identificatori(contesto_ui, "modella")
        for idname in STRUMENTI_SENZA_ELENCHI:
            with self.subTest(comando=idname):
                self.assertIn(idname, visibili)
                self.assertTrue(riga_di(contesto_ui, "modella", idname).disabilitata)

    def test_con_una_forma_scelta_gli_strumenti_si_accendono(self):
        contesto_ui = contesto(oggetto("Cubo", scelto=True, attivo=True))
        testo = testi(contesto_ui, "modella")
        self.assertIn(TESTI["ETICHETTA_MODELLA_SCELTA"], testo)
        self.assertIn("Cubo", testo)
        for idname in (comandi.ID_AMMORBIDISCI_SPIGOLI, comandi.ID_SPECCHIA):
            with self.subTest(comando=idname):
                self.assertFalse(riga_di(contesto_ui, "modella", idname).disabilitata)

    def test_con_piu_forme_scelte_si_unisce_e_si_allinea(self):
        due = contesto(
            oggetto("Cubo", scelto=True, attivo=True), oggetto("Sfera", scelto=True)
        )
        self.assertIn(
            TESTI["ETICHETTA_MODELLA_SCELTI"].format(numero=2), testi(due, "modella")
        )
        self.assertFalse(riga_di(due, "modella", comandi.ID_UNISCI_FORME).disabilitata)
        self.assertFalse(riga_di(due, "modella", comandi.ID_ALLINEA).disabilitata)

        una = contesto(oggetto("Cubo", scelto=True, attivo=True))
        self.assertTrue(riga_di(una, "modella", comandi.ID_UNISCI_FORME).disabilitata)
        self.assertTrue(riga_di(una, "modella", comandi.ID_ALLINEA).disabilitata)

    def test_la_trasformazione_in_forma_compare_solo_per_testi_e_curve(self):
        testo_scritta = contesto(
            oggetto("Scritta", "FONT", scelto=True, attivo=True)
        )
        self.assertFalse(
            riga_di(testo_scritta, "modella", comandi.ID_CONVERTI_IN_FORMA).disabilitata
        )
        contesto_ui = contesto(oggetto("Cubo", scelto=True, attivo=True))
        self.assertTrue(
            riga_di(contesto_ui, "modella", comandi.ID_CONVERTI_IN_FORMA).disabilitata
        )

    def test_ogni_strumento_guidato_ha_il_suo_pulsante(self):
        contesto_ui = contesto(
            oggetto("Cubo", scelto=True, attivo=True), modalita=configuration.MODALITA_COMPLETA
        )
        visibili = identificatori(contesto_ui, "modella")
        for idname in STRUMENTI_SENZA_ELENCHI:
            with self.subTest(comando=idname):
                self.assertIn(idname, visibili)
        for idname in comandi.ICONE_STRUMENTI_GUIDATI:
            self.assertIn(idname, comandi.ID_STRUMENTI_GUIDATI)

    def test_i_gruppi_si_sceglono_e_si_nascondono_dalla_loro_riga(self):
        contesto_ui = contesto(
            oggetto("Cubo", scelto=True, attivo=True),
            raccolte=(raccolta("Casetta", quanti=3), raccolta("Alberi", quanti=2, nascosto=True)),
        )
        testo = testi(contesto_ui, "modella")
        self.assertIn(TESTI["ETICHETTA_GRUPPO_RIGA"].format(nome="Casetta", numero=3), testo)

        righe = [
            riga
            for gruppo in pannello(contesto_ui, "modella").gruppi
            for riga in gruppo.righe
            if any(
                isinstance(elemento, Azione) and elemento.idname == comandi.ID_SCEGLI_GRUPPO
                for elemento in riga.elementi
            )
        ]
        scelte = [
            elemento
            for riga in righe
            for elemento in riga.elementi
            if isinstance(elemento, Azione) and elemento.idname == comandi.ID_SCEGLI_GRUPPO
        ]
        self.assertEqual(
            [dict(azione.parametri)["gruppo"] for azione in scelte], ["Casetta", "Alberi"]
        )
        nascosti = [
            elemento
            for riga in righe
            for elemento in riga.elementi
            if isinstance(elemento, Azione) and elemento.idname == comandi.ID_ALTERNA_GRUPPO
        ]
        self.assertEqual(
            [elemento.icona for elemento in nascosti], ["HIDE_OFF", "HIDE_ON"]
        )

    def test_senza_gruppi_lo_dice(self):
        contesto_ui = contesto(oggetto("Cubo", scelto=True, attivo=True))
        self.assertIn(TESTI["ETICHETTA_GRUPPI_VUOTA"], testi(contesto_ui, "modella"))

    def test_le_modifiche_non_applicate_si_possono_togliere_una_per_una(self):
        contesto_ui = contesto(
            oggetto("Cubo", scelto=True, attivo=True),
            modificatori=(
                modifica("Smusso"),
                modifica("Serie 1", tipo="ARRAY", problema=TESTI["AVVISO_SERIE_SENZA_CENTRO"]),
            ),
        )
        testo = testi(contesto_ui, "modella")
        self.assertIn(TESTI["ETICHETTA_MODIFICHE"].format(numero=2), testo)
        self.assertIn(TESTI["PAROLA_MOD_BEVEL"], testo)
        self.assertIn(TESTI["PAROLA_MOD_ARRAY"], testo)
        self.assertIn(TESTI["AVVISO_SERIE_SENZA_CENTRO"], testo)

        togli = [
            elemento
            for gruppo in pannello(contesto_ui, "modella").gruppi
            for riga in gruppo.righe
            for elemento in riga.elementi
            if isinstance(elemento, Azione) and elemento.idname == comandi.ID_TOGLI_MODIFICHE
        ]
        self.assertEqual(len(togli), 3)
        self.assertEqual(
            dict(togli[0].parametri).get("modificatore"), "Smusso"
        )
        self.assertEqual(dict(togli[-1].parametri), {})

    def test_senza_modifiche_lo_dice(self):
        contesto_ui = contesto(oggetto("Cubo", scelto=True, attivo=True))
        self.assertIn(TESTI["NOTA_MODIFICHE_NIENTE"], testi(contesto_ui, "modella"))

    def test_le_impostazioni_dell_allineamento_sono_campi_della_scena(self):
        contesto_ui = contesto(oggetto("Cubo", scelto=True, attivo=True))
        campi = [campo for campo in elementi(contesto_ui, "modella", Campo)]
        self.assertEqual(
            [campo.proprieta for campo in campi],
            [configuration.CAMPO_ASSE_ALLINEA, configuration.CAMPO_BORDO_ALLINEA],
        )
        for campo in campi:
            self.assertEqual(campo.riferimento, configuration.RIFERIMENTO_SCENA)
        self.assertTrue(all(campo.espanso for campo in campi))

        completo = contesto(
            oggetto("Cubo", scelto=True, attivo=True),
            modalita=configuration.MODALITA_COMPLETA,
        )
        riferimento = [
            campo
            for campo in elementi(completo, "modella", Campo)
            if campo.proprieta == configuration.CAMPO_RIFERIMENTO_ALLINEA
        ]
        self.assertEqual(len(riferimento), 1)
        self.assertFalse(riferimento[0].espanso)

    def test_la_guida_passo_passo_mostra_il_passo(self):
        contesto_ui = contesto(guida="casetta", passo_guida=0)
        testo = testi(contesto_ui, "modella")
        self.assertIn(TESTI["ETICHETTA_GUIDA_PASSO"].format(numero=1, totale=13), testo)
        self.assertIn(TESTI["GUIDA_CASETTA_CORPO_TITOLO"], testo)
        visibili = identificatori(contesto_ui, "modella")
        self.assertIn(comandi.ID_GUIDA_ESEGUI, visibili)
        self.assertEqual(visibili.count(comandi.ID_GUIDA_NAVIGA), 3)

    def test_la_guida_chiusa_invita_a_iniziare(self):
        contesto_ui = contesto(oggetto("Cubo"))
        testo = testi(contesto_ui, "modella")
        self.assertIn(TESTI["NOTA_GUIDA_CASETTA"], testo)
        self.assertIn(comandi.ID_GUIDA_APRI, identificatori(contesto_ui, "modella"))
        self.assertNotIn(comandi.ID_GUIDA_ESEGUI, identificatori(contesto_ui, "modella"))

    def test_la_guida_finita_lo_dice_e_non_propone_altri_passi(self):
        contesto_ui = contesto(guida="casetta", passo_guida=13)
        testo = testi(contesto_ui, "modella")
        self.assertIn(TESTI["ETICHETTA_GUIDA_FINITA"], testo)
        visibili = identificatori(contesto_ui, "modella")
        self.assertNotIn(comandi.ID_GUIDA_ESEGUI, visibili)
        self.assertIn(comandi.ID_GUIDA_NAVIGA, visibili)

    def test_una_guida_che_non_esiste_non_rompe_il_pannello(self):
        contesto_ui = contesto(guida="inesistente", passo_guida=4)
        testo = testi(contesto_ui, "modella")
        self.assertIn(TESTI["ERRORE_GUIDA_ASSENTE"], testo)
        self.assertIn(comandi.ID_GUIDA_APRI, identificatori(contesto_ui, "modella"))

    def test_in_modalita_semplice_nessun_nome_tecnico(self):
        contesto_ui = contesto(
            oggetto("Cubo", scelto=True, attivo=True),
            modificatori=(modifica("Smusso"),),
            raccolte=(raccolta("Casetta"),),
        )
        testo = " ".join(testi(contesto_ui, "modella"))
        for parola in ("MESH", "location", "scale", "BEVEL", "SUBSURF", "SOLIDIFY"):
            with self.subTest(parola=parola):
                self.assertNotIn(parola, testo)


class TestTestiLunghi(unittest.TestCase):
    """Le spiegazioni lunghe si spezzano invece di sparire."""

    def test_righe_di_testo_rispetta_la_larghezza(self):
        testo = " ".join(["parola"] * 40)
        righe = testi_lunghi.righe_di_testo(testo, 30)
        self.assertGreater(len(righe), 1)
        for riga in righe:
            self.assertLessEqual(len(riga), 30)
        self.assertEqual(" ".join(righe), testo)

    def test_righe_di_testo_non_spezza_le_parole(self):
        righe = testi_lunghi.righe_di_testo("parolalunghissima altra", 5)
        self.assertEqual(righe, ("parolalunghissima", "altra"))

    def test_righe_di_testo_ignora_le_righe_vuote(self):
        self.assertEqual(testi_lunghi.righe_di_testo("uno\n\n\ndue", 10), ("uno", "due"))

    def test_accorcia_segnala_il_taglio(self):
        accorciato = testi_lunghi.accorcia("Nome molto lungo di un oggetto", 10)
        self.assertLessEqual(len(accorciato), 10)
        self.assertTrue(accorciato.endswith(testi_lunghi.SEGNO_ACCORCIATO))
        self.assertEqual(testi_lunghi.accorcia("Corto", 10), "Corto")

    def test_le_spiegazioni_del_pannello_sono_spezzate(self):
        contesto_ui = contesto(guida="casetta", passo_guida=0)
        for etichetta in elementi(contesto_ui, "modella", Etichetta):
            with self.subTest(testo=etichetta.testo):
                self.assertLessEqual(
                    len(etichetta.testo), configuration.LUNGHEZZA_MASSIMA_ETICHETTA
                )


if __name__ == "__main__":
    unittest.main()
