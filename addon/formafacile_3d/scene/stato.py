"""Stato della scena usato dall'interfaccia: modalità, ricerca, passo, grandezza, messaggio.

Lo stato vive nella scena (un gruppo di proprietà chiamato `formafacile`):
funziona con qualsiasi modo di caricamento del componente aggiuntivo e viene
salvato insieme al progetto, quindi un principiante ritrova la modalità
semplice quando riapre il proprio file.
"""

from __future__ import annotations

import time

import bpy

from .. import comandi, configuration
from ..localization import TESTI


def _voci_asse_allinea():
    """Voci dell'asse di allineamento, con i testi italiani.

    Le voci si costruiscono in una funzione, non dentro l'annotazione della
    proprietà: Blender rilegge le annotazioni quando registra la classe e una
    comprensione scritta lì dentro fallirebbe in quel momento.
    """
    return tuple(
        (asse, TESTI[comandi.TESTI_ASSE[asse]], TESTI[comandi.AIUTI_ASSE[asse]])
        for asse in comandi.ASSI
    )


def _voci_bordo_allinea():
    """Voci del bordo di allineamento: inizio, centro o fine."""
    return tuple(
        (modo, TESTI[comandi.TESTI_ALLINEAMENTO[modo]], TESTI["AIUTO_BORDO_ALLINEA"])
        for modo in comandi.MODI_ALLINEAMENTO
    )


def _voci_riferimento_allinea():
    """Voci del riferimento: il bordo della forma o il suo punto di riferimento."""
    return tuple(
        (
            chiave,
            TESTI[comandi.TESTI_RIFERIMENTO[chiave]],
            TESTI["AIUTO_RIFERIMENTO_ALLINEA"],
        )
        for chiave in comandi.RIFERIMENTI_ALLINEAMENTO
    )


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
    # Impostazioni dell'allineamento: si scelgono una volta e valgono per ogni
    # pressione di Allinea e Spazia, come la modalità di lavoro.
    asse_allinea: bpy.props.EnumProperty(
        name=TESTI["ETICHETTA_ASSE_ALLINEA"],
        description=TESTI["AIUTO_ASSE_ALLINEA"],
        items=_voci_asse_allinea(),
        default=configuration.ALLINEA_ASSE_PREDEFINITO,
    )
    bordo_allinea: bpy.props.EnumProperty(
        name=TESTI["ETICHETTA_BORDO_ALLINEA"],
        description=TESTI["AIUTO_BORDO_ALLINEA"],
        items=_voci_bordo_allinea(),
        default=configuration.ALLINEA_BORDO_PREDEFINITO,
    )
    riferimento_allinea: bpy.props.EnumProperty(
        name=TESTI["ETICHETTA_RIFERIMENTO_ALLINEA"],
        description=TESTI["AIUTO_RIFERIMENTO_ALLINEA"],
        items=_voci_riferimento_allinea(),
        default=configuration.ALLINEA_RIFERIMENTO_PREDEFINITO,
    )
    # Guida passo passo in corso: la chiave della guida e il passo mostrato.
    guida: bpy.props.StringProperty(default="", options={"HIDDEN"})
    passo_guida: bpy.props.IntProperty(default=0, min=0, options={"HIDDEN"})
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


def allineamento_della_scena(scena) -> tuple[str, str, bool]:
    """Asse, bordo e riferimento scelti per Allinea e Spazia, con ripieghi sicuri."""
    stato = stato_della_scena(scena)
    if stato is None:
        return (
            configuration.ALLINEA_ASSE_PREDEFINITO,
            configuration.ALLINEA_BORDO_PREDEFINITO,
            configuration.ALLINEA_RIFERIMENTO_PREDEFINITO == comandi.RIFERIMENTO_PUNTO,
        )
    asse = str(getattr(stato, "asse_allinea", configuration.ALLINEA_ASSE_PREDEFINITO)).lower()
    if asse not in comandi.ASSI:
        asse = configuration.ALLINEA_ASSE_PREDEFINITO
    bordo = str(getattr(stato, "bordo_allinea", configuration.ALLINEA_BORDO_PREDEFINITO))
    if bordo not in comandi.MODI_ALLINEAMENTO:
        bordo = configuration.ALLINEA_BORDO_PREDEFINITO
    riferimento = str(
        getattr(stato, "riferimento_allinea", configuration.ALLINEA_RIFERIMENTO_PREDEFINITO)
    )
    return asse, bordo, riferimento == comandi.RIFERIMENTO_PUNTO


def guida_della_scena(scena) -> tuple[str, int]:
    """Chiave della guida in corso e passo mostrato, anche senza stato."""
    stato = stato_della_scena(scena)
    if stato is None:
        return "", 0
    return str(getattr(stato, "guida", "")), int(getattr(stato, "passo_guida", 0))
