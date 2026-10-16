"""Regole dell'aspetto della scena: materiali, luci, telecamera e immagine finale.

Questo modulo non dipende da Blender: descrive *che cosa* si può scegliere e con
quali valori. I materiali pronti dichiarano i loro numeri veri (colore, ruvidità,
metallico, trasparenza), la tavolozza dichiara i colori con un nome italiano,
le illuminazioni dichiarano le luci e lo sfondo, le qualità dichiarano
risoluzione e campioni. Chi applica davvero i valori è `blender/`: così le
regole si verificano senza aprire Blender e i comandi restano brevi.

Nessun materiale entra nell'elenco se non è configurato correttamente: la
trasparenza compare solo dove ha senso (il vetro) e i valori stanno nei limiti
fisici del nodo principale di Blender (0–1).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, replace
from datetime import datetime

from .. import configuration
from ..localization import TESTI

# Materiali pronti, nell'ordine in cui compaiono nel pannello.
MATERIALE_PLASTICA_OPACA = "plastica_opaca"
MATERIALE_METALLO = "metallo"
MATERIALE_LEGNO_STILIZZATO = "legno_stilizzato"
MATERIALE_VETRO = "vetro"
MATERIALE_CERAMICA = "ceramica"
MATERIALE_GOMMA = "gomma"

# Illuminazioni: la prima è l'azione automatica, le altre sono le situazioni
# tipiche. "automatica" si adatta alla grandezza della scena, le altre usano
# una disposizione fissa studiata per oggetti di qualche metro.
ILLUMINAZIONE_AUTOMATICA = "automatica"
ILLUMINAZIONE_PRODOTTO = "prodotto"
ILLUMINAZIONE_INTERNO_SEMPLICE = "interno_semplice"
ILLUMINAZIONE_ESTERNO_SEMPLICE = "esterno_semplice"
ILLUMINAZIONE_STUDIO_NEUTRO = "studio_neutro"

# Qualità dell'immagine finale: valori prudenti, pensati per un computer
# normale. La qualità alta non alza la risoluzione oltre quella della scena:
# alza solo i campioni, che è la differenza che si vede davvero.
QUALITA_ANTEPRIMA = "anteprima"
QUALITA_STANDARD = "standard"
QUALITA_ALTA = "alta"

MOTORE_COME_IN_BLENDER = "come_in_blender"
MOTORE_EEVEE = "eevee"
MOTORE_CYCLES = "cycles"

FORMATO_PNG = "png"
FORMATO_JPEG = "jpeg"

# Valori di partenza: la plastica opaca è neutra e va bene su qualsiasi forma;
# la qualità standard è già buona ma non pesante; il PNG non perde qualità.
MATERIALE_PREDEFINITO = MATERIALE_PLASTICA_OPACA
ILLUMINAZIONE_PREDEFINITA = ILLUMINAZIONE_PRODOTTO
QUALITA_PREDEFINITA = QUALITA_STANDARD
MOTORE_PREDEFINITO = MOTORE_COME_IN_BLENDER
FORMATO_PREDEFINITO = FORMATO_PNG

# Raggio di riferimento delle illuminazioni fisse: le luci sono posizionate
# per una scena di circa tre metri di raggio.
RAGGIO_RIFERIMENTO = 3.0
# Raggio usato quando la scena è vuota: una forma sola di due metri.
RAGGIO_SCENA_VUOTA = 2.0

# Motori di Blender corrispondenti alle voci semplici del pannello.
MOTORI_BLENDER = {
    MOTORE_EEVEE: "BLENDER_EEVEE_NEXT",
    MOTORE_CYCLES: "CYCLES",
}


@dataclass(frozen=True)
class Materiale:
    """Materiale pronto: come si chiama e con quali valori è configurato."""

    chiave: str
    colore: tuple[float, float, float]
    ruvidita: float
    metallico: float
    trasparenza: float = 0.0
    # La trasparenza si mostra solo dove ha senso: nel vetro.
    trasparenza_disponibile: bool = False
    # Un valore in più, usato solo dove serve davvero (il vetro è rifrangente).
    indice_rifrazione: float = 1.45
    parola_inglese: str = ""

    @property
    def nome(self) -> str:
        """Nome italiano mostrato nell'elenco dei materiali pronti."""
        return TESTI[CHIAVI_NOMI_MATERIALE[self.chiave]]

    @property
    def descrizione(self) -> str:
        """Spiegazione breve di come apparirà la superficie."""
        return TESTI[CHIAVI_DESCRIZIONI_MATERIALE[self.chiave]]

    def con_colore(self, colore) -> "Materiale":
        """Copia del materiale con un colore diverso."""
        return replace(self, colore=colore_valido(colore, self.colore))


CHIAVI_NOMI_MATERIALE = {
    MATERIALE_PLASTICA_OPACA: "MATERIALE_NOME_PLASTICA_OPACA",
    MATERIALE_METALLO: "MATERIALE_NOME_METALLO",
    MATERIALE_LEGNO_STILIZZATO: "MATERIALE_NOME_LEGNO_STILIZZATO",
    MATERIALE_VETRO: "MATERIALE_NOME_VETRO",
    MATERIALE_CERAMICA: "MATERIALE_NOME_CERAMICA",
    MATERIALE_GOMMA: "MATERIALE_NOME_GOMMA",
}

CHIAVI_DESCRIZIONI_MATERIALE = {
    MATERIALE_PLASTICA_OPACA: "MATERIALE_DESCRIZIONE_PLASTICA_OPACA",
    MATERIALE_METALLO: "MATERIALE_DESCRIZIONE_METALLO",
    MATERIALE_LEGNO_STILIZZATO: "MATERIALE_DESCRIZIONE_LEGNO_STILIZZATO",
    MATERIALE_VETRO: "MATERIALE_DESCRIZIONE_VETRO",
    MATERIALE_CERAMICA: "MATERIALE_DESCRIZIONE_CERAMICA",
    MATERIALE_GOMMA: "MATERIALE_DESCRIZIONE_GOMMA",
}

ORDINE_MATERIALI = (
    MATERIALE_PLASTICA_OPACA,
    MATERIALE_METALLO,
    MATERIALE_LEGNO_STILIZZATO,
    MATERIALE_VETRO,
    MATERIALE_CERAMICA,
    MATERIALE_GOMMA,
)

MATERIALI = {
    MATERIALE_PLASTICA_OPACA: Materiale(
        chiave=MATERIALE_PLASTICA_OPACA,
        colore=(0.35, 0.36, 0.38),
        ruvidita=0.55,
        metallico=0.0,
        parola_inglese="plastica",
    ),
    MATERIALE_METALLO: Materiale(
        chiave=MATERIALE_METALLO,
        colore=(0.55, 0.57, 0.60),
        ruvidita=0.28,
        metallico=1.0,
        parola_inglese="metallo",
    ),
    MATERIALE_LEGNO_STILIZZATO: Materiale(
        chiave=MATERIALE_LEGNO_STILIZZATO,
        colore=(0.16, 0.07, 0.03),
        ruvidita=0.62,
        metallico=0.0,
        parola_inglese="legno",
    ),
    MATERIALE_VETRO: Materiale(
        chiave=MATERIALE_VETRO,
        colore=(0.80, 0.87, 0.90),
        ruvidita=0.03,
        metallico=0.0,
        trasparenza=1.0,
        trasparenza_disponibile=True,
        indice_rifrazione=1.45,
        parola_inglese="vetro",
    ),
    MATERIALE_CERAMICA: Materiale(
        chiave=MATERIALE_CERAMICA,
        colore=(0.92, 0.88, 0.78),
        ruvidita=0.18,
        metallico=0.0,
        parola_inglese="ceramica",
    ),
    MATERIALE_GOMMA: Materiale(
        chiave=MATERIALE_GOMMA,
        colore=(0.03, 0.03, 0.035),
        ruvidita=0.85,
        metallico=0.0,
        parola_inglese="gomma",
    ),
}


@dataclass(frozen=True)
class Colore:
    """Colore della tavolozza, con un nome leggibile accanto al campione."""

    chiave: str
    rgb: tuple[float, float, float]

    @property
    def nome(self) -> str:
        """Nome italiano del colore, usato dal pulsante e dal suggerimento."""
        return TESTI[CHIAVI_NOMI_COLORE[self.chiave]]

    @property
    def aiuto(self) -> str:
        """Suggerimento del pulsante: dice che cosa cambia il colore."""
        return TESTI["AIUTO_COLORE_TAVOLOZZA"].format(nome=self.nome)


CHIAVI_NOMI_COLORE = {
    "panna": "COLORE_PANNA",
    "grigio": "COLORE_GRIGIO",
    "marrone": "COLORE_MARRONE",
    "azzurro": "COLORE_AZZURRO",
    "blu": "COLORE_BLU",
    "viola": "COLORE_VIOLA",
    "verde": "COLORE_VERDE",
    "giallo": "COLORE_GIALLO",
    "rosa": "COLORE_ROSA",
    "arancione": "COLORE_ARANCIONE",
    "rosso": "COLORE_ROSSO",
}

# Tavolozza accessibile: pochi colori, ben separati fra loro e con un nome
# scritto accanto. Il nome serve a chi distingue male i colori; il campo
# "Colore" resta per sceglierne uno qualsiasi.
ORDINE_TAVOLOZZA = (
    "panna",
    "grigio",
    "marrone",
    "azzurro",
    "blu",
    "viola",
    "verde",
    "giallo",
    "rosa",
    "arancione",
    "rosso",
)

TAVOLOZZA = {
    "panna": Colore("panna", (0.92, 0.88, 0.78)),
    "grigio": Colore("grigio", (0.35, 0.36, 0.38)),
    "marrone": Colore("marrone", (0.16, 0.07, 0.03)),
    "azzurro": Colore("azzurro", (0.20, 0.48, 0.75)),
    "blu": Colore("blu", (0.05, 0.13, 0.35)),
    "viola": Colore("viola", (0.20, 0.08, 0.35)),
    "verde": Colore("verde", (0.06, 0.28, 0.12)),
    "giallo": Colore("giallo", (0.80, 0.58, 0.06)),
    "rosa": Colore("rosa", (0.72, 0.35, 0.45)),
    "arancione": Colore("arancione", (0.75, 0.28, 0.05)),
    "rosso": Colore("rosso", (0.45, 0.04, 0.04)),
}


@dataclass(frozen=True)
class Luce:
    """Luce di una illuminazione pronta: posizione, potenza e colore.

    Le posizioni sono pensate per una scena di raggio pari a
    `RAGGIO_RIFERIMENTO`; le illuminazioni che si adattano alla scena vengono
    riscalate in proporzione.
    """

    nome_chiave: str
    tipo: str
    posizione: tuple[float, float, float]
    energia: float
    dimensione: float
    colore: tuple[float, float, float] = (1.0, 1.0, 1.0)
    # Ampiezza del disco del Sole, in radianti: più è grande, più l'ombra è morbida.
    angolo: float = 0.05


@dataclass(frozen=True)
class Illuminazione:
    """Illuminazione pronta: luci, sfondo e istruzioni per l'azione automatica."""

    chiave: str
    sfondo: tuple[float, float, float]
    sfondo_intensita: float
    luci: tuple[Luce, ...] = field(default_factory=tuple)
    adatta_alla_scena: bool = False

    @property
    def nome(self) -> str:
        """Nome italiano dell'illuminazione."""
        return TESTI[CHIAVI_NOMI_ILLUMINAZIONE[self.chiave]]

    @property
    def descrizione(self) -> str:
        """Spiegazione breve di quando usare questa illuminazione."""
        return TESTI[CHIAVI_DESCRIZIONI_ILLUMINAZIONE[self.chiave]]


CHIAVI_NOMI_ILLUMINAZIONE = {
    ILLUMINAZIONE_AUTOMATICA: "ILLUMINAZIONE_NOME_AUTOMATICA",
    ILLUMINAZIONE_PRODOTTO: "ILLUMINAZIONE_NOME_PRODOTTO",
    ILLUMINAZIONE_INTERNO_SEMPLICE: "ILLUMINAZIONE_NOME_INTERNO_SEMPLICE",
    ILLUMINAZIONE_ESTERNO_SEMPLICE: "ILLUMINAZIONE_NOME_ESTERNO_SEMPLICE",
    ILLUMINAZIONE_STUDIO_NEUTRO: "ILLUMINAZIONE_NOME_STUDIO_NEUTRO",
}

CHIAVI_DESCRIZIONI_ILLUMINAZIONE = {
    ILLUMINAZIONE_AUTOMATICA: "ILLUMINAZIONE_DESCRIZIONE_AUTOMATICA",
    ILLUMINAZIONE_PRODOTTO: "ILLUMINAZIONE_DESCRIZIONE_PRODOTTO",
    ILLUMINAZIONE_INTERNO_SEMPLICE: "ILLUMINAZIONE_DESCRIZIONE_INTERNO_SEMPLICE",
    ILLUMINAZIONE_ESTERNO_SEMPLICE: "ILLUMINAZIONE_DESCRIZIONE_ESTERNO_SEMPLICE",
    ILLUMINAZIONE_STUDIO_NEUTRO: "ILLUMINAZIONE_DESCRIZIONE_STUDIO_NEUTRO",
}

# Le quattro situazioni tipiche, nell'ordine dei pulsanti del pannello.
ORDINE_ILLUMINAZIONI = (
    ILLUMINAZIONE_PRODOTTO,
    ILLUMINAZIONE_INTERNO_SEMPLICE,
    ILLUMINAZIONE_ESTERNO_SEMPLICE,
    ILLUMINAZIONE_STUDIO_NEUTRO,
)

ILLUMINAZIONI = {
    ILLUMINAZIONE_AUTOMATICA: Illuminazione(
        chiave=ILLUMINAZIONE_AUTOMATICA,
        sfondo=(0.38, 0.39, 0.41),
        sfondo_intensita=0.40,
        luci=(
            Luce("NOME_LUCE_PRINCIPALE", "AREA", (-2.4, -2.8, 2.6), 420.0, 3.0),
            Luce("NOME_LUCE_RIEMPIMENTO", "AREA", (3.2, -1.0, 1.4), 160.0, 4.0),
            Luce("NOME_LUCE_CONTORNO", "AREA", (0.4, 3.0, 2.2), 260.0, 2.5),
        ),
        adatta_alla_scena=True,
    ),
    ILLUMINAZIONE_PRODOTTO: Illuminazione(
        chiave=ILLUMINAZIONE_PRODOTTO,
        sfondo=(0.36, 0.37, 0.39),
        sfondo_intensita=0.35,
        luci=(
            Luce("NOME_LUCE_PRINCIPALE", "AREA", (-2.5, -3.0, 2.6), 420.0, 3.0),
            Luce("NOME_LUCE_RIEMPIMENTO", "AREA", (3.0, -1.6, 1.6), 150.0, 4.0),
            Luce("NOME_LUCE_CONTORNO", "AREA", (0.6, 3.2, 2.4), 250.0, 2.5),
        ),
    ),
    ILLUMINAZIONE_INTERNO_SEMPLICE: Illuminazione(
        chiave=ILLUMINAZIONE_INTERNO_SEMPLICE,
        sfondo=(0.22, 0.20, 0.18),
        sfondo_intensita=0.30,
        luci=(
            Luce(
                "NOME_LUCE_SOFFITTO",
                "AREA",
                (0.0, 0.0, 2.8),
                320.0,
                3.0,
                colore=(1.0, 0.93, 0.84),
            ),
            Luce(
                "NOME_LUCE_FINESTRA",
                "AREA",
                (2.8, -1.2, 1.6),
                110.0,
                3.5,
                colore=(0.86, 0.92, 1.0),
            ),
        ),
    ),
    ILLUMINAZIONE_ESTERNO_SEMPLICE: Illuminazione(
        chiave=ILLUMINAZIONE_ESTERNO_SEMPLICE,
        sfondo=(0.28, 0.42, 0.62),
        sfondo_intensita=0.60,
        luci=(
            Luce(
                "NOME_LUCE_SOLE",
                "SUN",
                (-4.0, -3.0, 6.0),
                3.0,
                0.0,
                colore=(1.0, 0.96, 0.90),
                angolo=0.09,
            ),
            Luce(
                "NOME_LUCE_CIELO",
                "AREA",
                (3.0, 2.4, 3.6),
                200.0,
                6.0,
                colore=(0.76, 0.85, 1.0),
            ),
        ),
    ),
    ILLUMINAZIONE_STUDIO_NEUTRO: Illuminazione(
        chiave=ILLUMINAZIONE_STUDIO_NEUTRO,
        sfondo=(0.42, 0.42, 0.42),
        sfondo_intensita=0.50,
        luci=(
            Luce("NOME_LUCE_SINISTRA", "AREA", (-3.2, 0.0, 2.0), 300.0, 4.0),
            Luce("NOME_LUCE_DESTRA", "AREA", (3.2, 0.0, 2.0), 300.0, 4.0),
            Luce("NOME_LUCE_ALTO", "AREA", (0.0, 0.4, 3.6), 120.0, 5.0),
        ),
    ),
}


@dataclass(frozen=True)
class Qualita:
    """Qualità dell'immagine finale: valori prudenti, in chiaro."""

    chiave: str
    percentuale: int
    campioni_eevee: int
    campioni_cycles: int
    disturbo: bool

    @property
    def nome(self) -> str:
        """Nome italiano della qualità."""
        return TESTI[CHIAVI_NOMI_QUALITA[self.chiave]]

    @property
    def descrizione(self) -> str:
        """Spiegazione breve di che cosa comporta questa qualità."""
        return TESTI[CHIAVI_DESCRIZIONI_QUALITA[self.chiave]]

    def campioni(self, motore: str) -> int:
        """Campioni consigliati per il motore indicato da Blender."""
        if str(motore).upper() == "CYCLES":
            return self.campioni_cycles
        return self.campioni_eevee


CHIAVI_NOMI_QUALITA = {
    QUALITA_ANTEPRIMA: "QUALITA_NOME_ANTEPRIMA",
    QUALITA_STANDARD: "QUALITA_NOME_STANDARD",
    QUALITA_ALTA: "QUALITA_NOME_ALTA",
}

CHIAVI_DESCRIZIONI_QUALITA = {
    QUALITA_ANTEPRIMA: "QUALITA_DESCRIZIONE_ANTEPRIMA",
    QUALITA_STANDARD: "QUALITA_DESCRIZIONE_STANDARD",
    QUALITA_ALTA: "QUALITA_DESCRIZIONE_ALTA",
}

ORDINE_QUALITA = (QUALITA_ANTEPRIMA, QUALITA_STANDARD, QUALITA_ALTA)

QUALITA = {
    QUALITA_ANTEPRIMA: Qualita(
        chiave=QUALITA_ANTEPRIMA,
        percentuale=50,
        campioni_eevee=16,
        campioni_cycles=24,
        disturbo=False,
    ),
    QUALITA_STANDARD: Qualita(
        chiave=QUALITA_STANDARD,
        percentuale=100,
        campioni_eevee=64,
        campioni_cycles=64,
        disturbo=True,
    ),
    QUALITA_ALTA: Qualita(
        chiave=QUALITA_ALTA,
        percentuale=100,
        campioni_eevee=128,
        campioni_cycles=256,
        disturbo=True,
    ),
}

NOMI_MOTORI = {
    MOTORE_COME_IN_BLENDER: "MOTORE_NOME_COME_IN_BLENDER",
    MOTORE_EEVEE: "MOTORE_NOME_EEVEE",
    MOTORE_CYCLES: "MOTORE_NOME_CYCLES",
}

DESCRIZIONI_MOTORI = {
    MOTORE_COME_IN_BLENDER: "MOTORE_DESCRIZIONE_COME_IN_BLENDER",
    MOTORE_EEVEE: "MOTORE_DESCRIZIONE_EEVEE",
    MOTORE_CYCLES: "MOTORE_DESCRIZIONE_CYCLES",
}

ORDINE_MOTORI = (MOTORE_COME_IN_BLENDER, MOTORE_EEVEE, MOTORE_CYCLES)

NOMI_FORMATI = {
    FORMATO_PNG: "FORMATO_NOME_PNG",
    FORMATO_JPEG: "FORMATO_NOME_JPEG",
}

DESCRIZIONI_FORMATI = {
    FORMATO_PNG: "FORMATO_DESCRIZIONE_PNG",
    FORMATO_JPEG: "FORMATO_DESCRIZIONE_JPEG",
}

ESTENSIONI_FORMATI = {
    FORMATO_PNG: ".png",
    FORMATO_JPEG: ".jpg",
}

FORMATI_BLENDER = {
    FORMATO_PNG: "PNG",
    FORMATO_JPEG: "JPEG",
}

ORDINE_FORMATI = (FORMATO_PNG, FORMATO_JPEG)


# ------------------------------------------------------------------- lettura


def materiale(chiave: str) -> Materiale:
    """Materiale pronto della chiave indicata, con ripiego sul predefinito."""
    return MATERIALI.get(str(chiave), MATERIALI[MATERIALE_PREDEFINITO])


def colore(chiave: str):
    """Colore della tavolozza, oppure None se la chiave non esiste."""
    return TAVOLOZZA.get(str(chiave))


def limita(valore: float, minimo: float, massimo: float) -> float:
    """Riporta un numero dentro i limiti indicati, senza mai fallire."""
    try:
        numero = float(valore)
    except (TypeError, ValueError):
        return float(minimo)
    return max(float(minimo), min(float(massimo), numero))




def colore_valido(colore, ripiego=(0.5, 0.5, 0.5)) -> tuple[float, float, float]:
    """Riporta un colore a tre canali dentro i limiti 0–1.

    I campi colore di Blender hanno sempre tre componenti, ma un valore scritto
    da uno script può averne meno: senza questo controllo un colore corto
    arriverebbe fino al materiale e lo renderebbe imprevedibile.
    """
    if colore is None:
        return tuple(float(valore) for valore in ripiego[:3])
    canali = [limita(valore, 0.0, 1.0) for valore in list(colore)[:3]]
    for posizione in range(len(canali), 3):
        canali.append(float(ripiego[posizione]))
    return (canali[0], canali[1], canali[2])


def componi(
    chiave: str,
    colore_scelto=None,
    ruvidita: float | None = None,
    metallico: float | None = None,
    trasparenza: float | None = None,
) -> Materiale:
    """Materiale pronto con i valori corretti dall'utente.

    La trasparenza si applica solo dove ha senso: su un materiale che non la
    prevede resta a zero, così il vetro non diventa una superficie opaca
    "trasparente" per errore.
    """
    base = materiale(chiave)
    valori = base.con_colore(colore_scelto) if colore_scelto is not None else base
    if ruvidita is not None:
        valori = replace(
            valori,
            ruvidita=limita(
                ruvidita, configuration.MATERIALE_RUVIDITA_MINIMA, configuration.MATERIALE_RUVIDITA_MASSIMA
            ),
        )
    if metallico is not None:
        valori = replace(
            valori,
            metallico=limita(
                metallico,
                configuration.MATERIALE_METALLICO_MINIMO,
                configuration.MATERIALE_METALLICO_MASSIMO,
            ),
        )
    if trasparenza is not None:
        valori = replace(
            valori,
            trasparenza=(
                limita(
                    trasparenza,
                    configuration.MATERIALE_TRASPARENZA_MINIMA,
                    configuration.MATERIALE_TRASPARENZA_MASSIMA,
                )
                if base.trasparenza_disponibile
                else 0.0
            ),
        )
    return valori


def illuminazione(chiave: str) -> Illuminazione:
    """Illuminazione pronta della chiave indicata, con ripiego sulla predefinita."""
    return ILLUMINAZIONI.get(str(chiave), ILLUMINAZIONI[ILLUMINAZIONE_PREDEFINITA])


def qualita(chiave: str) -> Qualita:
    """Qualità dell'immagine finale, con ripiego sulla predefinita."""
    return QUALITA.get(str(chiave), QUALITA[QUALITA_PREDEFINITA])


def voci_materiali() -> tuple[tuple[str, str, str], ...]:
    """Voci dell'elenco dei materiali pronti, per l'interfaccia."""
    return tuple(
        (chiave, MATERIALI[chiave].nome, MATERIALI[chiave].descrizione)
        for chiave in ORDINE_MATERIALI
    )


def voci_tavolozza() -> tuple[tuple[str, str, str], ...]:
    """Voci dell'elenco dei colori della tavolozza, per l'interfaccia."""
    return tuple((chiave, TAVOLOZZA[chiave].nome, TAVOLOZZA[chiave].aiuto) for chiave in ORDINE_TAVOLOZZA)


def voci_qualita() -> tuple[tuple[str, str, str], ...]:
    """Voci dell'elenco delle qualità dell'immagine finale."""
    return tuple(
        (chiave, QUALITA[chiave].nome, QUALITA[chiave].descrizione) for chiave in ORDINE_QUALITA
    )


def voci_motori() -> tuple[tuple[str, str, str], ...]:
    """Voci dell'elenco dei motori di creazione dell'immagine."""
    return tuple(
        (chiave, TESTI[NOMI_MOTORI[chiave]], TESTI[DESCRIZIONI_MOTORI[chiave]])
        for chiave in ORDINE_MOTORI
    )


def voci_formati() -> tuple[tuple[str, str, str], ...]:
    """Voci dell'elenco dei formati dell'immagine finale."""
    return tuple(
        (chiave, TESTI[NOMI_FORMATI[chiave]], TESTI[DESCRIZIONI_FORMATI[chiave]])
        for chiave in ORDINE_FORMATI
    )


# ------------------------------------------------------------------- nomi


def nome_libero(base: str, esistenti) -> str:
    """Nome non ancora usato, aggiungendo un numero solo quando serve.

    Serve a due cose diverse: dare un nome al materiale applicato senza
    sovrascrivere quello di un altro oggetto, e creare una variazione senza
    toccare il materiale di partenza.
    """
    occupati = {str(nome) for nome in esistenti}
    base = str(base).strip() or TESTI["MATERIALE_NOME_VARIAZIONE_BASE"]
    base = base[: configuration.LUNGHEZZA_MASSIMA_NOME]
    if base not in occupati:
        return base
    for numero in range(2, 1000):
        suffisso = f" {numero}"
        candidato = f"{base[: configuration.LUNGHEZZA_MASSIMA_NOME - len(suffisso)]}{suffisso}"
        if candidato not in occupati:
            return candidato
    return base


def nome_materiale(materiale_scelto: Materiale, esistenti) -> str:
    """Nome del nuovo materiale da creare per il materiale pronto indicato."""
    return nome_libero(materiale_scelto.nome, esistenti)


def nome_variazione(nome_materiale_attuale: str, esistenti) -> str:
    """Nome della variazione, così si capisce da quale materiale deriva."""
    base = TESTI["MATERIALE_NOME_VARIAZIONE"].format(nome=str(nome_materiale_attuale))
    return nome_libero(base, esistenti)


def nome_file_immagine(quando: datetime | None, formato: str) -> str:
    """Nome del file dell'immagine finale, con data e ora per non sovrascrivere."""
    quando = datetime.now() if quando is None else quando
    estensione = ESTENSIONI_FORMATI.get(str(formato), ESTENSIONI_FORMATI[FORMATO_PREDEFINITO])
    return f"{TESTI['IMMAGINE_PREFISSO_FILE']}_{quando:%Y%m%d_%H%M%S}{estensione}"


# ------------------------------------------------------------------ percorso


def cartella_problema(cartella: str) -> str:
    """Chiave del testo da mostrare se la cartella scelta non va bene.

    Restituisce una stringa vuota quando la cartella è utilizzabile: chi
    chiama distingue subito il caso buono senza leggere messaggi.
    """
    percorso = str(cartella or "").strip()
    if not percorso:
        return "ERRORE_CARTELLA_MANCANTE"
    if not os.path.isdir(percorso):
        return "ERRORE_CARTELLA_INESISTENTE"
    if not os.access(percorso, os.W_OK):
        return "ERRORE_CARTELLA_NON_SCRIVIBILE"
    return ""


def percorso_immagine(cartella: str, nome_file: str) -> str:
    """Percorso completo del file dell'immagine finale."""
    return os.path.join(str(cartella), str(nome_file))


# ------------------------------------------------------------------ memoria


def pixel_immagine(larghezza: int, altezza: int, percentuale: int) -> int:
    """Numero di pixel dell'immagine finale, in base alla risoluzione della scena."""
    larghezza = max(int(larghezza), 1)
    altezza = max(int(altezza), 1)
    percentuale = max(int(percentuale), 1)
    return max(larghezza * percentuale // 100, 1) * max(altezza * percentuale // 100, 1)


def stima_memoria_mb(pixel: int) -> float:
    """Stima prudente della memoria richiesta per creare un'immagine.

    Un'immagine a colori con trasparenza occupa sedici byte per pixel; il
    calcolo usa il quadruplo, perché durante la creazione Blender tiene più
    copie dell'immagine in memoria (sfondo, passaggi e riduzione del disturbo).
    È una stima, non una misura: serve a fermarsi prima di far soffrire il
    computer, non a promettere un numero esatto.
    """
    return max(int(pixel), 1) * configuration.BYTE_PER_PIXEL_STIMA / (1024.0 * 1024.0)
