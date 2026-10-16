"""Servizi delle forme primitive disponibili nella base iniziale.

Sono presenti solo le forme che l'estensione sa creare in modo affidabile sulla
versione supportata di Blender: ogni creatore richiama un operatore nativo di
Blender, quindi la geometria è quella ufficiale e il risultato è annullabile
con `Ctrl+Z`. Nessuna forma è disegnata a mano e nessuna forma nuova entra
nell'elenco senza una prova automatica che la crei davvero.

La grandezza delle nuove forme si legge dallo stato della scena: un solo campo
nell'interfaccia (`Grandezza`) decide il lato più lungo di tutte le forme, così
chi inizia non deve imparare un parametro diverso per ognuna.
"""

from __future__ import annotations

from .. import configuration
from ..blender import adapter
from ..localization import TESTI
from .stato import grandezza_della_scena

DIMENSIONE_CUBO_PREDEFINITA = 2.0
RAGGIO_SFERA_PREDEFINITO = 1.0
RAGGIO_CILINDRO_PREDEFINITO = 1.0
ALTEZZA_CILINDRO_PREDEFINITA = 2.0
LATO_PIANO_PREDEFINITO = 2.0
DISTANZA_LIBERA = 2.5

# Rapporti fra la grandezza scelta e i parametri di ogni forma. La somma dei
# due raggi della ciambella è mezza grandezza, quindi il diametro esterno è
# esattamente la grandezza richiesta.
RAPPORTO_RAGGIO = 0.5
RAPPORTO_TORO_MAGGIORE = 0.4
RAPPORTO_TORO_MINORE = 0.1


def grandezza_delle_nuove_forme(context) -> float:
    """Grandezza in metri delle forme create adesso, letta dalla scena."""
    return grandezza_della_scena(getattr(context, "scene", None))


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
    grandezza = grandezza_delle_nuove_forme(context)
    posizione = posizione_libera(context)
    oggetto = adapter.aggiungi_cubo_nativo(context, grandezza, posizione)
    return _prepara(oggetto, TESTI["NOME_CUBO"], TESTI["NOME_MESH_CUBO"])


def crea_sfera(context):
    """Aggiunge una sfera alla scena."""
    grandezza = grandezza_delle_nuove_forme(context)
    posizione = posizione_libera(context)
    oggetto = adapter.aggiungi_sfera_nativa(context, grandezza * RAPPORTO_RAGGIO, posizione)
    return _prepara(oggetto, TESTI["NOME_SFERA"], TESTI["NOME_MESH_SFERA"])


def crea_cilindro(context):
    """Aggiunge un cilindro alla scena."""
    grandezza = grandezza_delle_nuove_forme(context)
    posizione = posizione_libera(context)
    oggetto = adapter.aggiungi_cilindro_nativo(
        context, grandezza * RAPPORTO_RAGGIO, grandezza, posizione
    )
    return _prepara(oggetto, TESTI["NOME_CILINDRO"], TESTI["NOME_MESH_CILINDRO"])


def crea_cono(context):
    """Aggiunge un cono alla scena, con la punta in alto."""
    grandezza = grandezza_delle_nuove_forme(context)
    posizione = posizione_libera(context)
    oggetto = adapter.aggiungi_cono_nativo(
        context, grandezza * RAPPORTO_RAGGIO, grandezza, posizione
    )
    return _prepara(oggetto, TESTI["NOME_CONO"], TESTI["NOME_MESH_CONO"])


def crea_piano(context):
    """Aggiunge un piano piatto alla scena, già disteso come un pavimento."""
    grandezza = grandezza_delle_nuove_forme(context)
    posizione = posizione_libera(context)
    oggetto = adapter.aggiungi_piano_nativo(context, grandezza, posizione)
    return _prepara(oggetto, TESTI["NOME_PIANO"], TESTI["NOME_MESH_PIANO"])


def crea_toro(context):
    """Aggiunge una ciambella alla scena."""
    grandezza = grandezza_delle_nuove_forme(context)
    posizione = posizione_libera(context)
    oggetto = adapter.aggiungi_toro_nativo(
        context,
        grandezza * RAPPORTO_TORO_MAGGIORE,
        grandezza * RAPPORTO_TORO_MINORE,
        posizione,
    )
    return _prepara(oggetto, TESTI["NOME_TORO"], TESTI["NOME_MESH_TORO"])


def crea_testo(context):
    """Aggiunge una scritta in piedi, con un testo di esempio da sostituire."""
    grandezza = grandezza_delle_nuove_forme(context)
    posizione = posizione_libera(context)
    oggetto = adapter.aggiungi_testo_nativo(
        context, grandezza * configuration.FATTORE_ALTEZZA_TESTO, posizione
    )
    if getattr(oggetto, "data", None) is not None:
        oggetto.data.body = TESTI["TESTO_INIZIALE"]
    return _prepara(oggetto, TESTI["NOME_TESTO"], TESTI["NOME_DATI_TESTO"])


def crea_luce(context):
    """Aggiunge una luce alla scena, in alto per illuminare gli oggetti."""
    posizione = adapter.cursore_3d(context)
    posizione = (posizione[0], posizione[1], posizione[2] + configuration.ALTEZZA_LUCE)
    oggetto = adapter.aggiungi_luce_nativa(context, posizione)
    return _prepara(oggetto, TESTI["NOME_LUCE"], "")
