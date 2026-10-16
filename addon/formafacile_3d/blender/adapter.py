"""Piccolo adattatore per la creazione di forme tramite l'API Blender.

Tutte le chiamate native stanno qui: i servizi di scena e l'interfaccia
restano leggibili e il comportamento è verificabile in un solo punto.
"""

from __future__ import annotations

import math

import bpy

# Un quarto di giro attorno all'asse X: rimette in piedi una scritta creata da
# Blender, che altrimenti nascerebbe distesa sul piano di lavoro.
ANGOLO_TESTO_IN_PIEDI = math.pi / 2.0


def _oggetto_attivo(context):
    """Restituisce l'oggetto appena creato da un operatore nativo."""
    oggetto = context.active_object or context.view_layer.objects.active
    if oggetto is None:
        raise RuntimeError("L'oggetto creato non è disponibile.")
    return oggetto


def _esegui(operatore, **parametri):
    """Esegue un operatore nativo e controlla l'esito."""
    risultato = operatore(**parametri)
    if "FINISHED" not in risultato:
        raise RuntimeError("L'operazione Blender non è stata completata.")


def aggiungi_cubo_nativo(context, dimensione: float, posizione=None):
    """Crea un cubo con l'operatore Blender e restituisce l'oggetto attivo."""
    parametri = {"size": dimensione}
    if posizione is not None:
        parametri["location"] = tuple(posizione)
    _esegui(bpy.ops.mesh.primitive_cube_add, **parametri)
    return _oggetto_attivo(context)


def aggiungi_sfera_nativa(context, raggio: float, posizione=None):
    """Crea una sfera con l'operatore Blender."""
    parametri = {"radius": raggio}
    if posizione is not None:
        parametri["location"] = tuple(posizione)
    _esegui(bpy.ops.mesh.primitive_uv_sphere_add, **parametri)
    return _oggetto_attivo(context)


def aggiungi_cilindro_nativo(context, raggio: float, altezza: float, posizione=None):
    """Crea un cilindro con l'operatore Blender."""
    parametri = {"radius": raggio, "depth": altezza}
    if posizione is not None:
        parametri["location"] = tuple(posizione)
    _esegui(bpy.ops.mesh.primitive_cylinder_add, **parametri)
    return _oggetto_attivo(context)


def aggiungi_piano_nativo(context, lato: float, posizione=None):
    """Crea un piano con l'operatore Blender."""
    parametri = {"size": lato}
    if posizione is not None:
        parametri["location"] = tuple(posizione)
    _esegui(bpy.ops.mesh.primitive_plane_add, **parametri)
    return _oggetto_attivo(context)


def aggiungi_cono_nativo(context, raggio: float, altezza: float, posizione=None):
    """Crea un cono con l'operatore Blender (base piena, punta in alto)."""
    parametri = {"radius1": raggio, "radius2": 0.0, "depth": altezza}
    if posizione is not None:
        parametri["location"] = tuple(posizione)
    _esegui(bpy.ops.mesh.primitive_cone_add, **parametri)
    return _oggetto_attivo(context)


def aggiungi_toro_nativo(
    context, raggio_maggiore: float, raggio_minore: float, posizione=None
):
    """Crea una ciambella con l'operatore Blender."""
    parametri = {"major_radius": raggio_maggiore, "minor_radius": raggio_minore}
    if posizione is not None:
        parametri["location"] = tuple(posizione)
    _esegui(bpy.ops.mesh.primitive_torus_add, **parametri)
    return _oggetto_attivo(context)


def aggiungi_testo_nativo(context, altezza: float, posizione=None):
    """Crea una scritta con l'operatore Blender, già in piedi.

    Blender crea il testo disteso sul piano; qui viene ruotato di un quarto di
    giro attorno all'asse X, così la scritta sta in piedi e si legge guardando
    la scena dalla vista iniziale. È una rotazione normale, annullabile.
    """
    parametri = {"radius": altezza}
    if posizione is not None:
        parametri["location"] = tuple(posizione)
    _esegui(bpy.ops.object.text_add, **parametri)
    oggetto = _oggetto_attivo(context)
    if str(getattr(oggetto, "rotation_mode", "XYZ")) == "XYZ":
        oggetto.rotation_euler = (ANGOLO_TESTO_IN_PIEDI, 0.0, 0.0)
    return oggetto


def aggiungi_luce_nativa(context, posizione=None):
    """Crea una luce puntiforme con l'operatore Blender."""
    parametri: dict[str, object] = {"type": "POINT"}
    if posizione is not None:
        parametri["location"] = tuple(posizione)
    _esegui(bpy.ops.object.light_add, **parametri)
    return _oggetto_attivo(context)


def cursore_3d(context):
    """Posizione del cursore 3D della scena, se disponibile."""
    scena = context.scene
    cursore = getattr(scena, "cursor", None)
    if cursore is None:
        return (0.0, 0.0, 0.0)
    posizione = cursore.location
    return (float(posizione[0]), float(posizione[1]), float(posizione[2]))


def posizioni_oggetti(view_layer):
    """Posizioni degli oggetti della scena, usate per trovare un posto libero."""
    posizioni = []
    for oggetto in view_layer.objects:
        posizione = oggetto.location
        posizioni.append((round(float(posizione[0]), 3), round(float(posizione[1]), 3), round(float(posizione[2]), 3)))
    return tuple(posizioni)
