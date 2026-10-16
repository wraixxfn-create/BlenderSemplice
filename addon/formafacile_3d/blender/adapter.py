"""Piccolo adattatore per la creazione di forme tramite l'API Blender."""

from __future__ import annotations

import bpy


def aggiungi_cubo_nativo(context, dimensione: float):
    """Crea un cubo con l'operatore Blender e restituisce l'oggetto attivo."""
    risultato = bpy.ops.mesh.primitive_cube_add(size=dimensione)
    if "FINISHED" not in risultato:
        raise RuntimeError("L'operazione Blender non è stata completata.")

    oggetto = context.active_object
    if oggetto is None:
        raise RuntimeError("L'oggetto creato non è disponibile.")
    return oggetto
