"""Comandi di vista, annullamento e ricerca."""

from __future__ import annotations

import bpy

from .. import comandi
from ..blender import vista as servizio_vista
from ..localization import TESTI
from ..logging_service import ottieni_logger
from ..scene.stato import stato_della_scena
from .base import OperatoreFormaFacile


class FORMAFACILE_OT_vista_iniziale(OperatoreFormaFacile):
    """Riporta la Vista 3D come all'avvio e inquadra tutta la scena."""

    bl_idname = comandi.ID_VISTA_INIZIALE
    bl_label = TESTI["AZIONE_VISTA_INIZIALE"]
    bl_description = TESTI["AIUTO_VISTA_INIZIALE"]
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return servizio_vista.aree_vista_disponibili(context)

    def execute(self, context):
        try:
            servizio_vista.torna_alla_vista_iniziale(context)
        except servizio_vista.ErroreVista as errore:
            ottieni_logger().warning(TESTI["LOG_ERRORE_VISTA"])
            self.report({"WARNING"}, str(errore))
            self.annuncia(context, str(errore))
            return {"CANCELLED"}
        self.annuncia(context, TESTI["MESSAGGIO_VISTA_INIZIALE"])
        return {"FINISHED"}


class FORMAFACILE_OT_inquadra_tutto(OperatoreFormaFacile):
    """Inquadra tutti gli oggetti lasciando la direzione della vista."""

    bl_idname = comandi.ID_INQUADRA_TUTTO
    bl_label = TESTI["AZIONE_INQUADRA_TUTTO"]
    bl_description = TESTI["AIUTO_INQUADRA_TUTTO"]
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return servizio_vista.aree_vista_disponibili(context)

    def execute(self, context):
        try:
            servizio_vista.inquadra_tutta_la_scena(context)
        except servizio_vista.ErroreVista as errore:
            ottieni_logger().warning(TESTI["LOG_ERRORE_VISTA"])
            self.report({"WARNING"}, str(errore))
            self.annuncia(context, str(errore))
            return {"CANCELLED"}
        self.annuncia(context, TESTI["MESSAGGIO_INQUADRA_TUTTO"])
        return {"FINISHED"}


class FORMAFACILE_OT_inquadra_scelti(OperatoreFormaFacile):
    """Inquadra soltanto gli oggetti scelti."""

    bl_idname = comandi.ID_INQUADRA_SCELTI
    bl_label = TESTI["AZIONE_INQUADRA_SCELTI"]
    bl_description = TESTI["AIUTO_INQUADRA_SCELTI"]
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return servizio_vista.aree_vista_disponibili(context) and bool(
            OperatoreFormaFacile.scelti(context)
        )

    def execute(self, context):
        try:
            servizio_vista.inquadra_scelti(context)
        except servizio_vista.ErroreVista as errore:
            ottieni_logger().warning(TESTI["LOG_ERRORE_VISTA"])
            self.report({"WARNING"}, str(errore))
            self.annuncia(context, str(errore))
            return {"CANCELLED"}
        self.annuncia(context, TESTI["MESSAGGIO_INQUADRA_SCELTI"])
        return {"FINISHED"}


class _OperatoreStoria(OperatoreFormaFacile):
    """Annulla o ripete l'ultima azione usando la storia di Blender."""

    id_nativo = ""
    chiave_messaggio = ""

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        nome_operatore = self.id_nativo.split(".")
        try:
            risultato = getattr(getattr(bpy.ops, nome_operatore[0]), nome_operatore[1])()
        except (AttributeError, RuntimeError):
            ottieni_logger().info(TESTI["LOG_ERRORE_STORIA"])
            self.report({"WARNING"}, TESTI["ERRORE_STORIA"])
            self.annuncia(context, TESTI["ERRORE_STORIA"])
            return {"CANCELLED"}
        if "FINISHED" not in risultato:
            self.annuncia(context, TESTI["ERRORE_STORIA"])
            return {"CANCELLED"}
        self.annuncia(context, TESTI[self.chiave_messaggio])
        return {"FINISHED"}


class FORMAFACILE_OT_annulla(_OperatoreStoria):
    """Annulla l'ultima azione."""

    bl_idname = comandi.ID_ANNULLA
    bl_label = TESTI["AZIONE_ANNULLA"]
    bl_description = TESTI["AIUTO_ANNULLA"]
    bl_options = {"REGISTER"}
    id_nativo = comandi.ID_NATIVO_ANNULLA
    chiave_messaggio = "MESSAGGIO_ANNULLA"


class FORMAFACILE_OT_ripeti(_OperatoreStoria):
    """Ripete l'azione annullata."""

    bl_idname = comandi.ID_RIPETI
    bl_label = TESTI["AZIONE_RIPETI"]
    bl_description = TESTI["AIUTO_RIPETI"]
    bl_options = {"REGISTER"}
    id_nativo = comandi.ID_NATIVO_RIPETI
    chiave_messaggio = "MESSAGGIO_RIPETI"


class FORMAFACILE_OT_pulisci_filtro(OperatoreFormaFacile):
    """Cancella il testo di ricerca dell'elenco oggetti."""

    bl_idname = comandi.ID_PULISCI_FILTRO
    bl_label = TESTI["AZIONE_PULISCI_FILTRO"]
    bl_description = TESTI["AIUTO_PULISCI_FILTRO"]
    bl_options = {"REGISTER"}

    def execute(self, context):
        stato = stato_della_scena(getattr(context, "scene", None))
        if stato is None:
            return {"CANCELLED"}
        stato.filtro = ""
        return {"FINISHED"}


CLASSI = (
    FORMAFACILE_OT_vista_iniziale,
    FORMAFACILE_OT_inquadra_tutto,
    FORMAFACILE_OT_inquadra_scelti,
    FORMAFACILE_OT_annulla,
    FORMAFACILE_OT_ripeti,
    FORMAFACILE_OT_pulisci_filtro,
)
