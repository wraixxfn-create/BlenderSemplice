"""Pannello di benvenuto di FormaFacile nella barra laterale della Vista 3D."""

from __future__ import annotations

import bpy

from ..localization import TESTI


class FORMAFACILE_PT_pannello(bpy.types.Panel):
    bl_label = TESTI["TITOLO_PANNELLO"]
    bl_idname = "FORMAFACILE_PT_pannello"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = TESTI["CATEGORIA_PANNELLO"]

    def draw(self, context):
        layout = self.layout
        layout.label(text=TESTI["DESCRIZIONE_PANNELLO"])
        layout.separator()
        layout.operator(
            "formafacile.aggiungi_cubo",
            text=TESTI["AZIONE_AGGIUNGI_CUBO"],
            icon="MESH_CUBE",
        )
