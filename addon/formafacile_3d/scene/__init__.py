"""Pacchetto dei servizi di scena di FormaFacile 3D."""

from __future__ import annotations

from . import primitives, stato
from .stato import CLASSI, registra_stato, rimuovi_stato

__all__ = ["CLASSI", "primitives", "registra_stato", "rimuovi_stato", "stato"]
