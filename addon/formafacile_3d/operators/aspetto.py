"""Comandi del pannello "Dai un bell'aspetto alla scena".

Qui l'interfaccia diventa azione: materiali, illuminazione, telecamera, modi di
guardare la scena e creazione dell'immagine finale. Ogni comando:

* usa i valori scritti nel pannello, non numeri nascosti;
* lascia un messaggio breve in italiano;
* è annullabile con `Ctrl+Z` quando cambia i dati della scena;
* quando non può fare quello che promette, lo dice e si ferma.

La creazione dell'immagine è l'unico comando lento: in una finestra vera passa
dal disegno di Blender (con l'avanzamento e l'interruzione con Esc), mentre
senza finestra aspetta la fine del lavoro. In entrambi i casi i controlli
difficili (telecamera, cartella, memoria, spazio su disco) vengono fatti prima.
"""

from __future__ import annotations

import bpy

from .. import comandi, configuration
from ..blender import illuminazione, materiali, rendering, telecamera
from ..localization import TESTI
from ..scene import aspetto
from ..scene.stato import (
    ambiente_della_scena,
    cartella_della_scena,
    immagine_della_scena,
    stato_della_scena,
    valori_materiale_della_scena,
)
from .base import OperatoreFormaFacile

# Tipi di oggetto che possono portare un materiale: gli altri (luci,
# telecamere, segnaposti) non hanno superfici da colorare.
TIPI_CON_MATERIALE = frozenset({"MESH", "CURVE", "SURFACE", "FONT", "META", "VOLUME", "GREASEPENCIL"})


def _oggetti_con_materiale(oggetti) -> list:
    """Oggetti scelti su cui si può davvero applicare un materiale."""
    return [
        oggetto
        for oggetto in oggetti
        if getattr(oggetto, "type", "") in TIPI_CON_MATERIALE and getattr(oggetto, "data", None) is not None
    ]


def _usato_da_altri(scena, oggetto, materiale) -> bool:
    """Indica se quel materiale è usato anche da un altro oggetto della scena."""
    for altro in getattr(scena, "objects", ()) or ():
        if altro is oggetto:
            continue
        if materiale in materiali.materiali_di(altro):
            return True
    return False


def _errore_bersagli(operatore, context) -> set[str]:
    """Spiega perché il materiale non si può applicare a quello che è scelto.

    Senza nulla di scelto serve una scelta; con una luce o una telecamera scelta
    il motivo è un altro, e il messaggio lo dice.
    """
    if not operatore.scelti(context):
        return operatore.richiedi_selezione(context)
    return operatore.errore("ERRORE_MATERIALE_NON_APPLICABILE", "LOG_ERRORE_MATERIALE", context)


def _telecamera_bersaglio(context):
    """Telecamera su cui agire: quella scelta, altrimenti la principale."""
    scena = getattr(context, "scene", None)
    attivo = OperatoreFormaFacile.oggetto_attivo(context)
    if attivo is not None and getattr(attivo, "type", "") == "CAMERA":
        return attivo
    for oggetto in OperatoreFormaFacile.scelti(context):
        if getattr(oggetto, "type", "") == "CAMERA":
            return oggetto
    return getattr(scena, "camera", None)


# ------------------------------------------------------------------ materiali


class FORMAFACILE_OT_applica_materiale(OperatoreFormaFacile):
    """Crea il materiale scelto e lo dà agli oggetti scelti."""

    bl_idname = comandi.ID_APPLICA_MATERIALE
    bl_label = TESTI["AZIONE_APPLICA_MATERIALE"]
    bl_description = TESTI["AIUTO_APPLICA_MATERIALE"]
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        if not self.in_modalita_oggetto(context):
            return self.richiedi_modalita_oggetto()
        scena = context.scene
        valori = valori_materiale_della_scena(scena)
        bersagli = _oggetti_con_materiale(self.scelti(context))
        if not bersagli:
            return _errore_bersagli(self, context)

        with self.con_attivo_salvo(context):
            applicati = 0
            for oggetto in bersagli:
                if self._applica_a(context, oggetto, valori):
                    applicati += 1
        if not applicati:
            return self.errore("ERRORE_MATERIALE_ASSENTE", "LOG_ERRORE_MATERIALE", context)

        if applicati == 1:
            testo = TESTI["MESSAGGIO_MATERIALE_APPLICATO_UNO"].format(nome=valori.nome)
        else:
            testo = TESTI["MESSAGGIO_MATERIALE_APPLICATO_MOLTI"].format(
                numero=applicati, nome=valori.nome
            )
        self.annuncia(context, testo)
        self.report({"INFO"}, testo)
        return {"FINISHED"}

    def _applica_a(self, context, oggetto, valori) -> bool:
        """Dà il materiale a un oggetto, riusando quello che è già solo suo.

        Se l'oggetto ha già un materiale creato da FormaFacile e nessun altro lo
        usa, i valori vengono aggiornati su quello: cambiare colore e riapplicare
        non riempie la scena di materiali doppioni.
        """
        attuale = materiali.materiale_principale(oggetto)
        if (
            attuale is not None
            and materiali.ricetta(attuale)
            and not _usato_da_altri(context.scene, oggetto, attuale)
        ):
            riuscito = materiali.imposta_valori(
                attuale,
                valori.colore,
                valori.ruvidita,
                valori.metallico,
                valori.trasparenza,
                valori.indice_rifrazione,
            )
            return bool(riuscito) and self._conserva_ricetta(attuale, valori)

        nuovo = materiali.crea_con_valori(valori)
        if nuovo is None:
            return False
        if not materiali.assegna(oggetto, nuovo):
            try:
                bpy.data.materials.remove(nuovo)
            except (AttributeError, ReferenceError, RuntimeError, TypeError):
                pass
            return False
        return True

    @staticmethod
    def _conserva_ricetta(materiale, valori) -> bool:
        """Tiene scritto sul materiale da quale ricetta nasce."""
        try:
            materiale[configuration.CHIAVE_MATERIALE_RICETTA] = valori.chiave
        except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
            return False
        return True


class FORMAFACILE_OT_crea_variazione(OperatoreFormaFacile):
    """Copia il materiale degli oggetti scelti, così le modifiche restano locali."""

    bl_idname = comandi.ID_CREA_VARIAZIONE
    bl_label = TESTI["AZIONE_CREA_VARIAZIONE"]
    bl_description = TESTI["AIUTO_CREA_VARIAZIONE"]
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        bersagli = _oggetti_con_materiale(self.scelti(context))
        if not bersagli:
            return _errore_bersagli(self, context)

        with self.con_attivo_salvo(context):
            create = []
            for oggetto in bersagli:
                attuale = materiali.materiale_principale(oggetto)
                if attuale is None:
                    continue
                copia = materiali.copia(attuale, materiali.nome_per_variazione(attuale))
                if copia is None:
                    continue
                if not materiali.sostituisci(oggetto, attuale, copia):
                    try:
                        bpy.data.materials.remove(copia)
                    except (AttributeError, ReferenceError, RuntimeError, TypeError):
                        pass
                    continue
                create.append(copia)

        if not create:
            return self.errore("ERRORE_MATERIALE_ASSENTE", "LOG_ERRORE_MATERIALE", context)
        if len(create) == 1:
            testo = TESTI["MESSAGGIO_VARIAZIONE_CREATA_UNO"].format(nome=create[0].name)
        else:
            testo = TESTI["MESSAGGIO_VARIAZIONE_CREATA_MOLTI"].format(numero=len(create))
        self.annuncia(context, testo)
        self.report({"INFO"}, testo)
        return {"FINISHED"}


class FORMAFACILE_OT_scegli_colore(OperatoreFormaFacile):
    """Sceglie un colore della tavolozza e lo scrive nello stato del pannello."""

    bl_idname = comandi.ID_SCEGLI_COLORE
    bl_label = TESTI["ETICHETTA_COLORE_MATERIALE"]
    bl_description = TESTI["AIUTO_COLORE_MATERIALE"]
    bl_options = {"REGISTER", "UNDO"}

    colore: bpy.props.EnumProperty(
        name=TESTI["ETICHETTA_COLORE_MATERIALE"],
        description=TESTI["AIUTO_COLORE_MATERIALE"],
        items=aspetto.voci_tavolozza(),
    )

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        scelto = aspetto.colore(self.colore)
        stato = stato_della_scena(context.scene)
        if scelto is None or stato is None:
            return self.errore("ERRORE_MATERIALE_ASSENTE", "LOG_ERRORE_MATERIALE", context)
        stato.materiale_colore = scelto.rgb
        testo = TESTI["MESSAGGIO_COLORE_SCELTO"].format(nome=scelto.nome)
        self.annuncia(context, testo)
        return {"FINISHED"}


# -------------------------------------------------------------- illuminazione


class FORMAFACILE_OT_illuminazione_automatica(OperatoreFormaFacile):
    """Crea l'illuminazione consigliata, regolata sulla grandezza della scena."""

    bl_idname = comandi.ID_ILLUMINAZIONE_AUTOMATICA
    bl_label = TESTI["AZIONE_ILLUMINAZIONE_AUTOMATICA"]
    bl_description = TESTI["AIUTO_ILLUMINAZIONE_AUTOMATICA"]
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        return _applica_illuminazione(self, context, aspetto.ILLUMINAZIONE_AUTOMATICA)


class FORMAFACILE_OT_illuminazione_preset(OperatoreFormaFacile):
    """Crea le luci di una situazione tipica: prodotto, interno, esterno, studio."""

    bl_idname = comandi.ID_ILLUMINAZIONE_PRESET
    bl_label = TESTI["GRUPPO_ILLUMINAZIONE"]
    bl_description = TESTI["AIUTO_ILLUMINAZIONE_PRESET"]
    bl_options = {"REGISTER", "UNDO"}

    preset: bpy.props.StringProperty(default="", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        return _applica_illuminazione(self, context, self.preset)


def _applica_illuminazione(operatore, context, chiave: str) -> set[str]:
    """Crea le luci scelte e riporta lo sfondo nei valori del pannello."""
    esito = illuminazione.applica(context, chiave)
    if esito is None:
        return operatore.errore("ERRORE_LUCI_NON_CREATE", "LOG_ERRORE_ILLUMINAZIONE", context)
    preset, luci = esito
    stato = stato_della_scena(context.scene)
    if stato is not None:
        stato.illuminazione = preset.chiave
        stato.sfondo_colore = preset.sfondo
        stato.sfondo_intensita = preset.sfondo_intensita
        stato.luce_intensita = configuration.INTENSITA_LUCE_PREDEFINITA
    testo = TESTI["MESSAGGIO_ILLUMINAZIONE_APPLICATA"].format(
        nome=preset.nome, numero=len(luci)
    )
    operatore.annuncia(context, testo)
    operatore.report({"INFO"}, testo)
    return {"FINISHED"}


class FORMAFACILE_OT_applica_ambiente(OperatoreFormaFacile):
    """Aggiorna sfondo e potenza delle luci con i valori scritti nel pannello."""

    bl_idname = comandi.ID_APPLICA_AMBIENTE
    bl_label = TESTI["AZIONE_APPLICA_AMBIENTE"]
    bl_description = TESTI["AIUTO_APPLICA_AMBIENTE"]
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        colore, intensita_sfondo, intensita_luci = ambiente_della_scena(context.scene)
        if not illuminazione.imposta_sfondo(context, colore, intensita_sfondo):
            return self.errore("ERRORE_SFONDO", "LOG_ERRORE_ILLUMINAZIONE", context)
        illuminazione.cambia_intensita(context.scene, intensita_luci)
        self.annuncia(context, TESTI["MESSAGGIO_AMBIENTE_APPLICATO"])
        return {"FINISHED"}


# --------------------------------------------------- telecamera e modi di guardare


class FORMAFACILE_OT_aggiungi_telecamera(OperatoreFormaFacile):
    """Crea una telecamera che inquadra la scena e la usa per l'immagine finale."""

    bl_idname = comandi.ID_AGGIUNGI_TELECAMERA
    bl_label = TESTI["AZIONE_AGGIUNGI_TELECAMERA"]
    bl_description = TESTI["AIUTO_AGGIUNGI_TELECAMERA"]
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        oggetto = telecamera.aggiungi(context)
        if oggetto is None:
            return self.errore("ERRORE_TELECAMERA_AGGIUNTA", "LOG_ERRORE_TELECAMERA", context)
        testo = TESTI["MESSAGGIO_TELECAMERA_AGGIUNTA"].format(nome=oggetto.name)
        self.annuncia(context, testo)
        self.report({"INFO"}, testo)
        return {"FINISHED"}


class FORMAFACILE_OT_inquadra_telecamera(OperatoreFormaFacile):
    """Fa inquadrare alla telecamera gli oggetti scelti, o tutta la scena."""

    bl_idname = comandi.ID_INQUADRA_TELECAMERA
    bl_label = TESTI["AZIONE_INQUADRA_TELECAMERA"]
    bl_description = TESTI["AIUTO_INQUADRA_TELECAMERA"]
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        senza_telecamera = self.errore("ERRORE_TELECAMERA", "LOG_ERRORE_TELECAMERA", context)
        bersaglio = _telecamera_bersaglio(context)
        if bersaglio is None:
            return senza_telecamera
        riuscito, erano_scelti = telecamera.inquadra(context, bersaglio, self.scelti(context))
        if not riuscito:
            return senza_telecamera
        testo = (
            TESTI["MESSAGGIO_TELECAMERA_SCELTI"]
            if erano_scelti
            else TESTI["MESSAGGIO_TELECAMERA_SCENA"]
        )
        self.annuncia(context, testo)
        return {"FINISHED"}


class FORMAFACILE_OT_centra_vista(OperatoreFormaFacile):
    """Porta al centro della vista gli oggetti scelti, senza cambiare lo zoom."""

    bl_idname = comandi.ID_CENTRA_VISTA
    bl_label = TESTI["AZIONE_CENTRA_VISTA"]
    bl_description = TESTI["AIUTO_CENTRA_VISTA"]
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        oggetti, erano_scelti = telecamera.oggetti_da_inquadrare(context, self.scelti(context))
        if not telecamera.centra_vista(context, oggetti):
            return self.errore("ERRORE_VISTA_NON_DISPONIBILE", "LOG_ERRORE_VISTA", context)
        testo = (
            TESTI["MESSAGGIO_VISTA_CENTRATA"]
            if erano_scelti
            else TESTI["MESSAGGIO_VISTA_CENTRATA_SCENA"]
        )
        self.annuncia(context, testo)
        return {"FINISHED"}


class FORMAFACILE_OT_ripristina_telecamera(OperatoreFormaFacile):
    """Riporta la telecamera alla posizione che aveva quando è stata creata."""

    bl_idname = comandi.ID_RIPRISTINA_TELECAMERA
    bl_label = TESTI["AZIONE_RIPRISTINA_TELECAMERA"]
    bl_description = TESTI["AIUTO_RIPRISTINA_TELECAMERA"]
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        bersaglio = _telecamera_bersaglio(context)
        if bersaglio is None:
            return self.errore("ERRORE_TELECAMERA", "LOG_ERRORE_TELECAMERA", context)
        if not telecamera.ripristina(bersaglio):
            return self.errore("ERRORE_TELECAMERA_INIZIALE", "LOG_ERRORE_TELECAMERA", context)
        self.annuncia(context, TESTI["MESSAGGIO_TELECAMERA_RIPRISTINATA"])
        return {"FINISHED"}


class FORMAFACILE_OT_vista_lavoro(OperatoreFormaFacile):
    """Mostra la scena con colori semplici: la vista per lavorare."""

    bl_idname = comandi.ID_VISTA_LAVORO
    bl_label = TESTI["AZIONE_VISTA_LAVORO"]
    bl_description = TESTI["AIUTO_VISTA_LAVORO"]
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        return _cambia_ombreggiatura(
            self, context, configuration.OMBREGGIATURA_LAVORO, "MESSAGGIO_VISTA_LAVORO"
        )


class FORMAFACILE_OT_anteprima_immagine(OperatoreFormaFacile):
    """Mostra la scena come verrà nell'immagine finale: materiali, luci e ombre."""

    bl_idname = comandi.ID_ANTEPRIMA_RENDER
    bl_label = TESTI["AZIONE_ANTEPRIMA_IMMAGINE"]
    bl_description = TESTI["AIUTO_ANTEPRIMA_IMMAGINE"]
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        return _cambia_ombreggiatura(
            self, context, configuration.OMBREGGIATURA_ANTEPRIMA, "MESSAGGIO_VISTA_ANTEPRIMA"
        )


def _cambia_ombreggiatura(operatore, context, tipo: str, chiave_messaggio: str) -> set[str]:
    """Cambia il modo di guardare la scena e lo dice, senza toccare i dati."""
    if not telecamera.imposta_ombreggiatura(context, tipo):
        return operatore.errore("ERRORE_VISTA_NON_DISPONIBILE", "LOG_ERRORE_VISTA", context)
    operatore.annuncia(context, TESTI[chiave_messaggio])
    return {"FINISHED"}


# ------------------------------------------------------------ immagine finale


class FORMAFACILE_OT_crea_immagine_finale(OperatoreFormaFacile):
    """Crea l'immagine finale e la salva nella cartella scelta dall'utente."""

    bl_idname = comandi.ID_CREA_IMMAGINE_FINALE
    bl_label = TESTI["AZIONE_CREA_IMMAGINE_FINALE"]
    bl_description = TESTI["AIUTO_CREA_IMMAGINE_FINALE"]
    bl_options = {"REGISTER", "UNDO"}

    # I valori del pannello si possono correggere al momento della chiamata:
    # restano vuoti quando si usa quello che c'è scritto nel pannello.
    cartella: bpy.props.StringProperty(default="", subtype="DIR_PATH", options={"SKIP_SAVE"})
    qualita: bpy.props.StringProperty(default="", options={"SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def invoke(self, context, event):
        """Avvia il disegno nella finestra di Blender, quando c'è una finestra."""
        problema = self._problema(context)
        if problema:
            return self._errore(problema, context)
        percorso = self._percorso(context)
        try:
            self._prepara(context)
        except rendering.ErroreImmaginazione as errore:
            return self._errore(errore.chiave_testo, context)

        if getattr(context, "window", None) is None:
            # Senza finestra non c'è nessun avanzamento da mostrare né Esc da
            # premere: si aspetta la fine del lavoro.
            return self._disegna_aspettando(context, percorso)

        rendering.prepara_file(context, percorso)
        if not rendering.disegna_immagine_in_finestra():
            return self._disegna_aspettando(context, percorso)
        rendering.segui_esito(percorso)
        self.annuncia(context, TESTI["MESSAGGIO_IMMAGINE_AVVIATA"])
        self.report({"INFO"}, TESTI["MESSAGGIO_IMMAGINE_AVVIATA"])
        return {"FINISHED"}

    def execute(self, context):
        problema = self._problema(context)
        if problema:
            return self._errore(problema, context)
        percorso = self._percorso(context)
        try:
            self._prepara(context)
        except rendering.ErroreImmaginazione as errore:
            return self._errore(errore.chiave_testo, context)
        return self._disegna_aspettando(context, percorso)

    # ---------------------------------------------------------------- parti

    def _disegna_aspettando(self, context, percorso: str) -> set[str]:
        """Crea l'immagine e aspetta la fine, controllando il file scritto.

        Qui non c'è una finestra di disegno da guardare: il messaggio dice che
        il lavoro è in corso e Blender scrive i suoi passaggi nella console.
        """
        self.annuncia(context, TESTI["MESSAGGIO_IMMAGINE_IN_CORSO"])
        try:
            rendering.disegna_immagine(context, percorso)
        except rendering.ErroreImmaginazione as errore:
            return self._errore(errore.chiave_testo, context)
        if rendering.dimensioni_immagine(percorso) is None:
            return self._errore("ERRORE_IMMAGINE_NON_LEGGIBILE", context)
        testo = TESTI["MESSAGGIO_IMMAGINE_CREATA"].format(percorso=percorso)
        self.annuncia(context, testo)
        self.report({"INFO"}, testo)
        return {"FINISHED"}

    def _problema(self, context) -> str:
        """Chiave del primo controllo non superato, oppure stringa vuota."""
        cartella = self._cartella(context)
        return rendering.controlla(context, cartella)

    def _cartella(self, context) -> str:
        return self.cartella.strip() or cartella_della_scena(context.scene)

    def _percorso(self, context) -> str:
        qualita, _percentuale, _campioni, _motore, formato = immagine_della_scena(context.scene)
        nome_file = aspetto.nome_file_immagine(None, formato)
        return aspetto.percorso_immagine(self._cartella(context), nome_file)

    def _prepara(self, context) -> None:
        """Applica motore, qualità e formato scritti nel pannello."""
        qualita, percentuale, campioni, motore, formato = immagine_della_scena(context.scene)
        rendering.prepara_render(
            context,
            qualita=self.qualita or qualita,
            motore=motore,
            formato=formato,
            percentuale=percentuale,
            campioni=campioni,
        )

    def _errore(self, chiave_testo: str, context=None) -> set[str]:
        """Segnala il problema con una spiegazione comprensibile."""
        return self.errore(chiave_testo, "LOG_ERRORE_IMMAGINE", context)


CLASSI = (
    FORMAFACILE_OT_applica_materiale,
    FORMAFACILE_OT_crea_variazione,
    FORMAFACILE_OT_scegli_colore,
    FORMAFACILE_OT_illuminazione_automatica,
    FORMAFACILE_OT_illuminazione_preset,
    FORMAFACILE_OT_applica_ambiente,
    FORMAFACILE_OT_aggiungi_telecamera,
    FORMAFACILE_OT_inquadra_telecamera,
    FORMAFACILE_OT_centra_vista,
    FORMAFACILE_OT_ripristina_telecamera,
    FORMAFACILE_OT_vista_lavoro,
    FORMAFACILE_OT_anteprima_immagine,
    FORMAFACILE_OT_crea_immagine_finale,
)
