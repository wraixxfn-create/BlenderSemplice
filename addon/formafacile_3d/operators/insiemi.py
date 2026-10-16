"""Comandi su più oggetti: allinea, spazia, raggruppa, togli le modifiche.

Sono i comandi che servono quando gli oggetti sono più di uno. L'asse e il
bordo dell'allineamento si leggono dallo stato della scena: sono impostazioni
che si vedono nel pannello e valgono per ogni clic, come la modalità semplice o
completa, così allineare più volte è un clic alla volta.
"""

from __future__ import annotations

import bpy

from .. import comandi, configuration
from ..blender import allineamento, modificatori, raccolte
from ..blender.allineamento import ErroreAllineamento
from ..blender.raccolte import ErroreGruppo
from ..localization import TESTI
from ..scene.stato import allineamento_della_scena
from .base import OperatoreFormaFacile


def _numero(valore: float, cifre: int = 2) -> str:
    return f"{round(float(valore), cifre):g}".replace(".", ",")


def _unita(context) -> str:
    return modificatori.unita_lunghezza(getattr(context, "scene", None))


def _nome_asse(asse: str) -> str:
    return TESTI[comandi.TESTI_ASSE.get(str(asse).lower(), "ASSE_X")]


class _OperatoreSuScelta(OperatoreFormaFacile):
    """Base dei comandi che lavorano sugli oggetti scelti."""

    @classmethod
    def poll(cls, context):
        return OperatoreFormaFacile.in_modalita_oggetto(context) and bool(
            OperatoreFormaFacile.scelti(context)
        )

    def esegui_sicuro(self, context, azione, tipo_errore=(ErroreAllineamento, ErroreGruppo)):
        """Esegue l'azione e trasforma gli errori conosciuti in un messaggio italiano."""
        if not self.in_modalita_oggetto(context):
            return self.richiedi_modalita_oggetto()
        try:
            messaggio = azione()
        except tipo_errore as errore:
            self.report({"WARNING"}, str(errore))
            self.annuncia(context, str(errore))
            return {"CANCELLED"}
        self.annuncia(context, messaggio)
        self.report({"INFO"}, messaggio)
        return {"FINISHED"}

    def scelta(self, context) -> list:
        return self.scelti(context)

    def impostazioni_allineamento(self, context) -> tuple[str, str, bool]:
        """Asse, bordo e riferimento scelti nel pannello, con ripieghi sicuri."""
        return allineamento_della_scena(getattr(context, "scene", None))


class FORMAFACILE_OT_allinea(_OperatoreSuScelta):
    """Allinea gli oggetti scelti su un asse, al bordo o al centro scelto."""

    bl_idname = comandi.ID_ALLINEA
    bl_label = TESTI["AZIONE_ALLINEA"]
    bl_description = TESTI["AIUTO_ALLINEA"]

    def execute(self, context):
        asse, bordo, per_punto = self.impostazioni_allineamento(context)

        def azione() -> str:
            esito = allineamento.allinea(
                context, self.scelta(context), asse, bordo, per_punto=per_punto
            )
            if esito.applicati == 0 and esito.invariati:
                return TESTI["MESSAGGIO_ALLINEATI_INVARIATI"]
            testo = TESTI["MESSAGGIO_ALLINEATI"].format(
                numero=esito.applicati + esito.invariati, asse=_nome_asse(asse)
            )
            if esito.bloccati:
                testo = f"{testo} {TESTI['AVVISO_TRASFORMAZIONE_PARZIALE'].format(numero=esito.bloccati)}"
            return testo

        return self.esegui_sicuro(context, azione)


class FORMAFACILE_OT_spazia(_OperatoreSuScelta):
    """Mette gli oggetti scelti alla stessa distanza l'uno dall'altro."""

    bl_idname = comandi.ID_SPAZIA
    bl_label = TESTI["AZIONE_SPAZIA"]
    bl_description = TESTI["AIUTO_SPAZIA"]

    def execute(self, context):
        asse, _bordo, per_punto = self.impostazioni_allineamento(context)

        def azione() -> str:
            esito = allineamento.spazia(context, self.scelta(context), asse, per_punto=per_punto)
            numero = esito.applicati + esito.invariati
            if esito.spazio < 0.0:
                return TESTI["MESSAGGIO_SPAZIATI_STRETTI"].format(
                    numero=numero, asse=_nome_asse(asse)
                )
            testo = TESTI["MESSAGGIO_SPAZIATI"].format(
                numero=numero,
                asse=_nome_asse(asse),
                spazio=_numero(esito.spazio, 3),
                unita=_unita(context),
            )
            if esito.bloccati:
                testo = f"{testo} {TESTI['AVVISO_TRASFORMAZIONE_PARZIALE'].format(numero=esito.bloccati)}"
            return testo

        return self.esegui_sicuro(context, azione)


class FORMAFACILE_OT_raggruppa(_OperatoreSuScelta):
    """Raccoglie gli oggetti scelti in un gruppo con un nome."""

    bl_idname = comandi.ID_RAGGRUPPA
    bl_label = TESTI["AZIONE_RAGGRUPPA"]
    bl_description = TESTI["AIUTO_RAGGRUPPA"]

    nome: bpy.props.StringProperty(
        name=TESTI["ETICHETTA_GRUPPO_NOME"],
        description=TESTI["AIUTO_GRUPPO_NOME"],
        default="",
    )

    def invoke(self, context, event):
        if not self.nome:
            self.nome = raccolte.nome_libero(
                getattr(context, "scene", None), configuration.GRUPPO_NOME_BASE
            )
        if getattr(context, "area", None) is None or getattr(context, "window", None) is None:
            return self.execute(context)
        return context.window_manager.invoke_props_dialog(self, width=360)

    def draw(self, context):
        colonna = self.layout.column()
        colonna.label(text=TESTI["DIALOGO_RAGGRUPPA"], icon="INFO")
        colonna.prop(self, "nome")

    def execute(self, context):
        scelti = self.scelta(context)

        def azione() -> str:
            nome = self.nome or raccolte.nome_libero(
                getattr(context, "scene", None), configuration.GRUPPO_NOME_BASE
            )
            nome_finale = raccolte.crea(getattr(context, "scene", None), nome, scelti)
            return TESTI["MESSAGGIO_GRUPPO"].format(nome=nome_finale, numero=len(scelti))

        return self.esegui_sicuro(context, azione)


class FORMAFACILE_OT_scegli_gruppo(OperatoreFormaFacile):
    """Sceglie tutti gli oggetti di un gruppo."""

    bl_idname = comandi.ID_SCEGLI_GRUPPO
    bl_label = TESTI["AZIONE_SCEGLI_GRUPPO"]
    bl_description = TESTI["AIUTO_SCEGLI_GRUPPO"]

    gruppo: bpy.props.StringProperty(default="", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return getattr(context, "view_layer", None) is not None

    def execute(self, context):
        try:
            esito = raccolte.scegli(
                getattr(context, "scene", None), self.gruppo, context.view_layer
            )
        except ErroreGruppo as errore:
            self.report({"WARNING"}, str(errore))
            self.annuncia(context, str(errore))
            return {"CANCELLED"}
        if esito.scelti == 0:
            self.annuncia(context, TESTI["MESSAGGIO_GRUPPO_GRUPPO_VUOTO"].format(nome=self.gruppo))
            return {"CANCELLED"}
        testo = TESTI["MESSAGGIO_GRUPPO_SCELTO"].format(numero=esito.scelti, nome=self.gruppo)
        if esito.saltati:
            testo = f"{testo} {TESTI['AVVISO_SELEZIONE_PARZIALE'].format(numero=esito.saltati)}"
        self.annuncia(context, testo)
        return {"FINISHED"}


class FORMAFACILE_OT_alterna_gruppo(OperatoreFormaFacile):
    """Nasconde o fa ricomparire tutti gli oggetti di un gruppo."""

    bl_idname = comandi.ID_ALTERNA_GRUPPO
    bl_label = TESTI["AZIONE_ALTERNA_GRUPPO"]
    bl_description = TESTI["AIUTO_ALTERNA_GRUPPO"]

    gruppo: bpy.props.StringProperty(default="", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return getattr(context, "scene", None) is not None

    def execute(self, context):
        try:
            nascosto = raccolte.alterna_visibilita(getattr(context, "scene", None), self.gruppo)
        except ErroreGruppo as errore:
            self.report({"WARNING"}, str(errore))
            self.annuncia(context, str(errore))
            return {"CANCELLED"}
        chiave = "MESSAGGIO_GRUPPO_NASCOSTO" if nascosto else "MESSAGGIO_GRUPPO_MOSTRATO"
        self.annuncia(context, TESTI[chiave].format(nome=self.gruppo))
        return {"FINISHED"}


class FORMAFACILE_OT_togli_dal_gruppo(_OperatoreSuScelta):
    """Riporta gli oggetti scelti nella raccolta principale della scena."""

    bl_idname = comandi.ID_TOGLI_DAL_GRUPPO
    bl_label = TESTI["AZIONE_TOGLI_DAL_GRUPPO"]
    bl_description = TESTI["AIUTO_TOGLI_DAL_GRUPPO"]

    def execute(self, context):
        scelti = self.scelta(context)

        def azione() -> str:
            spostati = raccolte.togli(getattr(context, "scene", None), scelti)
            if spostati == 0:
                return TESTI["MESSAGGIO_TOGLI_GRUPPO_NESSUNO"]
            return TESTI["MESSAGGIO_TOGLI_GRUPPO"].format(numero=spostati)

        return self.esegui_sicuro(context, azione)


class FORMAFACILE_OT_togli_modifiche(_OperatoreSuScelta):
    """Toglie le modifiche non applicate dagli oggetti scelti.

    È il modo per tornare indietro senza conoscere `Ctrl+Z`: la forma di
    partenza non è mai stata toccata, quindi togliere la modifica la rimette
    esattamente com'era.
    """

    bl_idname = comandi.ID_TOGLI_MODIFICHE
    bl_label = TESTI["AZIONE_TOGLI_MODIFICHE"]
    bl_description = TESTI["AIUTO_TOGLI_MODIFICHE"]

    modificatore: bpy.props.StringProperty(default="", options={"HIDDEN"})

    def execute(self, context):
        scelti = self.scelta(context)

        def azione() -> str:
            tolti = 0
            for oggetto in scelti:
                if self.modificatore:
                    for modificatore in modificatori.elenca(oggetto):
                        if modificatori.nome_di(modificatore) == self.modificatore:
                            tolti += 1 if modificatori.rimuovi(oggetto, modificatore) else 0
                            break
                    continue
                tolti += modificatori.rimuovi_tutti(oggetto)
            modificatori.aggiorna(context)
            if tolti == 0:
                return TESTI["MESSAGGIO_MODIFICHE_NESSUNA"]
            if tolti == 1:
                return TESTI["MESSAGGIO_MODIFICA_TOLTA"]
            return TESTI["MESSAGGIO_MODIFICHE_TOLTE"].format(numero=tolti)

        return self.esegui_sicuro(context, azione)


CLASSI = (
    FORMAFACILE_OT_allinea,
    FORMAFACILE_OT_spazia,
    FORMAFACILE_OT_raggruppa,
    FORMAFACILE_OT_scegli_gruppo,
    FORMAFACILE_OT_alterna_gruppo,
    FORMAFACILE_OT_togli_dal_gruppo,
    FORMAFACILE_OT_togli_modifiche,
)
