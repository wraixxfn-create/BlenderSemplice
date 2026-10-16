"""Gestione della Vista 3D: vista iniziale e inquadratura.

La navigazione normale (tasto centrale del mouse, rotella, scorciatoie di
Blender) non viene mai toccata: questo modulo si limita a richiamare gli
operatori nativi e, se non sono disponibili, a scrivere gli stessi valori che
Blender userebbe.

La vista di partenza di ogni disposizione dei pannelli viene registrata
all'avvio come numeri semplici (rotazione, distanza, tipo di vista): non
restano riferimenti a finestre che potrebbero sparire. "Torna alla vista
iniziale" rimette quei valori e poi inquadra tutta la scena.
"""

from __future__ import annotations

import contextlib

import bpy
import mathutils

from .. import comandi, configuration
from ..localization import TESTI
from ..logging_service import ottieni_logger

# Valori di `RegionView3D.view_perspective` accettati dal ripristino.
PUNTI_DI_VISTA = ("PERSP", "ORTHO", "CAMERA")


class ErroreVista(RuntimeError):
    """Errore gestibile quando non c'è una vista 3D da sistemare."""


_VISTE_INIZIALI: dict[int, list[dict[str, object]]] = {}


def aggiorna_scena(context) -> None:
    """Aggiorna le matrici della scena prima di leggere le posizioni.

    Serve quando un oggetto è stato spostato poco prima, per esempio da uno
    script: senza questo aggiornamento l'inquadratura userebbe la posizione
    vecchia.
    """
    vettore = getattr(context, "view_layer", None)
    aggiorna = getattr(vettore, "update", None)
    if aggiorna is None:
        return
    try:
        aggiorna()
    except (AttributeError, ReferenceError, RuntimeError):
        return


def _vista_predefinita() -> dict[str, object]:
    """Vista di partenza di Blender 4.5 LTS, usata quando non è registrata."""
    return {
        "rotazione": configuration.VISTA_INIZIALE_ROTAZIONE,
        "distanza": configuration.VISTA_INIZIALE_DISTANZA,
        "prospettiva": True,
        "punto_di_vista": "PERSP",
    }


def _chiave_schermo(schermo) -> int:
    """Chiave stabile di uno schermo: il suo indirizzo, che vale per la sessione."""
    return int(schermo.as_pointer())


def _leggi_vista(spazio) -> dict[str, object]:
    """Legge rotazione, distanza e tipo di vista di uno spazio Vista 3D."""
    regione_3d = spazio.region_3d
    return {
        "rotazione": tuple(float(valore) for valore in regione_3d.view_rotation),
        "distanza": float(regione_3d.view_distance),
        "prospettiva": bool(regione_3d.is_perspective),
        "punto_di_vista": str(regione_3d.view_perspective),
    }


def _aree_vista(context):
    """Le aree Vista 3D raggiungibili adesso, con tutto ciò che serve.

    Restituisce, per ogni area: finestra, schermo, indice, area, spazio e
    regione della finestra. L'indice conta le sole aree Vista 3D dello schermo,
    quindi non cambia se in futuro si spostano i pannelli.
    """
    finestre = list(getattr(context.window_manager, "windows", ()) or ())
    finestra_corrente = getattr(context, "window", None)
    if finestra_corrente is not None and finestra_corrente not in finestre:
        finestre.insert(0, finestra_corrente)

    for finestra in finestre:
        schermo = getattr(finestra, "screen", None)
        if schermo is None:
            continue
        indice = 0
        for area in schermo.areas:
            if area.type != "VIEW_3D" or not area.spaces:
                continue
            spazio = area.spaces.active
            if spazio is None or getattr(spazio, "region_3d", None) is None:
                continue
            regione = next((r for r in area.regions if r.type == "WINDOW"), None)
            yield finestra, schermo, indice, area, spazio, regione
            indice += 1


def aree_vista_disponibili(context) -> bool:
    """Indica se esiste almeno una Vista 3D utilizzabile."""
    try:
        return next(_aree_vista(context), None) is not None
    except (AttributeError, ReferenceError, RuntimeError, TypeError):
        return False


def prima_area(context):
    """Finestra, area e regione della prima Vista 3D disponibile."""
    try:
        for finestra, _schermo, _indice, area, _spazio, regione in _aree_vista(context):
            return finestra, area, regione
    except (AttributeError, ReferenceError, RuntimeError, TypeError):
        return None, None, None
    return None, None, None


@contextlib.contextmanager
def contesto_area_vista(context):
    """Esegue un blocco con il contesto di una Vista 3D.

    Alcuni comandi nativi (copia, incolla, strumenti) funzionano solo se il
    contesto è una Vista 3D. Senza finestre, o senza una Vista 3D, il blocco
    riceve `None`: chi chiama deve allora avvisare l'utente, non fallire.
    """
    finestra, area, regione = prima_area(context)
    if area is None:
        yield None
        return
    try:
        with bpy.context.temp_override(window=finestra, area=area, region=regione):
            yield area
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        yield None


def esegui_in_vista(context, idname: str, **parametri: object):
    """Richiama un comando nativo dentro una Vista 3D.

    Restituisce l'esito di Blender, oppure None quando il comando non esiste o
    non è possibile: nessuna eccezione arriva all'interfaccia.
    """
    modulo, _, nome = str(idname).partition(".")
    gruppo = getattr(bpy.ops, modulo, None)
    operatore = getattr(gruppo, nome, None)
    if operatore is None:
        return None
    try:
        with contesto_area_vista(context) as area:
            if area is None:
                return None
            if not operatore.poll():
                return None
            return operatore(**parametri)
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError) as errore:
        ottieni_logger().debug(f"{TESTI['LOG_ERRORE_VISTA']} {type(errore).__name__}")
        return None


def attiva_strumento(context, nome_strumento: str) -> bool:
    """Attiva uno strumento nativo di Blender e ne mostra le maniglie.

    Gli strumenti `builtin.move`, `builtin.rotate` e `builtin.scale` sono quelli
    della barra degli strumenti di Blender: attivarli è il modo pubblico per
    far comparire frecce, archi e cubetti nella Vista 3D. Gli interruttori che
    nascondono le maniglie vengono riaccesi, altrimenti il pulsante sembrerebbe
    non fare nulla.
    """
    with contesto_area_vista(context) as area:
        if area is None:
            return False
        riuscito = False
        try:
            esito = bpy.ops.wm.tool_set_by_id(name=nome_strumento)
            riuscito = "FINISHED" in esito
        except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
            riuscito = False
        if not riuscito:
            return False
        _mostra_maniglie(area)
        return True


def _mostra_maniglie(area) -> None:
    """Riaccende gli interruttori che rendono visibili le maniglie."""
    spazio = getattr(getattr(area, "spaces", None), "active", None)
    if spazio is None:
        return
    for nome in configuration.MOSTRA_MANIGLIE:
        if not hasattr(spazio, nome):
            continue
        try:
            setattr(spazio, nome, True)
        except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
            continue


def registra_viste_iniziali() -> int:
    """Memorizza la vista di partenza delle disposizioni dei pannelli.

    Viene chiamata al caricamento del componente aggiuntivo e legge tutte le
    disposizioni disponibili, non solo quella in uso: cambiando disposizione la
    vista iniziale resta quella giusta.
    """
    _VISTE_INIZIALI.clear()
    registrate = 0
    try:
        for disposizione in bpy.data.workspaces:
            for schermo in getattr(disposizione, "screens", ()) or ():
                viste = [
                    _leggi_vista(area.spaces.active)
                    for area in schermo.areas
                    if area.type == "VIEW_3D" and getattr(area.spaces.active, "region_3d", None) is not None
                ]
                if viste:
                    _VISTE_INIZIALI[_chiave_schermo(schermo)] = viste
                    registrate += len(viste)
    except (AttributeError, ReferenceError, RuntimeError, TypeError):
        ottieni_logger().warning(TESTI["LOG_ERRORE_REGISTRAZIONE_VISTA"])
    if not registrate:
        _VISTE_INIZIALI.clear()
    return registrate


def vista_iniziale(schermo, indice: int) -> dict[str, object]:
    """Vista iniziale registrata per uno schermo, altrimenti quella predefinita."""
    if schermo is None:
        return _vista_predefinita()
    viste = _VISTE_INIZIALI.get(_chiave_schermo(schermo), [])
    if 0 <= indice < len(viste):
        return viste[indice]
    return _vista_predefinita()


# --------------------------------------------------------------- inquadratura


def _riquadro(punti: list) -> tuple[object, float]:
    """Centro e raggio di un insieme di punti, usati per inquadrare."""
    if not punti:
        return mathutils.Vector((0.0, 0.0, 0.0)), 0.0
    minimo = mathutils.Vector(tuple(min(punto[i] for punto in punti) for i in range(3)))
    massimo = mathutils.Vector(tuple(max(punto[i] for punto in punti) for i in range(3)))
    centro = (minimo + massimo) * 0.5
    raggio = max((punto - centro).length for punto in punti)
    return centro, raggio


def _angoli(oggetto) -> list:
    """Gli otto angoli del riquadro dell'oggetto, nelle coordinate della scena."""
    matrice = oggetto.matrix_world
    return [matrice @ mathutils.Vector(angolo) for angolo in oggetto.bound_box]


def _riquadro_oggetti(oggetti) -> tuple[object, float]:
    punti: list = []
    for oggetto in oggetti:
        punti.extend(_angoli(oggetto))
    return _riquadro(punti)


def distanza_per(raggio: float) -> float:
    """Distanza della vista per inquadrare un oggetto di un certo raggio."""
    if raggio <= 0.0:
        return configuration.DISTANZA_VUOTA_PREDEFINITA
    return max(raggio * configuration.FATTORE_INQUADRATURA, configuration.DISTANZA_MINIMA_VISTA)


def inquadra_area(area, *, centro, raggio: float) -> bool:
    """Scrive in una Vista 3D il centro e la distanza calcolati sui dati reali."""
    regione_3d = getattr(getattr(area, "spaces", None), "active", None)
    regione_3d = getattr(regione_3d, "region_3d", None)
    if regione_3d is None:
        return False
    regione_3d.view_location = centro
    regione_3d.view_distance = distanza_per(float(raggio))
    return True


def _inquadra_con_operatore(finestra, area, regione, *, solo_scelti: bool) -> bool:
    """Richiama l'inquadratura nativa di Blender per una singola area."""
    if regione is None or finestra is None:
        return False
    try:
        with bpy.context.temp_override(window=finestra, area=area, region=regione):
            if solo_scelti:
                risultato = bpy.ops.view3d.view_selected()
            else:
                risultato = bpy.ops.view3d.view_all()
    except (AttributeError, ReferenceError, RuntimeError, TypeError):
        return False
    return "FINISHED" in risultato


def _inquadra_dati_reali(context, area, *, solo_scelti: bool = False) -> bool:
    """Inquadratura calcolata sui dati, usata quando l'operatore nativo non riesce."""
    oggetti = [oggetto for oggetto in context.view_layer.objects if oggetto.visible_get()]
    if solo_scelti:
        oggetti = [oggetto for oggetto in oggetti if oggetto.select_get()]
    if not oggetti:
        return False
    centro, raggio = _riquadro_oggetti(oggetti)
    return inquadra_area(area, centro=centro, raggio=raggio)


def _inquadra_una_area(context, finestra, area, regione, *, solo_scelti: bool) -> bool:
    """Inquadra un'area provando prima l'operatore nativo, poi il calcolo diretto."""
    if _inquadra_con_operatore(finestra, area, regione, solo_scelti=solo_scelti):
        return True
    return _inquadra_dati_reali(context, area, solo_scelti=solo_scelti)


def _applica_vista_iniziale(area, schermo, indice: int) -> None:
    """Riporta tipo di vista, prospettiva e rotazione a quelli di partenza."""
    valori = vista_iniziale(schermo, indice)
    regione_3d = area.spaces.active.region_3d
    punto = str(valori.get("punto_di_vista", "PERSP"))
    if punto in PUNTI_DI_VISTA and regione_3d.view_perspective != punto:
        regione_3d.view_perspective = punto
    if punto != "CAMERA":
        regione_3d.is_perspective = bool(valori.get("prospettiva", True))
    regione_3d.view_rotation = mathutils.Quaternion(valori["rotazione"])


def torna_alla_vista_iniziale(context) -> int:
    """Riporta ogni Vista 3D alla vista di partenza e inquadra tutta la scena."""
    aggiorna_scena(context)
    aree = list(_aree_vista(context))
    if not aree:
        raise ErroreVista(TESTI["ERRORE_VISTA_INIZIALE"])

    sistemate = 0
    for finestra, schermo, indice, area, _spazio, regione in aree:
        try:
            _inquadra_una_area(context, finestra, area, regione, solo_scelti=False)
            _applica_vista_iniziale(area, schermo, indice)
            sistemate += 1
        except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError) as errore:
            ottieni_logger().warning(f"{TESTI['LOG_ERRORE_VISTA']} {type(errore).__name__}")
    if not sistemate:
        raise ErroreVista(TESTI["ERRORE_VISTA_INIZIALE"])
    return sistemate


def inquadra_tutta_la_scena(context) -> int:
    """Inquadra tutti gli oggetti lasciando invariata la direzione della vista."""
    aggiorna_scena(context)
    return _inquadra_ogni_area(context, solo_scelti=False)


def inquadra_scelti(context) -> int:
    """Inquadra soltanto gli oggetti scelti."""
    aggiorna_scena(context)
    return _inquadra_ogni_area(context, solo_scelti=True)


def _inquadra_ogni_area(context, *, solo_scelti: bool) -> int:
    aree = list(_aree_vista(context))
    if not aree:
        raise ErroreVista(TESTI["ERRORE_VISTA_NON_DISPONIBILE"])

    sistemate = 0
    for finestra, _schermo, _indice, area, _spazio, regione in aree:
        try:
            if _inquadra_una_area(context, finestra, area, regione, solo_scelti=solo_scelti):
                sistemate += 1
        except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
            continue
    if not sistemate:
        raise ErroreVista(TESTI["ERRORE_VISTA_NON_DISPONIBILE"])
    return sistemate


def inquadra_oggetto(context, oggetto) -> int:
    """Inquadra un singolo oggetto in tutte le viste 3D disponibili."""
    aggiorna_scena(context)
    if oggetto.hide_viewport or not oggetto.visible_get():
        raise ErroreVista(TESTI["ERRORE_INQUADRA_OGGETTO"])

    aree = list(_aree_vista(context))
    if not aree:
        raise ErroreVista(TESTI["ERRORE_VISTA_NON_DISPONIBILE"])

    centro, raggio = _riquadro(_angoli(oggetto))
    sistemate = 0
    for _finestra, _schermo, _indice, area, _spazio, _regione in aree:
        try:
            if inquadra_area(area, centro=centro, raggio=raggio):
                sistemate += 1
        except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
            continue
    if not sistemate:
        raise ErroreVista(TESTI["ERRORE_VISTA_NON_DISPONIBILE"])
    return sistemate


def guarda_dalla_telecamera(context, telecamera=None) -> bool:
    """Mostra la scena dal punto di vista di una telecamera.

    Se la telecamera indicata non è quella principale, diventa tale: è quello
    che si aspetta chi preme "Guarda dalla telecamera" e non dipende dal fatto
    che la vista fosse già in modalità telecamera (che l'operatore nativo
    invece invertirebbe).
    """
    scena = getattr(context, "scene", None)
    if telecamera is not None and scena is not None and scena.camera is not telecamera:
        scena.camera = telecamera

    aree = list(_aree_vista(context))
    if not aree:
        return False

    sistemate = 0
    for finestra, _schermo, _indice, area, _spazio, regione in aree:
        try:
            regione_3d = area.spaces.active.region_3d
            regione_3d.view_perspective = "CAMERA"
            if regione is not None:
                with bpy.context.temp_override(window=finestra, area=area, region=regione):
                    bpy.ops.view3d.view_center_camera()
            sistemate += 1
        except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
            continue
    return bool(sistemate)


def comandi_nativi_di_navigazione() -> tuple[str, ...]:
    """I comandi di navigazione di Blender, lasciati intatti dall'estensione.

    Serve ai controlli automatici: nessuna scorciatoia di navigazione viene
    rimappata, quindi le abitudini di chi usa già Blender restano valide.
    """
    return (
        "view3d.view_rotate",
        "view3d.view_move",
        "view3d.view_zoom",
        "view3d.view_pan",
        "view3d.view_all",
        "view3d.view_selected",
        "view3d.view_axis",
        "view3d.view_persportho",
        "view3d.view_camera",
        "view3d.zoom",
    )
