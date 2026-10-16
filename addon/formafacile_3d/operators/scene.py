"""Comandi di creazione: cubo, sfera, cilindro, piano e luce."""

from __future__ import annotations

import bpy

from .. import comandi
from ..localization import TESTI
from ..scene import primitives
from .base import OperatoreFormaFacile


class _OperatoreCreazione(OperatoreFormaFacile):
    """Crea un oggetto e lo sceglie, con messaggio breve in italiano."""

    chiave_messaggio = "MESSAGGIO_OGGETTO_CREATO"

    def creatore(self, context):  # pragma: no cover - sostituito dai figli
        raise NotImplementedError

    @classmethod
    def poll(cls, context):
        return context.view_layer is not None

    def execute(self, context):
        if not self.in_modalita_oggetto(context):
            return self.richiedi_modalita_oggetto()
        try:
            oggetto = self.creatore(context)
        except Exception:  # noqa: BLE001 - un guasto non deve bloccare Blender
            return self.errore("ERRORE_CREAZIONE_OGGETTO", "LOG_ERRORE_CREAZIONE")
        self.annuncia(context, TESTI["MESSAGGIO_OGGETTO_CREATO"].format(nome=oggetto.name))
        self.report({"INFO"}, TESTI[self.chiave_messaggio])
        return {"FINISHED"}


class FORMAFACILE_OT_aggiungi_cubo(_OperatoreCreazione):
    """Aggiunge un cubo modificabile e registrato nell'annullamento di Blender."""

    bl_idname = comandi.ID_AGGIUNGI_CUBO
    bl_label = TESTI["AZIONE_AGGIUNGI_CUBO"]
    bl_description = TESTI["AIUTO_AGGIUNGI_CUBO"]
    chiave_messaggio = "CUBO_AGGIUNTO"

    def creatore(self, context):
        return primitives.crea_cubo(context)


class FORMAFACILE_OT_aggiungi_sfera(_OperatoreCreazione):
    """Aggiunge una sfera alla scena."""

    bl_idname = comandi.ID_AGGIUNGI_SFERA
    bl_label = TESTI["AZIONE_AGGIUNGI_SFERA"]
    bl_description = TESTI["AIUTO_AGGIUNGI_SFERA"]
    chiave_messaggio = "SFERA_AGGIUNTA"

    def creatore(self, context):
        return primitives.crea_sfera(context)


class FORMAFACILE_OT_aggiungi_cilindro(_OperatoreCreazione):
    """Aggiunge un cilindro alla scena."""

    bl_idname = comandi.ID_AGGIUNGI_CILINDRO
    bl_label = TESTI["AZIONE_AGGIUNGI_CILINDRO"]
    bl_description = TESTI["AIUTO_AGGIUNGI_CILINDRO"]
    chiave_messaggio = "CILINDRO_AGGIUNTO"

    def creatore(self, context):
        return primitives.crea_cilindro(context)


class FORMAFACILE_OT_aggiungi_piano(_OperatoreCreazione):
    """Aggiunge un piano piatto alla scena."""

    bl_idname = comandi.ID_AGGIUNGI_PIANO
    bl_label = TESTI["AZIONE_AGGIUNGI_PIANO"]
    bl_description = TESTI["AIUTO_AGGIUNGI_PIANO"]
    chiave_messaggio = "PIANO_AGGIUNTO"

    def creatore(self, context):
        return primitives.crea_piano(context)


class FORMAFACILE_OT_aggiungi_luce(_OperatoreCreazione):
    """Aggiunge una luce alla scena."""

    bl_idname = comandi.ID_AGGIUNGI_LUCE
    bl_label = TESTI["AZIONE_AGGIUNGI_LUCE"]
    bl_description = TESTI["AIUTO_AGGIUNGI_LUCE"]
    chiave_messaggio = "LUCE_AGGIUNTA"

    def creatore(self, context):
        return primitives.crea_luce(context)


class FORMAFACILE_OT_apri_barra(bpy.types.Operator):
    """Apre la barra laterale della Vista 3D sulla scheda FormaFacile."""

    bl_idname = comandi.ID_APRI_BARRA
    bl_label = TESTI["AZIONE_APRI_BARRA"]
    bl_description = TESTI["AIUTO_APRI_BARRA"]
    bl_options = {"REGISTER"}

    def execute(self, context):
        spazio = getattr(context, "space_data", None)
        if spazio is None or not hasattr(spazio, "show_region_ui"):
            self.report({"WARNING"}, TESTI["ERRORE_VISTA_NON_DISPONIBILE"])
            return {"CANCELLED"}
        spazio.show_region_ui = True
        return {"FINISHED"}


CLASSI = (
    FORMAFACILE_OT_aggiungi_cubo,
    FORMAFACILE_OT_aggiungi_sfera,
    FORMAFACILE_OT_aggiungi_cilindro,
    FORMAFACILE_OT_aggiungi_piano,
    FORMAFACILE_OT_aggiungi_luce,
    FORMAFACILE_OT_apri_barra,
)
