"""Pannelli di FormaFacile nella barra laterale della Vista 3D.

I pannelli sono quattro e seguono il risultato che l'utente vuole ottenere,
non la struttura interna di Blender:

* Azioni principali: costruisci, guarda la scena, annulla e ripeti;
* La mia scena: elenco oggetti, scelta, visibilità, rinomina;
* Oggetto scelto: comandi che cambiano in base alla scelta;
* Dai forma: strumenti guidati e guida passo passo per rifinire le forme;
* Comandi di Blender: solo nella modalità completa.
"""

from __future__ import annotations

import bpy

from .. import configuration
from ..localization import TESTI
from ..scene.stato import modalita_della_scena
from . import piano as piano_ui
from . import renderer, vista


class _PannelloFormaFacile(bpy.types.Panel):
    """Base comune: spazio, categoria e disegno del piano."""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = TESTI["CATEGORIA_PANNELLO"]
    chiave_piano = ""

    def draw(self, context):
        contesto, risolutore = vista.raccogli_contesto(context)
        pannello = _cerca_pannello(piano_ui.costruisci_piano(contesto), self.chiave_piano)
        if pannello is None:
            return
        renderer.disegna_pannello(self.layout, pannello, risolutore)


def _cerca_pannello(piano, chiave: str):
    for pannello in piano:
        if pannello.chiave == chiave:
            return pannello
    return None


class FORMAFACILE_PT_principale(_PannelloFormaFacile):
    """Barra delle azioni principali, sempre visibile."""

    bl_label = TESTI["TITOLO_PANNELLO_PRINCIPALE"]
    bl_idname = "FORMAFACILE_PT_principale"
    bl_order = 0
    chiave_piano = "principale"


class FORMAFACILE_PT_scena(_PannelloFormaFacile):
    """Elenco degli oggetti: la "mia scena" in parole semplici."""

    bl_label = TESTI["TITOLO_PANNELLO_SCENA"]
    bl_idname = "FORMAFACILE_PT_scena"
    bl_parent_id = "FORMAFACILE_PT_principale"
    bl_order = 1
    chiave_piano = "scena"


class FORMAFACILE_PT_oggetto(_PannelloFormaFacile):
    """Pannello contestuale: cambia con la scelta dell'utente."""

    bl_label = TESTI["TITOLO_PANNELLO_OGGETTO"]
    bl_idname = "FORMAFACILE_PT_oggetto"
    bl_parent_id = "FORMAFACILE_PT_principale"
    bl_order = 2
    chiave_piano = "oggetto"


class FORMAFACILE_PT_modella(_PannelloFormaFacile):
    """Strumenti guidati per rifinire una forma, spiegati passo per passo."""

    bl_label = TESTI["TITOLO_PANNELLO_MODELLA"]
    bl_idname = "FORMAFACILE_PT_modella"
    bl_parent_id = "FORMAFACILE_PT_principale"
    bl_order = 3
    chiave_piano = "modella"


class FORMAFACILE_PT_completo(_PannelloFormaFacile):
    """Comandi tecnici di Blender, visibili solo nella modalità completa."""

    bl_label = TESTI["TITOLO_PANNELLO_COMPLETO"]
    bl_idname = "FORMAFACILE_PT_completo"
    bl_parent_id = "FORMAFACILE_PT_principale"
    bl_order = 4
    bl_options = {"DEFAULT_CLOSED"}
    chiave_piano = "completo"

    @classmethod
    def poll(cls, context):
        return modalita_della_scena(getattr(context, "scene", None)) == configuration.MODALITA_COMPLETA


class FORMAFACILE_HT_barra(bpy.types.Header):
    """Pulsante nella testata della Vista 3D: apre la barra laterale.

    La testata nativa non viene sostituita: questo disegno si aggiunge e
    mostra soltanto un pulsante in più.
    """

    bl_idname = "FORMAFACILE_HT_barra"
    bl_space_type = "VIEW_3D"
    bl_region_type = "HEADER"

    def draw(self, context):
        self.layout.operator(
            "formafacile.apri_barra",
            text=TESTI["AZIONE_APRI_BARRA"],
            icon="MESH_CUBE",
        )


CLASSI = (
    FORMAFACILE_PT_principale,
    FORMAFACILE_PT_scena,
    FORMAFACILE_PT_oggetto,
    FORMAFACILE_PT_modella,
    FORMAFACILE_PT_completo,
    FORMAFACILE_HT_barra,
)
