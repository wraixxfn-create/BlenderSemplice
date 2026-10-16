"""Stato della scena usato dall'interfaccia: modalità, ricerca, passo, grandezza, messaggio.

Lo stato vive nella scena (un gruppo di proprietà chiamato `formafacile`):
funziona con qualsiasi modo di caricamento del componente aggiuntivo e viene
salvato insieme al progetto, quindi un principiante ritrova la modalità
semplice quando riapre il proprio file.
"""

from __future__ import annotations

import time

import bpy

from .. import configuration
from ..localization import TESTI


class FORMAFACILE_PG_stato(bpy.types.PropertyGroup):
    """Proprietà salvate nella scena per l'interfaccia semplice."""

    modalita: bpy.props.EnumProperty(
        name=TESTI["ETICHETTA_MODALITA"],
        description=TESTI["AIUTO_MODALITA_SEMPLICE"],
        items=(
            (configuration.MODALITA_SEMPLICE, TESTI["MODALITA_SEMPLICE"], TESTI["AIUTO_MODALITA_SEMPLICE"]),
            (configuration.MODALITA_COMPLETA, TESTI["MODALITA_COMPLETA"], TESTI["AIUTO_MODALITA_COMPLETA"]),
        ),
        default=configuration.MODALITA_SEMPLICE,
    )
    filtro: bpy.props.StringProperty(
        name=TESTI["ETICHETTA_CERCA"],
        description=TESTI["AIUTO_CERCA"],
        default="",
    )
    passo: bpy.props.FloatProperty(
        name=TESTI["ETICHETTA_PASSO"],
        description=TESTI["AIUTO_PASSO"],
        default=configuration.PASSO_PREDEFINITO,
        min=configuration.PASSO_MINIMO,
        max=configuration.PASSO_MASSIMO,
        precision=2,
        unit="LENGTH",
    )
    grandezza_forma: bpy.props.FloatProperty(
        name=TESTI["ETICHETTA_GRANDEZZA"],
        description=TESTI["AIUTO_GRANDEZZA"],
        default=configuration.DIMENSIONE_FORMA_PREDEFINITA,
        min=configuration.DIMENSIONE_FORMA_MINIMA,
        max=configuration.DIMENSIONE_FORMA_MASSIMA,
        precision=2,
        unit="LENGTH",
    )
    messaggio: bpy.props.StringProperty(default="", options={"HIDDEN"})
    tempo_messaggio: bpy.props.FloatProperty(default=0.0, options={"HIDDEN"})


CLASSI = (FORMAFACILE_PG_stato,)


def registra_stato() -> None:
    """Collega il gruppo di proprietà alla scena."""
    bpy.types.Scene.formafacile = bpy.props.PointerProperty(type=FORMAFACILE_PG_stato)


def rimuovi_stato() -> None:
    """Stacca il gruppo di proprietà dalla scena, se presente."""
    if hasattr(bpy.types.Scene, "formafacile"):
        del bpy.types.Scene.formafacile


def stato_della_scena(scena):
    """Restituisce lo stato della scena oppure None se non è disponibile."""
    if scena is None:
        return None
    return getattr(scena, configuration.GRUPPO_STATO_SCENA, None)


def modalita_della_scena(scena) -> str:
    """Modalità corrente, con ripiego sulla modalità semplice."""
    stato = stato_della_scena(scena)
    if stato is None:
        return configuration.MODALITA_SEMPLICE
    return stato.modalita


def passo_della_scena(scena) -> float:
    """Passo dello spostamento, mai nullo."""
    stato = stato_della_scena(scena)
    if stato is None:
        return configuration.PASSO_PREDEFINITO
    passo = float(stato.passo)
    if passo <= 0.0:
        return configuration.PASSO_PREDEFINITO
    return passo


def grandezza_della_scena(scena) -> float:
    """Grandezza delle nuove forme, in metri e sempre dentro i limiti."""
    stato = stato_della_scena(scena)
    if stato is None:
        return configuration.DIMENSIONE_FORMA_PREDEFINITA
    grandezza = float(stato.grandezza_forma)
    if grandezza <= 0.0:
        return configuration.DIMENSIONE_FORMA_PREDEFINITA
    return min(
        max(grandezza, configuration.DIMENSIONE_FORMA_MINIMA),
        configuration.DIMENSIONE_FORMA_MASSIMA,
    )


def messaggio_della_scena(scena, adesso: float | None = None) -> tuple[str, bool]:
    """Messaggio breve e se è ancora attuale."""
    stato = stato_della_scena(scena)
    if stato is None or not stato.messaggio:
        return "", False
    adesso = time.monotonic() if adesso is None else adesso
    return stato.messaggio, (adesso - float(stato.tempo_messaggio)) < configuration.DURATA_MESSAGGIO
