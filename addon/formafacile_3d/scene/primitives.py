"""Servizi delle forme primitive disponibili nella base iniziale."""

from __future__ import annotations

from ..blender.adapter import aggiungi_cubo_nativo
from ..localization import TESTI


DIMENSIONE_CUBO_PREDEFINITA = 2.0


def crea_cubo(context):
    """Aggiunge un cubo alla scena e assegna nomi italiani comprensibili."""
    oggetto = aggiungi_cubo_nativo(context, DIMENSIONE_CUBO_PREDEFINITA)
    oggetto.name = TESTI["NOME_CUBO"]
    if oggetto.data is not None:
        oggetto.data.name = TESTI["NOME_MESH_CUBO"]
    return oggetto
