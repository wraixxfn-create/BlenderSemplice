"""Comandi sugli oggetti: rinomina, duplica, elimina, nascondi, inquadra."""

from __future__ import annotations

from math import radians

import bpy

from .. import comandi, configuration
from ..blender import oggetti as servizio_oggetti
from ..blender import trasformazioni, vista as servizio_vista
from ..localization import TESTI
from .base import OperatoreFormaFacile


class FORMAFACILE_OT_rinomina(OperatoreFormaFacile):
    """Cambia il nome dell'oggetto scelto con una piccola finestra di conferma."""

    bl_idname = comandi.ID_RINOMINA
    bl_label = TESTI["TITOLO_RINOMINA"]
    bl_description = TESTI["AIUTO_RINOMINA"]

    oggetto: bpy.props.StringProperty(default="", options={"HIDDEN"})
    nome: bpy.props.StringProperty(
        name=TESTI["ETICHETTA_NUOVO_NOME"],
        description=TESTI["AIUTO_NUOVO_NOME"],
        default="",
    )

    @classmethod
    def poll(cls, context):
        return context.view_layer is not None

    def invoke(self, context, event):
        oggetto = self.risolvi_oggetto(context, self.oggetto) or self.oggetto_attivo(context)
        if oggetto is None:
            return {"CANCELLED"}
        self.oggetto = oggetto.name
        self.nome = oggetto.name
        return context.window_manager.invoke_props_dialog(self, width=320)

    def execute(self, context):
        oggetto = self.risolvi_oggetto(context, self.oggetto)
        if oggetto is None:
            return {"CANCELLED"}
        try:
            nome_finale, cambiato = servizio_oggetti.rinomina(oggetto, self.nome)
        except ValueError:
            return self.errore("ERRORE_NOME_VUOTO", "LOG_ERRORE_CREAZIONE", context)
        if not cambiato:
            self.annuncia(context, TESTI["MESSAGGIO_RINOMINA_INVARIATA"])
            return {"FINISHED"}
        self.annuncia(context, TESTI["MESSAGGIO_RINOMINATO"].format(nome=nome_finale))
        return {"FINISHED"}


class FORMAFACILE_OT_duplica(OperatoreFormaFacile):
    """Crea una copia indipendente degli oggetti scelti."""

    bl_idname = comandi.ID_DUPLICA
    bl_label = TESTI["AZIONE_DUPLICA"]
    bl_description = TESTI["AIUTO_DUPLICA"]

    @classmethod
    def poll(cls, context):
        return OperatoreFormaFacile.in_modalita_oggetto(context) and bool(
            OperatoreFormaFacile.scelti(context)
        )

    def execute(self, context):
        scelti = self.scelti(context)
        passo = configuration.PASSO_PREDEFINITO
        copie = []
        for oggetto in scelti:
            copie.append(servizio_oggetti.duplica(oggetto, (passo, 0.0, 0.0)))

        if not copie:
            return self.errore("ERRORE_CREAZIONE_OGGETTO", "LOG_ERRORE_CREAZIONE")

        for oggetto in scelti:
            oggetto.select_set(False)
        for copia in copie:
            copia.select_set(True)
        context.view_layer.objects.active = copie[-1]

        if len(copie) == 1:
            self.annuncia(context, TESTI["MESSAGGIO_DUPLICATO"].format(nome=copie[0].name))
        else:
            self.annuncia(context, TESTI["MESSAGGIO_DUPLICATI"].format(numero=len(copie)))
        return {"FINISHED"}


class FORMAFACILE_OT_elimina(OperatoreFormaFacile):
    """Elimina gli oggetti scelti, chiedendo conferma se sono più di uno."""

    bl_idname = comandi.ID_ELIMINA
    bl_label = TESTI["AZIONE_ELIMINA"]
    bl_description = TESTI["AIUTO_ELIMINA"]

    @classmethod
    def poll(cls, context):
        return OperatoreFormaFacile.in_modalita_oggetto(context) and bool(
            OperatoreFormaFacile.scelti(context)
        )

    def invoke(self, context, event):
        if len(self.scelti(context)) > 1:
            return context.window_manager.invoke_props_dialog(self, width=320)
        return self.execute(context)

    def draw(self, context):
        self.layout.label(
            text=TESTI["ETICHETTA_CONFERMA_ELIMINA"].format(numero=len(self.scelti(context)))
        )

    def execute(self, context):
        scelti = self.scelti(context)
        nomi = [oggetto.name for oggetto in scelti]
        quanti = servizio_oggetti.elimina(scelti)
        if not quanti:
            return self.errore("ERRORE_ELIMINA", "LOG_ERRORE_CREAZIONE")
        context.view_layer.objects.active = None
        if quanti == 1 and nomi:
            self.annuncia(context, TESTI["MESSAGGIO_ELIMINATO"].format(nome=nomi[0]))
        else:
            self.annuncia(context, TESTI["MESSAGGIO_ELIMINATI"].format(numero=quanti))
        return {"FINISHED"}


class FORMAFACILE_OT_alterna_visibilita(OperatoreFormaFacile):
    """Mostra o nasconde gli oggetti indicati."""

    bl_idname = comandi.ID_ALTERNA_VISIBILITA
    bl_label = TESTI["AZIONE_ALTERNA_VISIBILITA"]
    bl_description = TESTI["AIUTO_ALTERNA_VISIBILITA"]

    oggetto: bpy.props.StringProperty(default="", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return context.view_layer is not None

    def execute(self, context):
        bersagli = self.bersagli(context, self.oggetto)
        if not bersagli:
            return self.errore("ERRORE_VISIBILITA", "LOG_ERRORE_CREAZIONE")

        nascondi = not all(oggetto.hide_viewport for oggetto in bersagli)
        for oggetto in bersagli:
            servizio_oggetti.imposta_visibilita(oggetto, not nascondi)

        if nascondi:
            if len(bersagli) == 1:
                self.annuncia(context, TESTI["MESSAGGIO_NASCOSTO"].format(nome=bersagli[0].name))
            else:
                self.annuncia(context, TESTI["MESSAGGIO_NASCOSTI"].format(numero=len(bersagli)))
        else:
            if len(bersagli) == 1:
                self.annuncia(context, TESTI["MESSAGGIO_MOSTRATO"].format(nome=bersagli[0].name))
            else:
                self.annuncia(context, TESTI["MESSAGGIO_MOSTRATI"].format(numero=len(bersagli)))
        return {"FINISHED"}


class FORMAFACILE_OT_mostra_tutti(OperatoreFormaFacile):
    """Fa ricomparire tutti gli oggetti nascosti."""

    bl_idname = comandi.ID_MOSTRA_TUTTI
    bl_label = TESTI["AZIONE_MOSTRA_TUTTI"]
    bl_description = TESTI["AIUTO_MOSTRA_TUTTI"]

    @classmethod
    def poll(cls, context):
        return context.view_layer is not None

    def execute(self, context):
        mostrati = servizio_oggetti.mostra_tutti(context.view_layer)
        if not mostrati:
            return {"CANCELLED"}
        self.annuncia(context, TESTI["MESSAGGIO_MOSTRATI_TUTTI"])
        return {"FINISHED"}


class FORMAFACILE_OT_inquadra_oggetto(OperatoreFormaFacile):
    """Avvicina la vista a un singolo oggetto."""

    bl_idname = comandi.ID_INQUADRA_OGGETTO
    bl_label = TESTI["AZIONE_INQUADRA_OGGETTO"]
    bl_description = TESTI["AIUTO_INQUADRA_OGGETTO"]
    bl_options = {"REGISTER"}

    oggetto: bpy.props.StringProperty(default="", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return servizio_vista.aree_vista_disponibili(context)

    def execute(self, context):
        bersagli = self.bersagli(context, self.oggetto)
        if not bersagli:
            return {"CANCELLED"}
        try:
            servizio_vista.inquadra_oggetto(context, bersagli[0])
        except servizio_vista.ErroreVista as errore:
            self.report({"WARNING"}, str(errore))
            self.annuncia(context, str(errore))
            return {"CANCELLED"}
        self.annuncia(context, TESTI["MESSAGGIO_INQUADRA_OGGETTO"].format(nome=bersagli[0].name))
        return {"FINISHED"}


class FORMAFACILE_OT_luce_piu(OperatoreFormaFacile):
    """Aumenta la potenza delle luci scelte."""

    bl_idname = comandi.ID_LUCE_PIU
    bl_label = TESTI["AZIONE_PIU_LUMINOSA"]
    bl_description = TESTI["AIUTO_PIU_LUMINOSA"]

    oggetto: bpy.props.StringProperty(default="", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return OperatoreFormaFacile.in_modalita_oggetto(context) and bool(
            OperatoreFormaFacile.scelti(context)
        )

    def execute(self, context):
        return _cambia_luci(self, context, configuration.FATTORE_LUCE)


class FORMAFACILE_OT_luce_meno(OperatoreFormaFacile):
    """Riduce la potenza delle luci scelte."""

    bl_idname = comandi.ID_LUCE_MENO
    bl_label = TESTI["AZIONE_MENO_LUMINOSA"]
    bl_description = TESTI["AIUTO_MENO_LUMINOSA"]

    oggetto: bpy.props.StringProperty(default="", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return OperatoreFormaFacile.in_modalita_oggetto(context) and bool(
            OperatoreFormaFacile.scelti(context)
        )

    def execute(self, context):
        return _cambia_luci(self, context, 1.0 / configuration.FATTORE_LUCE)


def _cambia_luci(operatore, context, fattore: float) -> set[str]:
    """Applica il fattore a tutte le luci fra gli oggetti indicati."""
    luci = [oggetto for oggetto in operatore.bersagli(context, operatore.oggetto) if oggetto.type == "LIGHT"]
    if not luci:
        return {"CANCELLED"}
    try:
        for luce in luci:
            trasformazioni.cambia_potenza_luce(luce, fattore, configuration.POTENZA_LUCE_MINIMA)
    except trasformazioni.ErroreTrasformazione as errore:
        operatore.report({"WARNING"}, str(errore))
        return {"CANCELLED"}
    operatore.annuncia(context, TESTI["MESSAGGIO_LUCE_CAMBIATA"])
    return {"FINISHED"}


class FORMAFACILE_OT_guarda_da_camera(OperatoreFormaFacile):
    """Mostra la scena dal punto di vista della telecamera scelta.

    Se la telecamera non è ancora quella principale lo diventa: l'immagine
    finale e la vista restano così sempre d'accordo.
    """

    bl_idname = comandi.ID_GUARDA_DA_CAMERA
    bl_label = TESTI["AZIONE_GUARDA_DA_CAMERA"]
    bl_description = TESTI["AIUTO_GUARDA_DA_CAMERA"]
    bl_options = {"REGISTER", "UNDO"}

    oggetto: bpy.props.StringProperty(default="", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return servizio_vista.aree_vista_disponibili(context)

    def execute(self, context):
        bersagli = [oggetto for oggetto in self.bersagli(context, self.oggetto) if oggetto.type == "CAMERA"]
        if not bersagli:
            return self.errore("ERRORE_TELECAMERA", "LOG_ERRORE_VISTA")
        if not servizio_vista.guarda_dalla_telecamera(context, bersagli[0]):
            return self.errore("ERRORE_TELECAMERA", "LOG_ERRORE_VISTA")
        self.annuncia(context, TESTI["MESSAGGIO_GUARDA_DA_CAMERA"])
        return {"FINISHED"}


class FORMAFACILE_OT_telecamera_principale(OperatoreFormaFacile):
    """Imposta la telecamera scelta come principale."""

    bl_idname = comandi.ID_TELECAMERA_PRINCIPALE
    bl_label = TESTI["AZIONE_TELECAMERA_PRINCIPALE"]
    bl_description = TESTI["AIUTO_TELECAMERA_PRINCIPALE"]

    oggetto: bpy.props.StringProperty(default="", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        bersagli = [oggetto for oggetto in self.bersagli(context, self.oggetto) if oggetto.type == "CAMERA"]
        if not bersagli:
            return self.errore("ERRORE_TELECAMERA", "LOG_ERRORE_VISTA")
        if not servizio_oggetti.imposta_telecamera_principale(context.scene, bersagli[0]):
            return self.errore("ERRORE_TELECAMERA", "LOG_ERRORE_VISTA")
        self.annuncia(
            context, TESTI["MESSAGGIO_TELECAMERA_PRINCIPALE"].format(nome=bersagli[0].name)
        )
        return {"FINISHED"}


CLASSI = (
    FORMAFACILE_OT_rinomina,
    FORMAFACILE_OT_duplica,
    FORMAFACILE_OT_elimina,
    FORMAFACILE_OT_alterna_visibilita,
    FORMAFACILE_OT_mostra_tutti,
    FORMAFACILE_OT_inquadra_oggetto,
    FORMAFACILE_OT_luce_piu,
    FORMAFACILE_OT_luce_meno,
    FORMAFACILE_OT_guarda_da_camera,
    FORMAFACILE_OT_telecamera_principale,
)
