"""Misure, unità e blocchi: regole pure condivise dai comandi e dall'interfaccia.

Questo modulo non importa Blender. Riceve numeri e triple di numeri e
restituisce numeri e triple, così le regole più facili da sbagliare si
verificano con prove veloci, senza aprire Blender:

* quale unità va scritta accanto a un numero (metri, centimetri, gradi);
* quali assi di un oggetto si possono toccare, rispettando i blocchi che
  l'utente ha messo in Blender (posizione, rotazione e dimensione bloccate);
* come passare dai gradi ai radianti e viceversa.

Rispettare i blocchi non è un dettaglio: se Blender dice "asse X bloccato",
spostare lo stesso l'oggetto lungo X sarebbe una modifica che l'utente non ha
chiesto e che non si aspetta.
"""

from __future__ import annotations

import math

# Assi della scena, nell'ordine usato da Blender (X, Y, Z).
ASSI = ("x", "y", "z")
INDICE_ASSE = {"x": 0, "y": 1, "z": 2}
NOME_ASSE = ("X", "Y", "Z")

# Unità di lunghezza di Blender e loro abbreviazione italiana.
UNITA_LUNGHEZZA = {
    "KILOMETERS": "km",
    "METERS": "m",
    "CENTIMETERS": "cm",
    "MILLIMETERS": "mm",
    "MICROMETERS": "µm",
    "MILES": "mi",
    "FEET": "ft",
    "INCHES": "in",
    "THOU": "thou",
}

# Con il sistema "NONE" Blender non converte e non scrive nessuna unità.
SISTEMA_SENZA_UNITA = "NONE"
ABBREVIAZIONE_GRADI = "°"
ABBREVIAZIONE_RADIANTI = "rad"

# Numero di cifre decimali usato quando si mostrano le misure come testo.
CIFRE_DECIMALI = 3


def unita_lunghezza(sistema: str, unita: str) -> str:
    """Abbreviazione dell'unità di lunghezza della scena; vuota se non si usano unità."""
    if str(sistema) == SISTEMA_SENZA_UNITA:
        return ""
    return UNITA_LUNGHEZZA.get(str(unita), "")


def unita_angolo(sistema_rotazione: str) -> str:
    """Abbreviazione dell'unità degli angoli: gradi oppure radianti."""
    return ABBREVIAZIONE_GRADI if str(sistema_rotazione) == "DEGREES" else ABBREVIAZIONE_RADIANTI


def etichetta_con_unita(base: str, unita: str) -> str:
    """Scrive l'unità fra parentesi solo quando Blender la usa davvero."""
    return f"{base} ({unita})" if unita else base


def gradi_in_radianti(gradi: float) -> float:
    """Converte i gradi in radianti, che è l'unità usata da Blender."""
    return math.radians(float(gradi))


def radianti_in_gradi(radianti: float) -> float:
    """Converte i radianti in gradi, che è l'unità mostrata all'utente."""
    return math.degrees(float(radianti))


def numero_breve(valore: float) -> str:
    """Scrive un numero senza zeri inutili: 15.0 diventa 15, 7.5 resta 7.5."""
    arrotondato = round(float(valore), CIFRE_DECIMALI)
    if arrotondato == int(arrotondato):
        return str(int(arrotondato))
    return str(arrotondato).replace(".", ",")


# ------------------------------------------------------------------- blocchi


def _blocchi(blocchi) -> tuple[bool, bool, bool]:
    """Normalizza una terna di blocchi: accetta liste, tuple e valori mancanti."""
    if blocchi is None:
        return (False, False, False)
    valori = [bool(valore) for valore in list(blocchi)[:3]]
    while len(valori) < 3:
        valori.append(False)
    return (valori[0], valori[1], valori[2])


def assi_bloccati(blocchi) -> tuple[int, ...]:
    """Indici degli assi bloccati, nell'ordine X, Y, Z."""
    return tuple(indice for indice, bloccato in enumerate(_blocchi(blocchi)) if bloccato)


def tutti_bloccati(blocchi) -> bool:
    """Indica se nessuno dei tre assi si può toccare."""
    return len(assi_bloccati(blocchi)) == 3


def delta_consentito(delta, blocchi) -> tuple[float, float, float]:
    """Azzera le componenti dello spostamento che cadono su un asse bloccato."""
    valori = tuple(float(valore) for valore in list(delta)[:3])
    while len(valori) < 3:
        valori = (*valori, 0.0)
    permessi = _blocchi(blocchi)
    return tuple(0.0 if permessi[asse] else valori[asse] for asse in range(3))


def fattori_consentiti(fattore: float, blocchi) -> tuple[float, float, float]:
    """Restituisce il fattore per asse: 1.0 dove la dimensione è bloccata."""
    permessi = _blocchi(blocchi)
    return tuple(1.0 if permessi[asse] else float(fattore) for asse in range(3))


def posizione_consentita(attuale, nuova, blocchi) -> tuple[float, float, float]:
    """Nuova posizione assoluta, mantenendo il valore corrente sugli assi bloccati."""
    prima = tuple(float(valore) for valore in list(attuale)[:3])
    dopo = tuple(float(valore) for valore in list(nuova)[:3])
    while len(prima) < 3:
        prima = (*prima, 0.0)
    while len(dopo) < 3:
        dopo = (*dopo, 0.0)
    permessi = _blocchi(blocchi)
    return tuple(dopo[asse] if not permessi[asse] else prima[asse] for asse in range(3))


def spostamento_valutabile(delta) -> bool:
    """Indica se uno spostamento cambia davvero qualcosa (evita passi a vuoto)."""
    return any(abs(float(valore)) > 1e-12 for valore in list(delta)[:3])
