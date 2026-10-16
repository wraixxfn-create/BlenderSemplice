"""Pacchetto dei servizi di scena di FormaFacile 3D."""

from __future__ import annotations

from . import libreria, primitives, stato
from .stato import CLASSI, registra_stato, rimuovi_stato

__all__ = ["CLASSI", "libreria", "primitives", "registra_stato", "rimuovi_stato", "stato"]
