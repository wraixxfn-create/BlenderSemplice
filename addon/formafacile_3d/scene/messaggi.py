"""Messaggi di stato brevi in italiano.

Un messaggio viene mostrato per pochi secondi nel pannello FormaFacile e, se
possibile, anche nella barra di stato di Blender. Il testo resta semplice e
descrive che cosa è appena successo.
"""

from __future__ import annotations

import time

import bpy

from .. import configuration
from ..logging_service import ottieni_logger
from .stato import stato_della_scena


def messaggio_attuale(testo: str, tempo: float, adesso: float | None = None) -> bool:
    """Indica se il messaggio è ancora da mostrare (funzione pura, usata dai test)."""
    if not testo:
        return False
    adesso = time.monotonic() if adesso is None else adesso
    return (adesso - tempo) < configuration.DURATA_MESSAGGIO


def annuncia(context, testo: str) -> None:
    """Registra un messaggio breve e chiede a Blender di ridisegnare i pannelli."""
    scena = getattr(context, "scene", None)
    stato = stato_della_scena(scena)
    if stato is not None:
        stato.messaggio = testo
        stato.tempo_messaggio = time.monotonic()
    _scrivi_nella_barra_di_stato(context, testo)
    _aggiorna_interfaccia(context)


def _scrivi_nella_barra_di_stato(context, testo: str) -> None:
    """Scrive il messaggio nella barra di stato della disposizione corrente."""
    disposizione = getattr(context, "workspace", None)
    scrivi = getattr(disposizione, "status_text_set", None)
    if scrivi is None:
        return
    try:
        scrivi(testo)
    except (AttributeError, ReferenceError, RuntimeError, TypeError):
        ottieni_logger().debug("Barra di stato non disponibile.")


def _aggiorna_interfaccia(context) -> None:
    """Segnala a Blender che i pannelli devono essere ridisegnati."""
    segnala = getattr(context, "window_manager", None)
    if segnala is None:
        return
    try:
        for finestra in bpy.data.window_managers:
            for schermo in getattr(finestra, "windows", ()) or ():
                if schermo.screen is not None:
                    schermo.screen.tag_redraw()
    except (AttributeError, ReferenceError, RuntimeError):
        return
