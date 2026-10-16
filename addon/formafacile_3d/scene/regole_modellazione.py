"""Regole pure degli strumenti guidati di modellazione.

Come `scene/misure.py`, questo modulo non importa Blender: riceve numeri e
liste di coordinate e restituisce numeri, posizioni e giudizi. Così le regole
più facili da sbagliare (quanto arrotondare uno spigolo, quante facce aggiunge
una suddivisione, dove finiscono le copie di una ripetizione, quali oggetti
sono già speculari) si verificano con prove veloci, senza aprire Blender.

Un principio vale per tutte le funzioni: i valori richiesti dall'utente
vengono **limitati** a valori che Blender sa gestire, invece di essere passati
così come sono. Un raggio di smusso più grande della forma, o uno spessore
maggiore della parete, non fanno un risultato migliore: fanno una forma
rovinata.
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence

# Assi della scena, nell'ordine usato da Blender (X, Y, Z).
ASSI = ("x", "y", "z")
INDICE_ASSE = {"x": 0, "y": 1, "z": 2}

# Tipi di oggetto che Blender sa trasformare in una forma (mesh). L'elenco sta
# qui perché serve sia al servizio dei modificatori sia all'interfaccia, che
# non importa Blender: un solo posto, una sola verità.
TIPI_CONVERTIBILI = ("FONT", "CURVE", "SURFACE", "META")

# Gradi di un giro completo.
GRADI_GIRO = 360.0


# ------------------------------------------------------------------- smusso


def forza_valida(forza: object, minima: int, massima: int) -> int:
    """Forza dello smusso ridotta all'intervallo consentito."""
    try:
        numero = int(forza)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return minima
    return min(max(numero, minima), massima)


def raggio_smusso(
    dimensione_minima: float,
    forza: int,
    *,
    rapporto_per_forza: float,
    rapporto_massimo: float,
    raggio_minimo: float,
) -> float:
    """Raggio di smusso ricavato da quanto è piccola la forma.

    Il raggio cresce con la forza scelta ma resta sempre una frazione della
    dimensione più piccola: più di così lo smusso mangerebbe la forma invece di
    ammorbidirla.
    """
    dimensione = abs(float(dimensione_minima))
    rapporto = min(rapporto_per_forza * max(int(forza), 1), rapporto_massimo)
    return max(dimensione * rapporto, raggio_minimo)


def segmenti_smusso(forza: int, massimi: int) -> int:
    """Numero di segmenti del raccordo: più forza, più tondo (mai oltre il limite)."""
    return min(max(int(forza), 2), max(int(massimi), 2))


def spigoli_vivi(
    facce: Sequence[Sequence[int]],
    normali: Sequence[Sequence[float]],
    soglia_gradi: float,
) -> int:
    """Conta gli spigoli che formano un angolo vivo fra due facce.

    Un bordo aperto (una faccia sola) non conta: non è uno spigolo da
    ammorbidire, è il bordo di una superficie. Blender non lo smussa, quindi
    prometterlo sarebbe un errore.
    """
    per_spigolo: dict[tuple[int, int], list[int]] = {}
    for indice, vertici in enumerate(facce):
        elenco = [int(vertice) for vertice in vertici]
        for posizione, vertice in enumerate(elenco):
            altro = elenco[(posizione + 1) % len(elenco)]
            chiave = (min(vertice, altro), max(vertice, altro))
            per_spigolo.setdefault(chiave, []).append(indice)

    soglia = math.radians(float(soglia_gradi))
    conteggio = 0
    for indici in per_spigolo.values():
        if len(indici) != 2:
            continue
        prima, seconda = normali[indici[0]], normali[indici[1]]
        if _angolo_fra_normali(prima, seconda) > soglia:
            conteggio += 1
    return conteggio


def _angolo_fra_normali(prima: Sequence[float], seconda: Sequence[float]) -> float:
    """Angolo fra due normali, calcolato a mano (nessuna libreria esterna)."""
    prodotto = sum(float(prima[asse]) * float(seconda[asse]) for asse in range(3))
    lunghezza = math.sqrt(sum(float(valore) ** 2 for valore in prima)) * math.sqrt(
        sum(float(valore) ** 2 for valore in seconda)
    )
    if lunghezza <= 1e-12:
        return 0.0
    return math.acos(max(-1.0, min(1.0, prodotto / lunghezza)))


def bordi_aperti(facce: Sequence[Sequence[int]]) -> int:
    """Conta i bordi usati da una sola faccia: indicano una superficie non chiusa."""
    conteggio: dict[tuple[int, int], int] = {}
    for vertici in facce:
        elenco = [int(vertice) for vertice in vertici]
        for posizione, vertice in enumerate(elenco):
            altro = elenco[(posizione + 1) % len(elenco)]
            chiave = (min(vertice, altro), max(vertice, altro))
            conteggio[chiave] = conteggio.get(chiave, 0) + 1
    return sum(1 for usi in conteggio.values() if usi == 1)


# ---------------------------------------------------------------- simmetria


def simmetrica(
    coordinate: Iterable[Sequence[float]],
    asse: str,
    tolleranza: float,
    posizione_piano: float = 0.0,
) -> bool:
    """Indica se la forma è già uguale al suo specchio rispetto a un piano.

    Il piano è perpendicolare all'asse indicato e passa per `posizione_piano`
    (le stesse coordinate dei punti). Serve a non promettere un risultato che
    non si vedrebbe: specchiare una forma già simmetrica rispetto al piano non
    aggiunge nulla, e il comando deve dirlo invece di annunciare un
    cambiamento che non c'è.
    """
    indice = INDICE_ASSE.get(str(asse).lower())
    if indice is None:
        return False
    passo = max(float(tolleranza), 1e-9)
    chiavi: set[tuple[int, int, int]] = set()
    punti: list[tuple[int, int, int]] = []
    for punto in coordinate:
        arrotondati = (
            round(float(punto[0]) / passo),
            round(float(punto[1]) / passo),
            round(float(punto[2]) / passo),
        )
        punti.append(arrotondati)
        chiavi.add(arrotondati)
    if not punti:
        return False
    centro = round(float(posizione_piano) / passo)
    for arrotondati in punti:
        specchio = list(arrotondati)
        specchio[indice] = 2 * centro - specchio[indice]
        if tuple(specchio) not in chiavi:
            return False
    return True


# ------------------------------------------------------------------ liscio


def facce_dopo_suddivisione(facce: int, livelli: int) -> int:
    """Facce stimate dopo la suddivisione: ogni livello moltiplica per quattro."""
    return int(facce) * (4 ** max(int(livelli), 0))


def livelli_consentiti(facce: int, livelli: int, massimo_facce: int) -> int:
    """Riduce i livelli finché la forma resta leggera abbastanza da muoversi."""
    richiesti = max(int(livelli), 1)
    for livello in range(richiesti, 0, -1):
        if facce_dopo_suddivisione(facce, livello) <= massimo_facce:
            return livello
    return 1


# -------------------------------------------------------------- ripetizione


def copie_aggiuntive(quante: int) -> int:
    """Quante copie nuove vengono create oltre all'originale."""
    return max(int(quante) - 1, 0)


def fine_fila(spaziatura: float, quante: int, asse: str) -> tuple[float, float, float]:
    """Posizione dell'ultima copia di una fila, rispetto all'originale."""
    indice = INDICE_ASSE.get(str(asse).lower(), 0)
    valori = [0.0, 0.0, 0.0]
    valori[indice] = float(spaziatura) * copie_aggiuntive(quante)
    return (valori[0], valori[1], valori[2])


def direzione_da_punto(
    centro: Sequence[float], punto: Sequence[float]
) -> tuple[float, float]:
    """Distanza e angolo (in gradi) di un punto visto dal centro, nel piano orizzontale."""
    delta_x = float(punto[0]) - float(centro[0])
    delta_y = float(punto[1]) - float(centro[1])
    distanza = math.hypot(delta_x, delta_y)
    if distanza <= 1e-9:
        return 0.0, 0.0
    return distanza, math.degrees(math.atan2(delta_y, delta_x))


def punto_su_cerchio(
    centro: Sequence[float], distanza: float, angolo_gradi: float
) -> tuple[float, float, float]:
    """Punto del cerchio attorno al centro, alla distanza e all'angolo indicati."""
    radianti = math.radians(float(angolo_gradi))
    return (
        float(centro[0]) + float(distanza) * math.cos(radianti),
        float(centro[1]) + float(distanza) * math.sin(radianti),
        float(centro[2]),
    )


def posizioni_cerchio(
    centro: Sequence[float],
    quante: int,
    distanza: float,
    angolo_iniziale_gradi: float,
) -> tuple[tuple[tuple[float, float, float], float], ...]:
    """Posizioni e rotazioni delle copie di un giro, a partire dall'angolo iniziale.

    L'originale resta dov'è (l'angolo iniziale è il suo); le copie si
    distribuiscono a passi uguali sul giro completo, alla stessa distanza dal
    centro.
    """
    quante = max(int(quante), 1)
    passo = GRADI_GIRO / quante
    copie: list[tuple[tuple[float, float, float], float]] = []
    for indice in range(1, quante):
        angolo = float(angolo_iniziale_gradi) + passo * indice
        copie.append((punto_su_cerchio(centro, distanza, angolo), angolo))
    return tuple(copie)


# ---------------------------------------------------------------- spessore


def spessore_consentito(
    dimensione_minima: float,
    richiesto: float,
    *,
    rapporto_massimo: float,
    spessore_minimo: float,
) -> float:
    """Spessore ridotto a una frazione della forma, mai sotto il minimo visibile."""
    dimensione = abs(float(dimensione_minima))
    limite = dimensione * rapporto_massimo if dimensione > 0.0 else abs(float(richiesto))
    return max(min(abs(float(richiesto)), limite), spessore_minimo)


# ------------------------------------------------------------- allineamento


def spostamento_allineamento(
    minimo: float,
    massimo: float,
    riferimento_minimo: float,
    riferimento_massimo: float,
    modo: str,
) -> float:
    """Di quanto spostare un oggetto per allinearlo al riferimento.

    `inizio` porta i bordi iniziali a coincidere, `fine` i bordi finali,
    `centro` i centri: sono le tre scelte che si vedono nel pannello.
    """
    if modo == "centro":
        return (float(riferimento_minimo) + float(riferimento_massimo)) / 2.0 - (
            float(minimo) + float(massimo)
        ) / 2.0
    if modo == "fine":
        return float(riferimento_massimo) - float(massimo)
    return float(riferimento_minimo) - float(minimo)


def posizioni_spaziate(intervalli: Sequence[Sequence[float]]) -> tuple[float, ...]:
    """Nuovi bordi iniziali che lasciano lo stesso spazio fra gli oggetti.

    Il primo e l'ultimo restano dove sono: si spostano solo quelli in mezzo,
    che è quello che ci si aspetta da "spazia in modo uguale".
    """
    if len(intervalli) < 3:
        return tuple(float(intervallo[0]) for intervallo in intervalli)
    larghezze = [max(float(intervallo[1]) - float(intervallo[0]), 0.0) for intervallo in intervalli]
    inizio = float(intervalli[0][0])
    fine = float(intervalli[-1][1])
    spazio = (fine - inizio - sum(larghezze)) / (len(intervalli) - 1)
    posizioni: list[float] = []
    cursore = inizio
    for larghezza in larghezze:
        posizioni.append(cursore)
        cursore += larghezza + spazio
    return tuple(posizioni)


def spazio_fra_oggetti(intervalli: Sequence[Sequence[float]]) -> float:
    """Spazio che resterà fra un oggetto e il successivo (può essere negativo)."""
    if len(intervalli) < 3:
        return 0.0
    larghezze = [max(float(intervallo[1]) - float(intervallo[0]), 0.0) for intervallo in intervalli]
    return (
        float(intervalli[-1][1])
        - float(intervalli[0][0])
        - sum(larghezze)
    ) / (len(intervalli) - 1)


# ------------------------------------------------------------------ gruppi


def nome_gruppo_libero(nomi_esistenti: Iterable[str], base: str) -> str:
    """Primo nome libero della serie "Gruppo 1", "Gruppo 2", ..."""
    usati = {str(nome).casefold() for nome in nomi_esistenti}
    for numero in range(1, 1000):
        candidato = f"{base} {numero}"
        if candidato.casefold() not in usati:
            return candidato
    return f"{base} {len(usati) + 1}"
