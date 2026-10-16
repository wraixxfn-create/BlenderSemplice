"""Spostamenti, rotazioni e dimensioni applicati agli oggetti scelti.

Le formule sono volutamente semplici e verificabili:

* spostare aggiunge un vettore alla posizione dell'oggetto;
* ruotare moltiplica a sinistra la rotazione attorno all'asse verticale, così
  l'oggetto gira sempre rispetto alla scena e non rispetto a se stesso;
* ingrandire moltiplica la dimensione per un fattore.

Le tre rotazioni di Blender (angoli di Eulero, quaternioni e asse-angolo)
sono gestite tutte, senza cambiare la scelta dell'utente.

Due regole valgono per ogni funzione qui dentro:

* **si toccano solo gli oggetti ricevuti**, che i comandi prendono dalla
  scelta: un oggetto non scelto non viene mai modificato;
* **si rispettano i blocchi di Blender** (`lock_location`, `lock_rotation`,
  `lock_scale`): un asse bloccato resta dov'è, e se l'oggetto è bloccato su
  tutti gli assi entra nel conteggio dei "bloccati" invece di essere forzato.

Niente viene "applicato" in modo irreversibile: non si usano
`transform_apply`, né l'applicazione di modificatori, né conversioni. Ogni
cambio resta annullabile con `Ctrl+Z`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import mathutils

from .. import configuration
from ..localization import TESTI
from ..scene import misure


class ErroreTrasformazione(RuntimeError):
    """Errore gestibile di una trasformazione: il messaggio è già in italiano."""


@dataclass(frozen=True)
class EsitoTrasformazione:
    """Esito di una trasformazione, usato per i messaggi in italiano.

    `invariati` conta gli oggetti che erano già nella posizione richiesta: non
    sono un errore, quindi non devono finire nel conteggio dei bloccati.
    """

    applicati: int = 0
    bloccati: int = 0
    invariati: int = 0
    # Oggetti senza una forma propria (luci, telecamere, segnaposti): per
    # "Appoggia sul piano" si usa il loro punto di riferimento.
    senza_forma: int = 0


def _scelti(oggetti) -> list:
    elenco = [oggetto for oggetto in oggetti if oggetto is not None]
    if not elenco:
        raise ErroreTrasformazione(TESTI["ERRORE_TRASFORMAZIONE_NESSUNA_SCELTA"])
    return elenco


def _blocchi(oggetto, nome: str) -> tuple[bool, bool, bool]:
    """Terna di blocchi di un oggetto, tollerando attributi assenti."""
    valori = getattr(oggetto, nome, None)
    if valori is None:
        return (False, False, False)
    try:
        letti = [bool(valori[indice]) for indice in range(3)]
    except (IndexError, TypeError):
        return (False, False, False)
    return (letti[0], letti[1], letti[2])


def _posizione(oggetto) -> tuple[float, float, float]:
    letta = oggetto.location
    return (float(letta[0]), float(letta[1]), float(letta[2]))


def _spostamento_libero(oggetto, delta) -> tuple[float, float, float]:
    return misure.delta_consentito(delta, _blocchi(oggetto, "lock_location"))


def _rotazione_libera(oggetto) -> bool:
    """Indica se l'oggetto si può ruotare attorno all'asse verticale."""
    blocchi = _blocchi(oggetto, "lock_rotation")
    return not blocchi[2]


# ------------------------------------------------------------------- spostare


def _classifica(delta, effettuabile) -> str:
    """Dice che cosa fare di un oggetto: applicare, segnalare o lasciare stare."""
    if misure.spostamento_valutabile(effettuabile):
        return "applica"
    return "bloccato" if misure.spostamento_valutabile(delta) else "invariato"


def sposta(oggetti, spostamento: tuple[float, float, float]) -> EsitoTrasformazione:
    """Sposta gli oggetti indicati lungo gli assi della scena."""
    elenco = _scelti(oggetti)
    delta = tuple(float(valore) for valore in spostamento)
    applicati = bloccati = invariati = 0
    for oggetto in elenco:
        effettuabile = _spostamento_libero(oggetto, delta)
        esito = _classifica(delta, effettuabile)
        if esito == "bloccato":
            bloccati += 1
            continue
        if esito == "invariato":
            invariati += 1
            continue
        attuale = _posizione(oggetto)
        oggetto.location = (
            attuale[0] + effettuabile[0],
            attuale[1] + effettuabile[1],
            attuale[2] + effettuabile[2],
        )
        applicati += 1
    if not applicati and not invariati:
        raise ErroreTrasformazione(TESTI["ERRORE_TRASFORMAZIONE_BLOCCATA"])
    return EsitoTrasformazione(applicati, bloccati, invariati)


def centra(oggetti) -> EsitoTrasformazione:
    """Porta gli oggetti indicati al centro della scena, dove possono farlo."""
    elenco = _scelti(oggetti)
    origine = (0.0, 0.0, 0.0)
    applicati = bloccati = invariati = 0
    for oggetto in elenco:
        attuale = _posizione(oggetto)
        destinazione = misure.posizione_consentita(
            attuale, origine, _blocchi(oggetto, "lock_location")
        )
        delta = tuple(destinazione[asse] - attuale[asse] for asse in range(3))
        effettuabile = _spostamento_libero(oggetto, delta)
        esito = _classifica(delta, effettuabile)
        if esito == "bloccato":
            bloccati += 1
            continue
        if esito == "invariato":
            invariati += 1
            continue
        oggetto.location = destinazione
        applicati += 1
    if not applicati and not invariati:
        raise ErroreTrasformazione(TESTI["ERRORE_TRASFORMAZIONE_BLOCCATA"])
    return EsitoTrasformazione(applicati, bloccati, invariati)


def appoggia_sul_piano(oggetti, view_layer=None) -> EsitoTrasformazione:
    """Fa toccare il piano di lavoro agli oggetti indicati.

    L'oggetto viene spostato in verticale di quanto basta, senza toccare X e Y:
    appoggiare non deve far scivolare via l'oggetto. Gli oggetti senza una
    forma propria (una luce, una telecamera, un segnaposto) non hanno un
    "sotto": per loro finisce sul piano il punto di riferimento, e il messaggio
    lo dice.
    """
    elenco = _scelti(oggetti)
    _aggiorna_matrici(view_layer)
    applicati = bloccati = invariati = senza_forma = 0
    for oggetto in elenco:
        minimo = _minimo_in_verticale(oggetto)
        if minimo is None:
            senza_forma += 1
            minimo = _posizione(oggetto)[2]
        attuale = _posizione(oggetto)
        delta = (0.0, 0.0, -minimo)
        effettuabile = _spostamento_libero(oggetto, delta)
        esito = _classifica(delta, effettuabile)
        if esito == "bloccato":
            bloccati += 1
            continue
        if esito == "invariato":
            invariati += 1
            continue
        oggetto.location = (
            attuale[0] + effettuabile[0],
            attuale[1] + effettuabile[1],
            attuale[2] + effettuabile[2],
        )
        applicati += 1
    if not applicati and not invariati:
        raise ErroreTrasformazione(TESTI["ERRORE_TRASFORMAZIONE_BLOCCATA"])
    return EsitoTrasformazione(applicati, bloccati, invariati, senza_forma)


def _aggiorna_matrici(view_layer) -> None:
    """Ricalcola le matrici prima di leggere le misure, se possibile."""
    aggiorna = getattr(view_layer, "update", None)
    if aggiorna is None:
        return
    try:
        aggiorna()
    except (AttributeError, ReferenceError, RuntimeError):
        return


def _minimo_in_verticale(oggetto):
    """Quota più bassa dell'oggetto nella scena; None se non ha una forma."""
    riquadro = getattr(oggetto, "bound_box", None)
    matrice = getattr(oggetto, "matrix_world", None)
    if riquadro is None or matrice is None:
        return None
    try:
        angoli = [matrice @ mathutils.Vector(tuple(angolo)) for angolo in riquadro]
    except (AttributeError, TypeError, ValueError):
        return None
    if not angoli:
        return None
    if not _ha_una_forma(angoli):
        return None
    return min(float(angolo.z) for angolo in angoli)


def _ha_una_forma(angoli) -> bool:
    """Indica se il riquadro dell'oggetto ha una vera estensione.

    Luci, telecamere e segnaposti hanno un riquadro tutto nello stesso punto:
    non c'è un "sotto" da appoggiare, quindi per loro conta il punto stesso.
    """
    minimo = [min(float(angolo[i]) for angolo in angoli) for i in range(3)]
    massimo = [max(float(angolo[i]) for angolo in angoli) for i in range(3)]
    return any(massimo[i] - minimo[i] > 1e-9 for i in range(3))


# --------------------------------------------------------------------- ruotare


def ruota(oggetti, radianti: float) -> EsitoTrasformazione:
    """Ruota gli oggetti indicati attorno all'asse verticale della scena."""
    elenco = _scelti(oggetti)
    applicati = bloccati = 0
    for oggetto in elenco:
        if not _rotazione_libera(oggetto):
            bloccati += 1
            continue
        _ruota_uno(oggetto, radianti)
        applicati += 1
    if not applicati:
        raise ErroreTrasformazione(TESTI["ERRORE_TRASFORMAZIONE_BLOCCATA"])
    return EsitoTrasformazione(applicati, bloccati)


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


# ------------------------------------------------------------------ dimensione


def ingrandisci(oggetti, fattore: float) -> EsitoTrasformazione:
    """Moltiplica la dimensione degli oggetti indicati, asse per asse."""
    elenco = _scelti(oggetti)
    # Prima si controlla tutto, poi si applica: niente oggetti a metà.
    piani: list[tuple[object, tuple[float, float, float]]] = []
    bloccati = 0
    for oggetto in elenco:
        scala = oggetto.scale
        fattori = misure.fattori_consentiti(fattore, _blocchi(oggetto, "lock_scale"))
        nuova = (
            float(scala[0]) * fattori[0],
            float(scala[1]) * fattori[1],
            float(scala[2]) * fattori[2],
        )
        if (fattori[0], fattori[1], fattori[2]) == (1.0, 1.0, 1.0):
            bloccati += 1
            continue
        if max(abs(valore) for valore in nuova) < configuration.SCALA_MINIMA:
            raise ErroreTrasformazione(TESTI["MESSAGGIO_DIMENSIONE_MINIMA"])
        piani.append((oggetto, nuova))

    if not piani:
        raise ErroreTrasformazione(TESTI["ERRORE_TRASFORMAZIONE_BLOCCATA"])
    for oggetto, nuova in piani:
        oggetto.scale = nuova
    return EsitoTrasformazione(len(piani), bloccati)


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
