"""Comandi di scelta degli oggetti."""

from __future__ import annotations

import bpy

from .. import comandi
from ..blender import oggetti as servizio_oggetti
from ..blender import selezione
from ..localization import TESTI
from .base import OperatoreFormaFacile


def _mostra_se_nascosto(oggetto) -> bool:
    """Fa ricomparire un oggetto nascosto prima di sceglierlo.

    Blender non tiene scelto un oggetto che non si vede: senza questo passaggio
    il clic sul nome nell'elenco non avrebbe alcun effetto. Restituisce True
    quando l'oggetto è stato fatto ricomparire, così il messaggio può dirlo.
    """
    if selezione.bloccato(oggetto) or not selezione.nascosto(oggetto):
        return False
    servizio_oggetti.imposta_visibilita(oggetto, True)
    return True


def _messaggio_scelta(oggetto, modo: str, mostrato: bool) -> str:
    """Messaggio breve per la scelta di un oggetto dall'elenco."""
    if modo == "rimuovi":
        return TESTI["MESSAGGIO_TOLTO_DALLA_SCELTA"].format(nome=oggetto.name)
    if mostrato:
        chiave = (
            "MESSAGGIO_SCELTO_MOSTRATO" if modo == "sostituisci" else "MESSAGGIO_AGGIUNTO_MOSTRATO"
        )
    else:
        chiave = "MESSAGGIO_SCELTO" if modo == "sostituisci" else "MESSAGGIO_AGGIUNTO_ALLA_SCELTA"
    return TESTI[chiave].format(nome=oggetto.name)


def _messaggio_rifiuto(oggetto) -> str:
    """Spiega perché un singolo oggetto non è stato scelto."""
    if selezione.motivo_rifiuto(oggetto) == "bloccato":
        return TESTI["ERRORE_OGGETTO_NON_SELEZIONABILE"].format(nome=oggetto.name)
    return TESTI["ERRORE_OGGETTO_NASCOSTO"].format(nome=oggetto.name)


def _messaggio_saltati(testo: str, saltati: int) -> str:
    """Aggiunge una nota breve quando alcuni oggetti non erano scegliibili."""
    if not saltati:
        return testo
    return f"{testo} {TESTI['MESSAGGIO_SALTATI'].format(numero=saltati)}"


class FORMAFACILE_OT_scegli_tutto(OperatoreFormaFacile):
    """Sceglie tutti gli oggetti visibili."""

    bl_idname = comandi.ID_SCEGLI_TUTTO
    bl_label = TESTI["AZIONE_SELEZIONA_TUTTO"]
    bl_description = TESTI["AIUTO_SELEZIONA_TUTTO"]

    @classmethod
    def poll(cls, context):
        return context.view_layer is not None

    def execute(self, context):
        esito = selezione.scegli_tutto(context.view_layer)
        if not esito.scelti:
            self.annuncia(context, TESTI["MESSAGGIO_NIENTE_DA_SCEGLIERE"])
            return {"CANCELLED"}
        self.annuncia(
            context,
            _messaggio_saltati(TESTI["MESSAGGIO_SELEZIONA_TUTTO"].format(numero=esito.scelti), esito.saltati),
        )
        return {"FINISHED"}


class FORMAFACILE_OT_descegli_tutto(OperatoreFormaFacile):
    """Toglie la scelta da tutti gli oggetti."""

    bl_idname = comandi.ID_DESCEGLI_TUTTO
    bl_label = TESTI["AZIONE_DESCEGLI_TUTTO"]
    bl_description = TESTI["AIUTO_DESCEGLI_TUTTO"]

    @classmethod
    def poll(cls, context):
        return context.view_layer is not None

    def execute(self, context):
        selezione.descegli_tutto(context.view_layer)
        self.annuncia(context, TESTI["MESSAGGIO_DESELEZIONA_TUTTO"])
        return {"FINISHED"}


class FORMAFACILE_OT_inverti_scelta(OperatoreFormaFacile):
    """Sceglie gli oggetti non scelti e toglie la scelta agli altri."""

    bl_idname = comandi.ID_INVERTI_SCELTA
    bl_label = TESTI["AZIONE_INVERTI_SCELTA"]
    bl_description = TESTI["AIUTO_INVERTI_SCELTA"]

    @classmethod
    def poll(cls, context):
        return context.view_layer is not None

    def execute(self, context):
        esito = selezione.inverti_scelta(context.view_layer)
        if not esito.scelti:
            self.annuncia(context, TESTI["MESSAGGIO_DESELEZIONA_TUTTO"])
            return {"FINISHED"}
        self.annuncia(
            context,
            _messaggio_saltati(TESTI["MESSAGGIO_INVERTI_SELEZIONE"].format(numero=esito.scelti), esito.saltati),
        )
        return {"FINISHED"}


class FORMAFACILE_OT_scegli_stesso_tipo(OperatoreFormaFacile):
    """Sceglie tutti gli oggetti dello stesso tipo di quello attivo."""

    bl_idname = comandi.ID_SCEGLI_STESSO_TIPO
    bl_label = TESTI["AZIONE_SCEGLI_STESSO_TIPO"]
    bl_description = TESTI["AIUTO_SCEGLI_STESSO_TIPO"]

    @classmethod
    def poll(cls, context):
        return OperatoreFormaFacile.oggetto_attivo(context) is not None

    def execute(self, context):
        esito = selezione.scegli_stesso_tipo(context.view_layer, self.oggetto_attivo(context))
        if esito.scelti <= 1:
            self.annuncia(context, TESTI["MESSAGGIO_SELEZIONA_TIPO_NESSUNO"])
            return {"CANCELLED"}
        self.annuncia(
            context,
            _messaggio_saltati(TESTI["MESSAGGIO_SELEZIONA_TIPO"].format(numero=esito.scelti), esito.saltati),
        )
        return {"FINISHED"}


class FORMAFACILE_OT_scegli_oggetto(OperatoreFormaFacile):
    """Sceglie l'oggetto indicato nell'elenco.

    Con Maiusc premuto l'oggetto si aggiunge alla scelta, con Ctrl si toglie:
    sono le stesse abitudini della Vista 3D.
    """

    bl_idname = comandi.ID_SCEGLI_OGGETTO
    bl_label = TESTI["AZIONE_SCEGLI_OGGETTO"]
    bl_description = TESTI["AIUTO_SCEGLI_OGGETTO"]

    oggetto: bpy.props.StringProperty(default="", options={"HIDDEN"})
    modo: bpy.props.EnumProperty(
        items=tuple((modo, modo, "") for modo in comandi.MODI_SCELTA),
        default="sostituisci",
        options={"HIDDEN"},
    )

    @classmethod
    def poll(cls, context):
        return context.view_layer is not None

    def invoke(self, context, event):
        if event is not None and getattr(event, "shift", False):
            self.modo = "aggiungi"
        elif event is not None and getattr(event, "ctrl", False):
            self.modo = "rimuovi"
        return self.execute(context)

    def execute(self, context):
        oggetto = self.risolvi_oggetto(context, self.oggetto)
        if oggetto is None:
            return {"CANCELLED"}
        mostrato = _mostra_se_nascosto(oggetto)
        esito = selezione.scegli_oggetto(context.view_layer, oggetto, self.modo)
        if esito.saltati:
            self.annuncia(context, _messaggio_rifiuto(oggetto))
            return {"CANCELLED"}
        self.annuncia(context, _messaggio_scelta(oggetto, self.modo, mostrato))
        return {"FINISHED"}


class FORMAFACILE_OT_alterna_scelta(OperatoreFormaFacile):
    """Aggiunge o toglie l'oggetto indicato dalla scelta."""

    bl_idname = comandi.ID_ALTERNA_SCELTA
    bl_label = TESTI["AZIONE_ALTERNA_SCELTA"]
    bl_description = TESTI["AIUTO_ALTERNA_SCELTA"]

    oggetto: bpy.props.StringProperty(default="", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return context.view_layer is not None

    def execute(self, context):
        oggetto = self.risolvi_oggetto(context, self.oggetto) or self.oggetto_attivo(context)
        if oggetto is None:
            return {"CANCELLED"}
        mostrato = _mostra_se_nascosto(oggetto) if not oggetto.select_get() else False
        esito = selezione.alterna_scelta(context.view_layer, oggetto)
        if esito.saltati:
            self.annuncia(context, _messaggio_rifiuto(oggetto))
            return {"CANCELLED"}
        if oggetto.select_get():
            self.annuncia(context, _messaggio_scelta(oggetto, "sostituisci", mostrato))
        else:
            self.annuncia(context, TESTI["MESSAGGIO_TOLTO_DALLA_SCELTA"].format(nome=oggetto.name))
        return {"FINISHED"}


CLASSI = (
    FORMAFACILE_OT_scegli_tutto,
    FORMAFACILE_OT_descegli_tutto,
    FORMAFACILE_OT_inverti_scelta,
    FORMAFACILE_OT_scegli_stesso_tipo,
    FORMAFACILE_OT_scegli_oggetto,
    FORMAFACILE_OT_alterna_scelta,
)
