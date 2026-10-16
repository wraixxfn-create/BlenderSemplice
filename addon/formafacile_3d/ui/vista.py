"""Lettura della scena reale e costruzione del contesto per l'interfaccia.

Qui (e solo qui) i dati di Blender diventano il `Contesto` descritto in
`ui/modello.py`. L'interfaccia legge sempre la scena al momento del disegno,
quindi non può mostrare dati vecchi.
"""

from __future__ import annotations

from .. import configuration
from ..blender import selezione
from ..blender import vista as servizio_vista
from ..scene.stato import messaggio_della_scena, modalita_della_scena, passo_della_scena
from . import icone
from .modello import Contesto, Oggetto


def raccogli_contesto(context) -> tuple[Contesto, dict[str, object]]:
    """Fotografa la scena corrente e restituisce anche i dati collegati ai campi."""
    scena = getattr(context, "scene", None)
    vettore = getattr(context, "view_layer", None)
    modalita = modalita_della_scena(scena)

    oggetti: list[Oggetto] = []
    risolutore: dict[str, object] = {}
    if scena is not None:
        risolutore[configuration.CHIAVE_SCENA] = scena

    if vettore is not None:
        attivo = vettore.objects.active
        for oggetto in selezione.oggetti_della_scena(vettore):
            oggetti.append(_fotografa_oggetto(oggetto, scena, attivo))
            risolutore[oggetto.name] = oggetto

    messaggio, recente = messaggio_della_scena(scena)
    contesto = Contesto(
        modalita=modalita,
        in_modalita_oggetto=getattr(context, "mode", "OBJECT") == "OBJECT",
        oggetti=tuple(oggetti),
        filtro=_filtro(scena),
        passo=passo_della_scena(scena),
        messaggio=messaggio,
        messaggio_recente=recente,
        vista_disponibile=servizio_vista.aree_vista_disponibili(context),
        limite_elenco=(
            configuration.LIMITE_ELENCO_COMPLETA
            if modalita == configuration.MODALITA_COMPLETA
            else configuration.LIMITE_ELENCO_SEMPLICE
        ),
        soglia_filtro=configuration.SOGLIA_FILTRO,
        gradi_rotazione=configuration.ANGOLO_PREDEFINITO_GRADI,
        percentuale_scala=int(round((configuration.FATTORE_SCALA_PREDEFINITO - 1.0) * 100)),
    )
    return contesto, risolutore


def _nascosto_direttamente(oggetto) -> bool:
    """Nascondimento deciso dall'oggetto stesso (non dalla sua raccolta).

    Sono i due interruttori che FormaFacile sa rimettere a posto: l'occhio
    della Vista 3D (`hide_set`) e il pulsante "Nascondi nella vista"
    (`hide_viewport`).
    """
    if bool(getattr(oggetto, "hide_viewport", False)):
        return True
    try:
        return bool(oggetto.hide_get())
    except (AttributeError, ReferenceError, RuntimeError):
        return False


def _filtro(scena) -> str:
    stato = getattr(scena, configuration.GRUPPO_STATO_SCENA, None)
    if stato is None:
        return ""
    return stato.filtro


def _fotografa_oggetto(oggetto, scena, attivo) -> Oggetto:
    tipo = getattr(oggetto, "type", "")
    dati = getattr(oggetto, "data", None)
    vertici = facce = 0
    if tipo == "MESH" and dati is not None:
        try:
            vertici = len(dati.vertices)
            facce = len(dati.polygons)
        except (AttributeError, ReferenceError, RuntimeError):
            vertici = facce = 0

    potenza = 0.0
    if tipo == "LIGHT" and dati is not None:
        potenza = float(getattr(dati, "energy", 0.0))

    nascosto_direttamente = _nascosto_direttamente(oggetto)
    visibile = True
    try:
        visibile = bool(oggetto.visible_get())
    except (AttributeError, ReferenceError, RuntimeError):
        visibile = not nascosto_direttamente

    return Oggetto(
        chiave=oggetto.name,
        nome=oggetto.name,
        tipo=tipo,
        tipo_parola=icone.parola_tipo(tipo),
        icona=icone.icona_tipo(tipo),
        scelto=bool(oggetto.select_get()),
        attivo=oggetto is attivo,
        nascosto=nascosto_direttamente or not visibile,
        nascosto_direttamente=nascosto_direttamente,
        bloccato=bool(getattr(oggetto, "hide_select", False)),
        modo_rotazione=getattr(oggetto, "rotation_mode", "XYZ"),
        nome_dati=getattr(dati, "name", "") if dati is not None else "",
        vertici=vertici,
        facce=facce,
        potenza_luce=potenza,
        telecamera_principale=bool(scena is not None and getattr(scena, "camera", None) is oggetto),
    )
