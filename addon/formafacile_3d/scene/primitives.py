"""Servizi delle forme primitive disponibili nella base iniziale."""

from __future__ import annotations

from ..blender import adapter
from ..localization import TESTI


DIMENSIONE_CUBO_PREDEFINITA = 2.0
RAGGIO_SFERA_PREDEFINITO = 1.0
RAGGIO_CILINDRO_PREDEFINITO = 1.0
ALTEZZA_CILINDRO_PREDEFINITA = 2.0
LATO_PIANO_PREDEFINITO = 2.0
DISTANZA_LIBERA = 2.5


def posizione_libera(context) -> tuple[float, float, float]:
    """Trova un punto libero partendo dal cursore 3D.

    Il cursore 3D resta il riferimento di Blender: se però c'è già un oggetto
    proprio lì, il nuovo oggetto viene messo di fianco invece di finirci
    dentro, che è la sorpresa più fastidiosa per chi inizia.
    """
    posizione = list(adapter.cursore_3d(context))
    occupate = set(adapter.posizioni_oggetti(context.view_layer))
    for _ in range(24):
        chiave = (round(posizione[0], 3), round(posizione[1], 3), round(posizione[2], 3))
        if chiave not in occupate:
            return (posizione[0], posizione[1], posizione[2])
        posizione[0] += DISTANZA_LIBERA
    return (posizione[0], posizione[1], posizione[2])


def _prepara(oggetto, nome_oggetto: str, nome_dati: str):
    """Assegna i nomi italiani all'oggetto e alla sua geometria."""
    oggetto.name = nome_oggetto
    if oggetto.data is not None and nome_dati:
        oggetto.data.name = nome_dati
    return oggetto


def crea_cubo(context):
    """Aggiunge un cubo alla scena e assegna nomi italiani comprensibili."""
    posizione = posizione_libera(context)
    oggetto = adapter.aggiungi_cubo_nativo(context, DIMENSIONE_CUBO_PREDEFINITA, posizione)
    return _prepara(oggetto, TESTI["NOME_CUBO"], TESTI["NOME_MESH_CUBO"])


def crea_sfera(context):
    """Aggiunge una sfera alla scena."""
    posizione = posizione_libera(context)
    oggetto = adapter.aggiungi_sfera_nativa(context, RAGGIO_SFERA_PREDEFINITO, posizione)
    return _prepara(oggetto, TESTI["NOME_SFERA"], TESTI["NOME_MESH_SFERA"])


def crea_cilindro(context):
    """Aggiunge un cilindro alla scena."""
    posizione = posizione_libera(context)
    oggetto = adapter.aggiungi_cilindro_nativo(
        context, RAGGIO_CILINDRO_PREDEFINITO, ALTEZZA_CILINDRO_PREDEFINITA, posizione
    )
    return _prepara(oggetto, TESTI["NOME_CILINDRO"], TESTI["NOME_MESH_CILINDRO"])


def crea_piano(context):
    """Aggiunge un piano piatto alla scena."""
    posizione = posizione_libera(context)
    oggetto = adapter.aggiungi_piano_nativo(context, LATO_PIANO_PREDEFINITO, posizione)
    return _prepara(oggetto, TESTI["NOME_PIANO"], TESTI["NOME_MESH_PIANO"])


def crea_luce(context):
    """Aggiunge una luce alla scena, in alto per illuminare gli oggetti."""
    posizione = adapter.cursore_3d(context)
    posizione = (posizione[0], posizione[1], posizione[2] + 4.0)
    oggetto = adapter.aggiungi_luce_nativa(context, posizione)
    return _prepara(oggetto, TESTI["NOME_LUCE"], "")
