"""Estensione Blender di FormaFacile 3D."""

from __future__ import annotations

import bpy

from . import configuration, operators, scene, ui
from .blender import vista
from .localization import TESTI
from .logging_service import ottieni_logger

bl_info = {
    "name": TESTI["NOME_ESTENSIONE"],
    "author": TESTI["AUTORE_ESTENSIONE"],
    "version": (0, 3, 0),
    "blender": (4, 5, 0),
    "location": TESTI["POSIZIONE_ESTENSIONE"],
    "description": TESTI["DESCRIZIONE_ESTENSIONE"],
    "category": TESTI["CATEGORIA_PANNELLO"],
}

_CLASSI = (*scene.CLASSI, *operators.CLASSI, *ui.CLASSI)
_CLASSI_REGISTRATE: list[type] = []


def register() -> None:
    """Registra classi, stato della scena e vista iniziale in modo ripetibile."""
    logger = ottieni_logger()
    if not configuration.imposta_interfaccia_italiana(bpy):
        logger.warning(TESTI["ERRORE_LINGUA_ITALIANA"])

    try:
        for classe in _CLASSI:
            if classe in _CLASSI_REGISTRATE:
                continue
            bpy.utils.register_class(classe)
            _CLASSI_REGISTRATE.append(classe)
        scene.registra_stato()
    except Exception:
        _annulla_registrazione()
        logger.error(TESTI["ERRORE_REGISTRAZIONE"])
        raise

    vista.registra_viste_iniziali()
    logger.info(TESTI["LOG_COMPONENTE_REGISTRATO"])


def _annulla_registrazione() -> None:
    """Rimuove le classi registrate, senza interrompere la disattivazione."""
    scene.rimuovi_stato()
    for classe in reversed(_CLASSI_REGISTRATE):
        try:
            bpy.utils.unregister_class(classe)
        except RuntimeError:
            pass
    _CLASSI_REGISTRATE.clear()


def unregister() -> None:
    """Rimuove classi e stato della scena nell'ordine inverso."""
    _annulla_registrazione()
    ottieni_logger().info(TESTI["LOG_COMPONENTE_DISATTIVATO"])
