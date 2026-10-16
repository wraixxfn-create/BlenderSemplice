"""Estensione Blender di FormaFacile 3D."""

from __future__ import annotations

import bpy

from . import configuration, operators, ui
from .localization import TESTI
from .logging_service import ottieni_logger

bl_info = {
    "name": TESTI["NOME_ESTENSIONE"],
    "author": TESTI["AUTORE_ESTENSIONE"],
    "version": (0, 1, 0),
    "blender": (4, 5, 0),
    "location": TESTI["POSIZIONE_ESTENSIONE"],
    "description": TESTI["DESCRIZIONE_ESTENSIONE"],
    "category": TESTI["CATEGORIA_PANNELLO"],
}

_CLASSI = (*operators.CLASSI, *ui.CLASSI)
_CLASSI_REGISTRATE: list[type] = []


def register() -> None:
    """Registra classi e interfaccia in modo sicuro e ripetibile."""
    logger = ottieni_logger()
    if not configuration.imposta_interfaccia_italiana(bpy):
        logger.warning(TESTI["ERRORE_LINGUA_ITALIANA"])

    try:
        for classe in _CLASSI:
            if classe in _CLASSI_REGISTRATE:
                continue
            bpy.utils.register_class(classe)
            _CLASSI_REGISTRATE.append(classe)
    except Exception:
        for classe in reversed(_CLASSI_REGISTRATE):
            try:
                bpy.utils.unregister_class(classe)
            except RuntimeError:
                pass
        _CLASSI_REGISTRATE.clear()
        logger.error(TESTI["ERRORE_REGISTRAZIONE"])
        raise

    logger.info(TESTI["LOG_COMPONENTE_REGISTRATO"])


def unregister() -> None:
    """Rimuove le classi nell'ordine inverso della registrazione."""
    for classe in reversed(_CLASSI_REGISTRATE):
        try:
            bpy.utils.unregister_class(classe)
        except RuntimeError:
            pass
    _CLASSI_REGISTRATE.clear()
    ottieni_logger().info(TESTI["LOG_COMPONENTE_DISATTIVATO"])
