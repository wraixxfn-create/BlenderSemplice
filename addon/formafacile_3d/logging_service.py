"""Registrazione diagnostica essenziale, senza file o contenuti personali."""

from __future__ import annotations

import logging


_NOME_LOGGER = "formafacile"


def ottieni_logger() -> logging.Logger:
    logger = logging.getLogger(_NOME_LOGGER)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("[FormaFacile] %(levelname)s: %(message)s"))
        logger.addHandler(handler)

    return logger
