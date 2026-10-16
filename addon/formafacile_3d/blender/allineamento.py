"""Allineare e spaziare più oggetti scelti.

Le posizioni si calcolano dai riquadri veri degli oggetti nella scena (quelli
che si vedono, modificatori compresi) e si applicano rispettando i blocchi di
Blender: un asse bloccato non viene toccato, e il comando lo dice.

Non si usa `bpy.ops.object.align`: quella funzione lavora sul contesto della
Vista 3D e cambia le trasformazioni degli oggetti in modo poco leggibile per
chi inizia. Qui ogni oggetto riceve la posizione calcolata, come per i comandi
a passi già presenti.
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import configuration
from ..localization import TESTI
from ..scene import misure
from ..scene import regole_modellazione as regole
from . import modificatori


class ErroreAllineamento(RuntimeError):
    """Errore gestibile di allineamento: messaggio già in italiano."""


@dataclass(frozen=True)
class EsitoAllineamento:
    """Esito di allineamento o spaziatura, per i messaggi in italiano."""

    applicati: int = 0
    bloccati: int = 0
    invariati: int = 0
    spazio: float = 0.0


def _posizione(oggetto) -> list[float]:
    letta = oggetto.location
    return [float(letta[0]), float(letta[1]), float(letta[2])]


def _blocchi(oggetto) -> tuple[bool, bool, bool]:
    valori = getattr(oggetto, "lock_location", None)
    if valori is None:
        return (False, False, False)
    try:
        return (bool(valori[0]), bool(valori[1]), bool(valori[2]))
    except (IndexError, TypeError):
        return (False, False, False)


def riquadri(context, oggetti, *, per_punto: bool = False):
    """Riquadri degli oggetti scelti, in coordinate di scena.

    Con `per_punto` conta il punto di riferimento dell'oggetto invece del suo
    bordo: è la scelta della modalità completa, utile quando la forma non ha
    un'estensione propria (una luce, una telecamera).
    """
    misure_oggetti = []
    for oggetto in oggetti:
        if per_punto:
            punto = _posizione(oggetto)
            misure_oggetti.append((tuple(punto), tuple(punto)))
            continue
        forma = modificatori.forma_valutata(context, oggetto)
        if forma.vertici == 0 and forma.facce == 0:
            punto = _posizione(oggetto)
            misure_oggetti.append((tuple(punto), tuple(punto)))
            continue
        misure_oggetti.append((forma.minimo, forma.massimo))
    return misure_oggetti


def _sposta_asse(oggetto, asse: str, quanto: float) -> str:
    """Sposta l'oggetto su un asse rispettando i blocchi: "applicato", "bloccato", "invariato"."""
    indice = regole.INDICE_ASSE[asse]
    delta = [0.0, 0.0, 0.0]
    delta[indice] = quanto
    consentito = misure.delta_consentito(delta, _blocchi(oggetto))
    if misure.spostamento_valutabile(delta) and not misure.spostamento_valutabile(consentito):
        return "bloccato"
    if not misure.spostamento_valutabile(consentito):
        return "invariato"
    posizione = _posizione(oggetto)
    for posizione_asse in range(3):
        posizione[posizione_asse] += consentito[posizione_asse]
    oggetto.location = (posizione[0], posizione[1], posizione[2])
    return "applicato"


def allinea(
    context,
    oggetti,
    asse: str,
    modo: str,
    *,
    per_punto: bool = False,
) -> EsitoAllineamento:
    """Allinea gli oggetti scelti sul bordo (o sul centro) della loro unione."""
    indice = regole.INDICE_ASSE.get(str(asse).lower())
    if indice is None:
        raise ErroreAllineamento(TESTI["ERRORE_ALLINEA"])
    elenco = [oggetto for oggetto in oggetti if oggetto is not None]
    if len(elenco) < configuration.ALLINEA_OGGETTI_MINIMI:
        raise ErroreAllineamento(TESTI["ERRORE_ALLINEA_POCHI"])

    modificatori.aggiorna(context)
    riquadri_oggetti = riquadri(context, elenco, per_punto=per_punto)
    riferimento_minimo = min(riquadro[0][indice] for riquadro in riquadri_oggetti)
    riferimento_massimo = max(riquadro[1][indice] for riquadro in riquadri_oggetti)

    applicati = bloccati = invariati = 0
    for oggetto, (minimo, massimo) in zip(elenco, riquadri_oggetti):
        quanto = regole.spostamento_allineamento(
            minimo[indice], massimo[indice], riferimento_minimo, riferimento_massimo, modo
        )
        risultato = _sposta_asse(oggetto, asse, quanto)
        if risultato == "applicato":
            applicati += 1
        elif risultato == "bloccato":
            bloccati += 1
        else:
            invariati += 1
    if applicati == 0 and invariati == 0:
        raise ErroreAllineamento(TESTI["ERRORE_TRASFORMAZIONE_BLOCCATA"])
    return EsitoAllineamento(applicati, bloccati, invariati)


def spazia(
    context,
    oggetti,
    asse: str,
    *,
    per_punto: bool = False,
) -> EsitoAllineamento:
    """Mette gli oggetti in fila alla stessa distanza, fra il primo e l'ultimo."""
    indice = regole.INDICE_ASSE.get(str(asse).lower())
    if indice is None:
        raise ErroreAllineamento(TESTI["ERRORE_ALLINEA"])
    elenco = [oggetto for oggetto in oggetti if oggetto is not None]
    if len(elenco) < configuration.SPAZIA_OGGETTI_MINIMI:
        raise ErroreAllineamento(TESTI["ERRORE_SPAZIA_POCHI"])

    modificatori.aggiorna(context)
    riquadri_oggetti = riquadri(context, elenco, per_punto=per_punto)
    ordine = sorted(
        range(len(elenco)),
        key=lambda posizione: (riquadri_oggetti[posizione][0][indice] + riquadri_oggetti[posizione][1][indice]) / 2.0,
    )
    intervalli = [(riquadri_oggetti[posizione][0][indice], riquadri_oggetti[posizione][1][indice]) for posizione in ordine]
    nuove_posizioni = regole.posizioni_spaziate(intervalli)
    spazio = regole.spazio_fra_oggetti(intervalli)

    applicati = bloccati = invariati = 0
    for posizione, nuova in zip(ordine, nuove_posizioni):
        oggetto = elenco[posizione]
        quanto = nuova - riquadri_oggetti[posizione][0][indice]
        risultato = _sposta_asse(oggetto, asse, quanto)
        if risultato == "applicato":
            applicati += 1
        elif risultato == "bloccato":
            bloccati += 1
        else:
            invariati += 1
    if applicati == 0 and invariati == 0:
        raise ErroreAllineamento(TESTI["ERRORE_TRASFORMAZIONE_BLOCCATA"])
    return EsitoAllineamento(applicati, bloccati, invariati, spazio)
