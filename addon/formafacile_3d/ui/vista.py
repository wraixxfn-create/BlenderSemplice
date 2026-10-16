"""Lettura della scena reale e costruzione del contesto per l'interfaccia.

Qui (e solo qui) i dati di Blender diventano il `Contesto` descritto in
`ui/modello.py`. L'interfaccia legge sempre la scena al momento del disegno,
quindi non può mostrare dati vecchi.
"""

from __future__ import annotations

from .. import configuration
from ..blender import illuminazione as servizio_illuminazione
from ..blender import materiali as servizio_materiali
from ..blender import modificatori as servizio_modificatori
from ..blender import raccolte as servizio_raccolte
from ..blender import selezione
from ..blender import telecamera as servizio_telecamera
from ..blender import vista as servizio_vista
from ..scene import aspetto, libreria, misure
from ..scene.stato import (
    grandezza_della_scena,
    immagine_della_scena,
    materiale_della_scena,
    stato_della_scena,
    guida_della_scena,
    messaggio_della_scena,
    modalita_della_scena,
    passo_della_scena,
)
from . import icone
from .modello import Contesto, Modificatore, Oggetto, Raccolta


def raccogli_contesto(context) -> tuple[Contesto, dict[str, object]]:
    """Fotografa la scena corrente e restituisce anche i dati collegati ai campi."""
    scena = getattr(context, "scene", None)
    vettore = getattr(context, "view_layer", None)
    modalita = modalita_della_scena(scena)

    oggetti: list[Oggetto] = []
    risolutore: dict[str, object] = {}
    if scena is not None:
        risolutore[configuration.CHIAVE_SCENA] = scena
    stato = stato_della_scena(scena)
    if stato is not None:
        risolutore[configuration.CHIAVE_STATO] = stato
    asset_selezionato = str(
        getattr(stato, "asset_selezionato", libreria.ID_PREDEFINITO)
    )
    asset_descrizione = libreria.scheda(asset_selezionato).descrizione

    if vettore is not None:
        attivo = vettore.objects.active
        for oggetto in selezione.oggetti_della_scena(vettore):
            oggetti.append(_fotografa_oggetto(oggetto, scena, attivo))
            risolutore[oggetto.name] = oggetto

    messaggio, recente = messaggio_della_scena(scena)
    guida, passo_guida = guida_della_scena(scena)
    larghezza, altezza, campioni = _dimensioni_immagine(scena)
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
        unita_lunghezza=_unita_lunghezza(scena),
        unita_angolo=_unita_angolo(scena),
        grandezza_forma=grandezza_della_scena(scena),
        asset_selezionato=asset_selezionato,
        asset_descrizione=asset_descrizione,
        raccolte=_raccolte(scena),
        modificatori=_modificatori(context, vettore),
        guida=guida,
        passo_guida=passo_guida,
        qualita=immagine_della_scena(scena)[0],
        materiale=materiale_della_scena(scena),
        materiale_applicato=_materiale_applicato(scena, vettore),
        materiale_condiviso=_materiale_condiviso(scena, vettore),
        illuminazione=_illuminazione(context),
        illuminazione_luci=_luci(context),
        telecamera=_telecamera(scena),
        anteprima_immagine=servizio_telecamera.in_anteprima(context),
        immagine_larghezza=larghezza,
        immagine_altezza=altezza,
        immagine_campioni=campioni,
    )
    risolutore[configuration.CHIAVE_MATERIALE] = _risolutore_materiale(scena, vettore)
    return contesto, risolutore


def _risolutore_materiale(scena, vettore):
    """Materiale dell'oggetto attivo, usato per l'anteprima disegnata da Blender."""
    attivo = getattr(getattr(vettore, "objects", None), "active", None)
    if attivo is None:
        return None
    return servizio_materiali.materiale_principale(attivo)


def _materiale_applicato(scena, vettore) -> str:
    """Nome del materiale dell'oggetto attivo: è quello che l'utente vede."""
    materiale = _risolutore_materiale(scena, vettore)
    if materiale is None:
        return ""
    return str(getattr(materiale, "name", ""))


def _materiale_condiviso(scena, vettore) -> int:
    """Quanti oggetti usano il materiale dell'oggetto attivo."""
    materiale = _risolutore_materiale(scena, vettore)
    if materiale is None:
        return 0
    return servizio_materiali.quanti_oggetti_usano(scena, materiale)


def _illuminazione(context) -> str:
    """Chiave dell'illuminazione di FormaFacile presente adesso nella scena."""
    chiave, _quante = servizio_illuminazione.descrizione_attuale(
        getattr(context, "scene", None)
    )
    return chiave


def _luci(context) -> int:
    """Numero di luci create da FormaFacile."""
    return len(servizio_illuminazione.luci_formafacile(getattr(context, "scene", None)))


def _telecamera(scena) -> str:
    """Nome della telecamera principale, se c'è."""
    camera = getattr(scena, "camera", None)
    if camera is None:
        return ""
    return str(getattr(camera, "name", ""))


def _raccolte(scena) -> tuple[Raccolta, ...]:
    """Gruppi della scena, pronti per l'elenco dell'interfaccia."""
    return tuple(
        Raccolta(
            chiave=gruppo.chiave,
            nome=gruppo.nome,
            quanti=gruppo.quanti,
            scelti=gruppo.scelti,
            nascosto=gruppo.nascosto,
        )
        for gruppo in servizio_raccolte.gruppi(scena)
    )


def _modificatori(context, vettore) -> tuple[Modificatore, ...]:
    """Modifiche non applicate sull'oggetto attivo, in parole semplici.

    Le modifiche si mostrano per l'oggetto attivo: sono i comandi guidati a
    lavorare su quello, e la forma di partenza resta sempre quella creata
    dall'utente.
    """
    attivo = getattr(vettore, "objects", None)
    attivo = getattr(attivo, "active", None) if attivo is not None else None
    if attivo is None:
        return ()
    elenco = []
    for modificatore in servizio_modificatori.elenca(attivo):
        tipo = servizio_modificatori.tipo_di(modificatore)
        elenco.append(
            Modificatore(
                chiave=servizio_modificatori.nome_di(modificatore),
                nome=servizio_modificatori.nome_di(modificatore),
                parola=icone.parola_modificatore(tipo),
                icona=icone.icona_modificatore(tipo),
                problema=servizio_modificatori.problema_di(context, modificatore),
            )
        )
    return tuple(elenco)


def _impostazioni_unita(scena):
    """Impostazioni delle unità della scena, se disponibili."""
    return getattr(scena, "unit_settings", None)


def _unita_lunghezza(scena) -> str:
    """Abbreviazione dell'unità di lunghezza usata dalla scena."""
    impostazioni = _impostazioni_unita(scena)
    if impostazioni is None:
        return "m"
    return misure.unita_lunghezza(
        str(getattr(impostazioni, "system", "NONE")),
        str(getattr(impostazioni, "length_unit", "METERS")),
    )


def _unita_angolo(scena) -> str:
    """Abbreviazione dell'unità degli angoli usata dalla scena."""
    impostazioni = _impostazioni_unita(scena)
    if impostazioni is None:
        return "°"
    return misure.unita_angolo(str(getattr(impostazioni, "system_rotation", "DEGREES")))


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
        liscio=bool(tipo == "MESH" and servizio_modificatori.e_liscia(oggetto)),
        potenza_luce=potenza,
        telecamera_principale=bool(scena is not None and getattr(scena, "camera", None) is oggetto),
    )


def _dimensioni_immagine(scena) -> tuple[int, int, int]:
    """Grandezza in pixel e campioni dell'immagine finale.

    Sono i numeri che il pannello scrive accanto alla qualità scelta: prima di
    creare l'immagine l'utente sa quanto sarà grande e quanto lavoro chiederà.
    """
    render = getattr(scena, "render", None)
    if render is None:
        return 0, 0, 0
    _qualita, percentuale, campioni, motore, _formato = immagine_della_scena(scena)
    percentuale = max(int(percentuale), 1)
    larghezza = int(getattr(render, "resolution_x", 0) or 0) * percentuale // 100
    altezza = int(getattr(render, "resolution_y", 0) or 0) * percentuale // 100
    motore_blender = str(getattr(render, "engine", ""))
    if campioni <= configuration.CAMPIONI_AUTOMATICI:
        campioni = aspetto.qualita(_qualita).campioni(motore_blender)
    return larghezza, altezza, campioni
