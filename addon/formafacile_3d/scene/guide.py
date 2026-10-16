"""Guide passo passo: sequenze di comandi già esistenti.

Una guida è un elenco di passi. Ogni passo spiega che cosa si sta per fare e
contiene soltanto comandi che esistono davvero in questa versione (gli stessi
identificatori usati dai pulsanti dei pannelli), con gli stessi parametri.
Così una guida non può promettere una funzione che il programma non ha: quello
che si legge è quello che i pulsanti fanno.

Questo modulo non importa Blender: descrive i passi e le regole di
avanzamento, e le prove automatiche verificano che ogni comando citato esista.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .. import comandi

# Campi dello stato della scena che una guida può preparare prima del passo.
STATO_GRANDEZZA_FORMA = "grandezza_forma"
STATO_PASSO = "passo"


@dataclass(frozen=True)
class Testo:
    """Valore preso dalla mappa centrale dei testi.

    I nomi degli oggetti creati dalla guida ("Corpo", "Tetto") sono testi come
    gli altri: restano in `localization.py` e non vengono scritti qui.
    """

    chiave: str


@dataclass(frozen=True)
class Azione:
    """Un comando esistente, con i suoi parametri."""

    comando: str
    parametri: tuple[tuple[str, object], ...] = ()


@dataclass(frozen=True)
class Passo:
    """Un passo della guida: che cosa fare, perché, e con quali comandi."""

    chiave: str
    titolo: str
    spiegazione: str
    azioni: tuple[Azione, ...]
    impostazioni: tuple[tuple[str, object], ...] = ()
    # Nomi (chiavi di testo) degli oggetti da scegliere prima del passo; il
    # primo diventa l'oggetto attivo, come quando si sceglie a mano.
    selezione: tuple[Testo, ...] = ()


@dataclass(frozen=True)
class Guida:
    """Sequenza di passi con un titolo e una spiegazione iniziale."""

    chiave: str
    titolo: str
    descrizione: str
    passi: tuple[Passo, ...] = field(default_factory=tuple)


def _rinomina(chiave_nome: str) -> Azione:
    return Azione(comandi.ID_RINOMINA, (("nome", Testo(chiave_nome)),))


def _sposta(direzione: str) -> Azione:
    return Azione(comandi.ID_SPOSTA_PASSO, (("direzione", direzione),))


def _casetta() -> Guida:
    """La casetta: tre forme semplici, unite e raggruppate.

    Le misure sono scelte perché il risultato si regga in piedi senza
    aggiustamenti a mano: il cubo (2 m) sta sul pavimento, il cono appoggia un
    po' dentro il cubo e il camino esce dal tetto.
    """
    return Guida(
        chiave="casetta",
        titolo="GUIDA_CASETTA_TITOLO",
        descrizione="GUIDA_CASETTA_DESCRIZIONE",
        passi=(
            Passo(
                chiave="corpo",
                titolo="GUIDA_CASETTA_CORPO_TITOLO",
                spiegazione="GUIDA_CASETTA_CORPO_SPIEGAZIONE",
                impostazioni=((STATO_GRANDEZZA_FORMA, 2.0),),
                azioni=(
                    Azione(comandi.ID_AGGIUNGI_CUBO),
                    _rinomina("NOME_CASETTA_CORPO"),
                ),
            ),
            Passo(
                chiave="corpo_centro",
                titolo="GUIDA_CASETTA_CORPO_CENTRO_TITOLO",
                spiegazione="GUIDA_CASETTA_CORPO_CENTRO_SPIEGAZIONE",
                azioni=(Azione(comandi.ID_CENTRA),),
            ),
            Passo(
                chiave="corpo_piano",
                titolo="GUIDA_CASETTA_CORPO_PIANO_TITOLO",
                spiegazione="GUIDA_CASETTA_CORPO_PIANO_SPIEGAZIONE",
                azioni=(Azione(comandi.ID_APPOGGIA_SUL_PIANO),),
            ),
            Passo(
                chiave="tetto",
                titolo="GUIDA_CASETTA_TETTO_TITOLO",
                spiegazione="GUIDA_CASETTA_TETTO_SPIEGAZIONE",
                impostazioni=((STATO_GRANDEZZA_FORMA, 2.0),),
                azioni=(
                    Azione(comandi.ID_AGGIUNGI_CONO),
                    _rinomina("NOME_CASETTA_TETTO"),
                ),
            ),
            Passo(
                chiave="tetto_centro",
                titolo="GUIDA_CASETTA_TETTO_CENTRO_TITOLO",
                spiegazione="GUIDA_CASETTA_TETTO_CENTRO_SPIEGAZIONE",
                azioni=(Azione(comandi.ID_CENTRA),),
            ),
            Passo(
                chiave="tetto_piano",
                titolo="GUIDA_CASETTA_TETTO_PIANO_TITOLO",
                spiegazione="GUIDA_CASETTA_TETTO_PIANO_SPIEGAZIONE",
                azioni=(Azione(comandi.ID_APPOGGIA_SUL_PIANO),),
            ),
            Passo(
                chiave="tetto_alto",
                titolo="GUIDA_CASETTA_TETTO_ALTO_TITOLO",
                spiegazione="GUIDA_CASETTA_TETTO_ALTO_SPIEGAZIONE",
                impostazioni=((STATO_PASSO, 1.9),),
                azioni=(_sposta("su"),),
            ),
            Passo(
                chiave="camino",
                titolo="GUIDA_CASETTA_CAMINO_TITOLO",
                spiegazione="GUIDA_CASETTA_CAMINO_SPIEGAZIONE",
                impostazioni=((STATO_GRANDEZZA_FORMA, 0.5),),
                azioni=(
                    Azione(comandi.ID_AGGIUNGI_CILINDRO),
                    _rinomina("NOME_CASETTA_CAMINO"),
                ),
            ),
            Passo(
                chiave="camino_centro",
                titolo="GUIDA_CASETTA_CAMINO_CENTRO_TITOLO",
                spiegazione="GUIDA_CASETTA_CAMINO_CENTRO_SPIEGAZIONE",
                azioni=(Azione(comandi.ID_CENTRA),),
            ),
            Passo(
                chiave="camino_alto",
                titolo="GUIDA_CASETTA_CAMINO_ALTO_TITOLO",
                spiegazione="GUIDA_CASETTA_CAMINO_ALTO_SPIEGAZIONE",
                impostazioni=((STATO_PASSO, 2.55),),
                azioni=(_sposta("su"),),
            ),
            Passo(
                chiave="camino_lato",
                titolo="GUIDA_CASETTA_CAMINO_LATO_TITOLO",
                spiegazione="GUIDA_CASETTA_CAMINO_LATO_SPIEGAZIONE",
                impostazioni=((STATO_PASSO, 0.5),),
                azioni=(_sposta("destra"),),
            ),
            Passo(
                chiave="unire",
                titolo="GUIDA_CASETTA_UNIRE_TITOLO",
                spiegazione="GUIDA_CASETTA_UNIRE_SPIEGAZIONE",
                selezione=(Testo("NOME_CASETTA_CORPO"), Testo("NOME_CASETTA_TETTO")),
                azioni=(
                    Azione(
                        comandi.ID_UNISCI_FORME,
                        (("operazione", comandi.OPERAZIONE_UNIONE),),
                    ),
                ),
            ),
            Passo(
                chiave="gruppo",
                titolo="GUIDA_CASETTA_GRUPPO_TITOLO",
                spiegazione="GUIDA_CASETTA_GRUPPO_SPIEGAZIONE",
                selezione=(
                    Testo("NOME_CASETTA_CORPO"),
                    Testo("NOME_CASETTA_CAMINO"),
                ),
                azioni=(
                    Azione(
                        comandi.ID_RAGGRUPPA,
                        (("nome", Testo("NOME_CASETTA_GRUPPO")),),
                    ),
                ),
            ),
        ),
    )


GUIDE: Mapping[str, Guida] = {guida.chiave: guida for guida in (_casetta(),)}


def chiavi_guide() -> tuple[str, ...]:
    """Chiavi di tutte le guide disponibili, in ordine."""
    return tuple(GUIDE)


def guida(chiave: str) -> Guida | None:
    """Guida con la chiave indicata, se esiste."""
    return GUIDE.get(str(chiave))


def indice_valido(indice: object, totale: int) -> int:
    """Indice del passo ridotto all'intervallo dei passi esistenti."""
    try:
        numero = int(indice)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0
    return min(max(numero, 0), max(int(totale), 0))


def passo_corrente(chiave: str, indice: object) -> Passo | None:
    """Passo mostrato adesso, se la guida esiste e ha passi."""
    corrente = guida(chiave)
    if corrente is None or not corrente.passi:
        return None
    return corrente.passi[indice_valido(indice, len(corrente.passi) - 1)]


def prossimo_indice(indice: object, totale: int, modo: str) -> int:
    """Indice dopo "Avanti" o "Indietro".

    "Avanti" può arrivare a `totale`, che non è un passo ma lo stato "guida
    finita": senza quel valore l'ultimo passo resterebbe in eterno quello
    mostrato e si potrebbe eseguire all'infinito. "Indietro" non scende sotto
    zero.
    """
    ultimo = max(int(totale), 0)
    attuale = indice_valido(indice, ultimo)
    if modo == comandi.MODO_GUIDA_INDIETRO:
        return max(attuale - 1, 0)
    return min(attuale + 1, ultimo)


def completata(indice: object, totale: int) -> bool:
    """Indica se tutti i passi sono stati fatti."""
    if totale <= 0:
        return False
    return indice_valido(indice, totale) >= totale
