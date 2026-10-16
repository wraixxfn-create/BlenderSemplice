"""Pacchetto dei comandi di FormaFacile 3D."""

from __future__ import annotations

from . import (
    aspetto,
    assets,
    guide,
    insiemi,
    modellazione,
    oggetti,
    scene,
    selezione,
    trasformazioni,
    vista,
)

CLASSI = (
    *assets.CLASSI,
    *scene.CLASSI,
    *selezione.CLASSI,
    *oggetti.CLASSI,
    *trasformazioni.CLASSI,
    *vista.CLASSI,
    *modellazione.CLASSI,
    *insiemi.CLASSI,
    *guide.CLASSI,
    *aspetto.CLASSI,
)
