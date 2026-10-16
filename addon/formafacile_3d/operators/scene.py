"""Comandi di creazione: cubo, sfera, cilindro, cono, piano, ciambella, testo e luce.

Qui stanno anche i tre comandi che attivano gli strumenti di Blender con le
maniglie (frecce, archi e cubetti): non cambiano i dati della scena, quindi
non entrano nella storia di annullamento.
"""

from __future__ import annotations

import bpy

from .. import comandi
from ..blender import vista as servizio_vista
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


class FORMAFACILE_OT_aggiungi_cono(_OperatoreCreazione):
    """Aggiunge un cono alla scena."""

    bl_idname = comandi.ID_AGGIUNGI_CONO
    bl_label = TESTI["AZIONE_AGGIUNGI_CONO"]
    bl_description = TESTI["AIUTO_AGGIUNGI_CONO"]
    chiave_messaggio = "CONO_AGGIUNTO"

    def creatore(self, context):
        return primitives.crea_cono(context)


class FORMAFACILE_OT_aggiungi_toro(_OperatoreCreazione):
    """Aggiunge una ciambella alla scena."""

    bl_idname = comandi.ID_AGGIUNGI_TORO
    bl_label = TESTI["AZIONE_AGGIUNGI_TORO"]
    bl_description = TESTI["AIUTO_AGGIUNGI_TORO"]
    chiave_messaggio = "TORO_AGGIUNTO"

    def creatore(self, context):
        return primitives.crea_toro(context)


class FORMAFACILE_OT_aggiungi_testo(_OperatoreCreazione):
    """Aggiunge una scritta in piedi alla scena."""

    bl_idname = comandi.ID_AGGIUNGI_TESTO
    bl_label = TESTI["AZIONE_AGGIUNGI_TESTO"]
    bl_description = TESTI["AIUTO_AGGIUNGI_TESTO"]
    chiave_messaggio = "TESTO_AGGIUNTO"

    def creatore(self, context):
        return primitives.crea_testo(context)


class FORMAFACILE_OT_aggiungi_luce(_OperatoreCreazione):
    """Aggiunge una luce alla scena."""

    bl_idname = comandi.ID_AGGIUNGI_LUCE
    bl_label = TESTI["AZIONE_AGGIUNGI_LUCE"]
    bl_description = TESTI["AIUTO_AGGIUNGI_LUCE"]
    chiave_messaggio = "LUCE_AGGIUNTA"

    def creatore(self, context):
        return primitives.crea_luce(context)


class _OperatoreManiglie(OperatoreFormaFacile):
    """Attiva uno strumento nativo di Blender, quello che mostra le maniglie.

    Non cambia i dati della scena, quindi non finisce nella storia di Blender:
    si limita a scegliere lo strumento con cui l'utente lavorerà.
    """

    bl_options = {"REGISTER"}
    chiave_strumento = ""
    chiave_messaggio = ""

    @classmethod
    def poll(cls, context):
        return servizio_vista.aree_vista_disponibili(context)

    def execute(self, context):
        nome_strumento = comandi.STRUMENTI[self.chiave_strumento][0]
        if not servizio_vista.attiva_strumento(context, nome_strumento):
            self.report({"WARNING"}, TESTI["ERRORE_STRUMENTO"])
            self.annuncia(context, TESTI["ERRORE_STRUMENTO"])
            return {"CANCELLED"}
        messaggio = TESTI[comandi.STRUMENTI[self.chiave_strumento][1]]
        self.annuncia(context, messaggio)
        self.report({"INFO"}, messaggio)
        return {"FINISHED"}


class FORMAFACILE_OT_strumento_sposta(_OperatoreManiglie):
    """Mostra le frecce per spostare l'oggetto con il mouse."""

    bl_idname = comandi.ID_STRUMENTO_SPOSTA
    bl_label = TESTI["AZIONE_STRUMENTO_SPOSTA"]
    bl_description = TESTI["AIUTO_STRUMENTO_SPOSTA"]
    chiave_strumento = comandi.ID_STRUMENTO_SPOSTA
    chiave_messaggio = "MESSAGGIO_STRUMENTO_SPOSTA"


class FORMAFACILE_OT_strumento_ruota(_OperatoreManiglie):
    """Mostra gli archi per ruotare l'oggetto con il mouse."""

    bl_idname = comandi.ID_STRUMENTO_RUOTA
    bl_label = TESTI["AZIONE_STRUMENTO_RUOTA"]
    bl_description = TESTI["AIUTO_STRUMENTO_RUOTA"]
    chiave_strumento = comandi.ID_STRUMENTO_RUOTA
    chiave_messaggio = "MESSAGGIO_STRUMENTO_RUOTA"


class FORMAFACILE_OT_strumento_scala(_OperatoreManiglie):
    """Mostra i cubetti per cambiare la dimensione con il mouse."""

    bl_idname = comandi.ID_STRUMENTO_SCALA
    bl_label = TESTI["AZIONE_STRUMENTO_SCALA"]
    bl_description = TESTI["AIUTO_STRUMENTO_SCALA"]
    chiave_strumento = comandi.ID_STRUMENTO_SCALA
    chiave_messaggio = "MESSAGGIO_STRUMENTO_SCALA"


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
    FORMAFACILE_OT_aggiungi_cono,
    FORMAFACILE_OT_aggiungi_piano,
    FORMAFACILE_OT_aggiungi_toro,
    FORMAFACILE_OT_aggiungi_testo,
    FORMAFACILE_OT_aggiungi_luce,
    FORMAFACILE_OT_strumento_sposta,
    FORMAFACILE_OT_strumento_ruota,
    FORMAFACILE_OT_strumento_scala,
    FORMAFACILE_OT_apri_barra,
)
