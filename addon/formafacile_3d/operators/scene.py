"""Operazioni di base sulla scena di Blender."""

from __future__ import annotations

import bpy

from ..localization import TESTI
from ..logging_service import ottieni_logger
from ..scene.primitives import crea_cubo


class FORMAFACILE_OT_aggiungi_cubo(bpy.types.Operator):
    """Aggiunge un cubo modificabile e registrato nell'annullamento di Blender."""

    bl_idname = "formafacile.aggiungi_cubo"
    bl_label = TESTI["AZIONE_AGGIUNGI_CUBO"]
    bl_description = TESTI["AIUTO_AGGIUNGI_CUBO"]
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            crea_cubo(context)
            self.report({"INFO"}, TESTI["CUBO_AGGIUNTO"])
            return {"FINISHED"}
        except Exception:
            # Non si registrano percorsi, nomi di file o dettagli della scena.
            ottieni_logger().error(TESTI["LOG_ERRORE_CUBO"])
            self.report({"ERROR"}, TESTI["ERRORE_AGGIUNTA_CUBO"])
            return {"CANCELLED"}
