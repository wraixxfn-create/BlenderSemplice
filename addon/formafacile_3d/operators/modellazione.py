"""Strumenti guidati di modellazione: smusso, superficie, specchio, copie, spessore, taglio.

Ogni comando segue lo stesso schema, pensato per chi non conosce il gergo
della modellazione:

* **spiega prima**: la finestrella di conferma dice che cosa succederà e mostra
  solo i parametri che servono davvero (gli altri compaiono soltanto nella
  modalità completa);
* **non distrugge**: si usano modificatori, quindi la forma di partenza resta e
  tutto si annulla con `Ctrl+Z`;
* **controlla l'esito**: se Blender non fa quello che il comando ha promesso
  (nessuno spigolo da ammorbidire, un taglio che non toglie nulla, una forma
  già simmetrica), la modifica viene tolta e l'utente riceve una spiegazione in
  italiano, mai un falso successo.
"""

from __future__ import annotations

import math

import bpy
import mathutils

from .. import comandi, configuration
from ..blender import adapter, modificatori
from ..blender.modificatori import ErroreModellazione
from ..localization import TESTI
from ..scene import regole_modellazione as regole
from ..scene import testi as testi_lunghi
from ..scene.stato import modalita_della_scena
from .base import OperatoreFormaFacile


def _numero(valore: float, cifre: int = 2) -> str:
    """Numero scritto come in italiano, con la virgola dei decimali."""
    return f"{round(float(valore), cifre):g}".replace(".", ",")


def _voci_asse(aiuto: str = ""):
    """Voci degli assi, con la spiegazione di ogni asse presa dalla tabella."""
    return tuple(
        (
            asse,
            TESTI[comandi.TESTI_ASSE[asse]],
            TESTI[aiuto] if aiuto else TESTI[comandi.AIUTI_ASSE[asse]],
        )
        for asse in comandi.ASSI
    )


def _voci_ripetizione():
    """Voci della ripetizione: in fila oppure in cerchio."""
    return tuple(
        (modo, TESTI[comandi.TESTI_RIPETIZIONE[modo]], TESTI[comandi.AIUTI_RIPETIZIONE[modo]])
        for modo in comandi.MODI_RIPETIZIONE
    )


def _voci_centro():
    """Voci del centro del giro: il cursore 3D o il centro della scena."""
    return tuple(
        (chiave, TESTI[comandi.TESTI_CENTRO[chiave]], TESTI["AIUTO_CENTRO_GIRO"])
        for chiave in comandi.CENTRI_RIPETIZIONE
    )


def _voci_verso_spessore():
    """Voci del verso dello spessore: dentro o fuori dalla forma."""
    return tuple(
        (chiave, TESTI[comandi.TESTI_SPESSORE[chiave]], TESTI["AIUTO_VERSO_SPESSORE"])
        for chiave in comandi.VERSI_SPESSORE
    )


def _voci_operazione():
    """Voci delle operazioni fra forme: unione, taglio o incrocio."""
    return tuple(
        (
            modo,
            TESTI[comandi.TESTI_OPERAZIONE[modo]],
            TESTI[comandi.AIUTI_OPERAZIONE[modo]],
        )
        for modo in comandi.OPERAZIONI_BOOLEANE
    )


class _StrumentoGuidato(OperatoreFormaFacile):
    """Base degli strumenti con finestrella di conferma e spiegazione."""

    chiave_spiegazione = ""

    # ------------------------------------------------------------- conferma

    def puo_confermare(self, context) -> bool:
        """La finestrella di conferma si apre solo dove c'è una finestra vera."""
        return getattr(context, "area", None) is not None and getattr(context, "window", None) is not None

    def invoke(self, context, event):
        """Apre la conferma; senza finestre (o da uno script) esegue direttamente."""
        if not self.puo_confermare(context):
            return self.execute(context)
        return context.window_manager.invoke_props_dialog(self, width=380)

    def campi_essenziali(self) -> tuple[str, ...]:
        """Nomi dei parametri che si vedono anche nella modalità semplice."""
        return ()

    def campi_avanzati(self) -> tuple[str, ...]:
        """Nomi dei parametri che compaiono solo nella modalità completa."""
        return ()

    def in_modalita_completa(self, context) -> bool:
        return modalita_della_scena(getattr(context, "scene", None)) == configuration.MODALITA_COMPLETA

    def draw(self, context):
        """Spiegazione, parametri essenziali e, se serve, quelli avanzati."""
        colonna = self.layout.column()
        for testo in self.righe_spiegazione():
            colonna.label(text=testo)
        for nome in self.campi_essenziali():
            colonna.prop(self, nome)
        for chiave, testo in self.righe_extra(context):
            colonna.label(text=testo, icon=chiave)
        avanzati = self.campi_avanzati()
        if avanzati and self.in_modalita_completa(context):
            colonna.separator()
            colonna.label(text=TESTI["ETICHETTA_OPZIONI_AVANZATE"])
            for nome in avanzati:
                colonna.prop(self, nome)

    def righe_spiegazione(self) -> tuple[str, ...]:
        """Spiegazione del risultato, spezzata in righe che stanno nella finestra.

        La finestra di conferma è larga poche righe: senza questo spezzamento le
        frasi lunghe verrebbero tagliate e l'utente confermerebbe qualcosa che
        non ha potuto leggere.
        """
        if not self.chiave_spiegazione:
            return ()
        return testi_lunghi.righe_di_testo(
            TESTI[self.chiave_spiegazione], configuration.LUNGHEZZA_MASSIMA_FINESTRA
        )

    def righe_extra(self, context) -> tuple[tuple[str, str], ...]:
        """Righe di solo testo mostrate nella conferma (es. stime e avvisi)."""
        return ()

    # -------------------------------------------------------------- bersagli

    def bersaglio(self, context, nome: str = ""):
        """Unico oggetto su cui lavorare, indicato dal pannello o dalla scelta."""
        oggetto = self.risolvi_oggetto(context, nome) if nome else None
        if oggetto is None:
            oggetto = self.oggetto_attivo(context)
        if oggetto is None:
            scelti = self.scelti(context)
            oggetto = scelti[0] if len(scelti) == 1 else None
        if oggetto is None:
            raise ErroreModellazione(TESTI["ERRORE_NESSUNA_SCELTA"])
        return oggetto

    def richiedi_forma(self, oggetto) -> None:
        """Controlla che l'oggetto sia una forma lavorabile, spiegando cosa serve."""
        if getattr(oggetto, "type", "") == "MESH" and modificatori.e_forma(oggetto):
            return
        if modificatori.puo_diventare_forma(oggetto):
            raise ErroreModellazione(TESTI["ERRORE_SERVE_FORMA"])
        if getattr(oggetto, "type", "") == "MESH":
            raise ErroreModellazione(TESTI["ERRORE_FORMA_VUOTA"])
        raise ErroreModellazione(TESTI["ERRORE_SERVE_FORMA_ALTRO"])

    def esegui_sicuro(self, context, azione):
        """Esegue l'azione e trasforma gli errori conosciuti in un messaggio italiano."""
        if not self.in_modalita_oggetto(context):
            return self.richiedi_modalita_oggetto()
        try:
            messaggio = azione()
        except ErroreModellazione as errore:
            self.report({"WARNING"}, str(errore))
            self.annuncia(context, str(errore))
            return {"CANCELLED"}
        self.annuncia(context, messaggio)
        self.report({"INFO"}, messaggio)
        return {"FINISHED"}


# ------------------------------------------------------------------- spigoli


class FORMAFACILE_OT_ammorbidisci_spigoli(_StrumentoGuidato):
    """Arrotonda gli spigoli vivi con un modificatore, senza rifare la forma."""

    bl_idname = comandi.ID_AMMORBIDISCI_SPIGOLI
    bl_label = TESTI["AZIONE_AMMORBIDISCI_SPIGOLI"]
    bl_description = TESTI["AIUTO_AMMORBIDISCI_SPIGOLI"]
    chiave_spiegazione = "DIALOGO_AMMORBIDISCI_SPIGOLI"

    oggetto: bpy.props.StringProperty(default="", options={"HIDDEN"})
    forza: bpy.props.IntProperty(
        name=TESTI["ETICHETTA_FORZA"],
        description=TESTI["AIUTO_FORZA"],
        default=configuration.SMUSSO_FORZA_PREDEFINITA,
        min=configuration.SMUSSO_FORZA_MINIMA,
        max=configuration.SMUSSO_FORZA_MASSIMA,
    )
    raggio: bpy.props.FloatProperty(
        name=TESTI["ETICHETTA_RAGGIO"],
        description=TESTI["AIUTO_RAGGIO"],
        default=0.0,
        min=0.0,
        unit="LENGTH",
    )
    segmenti: bpy.props.IntProperty(
        name=TESTI["ETICHETTA_SEGMENTI"],
        description=TESTI["AIUTO_SEGMENTI"],
        default=0,
        min=0,
        max=configuration.SMUSSO_SEGMENTI_MASSIMI,
    )
    angolo: bpy.props.FloatProperty(
        name=TESTI["ETICHETTA_ANGOLO_SPIGOLO"],
        description=TESTI["AIUTO_ANGOLO_SPIGOLO"],
        default=configuration.SMUSSO_ANGOLO_PREDEFINITO_GRADI,
        min=0.0,
        max=180.0,
        subtype="ANGLE",
        unit="ROTATION",
    )

    def campi_essenziali(self) -> tuple[str, ...]:
        return ("forza",)

    def campi_avanzati(self) -> tuple[str, ...]:
        return ("raggio", "segmenti", "angolo")

    @classmethod
    def poll(cls, context):
        return context.view_layer is not None

    def execute(self, context):
        return self.esegui_sicuro(context, lambda: self._applica(context))

    def _applica(self, context) -> str:
        oggetto = self.bersaglio(context, self.oggetto)
        self.richiedi_forma(oggetto)

        angolo = float(self.angolo) if self.angolo > 0.0 else configuration.SMUSSO_ANGOLO_PREDEFINITO_GRADI
        spigoli = modificatori.spigoli_vivi(oggetto, angolo)
        if spigoli == 0:
            raise ErroreModellazione(TESTI["ERRORE_SENZA_SPIGOLI"])

        dimensione_minima, _massima = modificatori.dimensioni_oggetto(context, oggetto)
        larghezza = (
            float(self.raggio)
            if self.raggio > 0.0
            else regole.raggio_smusso(
                dimensione_minima,
                regole.forza_valida(self.forza, configuration.SMUSSO_FORZA_MINIMA, configuration.SMUSSO_FORZA_MASSIMA),
                rapporto_per_forza=configuration.SMUSSO_RAPPORTO_PER_FORZA,
                rapporto_massimo=configuration.SMUSSO_RAPPORTO_MASSIMO,
                raggio_minimo=configuration.SMUSSO_RAGGIO_MINIMO,
            )
        )
        segmenti = (
            int(self.segmenti)
            if self.segmenti > 0
            else regole.segmenti_smusso(self.forza, configuration.SMUSSO_SEGMENTI_MASSIMI)
        )

        prima = modificatori.facce_e_vertici(oggetto)
        modificatore = modificatori.aggiungi(
            oggetto, "BEVEL", TESTI["AZIONE_AMMORBIDISCI_SPIGOLI"]
        )
        modificatori.imposta(
            modificatore,
            width=larghezza,
            segments=segmenti,
            limit_method="ANGLE",
            angle_limit=math.radians(angolo),
            use_clamp_overlap=True,
            affect="EDGES",
        )

        dopo = modificatori.facce_e_vertici(oggetto)
        forma = modificatori.forma_valutata(context, oggetto)
        if forma.vertici <= dopo[1] or forma.facce <= dopo[0]:
            modificatori.rimuovi(oggetto, modificatore)
            raise ErroreModellazione(TESTI["ERRORE_SPIGOLI_NON_RIUSCITI"])
        modificatori.aggiorna(context)
        unita = _unita_lunghezza(context)
        return TESTI["MESSAGGIO_SPIGOLI_RAGGIO"].format(
            nome=oggetto.name, raggio=_numero(larghezza, 3), unita=unita
        )

    def righe_extra(self, context) -> tuple[tuple[str, str], ...]:
        try:
            oggetto = self.bersaglio(context, self.oggetto)
        except ErroreModellazione:
            return ()
        if getattr(oggetto, "type", "") != "MESH" or not modificatori.e_forma(oggetto):
            return ()
        angolo = float(self.angolo) if self.angolo > 0.0 else configuration.SMUSSO_ANGOLO_PREDEFINITO_GRADI
        spigoli = modificatori.spigoli_vivi(oggetto, angolo)
        if spigoli == 0:
            return (("ERROR", TESTI["ERRORE_SENZA_SPIGOLI"]),)
        return (("INFO", TESTI["ETICHETTA_SPIGOLI_TROVATI"].format(numero=spigoli)),)


def _unita_lunghezza(context) -> str:
    """Unità di lunghezza della scena, con ripiego sui metri."""
    return modificatori.unita_lunghezza(getattr(context, "scene", None))


# ----------------------------------------------------------------- superficie


class _Superficie(_StrumentoGuidato):
    """Base dei due comandi che cambiano solo l'aspetto della superficie.

    Sono gli unici strumenti guidati senza finestrella di conferma: cambiano
    soltanto l'illuminazione della superficie, il pannello lo scrive accanto ai
    pulsanti e il risultato si annulla con `Ctrl+Z`.
    """

    liscia = True

    oggetto: bpy.props.StringProperty(default="", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return context.view_layer is not None

    def invoke(self, context, event):
        """Nessuna conferma: l'effetto è immediato e si vede nella Vista 3D."""
        return self.execute(context)

    def execute(self, context):
        return self.esegui_sicuro(context, lambda: self._applica(context))

    def _applica(self, context) -> str:
        oggetto = self.bersaglio(context, self.oggetto)
        self.richiedi_forma(oggetto)
        if modificatori.e_liscia(oggetto) == self.liscia:
            return TESTI["MESSAGGIO_SUPERFICIE_INVARIATA"]
        if not modificatori.superficie_liscia(oggetto, self.liscia):
            raise ErroreModellazione(TESTI["ERRORE_SUPERFICIE"])
        modificatori.aggiorna(context)
        chiave = "MESSAGGIO_SUPERFICIE_LISCIA" if self.liscia else "MESSAGGIO_SUPERFICIE_A_FACCE"
        return TESTI[chiave]


class FORMAFACILE_OT_superficie_liscia(_Superficie):
    """Mostra la superficie come continua: nessuna faccia viene aggiunta."""

    bl_idname = comandi.ID_SUPERFICIE_LISCIA
    bl_label = TESTI["AZIONE_SUPERFICIE_LISCIA"]
    bl_description = TESTI["AIUTO_SUPERFICIE_LISCIA"]
    liscia = True


class FORMAFACILE_OT_superficie_a_facce(_Superficie):
    """Rimette in evidenza le facce: è l'aspetto di partenza."""

    bl_idname = comandi.ID_SUPERFICIE_A_FACCE
    bl_label = TESTI["AZIONE_SUPERFICIE_A_FACCE"]
    bl_description = TESTI["AIUTO_SUPERFICIE_A_FACCE"]
    liscia = False


class FORMAFACILE_OT_forma_piu_liscia(_StrumentoGuidato):
    """Aggiunge facce alla forma, con la suddivisione di Blender."""

    bl_idname = comandi.ID_FORMA_PIU_LISCIA
    bl_label = TESTI["AZIONE_FORMA_PIU_LISCIA"]
    bl_description = TESTI["AIUTO_FORMA_PIU_LISCIA"]
    chiave_spiegazione = "DIALOGO_FORMA_PIU_LISCIA"

    oggetto: bpy.props.StringProperty(default="", options={"HIDDEN"})
    livelli: bpy.props.IntProperty(
        name=TESTI["ETICHETTA_LIVELLI"],
        description=TESTI["AIUTO_LIVELLI"],
        default=configuration.LISCIO_LIVELLI_PREDEFINITI,
        min=1,
        max=configuration.LISCIO_LIVELLI_MASSIMI,
    )

    def campi_essenziali(self) -> tuple[str, ...]:
        return ("livelli",)

    @classmethod
    def poll(cls, context):
        return context.view_layer is not None

    def execute(self, context):
        return self.esegui_sicuro(context, lambda: self._applica(context))

    def _applica(self, context) -> str:
        oggetto = self.bersaglio(context, self.oggetto)
        self.richiedi_forma(oggetto)
        # Si conta quello che si vede adesso, modificatori compresi: chiedere
        # "più liscia" due volte deve alzare il livello della stessa
        # suddivisione, non impilarne una seconda sopra la prima.
        prima = modificatori.forma_valutata(context, oggetto)
        livelli = regole.livelli_consentiti(
            prima.facce, self.livelli, configuration.LISCIO_FACCE_MASSIME
        )
        modificatore = modificatori.trova(oggetto, "SUBSURF")
        nuova = modificatore is None
        if modificatore is None:
            modificatore = modificatori.aggiungi(
                oggetto, "SUBSURF", TESTI["AZIONE_FORMA_PIU_LISCIA"]
            )
        elif livelli <= int(getattr(modificatore, "levels", 0)):
            return TESTI["MESSAGGIO_FORMA_LISCIA_GIA"]
        modificatori.imposta(modificatore, levels=livelli, render_levels=livelli)
        forma = modificatori.forma_valutata(context, oggetto)
        if forma.facce <= prima.facce:
            if nuova:
                modificatori.rimuovi(oggetto, modificatore)
            raise ErroreModellazione(TESTI["ERRORE_FORMA_LISCIA"])
        modificatori.aggiorna(context)
        testo = TESTI["MESSAGGIO_FORMA_LISCIA"].format(nome=oggetto.name, facce=forma.facce)
        if livelli < int(self.livelli):
            testo = f"{testo} {TESTI['AVVISO_LIVELLI_RIDOTTI']}"
        return testo

    def righe_extra(self, context) -> tuple[tuple[str, str], ...]:
        try:
            oggetto = self.bersaglio(context, self.oggetto)
        except ErroreModellazione:
            return ()
        facce, _vertici = modificatori.facce_e_vertici(oggetto)
        if facce == 0:
            return ()
        dopo = regole.facce_dopo_suddivisione(facce, self.livelli)
        return (
            (
                "INFO",
                TESTI["DIALOGO_FORMA_PIU_LISCIA"].format(prima=facce, dopo=dopo),
            ),
        )


# ------------------------------------------------------------------ specchio


class FORMAFACILE_OT_specchia(_StrumentoGuidato):
    """Crea il lato uguale e opposto rispetto al centro dell'oggetto."""

    bl_idname = comandi.ID_SPECCHIA
    bl_label = TESTI["AZIONE_SPECCHIA"]
    bl_description = TESTI["AIUTO_SPECCHIA"]
    chiave_spiegazione = "DIALOGO_SPECCHIA"

    oggetto: bpy.props.StringProperty(default="", options={"HIDDEN"})
    asse: bpy.props.EnumProperty(
        name=TESTI["ETICHETTA_ASSE"],
        description=TESTI["AIUTO_ASSE_SPECCHIO"],
        items=_voci_asse("AIUTO_ASSE_SPECCHIO"),
        default=configuration.SPECCHIO_ASSE_PREDEFINITO,
    )
    unisci_centro: bpy.props.BoolProperty(
        name=TESTI["ETICHETTA_UNISCI_CENTRO"],
        description=TESTI["AIUTO_UNISCI_CENTRO"],
        default=False,
    )
    distanza_unione: bpy.props.FloatProperty(
        name=TESTI["ETICHETTA_DISTANZA_UNIONE"],
        description=TESTI["AIUTO_DISTANZA_UNIONE"],
        default=0.001,
        min=0.0,
        unit="LENGTH",
    )

    def campi_essenziali(self) -> tuple[str, ...]:
        return ("asse",)

    def campi_avanzati(self) -> tuple[str, ...]:
        return ("unisci_centro", "distanza_unione")

    @classmethod
    def poll(cls, context):
        return context.view_layer is not None

    def execute(self, context):
        return self.esegui_sicuro(context, lambda: self._applica(context))

    def _applica(self, context) -> str:
        oggetto = self.bersaglio(context, self.oggetto)
        self.richiedi_forma(oggetto)
        asse = str(self.asse).lower()
        # Il piano dello specchio è il cursore 3D: è l'unico punto della scena
        # che l'utente vede e può spostare senza conoscere il gergo di Blender.
        posizione = adapter.cursore_3d(context)
        if modificatori.simmetrica(
            oggetto,
            asse,
            float(posizione[regole.INDICE_ASSE[asse]]),
            configuration.SPECCHIO_TOLLERANZA,
        ):
            raise ErroreModellazione(TESTI["ERRORE_SPECCHIO_SIMMETRICA"])

        segnaposto = modificatori.segnaposto(context, posizione, TESTI["NOME_SPECCHIO"])
        if segnaposto is None:
            raise ErroreModellazione(TESTI["ERRORE_SPECCHIO_SEGNAPOSTO"])

        prima = modificatori.forma_valutata(context, oggetto)
        modificatore = modificatori.aggiungi(oggetto, "MIRROR", TESTI["AZIONE_SPECCHIA"])
        modificatori.imposta(
            modificatore,
            use_axis=tuple(
                asse == nome for nome in comandi.ASSI
            ),
            use_clip=bool(self.unisci_centro),
            use_mirror_merge=True,
            merge_threshold=float(self.distanza_unione),
            mirror_object=segnaposto,
        )
        dopo = modificatori.forma_valutata(context, oggetto)
        if dopo.vertici <= prima.vertici:
            modificatori.rimuovi(oggetto, modificatore)
            raise ErroreModellazione(TESTI["ERRORE_SPECCHIO"])
        modificatori.aggiorna(context)
        return TESTI["MESSAGGIO_SPECCHIATA"].format(
            asse=TESTI[comandi.TESTI_ASSE[asse]], nome=oggetto.name
        )


# -------------------------------------------------------------- ripetizione


class FORMAFACILE_OT_ripeti(_StrumentoGuidato):
    """Crea altre copie della forma: in fila oppure in cerchio."""

    bl_idname = comandi.ID_RIPETI_COPIE
    bl_label = TESTI["AZIONE_RIPETI"]
    bl_description = TESTI["AIUTO_RIPETI"]

    oggetto: bpy.props.StringProperty(default="", options={"HIDDEN"})
    modo: bpy.props.EnumProperty(
        name=TESTI["AZIONE_RIPETI"],
        description=TESTI["AIUTO_RIPETI"],
        items=_voci_ripetizione(),
        default=configuration.RIPETI_MODO_PREDEFINITO,
    )
    quante: bpy.props.IntProperty(
        name=TESTI["ETICHETTA_QUANTE_COPIE"],
        description=TESTI["AIUTO_QUANTE_COPIE"],
        default=configuration.RIPETI_COPIE_PREDEFINITE,
        min=configuration.RIPETI_COPIE_MINIME,
        max=configuration.RIPETI_COPIE_MASSIME,
    )
    distanza: bpy.props.FloatProperty(
        name=TESTI["ETICHETTA_SPAZIATURA"],
        description=TESTI["AIUTO_SPAZIATURA"],
        default=configuration.RIPETI_DISTANZA_PREDEFINITA,
        min=configuration.RIPETI_SPAZIATURA_MINIMA,
        max=configuration.RIPETI_SPAZIATURA_MASSIMA,
        unit="LENGTH",
    )
    asse: bpy.props.EnumProperty(
        name=TESTI["ETICHETTA_ASSE"],
        description=TESTI["AIUTO_ASSE_ALLINEA"],
        items=_voci_asse(),
        default=configuration.RIPETI_ASSE_PREDEFINITO,
    )
    centro: bpy.props.EnumProperty(
        name=TESTI["ETICHETTA_CENTRO_GIRO"],
        description=TESTI["AIUTO_CENTRO_GIRO"],
        items=_voci_centro(),
        default=configuration.RIPETI_CENTRO_PREDEFINITO,
    )
    volta_copie: bpy.props.BoolProperty(
        name=TESTI["ETICHETTA_VOLTA_COPIE"],
        description=TESTI["AIUTO_VOLTA_COPIE"],
        default=True,
    )

    def campi_essenziali(self) -> tuple[str, ...]:
        return ("modo", "quante", "distanza")

    def campi_avanzati(self) -> tuple[str, ...]:
        return ("asse", "centro", "volta_copie")

    @classmethod
    def poll(cls, context):
        return context.view_layer is not None

    @property
    def chiave_spiegazione(self) -> str:  # type: ignore[override]
        return (
            "DIALOGO_RIPETI_CERCHIO"
            if self.modo == comandi.MODO_RIPETI_CERCHIO
            else "DIALOGO_RIPETI_FILA"
        )

    def execute(self, context):
        return self.esegui_sicuro(context, lambda: self._applica(context))

    def _applica(self, context) -> str:
        oggetto = self.bersaglio(context, self.oggetto)
        self.richiedi_forma(oggetto)
        quante = max(int(self.quante), configuration.RIPETI_COPIE_MINIME)
        if self.modo == comandi.MODO_RIPETI_CERCHIO:
            return self._in_cerchio(context, oggetto, quante)
        return self._in_fila(context, oggetto, quante)

    def _in_fila(self, context, oggetto, quante: int) -> str:
        asse = str(self.asse).lower()
        distanza = abs(float(self.distanza))
        spostamento = [0.0, 0.0, 0.0]
        spostamento[regole.INDICE_ASSE[asse]] = distanza

        prima = modificatori.facce_e_vertici(oggetto)
        modificatore = modificatori.aggiungi(oggetto, "ARRAY", TESTI["AZIONE_RIPETI"])
        modificatori.imposta(
            modificatore,
            count=quante,
            use_relative_offset=False,
            use_constant_offset=True,
            constant_offset_displace=tuple(spostamento),
            use_object_offset=False,
        )
        forma = modificatori.forma_valutata(context, oggetto)
        if forma.vertici <= prima[1]:
            modificatori.rimuovi(oggetto, modificatore)
            raise ErroreModellazione(TESTI["ERRORE_RIPETI"])
        modificatori.aggiorna(context)
        unita = _unita_lunghezza(context)
        return TESTI["MESSAGGIO_RIPETUTE_FILA"].format(
            numero=quante, distanza=_numero(distanza), unita=unita
        )

    def _in_cerchio(self, context, oggetto, quante: int) -> str:
        distanza = abs(float(self.distanza))
        if distanza <= 1e-6:
            raise ErroreModellazione(TESTI["ERRORE_RIPETI_CENTRO"])
        posizione_oggetto = tuple(float(valore) for valore in oggetto.location)
        # Il giro sta nel piano orizzontale dell'oggetto: il centro serve solo
        # per la posizione in pianta, quindi la quota è quella dell'oggetto.
        centro_base = self._centro(context)
        centro = (centro_base[0], centro_base[1], posizione_oggetto[2])
        distanza_finale, angolo = regole.direzione_da_punto(centro, posizione_oggetto)
        if distanza_finale <= 1e-6:
            # L'oggetto è fermo sul centro del giro: senza una direzione non
            # ci sarebbe nessun cerchio. Viene messo a destra del centro, alla
            # distanza indicata, e le copie si distribuiscono da lì.
            angolo = 0.0
            distanza_finale = distanza
            oggetto.location = regole.punto_su_cerchio(centro, distanza_finale, angolo)

        copie = self._crea_copie(context, oggetto, centro, quante, distanza_finale, angolo)
        if not copie:
            raise ErroreModellazione(TESTI["ERRORE_RIPETI"])
        self._scegli(context, [oggetto, *copie], copie[0])
        modificatori.aggiorna(context)
        unita = _unita_lunghezza(context)
        return TESTI["MESSAGGIO_RIPETUTE_CERCHIO"].format(
            numero=quante, distanza=_numero(distanza_finale), unita=unita
        )

    def _centro(self, context) -> tuple[float, float, float]:
        if self.centro == comandi.CENTRO_SCENA:
            return (0.0, 0.0, 0.0)
        return adapter.cursore_3d(context)

    def _crea_copie(self, context, oggetto, centro, quante, distanza, angolo) -> list:
        """Crea le copie attorno al centro, con la stessa forma dell'originale."""
        scena = getattr(context, "scene", None)
        if scena is None:
            return []
        copie = []
        for numero, (posizione, rotazione) in enumerate(
            regole.posizioni_cerchio(centro, quante, distanza, angolo), start=1
        ):
            copia = oggetto.copy()
            if getattr(oggetto, "data", None) is not None:
                copia.data = oggetto.data.copy()
            raccolte = list(getattr(oggetto, "users_collection", ()) or ())
            for raccolta in raccolte or [scena.collection]:
                try:
                    raccolta.objects.link(copia)
                except (AttributeError, ReferenceError, RuntimeError):
                    continue
            copia.name = f"{oggetto.name} {numero}"
            copia.location = (posizione[0], posizione[1], posizione[2])
            if self.volta_copie:
                _ruota_attorno_asse_verticale(oggetto, copia, rotazione)
            copie.append(copia)
        return copie

    def _scegli(self, context, oggetti, attivo) -> None:
        vettore = getattr(context, "view_layer", None)
        if vettore is None:
            return
        try:
            for altro in vettore.objects:
                if altro.select_get():
                    altro.select_set(False)
            for oggetto in oggetti:
                oggetto.select_set(True)
            vettore.objects.active = attivo
        except (AttributeError, ReferenceError, RuntimeError):
            return


def _ruota_attorno_asse_verticale(originale, copia, gradi: float) -> None:
    """Volta la copia attorno all'asse verticale della scena, mantenendo la scala.

    La rotazione viene applicata alla posa completa dell'originale (rotazione e
    scala, in qualsiasi modo di rotazione sia impostato), così la copia guarda
    fuori dal cerchio anche se l'originale era già ruotato.
    """
    try:
        posa = originale.matrix_world.to_3x3().to_4x4()
        copia.matrix_world = (
            mathutils.Matrix.Translation(copia.location)
            @ mathutils.Matrix.Rotation(math.radians(float(gradi)), 4, "Z")
            @ posa
        )
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        return


# ------------------------------------------------------------------ spessore


class FORMAFACILE_OT_spessore_parete(_StrumentoGuidato):
    """Dà spessore a una superficie sottile, senza cambiare la forma di partenza."""

    bl_idname = comandi.ID_SPESSORE_PARETE
    bl_label = TESTI["AZIONE_SPESSORE_PARETE"]
    bl_description = TESTI["AIUTO_SPESSORE_PARETE"]
    chiave_spiegazione = "DIALOGO_SPESSORE"

    oggetto: bpy.props.StringProperty(default="", options={"HIDDEN"})
    spessore: bpy.props.FloatProperty(
        name=TESTI["ETICHETTA_SPESSORE"],
        description=TESTI["AIUTO_SPESSORE"],
        default=0.0,
        min=0.0,
        unit="LENGTH",
    )
    verso: bpy.props.EnumProperty(
        name=TESTI["ETICHETTA_VERSO_SPESSORE"],
        description=TESTI["AIUTO_VERSO_SPESSORE"],
        items=_voci_verso_spessore(),
        default=configuration.SPESSORE_VERSO_PREDEFINITO,
    )

    def campi_essenziali(self) -> tuple[str, ...]:
        return ("spessore",)

    def campi_avanzati(self) -> tuple[str, ...]:
        return ("verso",)

    @classmethod
    def poll(cls, context):
        return context.view_layer is not None

    def execute(self, context):
        return self.esegui_sicuro(context, lambda: self._applica(context))

    def _applica(self, context) -> str:
        oggetto = self.bersaglio(context, self.oggetto)
        self.richiedi_forma(oggetto)
        dimensione_minima, _massima = modificatori.dimensioni_oggetto(context, oggetto)
        richiesto = float(self.spessore) if self.spessore > 0.0 else (
            dimensione_minima * configuration.SPESSORE_RAPPORTO_PREDEFINITO
        )
        spessore = regole.spessore_consentito(
            dimensione_minima,
            richiesto,
            rapporto_massimo=configuration.SPESSORE_RAPPORTO_MASSIMO,
            spessore_minimo=configuration.SPESSORE_MINIMO,
        )
        chiusa = modificatori.bordi_aperti(oggetto) == 0

        prima = modificatori.facce_e_vertici(oggetto)
        modificatore = modificatori.aggiungi(
            oggetto, "SOLIDIFY", TESTI["AZIONE_SPESSORE_PARETE"]
        )
        modificatori.imposta(
            modificatore,
            thickness=spessore,
            offset=-1.0 if self.verso == comandi.VERSO_DENTRO else 1.0,
            use_even_offset=True,
            use_rim=not chiusa,
            use_quality_normals=True,
        )
        forma = modificatori.forma_valutata(context, oggetto)
        if forma.vertici <= prima[1]:
            modificatori.rimuovi(oggetto, modificatore)
            raise ErroreModellazione(TESTI["ERRORE_SPESSORE"])
        modificatori.aggiorna(context)
        unita = _unita_lunghezza(context)
        ridotto = abs(float(self.spessore)) > spessore + 1e-9 and self.spessore > 0.0
        chiave = "MESSAGGIO_SPESSORE_RIDOTTO" if ridotto or chiusa else "MESSAGGIO_SPESSORE"
        testo = TESTI[chiave].format(
            nome=oggetto.name, spessore=_numero(spessore, 3), unita=unita
        )
        if chiusa:
            testo = f"{testo} {TESTI['AVVISO_SPESSORE_FORMA_CHIUSA']}"
        return testo


# -------------------------------------------------------------------- taglio


class FORMAFACILE_OT_unisci_forme(_StrumentoGuidato):
    """Unisce, taglia o incrocia due forme, dicendo sempre quale è quale."""

    bl_idname = comandi.ID_UNISCI_FORME
    bl_label = TESTI["AZIONE_UNISCI"]
    bl_description = TESTI["AIUTO_UNISCI"]
    chiave_spiegazione = "DIALOGO_UNISCI"

    operazione: bpy.props.EnumProperty(
        name=TESTI["ETICHETTA_OPERAZIONE"],
        description=TESTI["AIUTO_OPERAZIONE"],
        items=_voci_operazione(),
        default=comandi.OPERAZIONE_UNIONE,
    )

    def campi_essenziali(self) -> tuple[str, ...]:
        return ("operazione",)

    @classmethod
    def poll(cls, context):
        return OperatoreFormaFacile.in_modalita_oggetto(context) and bool(
            OperatoreFormaFacile.scelti(context)
        )

    def coppia(self, context):
        """Forma principale e forma che taglia, dalla scelta di Blender.

        La forma principale è quella attiva: è la stessa idea di Blender
        ("l'oggetto attivo riceve la modifica"), e il pannello lo scrive.
        """
        scelti = self.scelti(context)
        attivo = self.oggetto_attivo(context)
        principale = None
        for oggetto in scelti:
            if attivo is not None and oggetto.name == attivo.name:
                principale = oggetto
                break
        if principale is None and scelti:
            principale = scelti[0]
        attrezzo = next((oggetto for oggetto in scelti if oggetto is not principale), None)
        return principale, attrezzo

    def draw(self, context):
        """Nome delle due forme, spiegazione e scelta dell'operazione."""
        principale, attrezzo = self.coppia(context)
        colonna = self.layout.column()
        if principale is None or attrezzo is None or len(self.scelti(context)) != 2:
            colonna.label(text=TESTI["ERRORE_UNISCI_POCHI"], icon="ERROR")
            return
        spiegazione = TESTI[self.chiave_spiegazione].format(
            principale=principale.name, attrezzo=attrezzo.name
        )
        for riga in testi_lunghi.righe_di_testo(
            spiegazione, configuration.LUNGHEZZA_MASSIMA_FINESTRA
        ):
            colonna.label(text=riga)
        colonna.label(
            text=TESTI["ETICHETTA_OGGETTO_PRINCIPALE"].format(nome=principale.name),
            icon="MESH_DATA",
        )
        colonna.label(
            text=TESTI["ETICHETTA_OGGETTO_ATTREZZO"].format(nome=attrezzo.name),
            icon="MESH_DATA",
        )
        colonna.prop(self, "operazione")
        if self.in_modalita_completa(context):
            colonna.separator()
            colonna.label(text=TESTI["ETICHETTA_OPZIONI_AVANZATE"])
            for riga in testi_lunghi.righe_di_testo(
                TESTI["NOTA_UNISCI_MODIFICATORE"], configuration.LUNGHEZZA_MASSIMA_FINESTRA
            ):
                colonna.label(text=riga)

    def execute(self, context):
        return self.esegui_sicuro(context, lambda: self._applica(context))

    def _applica(self, context) -> str:
        scelti = self.scelti(context)
        principale, attrezzo = self.coppia(context)
        if len(scelti) > 2:
            raise ErroreModellazione(TESTI["ERRORE_UNISCI_TROPPI"])
        if principale is None or attrezzo is None:
            raise ErroreModellazione(TESTI["ERRORE_UNISCI_POCHI"])
        if principale.name == attrezzo.name:
            raise ErroreModellazione(TESTI["ERRORE_UNISCI_STESSA_FORMA"])
        for oggetto in (principale, attrezzo):
            if getattr(oggetto, "type", "") != "MESH" or not modificatori.e_forma(oggetto):
                raise ErroreModellazione(
                    TESTI["ERRORE_UNISCI_SERVE_FORMA"].format(nome=oggetto.name)
                )
        if modificatori.bordi_aperti(attrezzo) > 0:
            raise ErroreModellazione(TESTI["ERRORE_UNISCI_ATTREZZO_APERTO"])

        prima = modificatori.forma_valutata(context, principale)
        modificatore = modificatori.aggiungi(principale, "BOOLEAN", TESTI["AZIONE_UNISCI"])
        modificatori.imposta(
            modificatore,
            operation=comandi.OPERAZIONI_BLENDER[str(self.operazione)],
            object=attrezzo,
            solver=configuration.BOOLEANA_SOLVER,
            operand_type="OBJECT",
        )
        forma = modificatori.forma_valutata(context, principale)

        if forma.facce == 0:
            modificatori.rimuovi(principale, modificatore)
            raise ErroreModellazione(TESTI["ERRORE_UNISCI_VUOTO"])
        if forma.facce > configuration.BOOLEANA_FACCE_MASSIME:
            modificatori.rimuovi(principale, modificatore)
            raise ErroreModellazione(TESTI["ERRORE_UNISCI_TROPPE_FACCE"])
        if self.operazione != comandi.OPERAZIONE_UNIONE and forma.facce == prima.facce:
            modificatori.rimuovi(principale, modificatore)
            raise ErroreModellazione(TESTI["ERRORE_UNISCI_NESSUN_CAMBIO"])
        modificatori.nascondi_attrezzo(attrezzo, True)
        modificatori.aggiorna(context)

        chiave = {
            comandi.OPERAZIONE_UNIONE: "MESSAGGIO_UNIONE",
            comandi.OPERAZIONE_DIFFERENZA: "MESSAGGIO_DIFFERENZA",
            comandi.OPERAZIONE_INTERSEZIONE: "MESSAGGIO_INTERSEZIONE",
        }[str(self.operazione)]
        return TESTI[chiave].format(principale=principale.name, attrezzo=attrezzo.name)


# --------------------------------------------------------------- conversione


class FORMAFACILE_OT_converti_in_forma(_StrumentoGuidato):
    """Trasforma una scritta o una curva in una forma (mesh)."""

    bl_idname = comandi.ID_CONVERTI_IN_FORMA
    bl_label = TESTI["AZIONE_CONVERTI_IN_FORMA"]
    bl_description = TESTI["AIUTO_CONVERTI_IN_FORMA"]
    chiave_spiegazione = "DIALOGO_CONVERTI_IN_FORMA"

    oggetto: bpy.props.StringProperty(default="", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return OperatoreFormaFacile.in_modalita_oggetto(context) and bool(
            OperatoreFormaFacile.scelti(context)
        )

    def execute(self, context):
        return self.esegui_sicuro(context, lambda: self._applica(context))

    def _applica(self, context) -> str:
        oggetto = self.bersaglio(context, self.oggetto)
        if not modificatori.puo_diventare_forma(oggetto):
            raise ErroreModellazione(TESTI["ERRORE_CONVERTI_NIENTE"])
        if not modificatori.converti_in_forma(context, oggetto):
            raise ErroreModellazione(TESTI["ERRORE_CONVERTI"])
        if not modificatori.e_forma(oggetto):
            raise ErroreModellazione(TESTI["ERRORE_CONVERTI_VUOTA"])
        modificatori.aggiorna(context)
        return TESTI["MESSAGGIO_CONVERTITA"].format(nome=oggetto.name)


CLASSI = (
    FORMAFACILE_OT_ammorbidisci_spigoli,
    FORMAFACILE_OT_superficie_liscia,
    FORMAFACILE_OT_superficie_a_facce,
    FORMAFACILE_OT_forma_piu_liscia,
    FORMAFACILE_OT_specchia,
    FORMAFACILE_OT_ripeti,
    FORMAFACILE_OT_spessore_parete,
    FORMAFACILE_OT_unisci_forme,
    FORMAFACILE_OT_converti_in_forma,
)
