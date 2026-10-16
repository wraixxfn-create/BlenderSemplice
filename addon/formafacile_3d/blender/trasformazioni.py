"""Spostamenti, rotazioni e dimensioni applicati a passi.

Le formule sono volutamente semplici e verificabili:

* spostare aggiunge un vettore alla posizione dell'oggetto;
* ruotare moltiplica a sinistra la rotazione attorno all'asse verticale, così
  l'oggetto gira sempre rispetto alla scena e non rispetto a se stesso;
* ingrandire moltiplica la dimensione per un fattore.

Le tre rotazioni di Blender (angoli di Eulero, quaternioni e asse-angolo)
sono gestite tutte, senza cambiare la scelta dell'utente.
"""

from __future__ import annotations

import math

import mathutils

from .. import configuration
from ..localization import TESTI


class ErroreTrasformazione(RuntimeError):
    """Errore gestibile di una trasformazione a passi."""


def _scelti(oggetti) -> list:
    elenco = [oggetto for oggetto in oggetti if oggetto is not None]
    if not elenco:
        raise ErroreTrasformazione(TESTI["ERRORE_TRASFORMAZIONE_NESSUNA_SCELTA"])
    return elenco


def sposta(oggetti, spostamento: tuple[float, float, float]) -> int:
    """Sposta gli oggetti indicati lungo gli assi della scena."""
    vettore = mathutils.Vector(spostamento)
    elenco = _scelti(oggetti)
    for oggetto in elenco:
        oggetto.location = oggetto.location + vettore
    return len(elenco)


def ruota(oggetti, radianti: float) -> int:
    """Ruota gli oggetti indicati attorno all'asse verticale della scena."""
    elenco = _scelti(oggetti)
    for oggetto in elenco:
        _ruota_uno(oggetto, radianti)
    return len(elenco)


def _ruota_uno(oggetto, radianti: float) -> None:
    modo = getattr(oggetto, "rotation_mode", "XYZ")
    if modo == "QUATERNION":
        rotazione = mathutils.Quaternion((0.0, 0.0, 1.0), radianti)
        oggetto.rotation_quaternion = rotazione @ oggetto.rotation_quaternion
        return
    if modo == "AXIS_ANGLE":
        angolo, asse_x, asse_y, asse_z = oggetto.rotation_axis_angle
        corrente = mathutils.Matrix.Rotation(
            angolo, 4, mathutils.Vector((asse_x, asse_y, asse_z)).normalized()
        )
        nuova = mathutils.Matrix.Rotation(radianti, 4, "Z") @ corrente
        asse, angolo_nuovo = nuova.to_quaternion().to_axis_angle()
        oggetto.rotation_axis_angle = (angolo_nuovo, asse.x, asse.y, asse.z)
        return
    eulero = oggetto.rotation_euler
    oggetto.rotation_euler = (eulero.x, eulero.y, eulero.z + radianti)


def ingrandisci(oggetti, fattore: float) -> int:
    """Moltiplica la dimensione degli oggetti indicati."""
    elenco = _scelti(oggetti)
    # Prima si controlla tutto, poi si applica: niente oggetti a metà.
    nuove = []
    for oggetto in elenco:
        scala = oggetto.scale
        nuova = (scala[0] * fattore, scala[1] * fattore, scala[2] * fattore)
        if max(abs(valore) for valore in nuova) < configuration.SCALA_MINIMA:
            raise ErroreTrasformazione(TESTI["MESSAGGIO_DIMENSIONE_MINIMA"])
        nuove.append(nuova)
    for oggetto, nuova in zip(elenco, nuove):
        oggetto.scale = nuova
    return len(elenco)


def cambia_potenza_luce(oggetto, fattore: float, minimo: float) -> float:
    """Cambia la potenza di una luce, mai sotto il minimo indicato."""
    dati = getattr(oggetto, "data", None)
    if dati is None or not hasattr(dati, "energy"):
        raise ErroreTrasformazione(TESTI["ERRORE_TRASFORMAZIONE"])
    potenza = float(dati.energy) * fattore
    dati.energy = max(potenza, minimo)
    return float(dati.energy)


def gradi_in_radianti(gradi: float) -> float:
    """Converte i gradi in radianti, usata dagli operatori."""
    return math.radians(gradi)
