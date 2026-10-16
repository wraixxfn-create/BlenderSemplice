"""Catalogo della libreria di oggetti, indipendente da Blender.

Ogni voce descrive un modello costruito da FormaFacile: nome e descrizione
provengono dalla risorsa italiana centrale e i campi indicano quali valori
mostrare prima dell'inserimento. Nessuna voce contiene immagini o modelli di
terzi: la geometria viene generata dal codice dell'estensione.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType

from ..localization import TESTI


ASSET_TAVOLINO = "tavolino"
ASSET_SCAFFALE = "scaffale"
ASSET_SEDIA = "sedia"
ASSET_PIEDISTALLO = "piedistallo"
ASSET_VASO = "vaso"
ASSET_INSEGNA = "insegna"
ASSET_STANZA = "stanza"
ASSET_PEDANA = "pedana"
ASSET_SET_FOTOGRAFICO = "set_fotografico"
ASSET_FORMA_STAMPA = "forme_stampa_3d"

CAMPO_LARGHEZZA = "asset_larghezza"
CAMPO_PROFONDITA = "asset_profondita"
CAMPO_ALTEZZA = "asset_altezza"
CAMPO_SPESSORE = "asset_spessore"
CAMPO_SPESSORE_GAMBA = "asset_spessore_gamba"
CAMPO_NUMERO_RIPIANI = "asset_numero_ripiani"
CAMPO_RAGGIO = "asset_raggio"
CAMPO_SPESSORE_PARETE = "asset_spessore_parete"
CAMPO_TESTO = "asset_testo"
CAMPO_COLORE = "asset_colore"
CAMPO_DIAMETRO = "asset_diametro"
CAMPO_GRANDEZZA = "asset_grandezza"
CAMPO_POTENZA_LUCE = "asset_potenza_luce"


@dataclass(frozen=True)
class SchedaAsset:
    """Descrizione stabile di un modello disponibile nella libreria."""

    identificatore: str
    chiave_nome: str
    chiave_descrizione: str
    campi: tuple[str, ...]

    @property
    def nome(self) -> str:
        """Nome mostrato nell'elenco, sempre in italiano."""
        return TESTI[self.chiave_nome]

    @property
    def descrizione(self) -> str:
        """Descrizione mostrata prima di creare la geometria."""
        return TESTI[self.chiave_descrizione]


SCHEDE = (
    SchedaAsset(
        ASSET_TAVOLINO,
        "ASSET_NOME_TAVOLINO",
        "ASSET_DESCRIZIONE_TAVOLINO",
        (CAMPO_LARGHEZZA, CAMPO_PROFONDITA, CAMPO_ALTEZZA, CAMPO_SPESSORE, CAMPO_SPESSORE_GAMBA, CAMPO_COLORE),
    ),
    SchedaAsset(
        ASSET_SCAFFALE,
        "ASSET_NOME_SCAFFALE",
        "ASSET_DESCRIZIONE_SCAFFALE",
        (CAMPO_LARGHEZZA, CAMPO_PROFONDITA, CAMPO_ALTEZZA, CAMPO_NUMERO_RIPIANI, CAMPO_SPESSORE, CAMPO_COLORE),
    ),
    SchedaAsset(
        ASSET_SEDIA,
        "ASSET_NOME_SEDIA",
        "ASSET_DESCRIZIONE_SEDIA",
        (CAMPO_LARGHEZZA, CAMPO_PROFONDITA, CAMPO_ALTEZZA, CAMPO_SPESSORE, CAMPO_SPESSORE_GAMBA, CAMPO_COLORE),
    ),
    SchedaAsset(
        ASSET_PIEDISTALLO,
        "ASSET_NOME_PIEDISTALLO",
        "ASSET_DESCRIZIONE_PIEDISTALLO",
        (CAMPO_LARGHEZZA, CAMPO_PROFONDITA, CAMPO_ALTEZZA, CAMPO_SPESSORE, CAMPO_COLORE),
    ),
    SchedaAsset(
        ASSET_VASO,
        "ASSET_NOME_VASO",
        "ASSET_DESCRIZIONE_VASO",
        (CAMPO_ALTEZZA, CAMPO_RAGGIO, CAMPO_SPESSORE_PARETE, CAMPO_COLORE),
    ),
    SchedaAsset(
        ASSET_INSEGNA,
        "ASSET_NOME_INSEGNA",
        "ASSET_DESCRIZIONE_INSEGNA",
        (CAMPO_LARGHEZZA, CAMPO_ALTEZZA, CAMPO_SPESSORE, CAMPO_TESTO, CAMPO_COLORE),
    ),
    SchedaAsset(
        ASSET_STANZA,
        "ASSET_NOME_STANZA",
        "ASSET_DESCRIZIONE_STANZA",
        (CAMPO_LARGHEZZA, CAMPO_PROFONDITA, CAMPO_ALTEZZA, CAMPO_SPESSORE, CAMPO_COLORE),
    ),
    SchedaAsset(
        ASSET_PEDANA,
        "ASSET_NOME_PEDANA",
        "ASSET_DESCRIZIONE_PEDANA",
        (CAMPO_DIAMETRO, CAMPO_ALTEZZA, CAMPO_COLORE),
    ),
    SchedaAsset(
        ASSET_SET_FOTOGRAFICO,
        "ASSET_NOME_SET_FOTOGRAFICO",
        "ASSET_DESCRIZIONE_SET_FOTOGRAFICO",
        (CAMPO_LARGHEZZA, CAMPO_PROFONDITA, CAMPO_ALTEZZA, CAMPO_SPESSORE, CAMPO_POTENZA_LUCE, CAMPO_COLORE),
    ),
    SchedaAsset(
        ASSET_FORMA_STAMPA,
        "ASSET_NOME_FORMA_STAMPA",
        "ASSET_DESCRIZIONE_FORMA_STAMPA",
        (CAMPO_GRANDEZZA, CAMPO_COLORE),
    ),
)

_SCHEDE_PER_ID = MappingProxyType({scheda.identificatore: scheda for scheda in SCHEDE})
ID_PREDEFINITO = ASSET_TAVOLINO
CAMPI = MappingProxyType(
    {
        CAMPO_LARGHEZZA: "ASSET_CAMPO_LARGHEZZA",
        CAMPO_PROFONDITA: "ASSET_CAMPO_PROFONDITA",
        CAMPO_ALTEZZA: "ASSET_CAMPO_ALTEZZA",
        CAMPO_SPESSORE: "ASSET_CAMPO_SPESSORE",
        CAMPO_SPESSORE_GAMBA: "ASSET_CAMPO_SPESSORE_GAMBA",
        CAMPO_NUMERO_RIPIANI: "ASSET_CAMPO_NUMERO_RIPIANI",
        CAMPO_RAGGIO: "ASSET_CAMPO_RAGGIO",
        CAMPO_SPESSORE_PARETE: "ASSET_CAMPO_SPESSORE_PARETE",
        CAMPO_TESTO: "ASSET_CAMPO_TESTO",
        CAMPO_COLORE: "ASSET_CAMPO_COLORE",
        CAMPO_DIAMETRO: "ASSET_CAMPO_DIAMETRO",
        CAMPO_GRANDEZZA: "ASSET_CAMPO_GRANDEZZA",
        CAMPO_POTENZA_LUCE: "ASSET_CAMPO_POTENZA_LUCE",
    }
)


def scheda(identificatore: str) -> SchedaAsset:
    """Restituisce la scheda richiesta o quella predefinita se non esiste."""
    return _SCHEDE_PER_ID.get(str(identificatore), _SCHEDE_PER_ID[ID_PREDEFINITO])


def identificatore_valido(identificatore: str) -> bool:
    """Indica se l'identificatore corrisponde a un modello dichiarato."""
    return str(identificatore) in _SCHEDE_PER_ID


def voci_elenco() -> tuple[tuple[str, str, str], ...]:
    """Voci dell'elenco a discesa, con nome e descrizione in italiano."""
    return tuple(
        (voce.identificatore, voce.nome, voce.descrizione)
        for voce in SCHEDE
    )


def nome_campo(chiave: str) -> str:
    """Etichetta italiana del parametro indicato."""
    return TESTI[CAMPI[chiave]]


def parametri(stato, identificatore: str) -> dict[str, object]:
    """Legge soltanto i parametri usati dal modello selezionato."""
    voce = scheda(identificatore)
    return {chiave: getattr(stato, chiave) for chiave in voce.campi}
