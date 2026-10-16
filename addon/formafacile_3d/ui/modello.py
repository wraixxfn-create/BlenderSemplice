"""Modello dei dati mostrati dall'interfaccia.

Questo modulo non dipende da Blender: descrive in modo dichiarativo che cosa
l'interfaccia deve mostrare. Il disegno vero e proprio è compito di
`ui/renderer.py`, così le regole dell'interfaccia restano verificabili senza
aprire Blender.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union


@dataclass(frozen=True)
class Azione:
    """Pulsante che richiama un comando di FormaFacile."""

    idname: str
    testo: str
    icona: str = ""
    premuto: bool = False
    solo_icona: bool = False
    parametri: tuple[tuple[str, object], ...] = ()


@dataclass(frozen=True)
class Campo:
    """Campo collegato a un dato reale della scena.

    Con `indice` si disegna un solo asse di una proprietà a tre valori (per
    esempio la sola X della posizione): è così che i campi numerici restano
    brevi e leggibili nella barra laterale.
    """

    riferimento: str
    chiave: str
    proprieta: str
    testo: str = ""
    icona: str = ""
    solo_icona: bool = False
    espanso: bool = False
    interruttore: bool = False
    indice: int | None = None


@dataclass(frozen=True)
class Etichetta:
    """Testo semplice; con `avviso` viene evidenziato come avvertimento."""

    testo: str
    icona: str = ""
    avviso: bool = False
    evidenzia: bool = False


Elemento = Union[Azione, Campo, Etichetta]


@dataclass(frozen=True)
class Riga:
    """Una riga orizzontale di elementi."""

    elementi: tuple[Elemento, ...]
    distanziata: bool = False
    disabilitata: bool = False


@dataclass(frozen=True)
class Gruppo:
    """Riquadro con titolo che raccoglie comandi dello stesso risultato."""

    titolo: str
    righe: tuple[Riga, ...]


@dataclass(frozen=True)
class Pannello:
    """Contenuto di un pannello della barra laterale."""

    chiave: str
    gruppi: tuple[Gruppo, ...]


@dataclass(frozen=True)
class Oggetto:
    """Fotografia dei dati di un oggetto utili all'interfaccia."""

    chiave: str
    nome: str
    tipo: str
    tipo_parola: str
    icona: str
    scelto: bool = False
    attivo: bool = False
    # `nascosto` vale anche quando è la raccolta a nascondere l'oggetto;
    # `nascosto_direttamente` dice invece se il nascondimento è un interruttore
    # dell'oggetto, che FormaFacile può rimettere a posto.
    nascosto: bool = False
    nascosto_direttamente: bool = False
    bloccato: bool = False
    modo_rotazione: str = "XYZ"
    nome_dati: str = ""
    vertici: int = 0
    facce: int = 0
    # Aspetto della superficie: `True` quando la forma si vede liscia.
    liscio: bool = False
    potenza_luce: float = 0.0
    telecamera_principale: bool = False


@dataclass(frozen=True)
class Raccolta:
    """Fotografia di un gruppo della scena, per l'interfaccia.

    Un gruppo di FormaFacile è una raccolta di Blender: si sceglie e si nasconde
    tutto insieme. L'interfaccia ne ha bisogno per mostrare l'elenco dei gruppi
    senza sapere nulla di Blender.
    """

    chiave: str
    nome: str
    quanti: int = 0
    scelti: int = 0
    nascosto: bool = False


@dataclass(frozen=True)
class Modificatore:
    """Fotografia di una modifica non applicata, letta dall'oggetto attivo.

    `parola` è il nome semplice del tipo di modifica ("Specchio"), `problema` è
    la spiegazione di quando la modifica non fa quello che promette (per
    esempio una serie senza il centro del giro).
    """

    chiave: str
    nome: str
    parola: str = ""
    icona: str = ""
    problema: str = ""


@dataclass(frozen=True)
class Contesto:
    """Tutto ciò che serve per decidere che cosa mostrare."""

    modalita: str
    in_modalita_oggetto: bool
    oggetti: tuple[Oggetto, ...] = ()
    filtro: str = ""
    passo: float = 0.5
    messaggio: str = ""
    messaggio_recente: bool = False
    vista_disponibile: bool = True
    limite_elenco: int = 12
    soglia_filtro: int = 8
    gradi_rotazione: float = 15.0
    percentuale_scala: int = 10
    # Unità lette dalla scena: l'interfaccia le scrive accanto ai numeri, così
    # "2" diventa "2 m" e "15" diventa "15°" senza inventare nulla.
    unita_lunghezza: str = "m"
    unita_angolo: str = "°"
    grandezza_forma: float = 2.0

    @property
    def unita_lunghezza_o_predefinita(self) -> str:
        """Unità di lunghezza, con ripiego sui metri quando la scena non ne usa."""
        return self.unita_lunghezza or "m"

    # Gruppi della scena e modifiche non applicate sull'oggetto attivo: le
    # legge `ui/vista.py` dai servizi di Blender e l'interfaccia le disegna.
    raccolte: tuple[Raccolta, ...] = ()
    modificatori: tuple[Modificatore, ...] = ()
    # Guida passo passo in corso: la chiave e il passo mostrato.
    guida: str = ""
    passo_guida: int = 0
    # Modello scelto nella libreria e descrizione mostrata prima dell'inserimento.
    asset_selezionato: str = "tavolino"
    asset_descrizione: str = ""

    # Campi derivati, calcolati una volta sola.
    elenco: tuple[Oggetto, ...] = field(default=(), repr=False)

    @property
    def scelti(self) -> tuple[Oggetto, ...]:
        """Oggetti scelti, nell'ordine dell'elenco."""
        return tuple(oggetto for oggetto in self.oggetti if oggetto.scelto)

    @property
    def attivo(self) -> Oggetto | None:
        """Oggetto attivo, se presente nell'elenco."""
        for oggetto in self.oggetti:
            if oggetto.attivo:
                return oggetto
        return None

    @property
    def nascosti(self) -> tuple[Oggetto, ...]:
        """Oggetti nascosti nella Vista 3D."""
        return tuple(oggetto for oggetto in self.oggetti if oggetto.nascosto)

    def filtrati(self) -> tuple[Oggetto, ...]:
        """Oggetti che superano il filtro di ricerca per nome."""
        if not self.filtro.strip():
            return self.oggetti
        cercato = self.filtro.strip().casefold()
        return tuple(oggetto for oggetto in self.oggetti if cercato in oggetto.nome.casefold())


def crea_contesto(**valori: object) -> Contesto:
    """Costruisce un contesto applicando i valori predefiniti della configurazione."""
    from .. import configuration

    valori.setdefault("modalita", configuration.MODALITA_SEMPLICE)
    valori.setdefault("in_modalita_oggetto", True)
    valori.setdefault("passo", configuration.PASSO_PREDEFINITO)
    valori.setdefault("limite_elenco", configuration.LIMITE_ELENCO_SEMPLICE)
    valori.setdefault("soglia_filtro", configuration.SOGLIA_FILTRO)
    valori.setdefault("gradi_rotazione", configuration.ANGOLO_PREDEFINITO_GRADI)
    valori.setdefault(
        "percentuale_scala",
        int(round((configuration.FATTORE_SCALA_PREDEFINITO - 1.0) * 100)),
    )
    valori.setdefault("unita_lunghezza", "m")
    valori.setdefault("unita_angolo", "°")
    valori.setdefault("grandezza_forma", configuration.DIMENSIONE_FORMA_PREDEFINITA)
    return Contesto(**valori)  # type: ignore[arg-type]
