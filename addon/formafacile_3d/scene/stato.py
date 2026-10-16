"""Stato della scena usato dall'interfaccia: modalità, ricerca, passo, grandezza, messaggio.

Lo stato vive nella scena (un gruppo di proprietà chiamato `formafacile`):
funziona con qualsiasi modo di caricamento del componente aggiuntivo e viene
salvato insieme al progetto, quindi un principiante ritrova la modalità
semplice quando riapre il proprio file.
"""

from __future__ import annotations

import time

import bpy

from .. import comandi, configuration
from ..localization import TESTI
from . import aspetto, libreria


def _voci_asse_allinea():
    """Voci dell'asse di allineamento, con i testi italiani.

    Le voci si costruiscono in una funzione, non dentro l'annotazione della
    proprietà: Blender rilegge le annotazioni quando registra la classe e una
    comprensione scritta lì dentro fallirebbe in quel momento.
    """
    return tuple(
        (asse, TESTI[comandi.TESTI_ASSE[asse]], TESTI[comandi.AIUTI_ASSE[asse]])
        for asse in comandi.ASSI
    )


def _voci_bordo_allinea():
    """Voci del bordo di allineamento: inizio, centro o fine."""
    return tuple(
        (modo, TESTI[comandi.TESTI_ALLINEAMENTO[modo]], TESTI["AIUTO_BORDO_ALLINEA"])
        for modo in comandi.MODI_ALLINEAMENTO
    )


def _voci_riferimento_allinea():
    """Voci del riferimento: il bordo della forma o il suo punto di riferimento."""
    return tuple(
        (
            chiave,
            TESTI[comandi.TESTI_RIFERIMENTO[chiave]],
            TESTI["AIUTO_RIFERIMENTO_ALLINEA"],
        )
        for chiave in comandi.RIFERIMENTI_ALLINEAMENTO
    )


_PREIMPOSTAZIONI_ASSET = {
    libreria.ASSET_TAVOLINO: {"asset_larghezza": 1.2, "asset_profondita": 0.7, "asset_altezza": 0.75, "asset_spessore": 0.06, "asset_spessore_gamba": 0.07},
    libreria.ASSET_SCAFFALE: {"asset_larghezza": 1.2, "asset_profondita": 0.35, "asset_altezza": 2.0, "asset_spessore": 0.04, "asset_numero_ripiani": 3},
    libreria.ASSET_SEDIA: {"asset_larghezza": 0.45, "asset_profondita": 0.5, "asset_altezza": 0.9, "asset_spessore": 0.045, "asset_spessore_gamba": 0.05},
    libreria.ASSET_PIEDISTALLO: {"asset_larghezza": 0.8, "asset_profondita": 0.8, "asset_altezza": 1.2, "asset_spessore": 0.08},
    libreria.ASSET_VASO: {"asset_altezza": 0.5, "asset_raggio": 0.2, "asset_spessore_parete": 0.02},
    libreria.ASSET_INSEGNA: {"asset_larghezza": 1.2, "asset_altezza": 0.6, "asset_spessore": 0.06},
    libreria.ASSET_STANZA: {"asset_larghezza": 4.0, "asset_profondita": 4.0, "asset_altezza": 3.0, "asset_spessore": 0.12},
    libreria.ASSET_PEDANA: {"asset_diametro": 1.2, "asset_altezza": 0.12},
    libreria.ASSET_SET_FOTOGRAFICO: {"asset_larghezza": 4.0, "asset_profondita": 3.5, "asset_altezza": 3.0, "asset_spessore": 0.08, "asset_potenza_luce": 1200.0},
    libreria.ASSET_FORMA_STAMPA: {"asset_grandezza": 0.5},
}


def _aggiorna_preimpostazione_asset(stato, _contesto) -> None:
    """Carica misure di partenza adatte al modello appena selezionato."""
    for nome, valore in _PREIMPOSTAZIONI_ASSET.get(stato.asset_selezionato, {}).items():
        setattr(stato, nome, valore)


def _aggiorna_materiale(stato, _contesto) -> None:
    """Riporta i valori a quelli del materiale appena scelto.

    Colore, ruvidità, metallico e trasparenza cambiano insieme al materiale
    scelto: evitano che il pannello mostri, per esempio, un vetro con la
    ruvidità della gomma e faccia applicare qualcosa che non si è scelto.
    """
    valori = aspetto.materiale(stato.materiale_scelto)
    stato.materiale_colore = valori.colore
    stato.materiale_ruvidita = valori.ruvidita
    stato.materiale_metallico = valori.metallico
    stato.materiale_trasparenza = valori.trasparenza


class FORMAFACILE_PG_stato(bpy.types.PropertyGroup):
    """Proprietà salvate nella scena per l'interfaccia semplice."""

    modalita: bpy.props.EnumProperty(
        name=TESTI["ETICHETTA_MODALITA"],
        description=TESTI["AIUTO_MODALITA_SEMPLICE"],
        items=(
            (configuration.MODALITA_SEMPLICE, TESTI["MODALITA_SEMPLICE"], TESTI["AIUTO_MODALITA_SEMPLICE"]),
            (configuration.MODALITA_COMPLETA, TESTI["MODALITA_COMPLETA"], TESTI["AIUTO_MODALITA_COMPLETA"]),
        ),
        default=configuration.MODALITA_SEMPLICE,
    )
    filtro: bpy.props.StringProperty(
        name=TESTI["ETICHETTA_CERCA"],
        description=TESTI["AIUTO_CERCA"],
        default="",
    )
    passo: bpy.props.FloatProperty(
        name=TESTI["ETICHETTA_PASSO"],
        description=TESTI["AIUTO_PASSO"],
        default=configuration.PASSO_PREDEFINITO,
        min=configuration.PASSO_MINIMO,
        max=configuration.PASSO_MASSIMO,
        precision=2,
        unit="LENGTH",
    )
    grandezza_forma: bpy.props.FloatProperty(
        name=TESTI["ETICHETTA_GRANDEZZA"],
        description=TESTI["AIUTO_GRANDEZZA"],
        default=configuration.DIMENSIONE_FORMA_PREDEFINITA,
        min=configuration.DIMENSIONE_FORMA_MINIMA,
        max=configuration.DIMENSIONE_FORMA_MASSIMA,
        precision=2,
        unit="LENGTH",
    )
    asset_selezionato: bpy.props.EnumProperty(
        name=TESTI["ASSET_SELEZIONA"],
        description=TESTI["ASSET_AIUTO_SELEZIONA"],
        items=libreria.voci_elenco(),
        default=libreria.ID_PREDEFINITO,
        update=_aggiorna_preimpostazione_asset,
    )
    asset_larghezza: bpy.props.FloatProperty(
        name=TESTI["ASSET_CAMPO_LARGHEZZA"], description=TESTI["ASSET_CAMPO_LARGHEZZA"],
        default=1.2, min=0.05, max=50.0, precision=2, unit="LENGTH",
    )
    asset_profondita: bpy.props.FloatProperty(
        name=TESTI["ASSET_CAMPO_PROFONDITA"], description=TESTI["ASSET_CAMPO_PROFONDITA"],
        default=0.7, min=0.05, max=50.0, precision=2, unit="LENGTH",
    )
    asset_altezza: bpy.props.FloatProperty(
        name=TESTI["ASSET_CAMPO_ALTEZZA"], description=TESTI["ASSET_CAMPO_ALTEZZA"],
        default=0.75, min=0.05, max=50.0, precision=2, unit="LENGTH",
    )
    asset_spessore: bpy.props.FloatProperty(
        name=TESTI["ASSET_CAMPO_SPESSORE"], description=TESTI["ASSET_CAMPO_SPESSORE"],
        default=0.06, min=0.005, max=5.0, precision=3, unit="LENGTH",
    )
    asset_spessore_gamba: bpy.props.FloatProperty(
        name=TESTI["ASSET_CAMPO_SPESSORE_GAMBA"], description=TESTI["ASSET_CAMPO_SPESSORE_GAMBA"],
        default=0.07, min=0.01, max=5.0, precision=3, unit="LENGTH",
    )
    asset_numero_ripiani: bpy.props.IntProperty(
        name=TESTI["ASSET_CAMPO_NUMERO_RIPIANI"],
        description=TESTI["ASSET_CAMPO_NUMERO_RIPIANI"], default=3, min=1, max=8,
    )
    asset_raggio: bpy.props.FloatProperty(
        name=TESTI["ASSET_CAMPO_RAGGIO"], description=TESTI["ASSET_CAMPO_RAGGIO"],
        default=0.2, min=0.03, max=10.0, precision=2, unit="LENGTH",
    )
    asset_spessore_parete: bpy.props.FloatProperty(
        name=TESTI["ASSET_CAMPO_SPESSORE_PARETE"],
        description=TESTI["ASSET_CAMPO_SPESSORE_PARETE"],
        default=0.02, min=0.002, max=2.0, precision=3, unit="LENGTH",
    )
    asset_testo: bpy.props.StringProperty(
        name=TESTI["ASSET_CAMPO_TESTO"], description=TESTI["ASSET_CAMPO_TESTO"],
        default="CIAO", maxlen=64,
    )
    asset_colore: bpy.props.FloatVectorProperty(
        name=TESTI["ASSET_CAMPO_COLORE"], description=TESTI["ASSET_CAMPO_COLORE"],
        subtype="COLOR", size=4, min=0.0, max=1.0, default=(0.56, 0.32, 0.16, 1.0),
    )
    asset_diametro: bpy.props.FloatProperty(
        name=TESTI["ASSET_CAMPO_DIAMETRO"], description=TESTI["ASSET_CAMPO_DIAMETRO"],
        default=1.2, min=0.05, max=50.0, precision=2, unit="LENGTH",
    )
    asset_grandezza: bpy.props.FloatProperty(
        name=TESTI["ASSET_CAMPO_GRANDEZZA"], description=TESTI["ASSET_CAMPO_GRANDEZZA"],
        default=0.5, min=0.05, max=20.0, precision=2, unit="LENGTH",
    )
    asset_potenza_luce: bpy.props.FloatProperty(
        name=TESTI["ASSET_CAMPO_POTENZA_LUCE"], description=TESTI["ASSET_CAMPO_POTENZA_LUCE"],
        default=1200.0, min=10.0, max=20000.0, precision=0,
    )
    # Impostazioni dell'allineamento: si scelgono una volta e valgono per ogni
    # pressione di Allinea e Spazia, come la modalità di lavoro.
    asse_allinea: bpy.props.EnumProperty(
        name=TESTI["ETICHETTA_ASSE_ALLINEA"],
        description=TESTI["AIUTO_ASSE_ALLINEA"],
        items=_voci_asse_allinea(),
        default=configuration.ALLINEA_ASSE_PREDEFINITO,
    )
    bordo_allinea: bpy.props.EnumProperty(
        name=TESTI["ETICHETTA_BORDO_ALLINEA"],
        description=TESTI["AIUTO_BORDO_ALLINEA"],
        items=_voci_bordo_allinea(),
        default=configuration.ALLINEA_BORDO_PREDEFINITO,
    )
    riferimento_allinea: bpy.props.EnumProperty(
        name=TESTI["ETICHETTA_RIFERIMENTO_ALLINEA"],
        description=TESTI["AIUTO_RIFERIMENTO_ALLINEA"],
        items=_voci_riferimento_allinea(),
        default=configuration.ALLINEA_RIFERIMENTO_PREDEFINITO,
    )
    # Aspetto della scena: materiale pronto scelto e valori da applicare.
    # Cambiando materiale i valori si riportano a quelli della ricetta, così il
    # pannello non mostra mai numeri che non appartengono al materiale scelto.
    materiale_scelto: bpy.props.EnumProperty(
        name=TESTI["ETICHETTA_MATERIALE_SCELTO"],
        description=TESTI["AIUTO_MATERIALE_SCELTO"],
        items=aspetto.voci_materiali(),
        default=aspetto.MATERIALE_PREDEFINITO,
        update=_aggiorna_materiale,
    )
    materiale_colore: bpy.props.FloatVectorProperty(
        name=TESTI["ETICHETTA_COLORE_MATERIALE"],
        description=TESTI["AIUTO_COLORE_MATERIALE"],
        subtype="COLOR", size=3, min=0.0, max=1.0,
        default=aspetto.materiale(aspetto.MATERIALE_PREDEFINITO).colore,
    )
    materiale_ruvidita: bpy.props.FloatProperty(
        name=TESTI["ETICHETTA_RUVIDITA"],
        description=TESTI["AIUTO_RUVIDITA"],
        default=aspetto.materiale(aspetto.MATERIALE_PREDEFINITO).ruvidita,
        min=configuration.MATERIALE_RUVIDITA_MINIMA,
        max=configuration.MATERIALE_RUVIDITA_MASSIMA,
        precision=2,
    )
    materiale_metallico: bpy.props.FloatProperty(
        name=TESTI["ETICHETTA_METALLICO"],
        description=TESTI["AIUTO_METALLICO"],
        default=aspetto.materiale(aspetto.MATERIALE_PREDEFINITO).metallico,
        min=configuration.MATERIALE_METALLICO_MINIMO,
        max=configuration.MATERIALE_METALLICO_MASSIMO,
        precision=2,
    )
    materiale_trasparenza: bpy.props.FloatProperty(
        name=TESTI["ETICHETTA_TRASPARENZA_MATERIALE"],
        description=TESTI["AIUTO_TRASPARENZA_MATERIALE"],
        default=aspetto.materiale(aspetto.MATERIALE_PREDEFINITO).trasparenza,
        min=configuration.MATERIALE_TRASPARENZA_MINIMA,
        max=configuration.MATERIALE_TRASPARENZA_MASSIMA,
        precision=2,
    )
    # Illuminazione applicata, sfondo e potenza: l'intensità è un
    # moltiplicatore, quindi partire da 1 significa "come è stata creata".
    illuminazione: bpy.props.StringProperty(default="", options={"HIDDEN"})
    sfondo_colore: bpy.props.FloatVectorProperty(
        name=TESTI["ETICHETTA_SFONDO_COLORE"],
        description=TESTI["AIUTO_SFONDO_COLORE"],
        subtype="COLOR", size=3, min=0.0, max=1.0,
        default=configuration.SFONDO_COLORE_PREDEFINITO,
    )
    sfondo_intensita: bpy.props.FloatProperty(
        name=TESTI["ETICHETTA_SFONDO_INTENSITA"],
        description=TESTI["AIUTO_SFONDO_INTENSITA"],
        default=configuration.SFONDO_INTENSITA_PREDEFINITA,
        min=configuration.SFONDO_INTENSITA_MINIMA,
        max=configuration.SFONDO_INTENSITA_MASSIMA,
        precision=2,
    )
    luce_intensita: bpy.props.FloatProperty(
        name=TESTI["ETICHETTA_LUCE_INTENSITA"],
        description=TESTI["AIUTO_LUCE_INTENSITA"],
        default=configuration.INTENSITA_LUCE_PREDEFINITA,
        min=configuration.INTENSITA_LUCE_MINIMA,
        max=configuration.INTENSITA_LUCE_MASSIMA,
        precision=2,
    )
    # Immagine finale: qualità, cartella e i valori tecnici della modalità completa.
    qualita: bpy.props.EnumProperty(
        name=TESTI["ETICHETTA_QUALITA"],
        description=TESTI["AIUTO_QUALITA"],
        items=aspetto.voci_qualita(),
        default=aspetto.QUALITA_PREDEFINITA,
    )
    render_percentuale: bpy.props.IntProperty(
        name=TESTI["ETICHETTA_RENDER_PERCENTUALE"],
        description=TESTI["AIUTO_RENDER_PERCENTUALE"],
        default=aspetto.qualita(aspetto.QUALITA_PREDEFINITA).percentuale,
        min=configuration.QUALITA_PERCENTUALE_MINIMA,
        max=configuration.QUALITA_PERCENTUALE_MASSIMA,
        subtype="PERCENTAGE",
    )
    render_campioni: bpy.props.IntProperty(
        name=TESTI["ETICHETTA_RENDER_CAMPIONI"],
        description=TESTI["AIUTO_RENDER_CAMPIONI"],
        default=configuration.CAMPIONI_AUTOMATICI,
        min=configuration.CAMPIONI_AUTOMATICI,
        max=configuration.CAMPIONI_MASSIMI,
    )
    render_motore: bpy.props.EnumProperty(
        name=TESTI["ETICHETTA_RENDER_MOTORE"],
        description=TESTI["AIUTO_RENDER_MOTORE"],
        items=aspetto.voci_motori(),
        default=aspetto.MOTORE_PREDEFINITO,
    )
    render_formato: bpy.props.EnumProperty(
        name=TESTI["ETICHETTA_RENDER_FORMATO"],
        description=TESTI["AIUTO_RENDER_FORMATO"],
        items=aspetto.voci_formati(),
        default=aspetto.FORMATO_PREDEFINITO,
    )
    cartella_immagine: bpy.props.StringProperty(
        name=TESTI["ETICHETTA_CARTELLA_IMMAGINE"],
        description=TESTI["AIUTO_CARTELLA_IMMAGINE"],
        subtype="DIR_PATH",
        default="",
    )
    # Guida passo passo in corso: la chiave della guida e il passo mostrato.
    guida: bpy.props.StringProperty(default="", options={"HIDDEN"})
    passo_guida: bpy.props.IntProperty(default=0, min=0, options={"HIDDEN"})
    messaggio: bpy.props.StringProperty(default="", options={"HIDDEN"})
    tempo_messaggio: bpy.props.FloatProperty(default=0.0, options={"HIDDEN"})


CLASSI = (FORMAFACILE_PG_stato,)


def registra_stato() -> None:
    """Collega il gruppo di proprietà alla scena."""
    bpy.types.Scene.formafacile = bpy.props.PointerProperty(type=FORMAFACILE_PG_stato)


def rimuovi_stato() -> None:
    """Stacca il gruppo di proprietà dalla scena, se presente."""
    if hasattr(bpy.types.Scene, "formafacile"):
        del bpy.types.Scene.formafacile


def stato_della_scena(scena):
    """Restituisce lo stato della scena oppure None se non è disponibile."""
    if scena is None:
        return None
    return getattr(scena, configuration.GRUPPO_STATO_SCENA, None)


def modalita_della_scena(scena) -> str:
    """Modalità corrente, con ripiego sulla modalità semplice."""
    stato = stato_della_scena(scena)
    if stato is None:
        return configuration.MODALITA_SEMPLICE
    return stato.modalita


def passo_della_scena(scena) -> float:
    """Passo dello spostamento, mai nullo."""
    stato = stato_della_scena(scena)
    if stato is None:
        return configuration.PASSO_PREDEFINITO
    passo = float(stato.passo)
    if passo <= 0.0:
        return configuration.PASSO_PREDEFINITO
    return passo


def grandezza_della_scena(scena) -> float:
    """Grandezza delle nuove forme, in metri e sempre dentro i limiti."""
    stato = stato_della_scena(scena)
    if stato is None:
        return configuration.DIMENSIONE_FORMA_PREDEFINITA
    grandezza = float(stato.grandezza_forma)
    if grandezza <= 0.0:
        return configuration.DIMENSIONE_FORMA_PREDEFINITA
    return min(
        max(grandezza, configuration.DIMENSIONE_FORMA_MINIMA),
        configuration.DIMENSIONE_FORMA_MASSIMA,
    )


def messaggio_della_scena(scena, adesso: float | None = None) -> tuple[str, bool]:
    """Messaggio breve e se è ancora attuale."""
    stato = stato_della_scena(scena)
    if stato is None or not stato.messaggio:
        return "", False
    adesso = time.monotonic() if adesso is None else adesso
    return stato.messaggio, (adesso - float(stato.tempo_messaggio)) < configuration.DURATA_MESSAGGIO


def allineamento_della_scena(scena) -> tuple[str, str, bool]:
    """Asse, bordo e riferimento scelti per Allinea e Spazia, con ripieghi sicuri."""
    stato = stato_della_scena(scena)
    if stato is None:
        return (
            configuration.ALLINEA_ASSE_PREDEFINITO,
            configuration.ALLINEA_BORDO_PREDEFINITO,
            configuration.ALLINEA_RIFERIMENTO_PREDEFINITO == comandi.RIFERIMENTO_PUNTO,
        )
    asse = str(getattr(stato, "asse_allinea", configuration.ALLINEA_ASSE_PREDEFINITO)).lower()
    if asse not in comandi.ASSI:
        asse = configuration.ALLINEA_ASSE_PREDEFINITO
    bordo = str(getattr(stato, "bordo_allinea", configuration.ALLINEA_BORDO_PREDEFINITO))
    if bordo not in comandi.MODI_ALLINEAMENTO:
        bordo = configuration.ALLINEA_BORDO_PREDEFINITO
    riferimento = str(
        getattr(stato, "riferimento_allinea", configuration.ALLINEA_RIFERIMENTO_PREDEFINITO)
    )
    return asse, bordo, riferimento == comandi.RIFERIMENTO_PUNTO


def guida_della_scena(scena) -> tuple[str, int]:
    """Chiave della guida in corso e passo mostrato, anche senza stato."""
    stato = stato_della_scena(scena)
    if stato is None:
        return "", 0
    return str(getattr(stato, "guida", "")), int(getattr(stato, "passo_guida", 0))


def materiale_della_scena(scena) -> str:
    """Chiave del materiale pronto scelto nel pannello dell'aspetto."""
    stato = stato_della_scena(scena)
    if stato is None:
        return aspetto.MATERIALE_PREDEFINITO
    chiave = str(getattr(stato, "materiale_scelto", aspetto.MATERIALE_PREDEFINITO))
    return chiave if chiave in aspetto.MATERIALI else aspetto.MATERIALE_PREDEFINITO


def valori_materiale_della_scena(scena):
    """Materiale pronto con i valori scritti dall'utente nel pannello.

    È il materiale che verrà creato davvero: si compone qui, una volta sola,
    così il comando e i controlli automatici leggono gli stessi numeri.
    """
    stato = stato_della_scena(scena)
    if stato is None:
        return aspetto.materiale(aspetto.MATERIALE_PREDEFINITO)
    return aspetto.componi(
        materiale_della_scena(scena),
        getattr(stato, "materiale_colore", None),
        getattr(stato, "materiale_ruvidita", None),
        getattr(stato, "materiale_metallico", None),
        getattr(stato, "materiale_trasparenza", None),
    )


def ambiente_della_scena(scena) -> tuple[tuple[float, float, float], float, float]:
    """Colore di sfondo, luminosità dello sfondo e potenza delle luci."""
    stato = stato_della_scena(scena)
    if stato is None:
        return (
            configuration.SFONDO_COLORE_PREDEFINITO,
            configuration.SFONDO_INTENSITA_PREDEFINITA,
            configuration.INTENSITA_LUCE_PREDEFINITA,
        )
    colore = tuple(float(valore) for valore in getattr(stato, "sfondo_colore", ()))
    if len(colore) != 3:
        colore = configuration.SFONDO_COLORE_PREDEFINITO
    intensita = aspetto.limita(
        getattr(stato, "sfondo_intensita", configuration.SFONDO_INTENSITA_PREDEFINITA),
        configuration.SFONDO_INTENSITA_MINIMA,
        configuration.SFONDO_INTENSITA_MASSIMA,
    )
    luce = aspetto.limita(
        getattr(stato, "luce_intensita", configuration.INTENSITA_LUCE_PREDEFINITA),
        configuration.INTENSITA_LUCE_MINIMA,
        configuration.INTENSITA_LUCE_MASSIMA,
    )
    return colore, intensita, luce


def illuminazione_della_scena(scena) -> str:
    """Chiave dell'ultima illuminazione applicata da FormaFacile."""
    stato = stato_della_scena(scena)
    if stato is None:
        return ""
    return str(getattr(stato, "illuminazione", ""))


def immagine_della_scena(scena) -> tuple[str, int, int, str, str]:
    """Qualità, percentuale, campioni, motore e formato dell'immagine finale."""
    stato = stato_della_scena(scena)
    if stato is None:
        qualita = aspetto.qualita(aspetto.QUALITA_PREDEFINITA)
        return (
            qualita.chiave,
            qualita.percentuale,
            configuration.CAMPIONI_AUTOMATICI,
            aspetto.MOTORE_PREDEFINITO,
            aspetto.FORMATO_PREDEFINITO,
        )
    qualita = aspetto.qualita(str(getattr(stato, "qualita", aspetto.QUALITA_PREDEFINITA)))
    return (
        qualita.chiave,
        int(getattr(stato, "render_percentuale", qualita.percentuale)),
        int(getattr(stato, "render_campioni", configuration.CAMPIONI_AUTOMATICI)),
        str(getattr(stato, "render_motore", aspetto.MOTORE_PREDEFINITO)),
        str(getattr(stato, "render_formato", aspetto.FORMATO_PREDEFINITO)),
    )


def cartella_della_scena(scena) -> str:
    """Cartella scelta per l'immagine finale, ripulita dagli spazi esterni."""
    stato = stato_della_scena(scena)
    if stato is None:
        return ""
    return str(getattr(stato, "cartella_immagine", "")).strip()
