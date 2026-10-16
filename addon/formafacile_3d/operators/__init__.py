"""Pacchetto dei comandi di FormaFacile 3D."""

from __future__ import annotations

from . import oggetti, scene, selezione, trasformazioni, vista

CLASSI = (
    *scene.CLASSI,
    *selezione.CLASSI,
    *oggetti.CLASSI,
    *trasformazioni.CLASSI,
    *vista.CLASSI,
)
