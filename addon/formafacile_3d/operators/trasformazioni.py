"""Spostamenti, rotazioni e dimensioni a passi."""

from __future__ import annotations

import bpy

from .. import comandi, configuration
from ..blender import trasformazioni
from ..localization import TESTI
from ..scene.stato import stato_della_scena
from .base import OperatoreFormaFacile


def _passo(context) -> float:
    """Passo corrente, letto dallo stato della scena."""
    stato = stato_della_scena(getattr(context, "scene", None))
    if stato is None or stato.passo <= 0.0:
        return configuration.PASSO_PREDEFINITO
    return float(stato.passo)


def _voci_direzione():
    return tuple(
        (
            direzione,
            TESTI[comandi.TESTI_DIREZIONE[direzione]],
            TESTI[comandi.AIUTI_DIREZIONE[direzione]].format(
                passo=f"{configuration.PASSO_PREDEFINITO:g}".replace(".", ",")
            ),
        )
        for direzione in comandi.DIREZIONI
    )


def _voci_rotazione():
    return tuple(
        (
            verso,
            TESTI[comandi.TESTI_ROTAZIONE[verso]],
            TESTI[comandi.AIUTI_ROTAZIONE[verso]].format(
                gradi=f"{configuration.ANGOLO_PREDEFINITO_GRADI:g}".replace(".", ",")
            ),
        )
        for verso in comandi.VERSI_ROTAZIONE
    )


def _voci_dimensione():
    percentuale = int(round((configuration.FATTORE_SCALA_PREDEFINITO - 1.0) * 100))
    return tuple(
        (
            verso,
            TESTI[comandi.TESTI_DIMENSIONE[verso]],
            TESTI[comandi.AIUTI_DIMENSIONE[verso]].format(percentuale=percentuale),
        )
        for verso in comandi.VERSI_DIMENSIONE
    )


class _OperatoreTrasformazione(OperatoreFormaFacile):
    """Base per i comandi a passi che agiscono sugli oggetti scelti."""

    @classmethod
    def poll(cls, context):
        return OperatoreFormaFacile.in_modalita_oggetto(context) and bool(
            OperatoreFormaFacile.scelti(context)
        )

    def messaggio(self, context, quanti: int, nomi: list[str]) -> str:
        raise NotImplementedError


class FORMAFACILE_OT_sposta_passo(_OperatoreTrasformazione):
    """Sposta gli oggetti scelti nella direzione indicata."""

    bl_idname = comandi.ID_SPOSTA_PASSO
    bl_label = TESTI["GRUPPO_SPOSTA"]
    bl_description = TESTI["AIUTO_VERSO_DESTRA"]

    direzione: bpy.props.EnumProperty(items=_voci_direzione(), default="destra", options={"HIDDEN"})

    def messaggio(self, context, quanti: int, nomi: list[str]) -> str:
        verso = TESTI[comandi.TESTI_DIREZIONE[self.direzione]].lower()
        if quanti == 1:
            return TESTI["MESSAGGIO_MOSSO"].format(nome=nomi[0], verso=verso)
        return TESTI["MESSAGGIO_MOSSI"].format(numero=quanti, verso=verso)

    def execute(self, context):
        passo = _passo(context)
        vettore = comandi.VETTORI_DIREZIONE[self.direzione]
        spostamento = (vettore[0] * passo, vettore[1] * passo, vettore[2] * passo)
        scelti = self.scelti(context)
        nomi = [oggetto.name for oggetto in scelti]
        try:
            quanti = trasformazioni.sposta(scelti, spostamento)
        except trasformazioni.ErroreTrasformazione as errore:
            self.report({"WARNING"}, str(errore))
            return {"CANCELLED"}
        self.annuncia(context, self.messaggio(context, quanti, nomi))
        return {"FINISHED"}


class FORMAFACILE_OT_ruota_passo(_OperatoreTrasformazione):
    """Ruota gli oggetti scelti attorno all'asse verticale."""

    bl_idname = comandi.ID_RUOTA_PASSO
    bl_label = TESTI["GRUPPO_RUOTA"]
    bl_description = TESTI["AIUTO_RUOTA_DESTRA"]

    verso: bpy.props.EnumProperty(items=_voci_rotazione(), default="destra", options={"HIDDEN"})

    def messaggio(self, context, quanti: int, nomi: list[str]) -> str:
        if quanti == 1:
            return TESTI["MESSAGGIO_RUOTATO"].format(nome=nomi[0])
        return TESTI["MESSAGGIO_RUOTATI"].format(numero=quanti)

    def execute(self, context):
        gradi = configuration.ANGOLO_PREDEFINITO_GRADI * comandi.SEGNI_ROTAZIONE[self.verso]
        scelti = self.scelti(context)
        nomi = [oggetto.name for oggetto in scelti]
        try:
            quanti = trasformazioni.ruota(scelti, trasformazioni.gradi_in_radianti(gradi))
        except trasformazioni.ErroreTrasformazione as errore:
            self.report({"WARNING"}, str(errore))
            return {"CANCELLED"}
        self.annuncia(context, self.messaggio(context, quanti, nomi))
        return {"FINISHED"}


class FORMAFACILE_OT_scala_passo(_OperatoreTrasformazione):
    """Ingrandisce o rimpicciolisce gli oggetti scelti."""

    bl_idname = comandi.ID_SCALA_PASSO
    bl_label = TESTI["GRUPPO_INGRANDISCI"]
    bl_description = TESTI["AIUTO_PIU_GRANDE"]

    verso: bpy.props.EnumProperty(items=_voci_dimensione(), default="grande", options={"HIDDEN"})

    def messaggio(self, context, quanti: int, nomi: list[str]) -> str:
        if quanti == 1:
            return TESTI["MESSAGGIO_SCALATO"].format(nome=nomi[0])
        return TESTI["MESSAGGIO_SCALATI"].format(numero=quanti)

    def execute(self, context):
        fattore = configuration.FATTORE_SCALA_PREDEFINITO
        if self.verso == "piccolo":
            fattore = 1.0 / configuration.FATTORE_SCALA_PREDEFINITO
        scelti = self.scelti(context)
        nomi = [oggetto.name for oggetto in scelti]
        try:
            quanti = trasformazioni.ingrandisci(scelti, fattore)
        except trasformazioni.ErroreTrasformazione as errore:
            self.report({"WARNING"}, str(errore))
            self.annuncia(context, str(errore))
            return {"CANCELLED"}
        self.annuncia(context, self.messaggio(context, quanti, nomi))
        return {"FINISHED"}


CLASSI = (
    FORMAFACILE_OT_sposta_passo,
    FORMAFACILE_OT_ruota_passo,
    FORMAFACILE_OT_scala_passo,
)
