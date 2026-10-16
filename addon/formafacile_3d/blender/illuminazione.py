"""Illuminazione della scena: luci pronte, sfondo e intensità.

Le illuminazioni sono quelle dichiarate in `scene/aspetto.py`: qui vengono
create come vere luci di Blender dentro una raccolta dedicata. Ogni luce porta
un segno di riconoscimento, quindi una nuova illuminazione sostituisce quella
creata da FormaFacile *senza toccare* le luci dell'utente.

L'azione automatica legge la grandezza della scena e riscala posizioni, potenze
e dimensioni delle luci: una scena piccola e una grande ricevono la stessa
luminosità, invece di valori fissi che vanno bene solo per un caso.
"""

from __future__ import annotations

import bpy
import mathutils

from .. import configuration
from ..localization import TESTI
from ..scene import aspetto


def _raccolta(scena):
    """Raccolta delle luci di FormaFacile, creata la prima volta che serve."""
    nome = TESTI["NOME_RACCOLTA_ILLUMINAZIONE"]
    raccolta = bpy.data.collections.get(nome)
    if raccolta is None:
        try:
            raccolta = bpy.data.collections.new(nome)
            scena.collection.children.link(raccolta)
        except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
            return None
    elif raccolta.name not in {figlia.name for figlia in scena.collection.children}:
        try:
            scena.collection.children.link(raccolta)
        except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
            return None
    return raccolta


def luci_formafacile(scena) -> list:
    """Luci create da FormaFacile, riconosciute dal segno lasciato sull'oggetto."""
    trovate = []
    for oggetto in getattr(scena, "objects", ()) or ():
        if getattr(oggetto, "type", "") != "LIGHT":
            continue
        try:
            if configuration.CHIAVE_MARCATORE_LUCI in oggetto:
                trovate.append(oggetto)
        except (AttributeError, ReferenceError, RuntimeError, TypeError):
            continue
    return trovate


def rimuovi_luci(scena) -> int:
    """Toglie le luci di FormaFacile, lasciando quelle dell'utente."""
    rimosse = 0
    for oggetto in list(luci_formafacile(scena)):
        dati = getattr(oggetto, "data", None)
        try:
            bpy.data.objects.remove(oggetto, do_unlink=True)
            rimosse += 1
        except (AttributeError, ReferenceError, RuntimeError, TypeError):
            continue
        try:
            if dati is not None and dati.users == 0:
                bpy.data.lights.remove(dati)
        except (AttributeError, ReferenceError, RuntimeError, TypeError):
            continue
    return rimosse


def raggio_scena(context) -> float:
    """Raggio della scena: metà della diagonale degli oggetti visibili.

    Serve all'illuminazione automatica. Senza oggetti si usa un raggio di
    ripiego, così le luci non finiscono tutte addosso al cursore 3D.
    """
    punti: list = []
    scena = getattr(context, "scene", None)
    for oggetto in getattr(scena, "objects", ()) or ():
        if getattr(oggetto, "type", "") == "LIGHT":
            continue
        if getattr(oggetto, "type", "") == "CAMERA":
            continue
        try:
            matrice = oggetto.matrix_world
            punti.extend(matrice @ mathutils.Vector(angolo) for angolo in oggetto.bound_box)
        except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
            continue
    if not punti:
        return aspetto.RAGGIO_SCENA_VUOTA
    minimo = mathutils.Vector(tuple(min(punto[i] for punto in punti) for i in range(3)))
    massimo = mathutils.Vector(tuple(max(punto[i] for punto in punti) for i in range(3)))
    centro = (minimo + massimo) * 0.5
    return max(
        max((punto - centro).length for punto in punti),
        configuration.DISTANZA_MINIMA_VISTA,
    )


def centro_scena(context):
    """Centro del riquadro della scena: dove puntano le luci."""
    punti: list = []
    scena = getattr(context, "scene", None)
    for oggetto in getattr(scena, "objects", ()) or ():
        if getattr(oggetto, "type", "") in {"LIGHT", "CAMERA"}:
            continue
        try:
            matrice = oggetto.matrix_world
            punti.extend(matrice @ mathutils.Vector(angolo) for angolo in oggetto.bound_box)
        except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
            continue
    if not punti:
        return mathutils.Vector((0.0, 0.0, 0.0))
    minimo = mathutils.Vector(tuple(min(punto[i] for punto in punti) for i in range(3)))
    massimo = mathutils.Vector(tuple(max(punto[i] for punto in punti) for i in range(3)))
    return (minimo + massimo) * 0.5


def _fattore_adattamento(context, preset: aspetto.Illuminazione) -> float:
    """Di quanto ingrandire le luci per adattarle alla scena.

    Le potenze crescono con il quadrato della distanza: così l'oggetto resta
    illuminato allo stesso modo sia in una scena piccola sia in una grande.
    Il fattore è limitato per non creare valori assurdi su scene enormi.
    """
    if not preset.adatta_alla_scena:
        return 1.0
    return max(0.20, min(20.0, raggio_scena(context) / aspetto.RAGGIO_RIFERIMENTO))


def _orienta_verso(oggetto, bersaglio) -> None:
    """Gira la luce (che punta lungo -Z) verso il centro della scena."""
    try:
        direzione = mathutils.Vector(bersaglio) - mathutils.Vector(oggetto.location)
        if direzione.length == 0.0:
            return
        oggetto.rotation_euler = direzione.to_track_quat("-Z", "Y").to_euler()
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        return


def _crea_luce(raccolta, descrizione: aspetto.Luce, bersaglio, fattore: float, preset: str):
    """Crea una luce del preset, orientata verso il centro della scena."""
    try:
        dati = bpy.data.lights.new(name=TESTI[descrizione.nome_chiave], type=descrizione.tipo)
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        return None

    energia = float(descrizione.energia) * fattore * fattore
    try:
        dati.energy = energia
        dati.color = tuple(float(valore) for valore in descrizione.colore)
        if descrizione.tipo == "AREA":
            dati.shape = "SQUARE"
            dati.size = max(float(descrizione.dimensione) * fattore, 0.05)
        elif descrizione.tipo == "SUN":
            # Il Sole non si "avvicina": l'angolo decide quanto sono morbide le ombre.
            dati.angle = max(float(descrizione.angolo), 0.0)
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        pass

    try:
        oggetto = bpy.data.objects.new(TESTI[descrizione.nome_chiave], dati)
        raccolta.objects.link(oggetto)
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        try:
            bpy.data.lights.remove(dati)
        except (AttributeError, ReferenceError, RuntimeError, TypeError):
            pass
        return None

    try:
        oggetto.location = tuple(float(valore) * fattore for valore in descrizione.posizione)
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        pass
    _orienta_verso(oggetto, bersaglio)
    for chiave, valore in (
        (configuration.CHIAVE_MARCATORE_LUCI, preset),
        (configuration.CHIAVE_ENERGIA_BASE, energia),
    ):
        try:
            oggetto[chiave] = valore
        except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
            continue
    return oggetto


def imposta_sfondo(context, colore, intensita: float) -> bool:
    """Imposta il colore e la luminosità dello sfondo della scena.

    Se la scena non ha ancora un fondale, ne viene creato uno: senza, le
    superfici riflettenti resterebbero nere.
    """
    scena = getattr(context, "scene", None)
    if scena is None:
        return False
    mondo = getattr(scena, "world", None)
    if mondo is None:
        try:
            mondo = bpy.data.worlds.new(TESTI["NOME_RACCOLTA_ILLUMINAZIONE"])
            scena.world = mondo
        except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
            return False

    colore = tuple(
        aspetto.limita(valore, 0.0, 1.0) for valore in (tuple(colore)[:3] if colore else (0.0, 0.0, 0.0))
    )
    intensita = aspetto.limita(
        intensita, configuration.SFONDO_INTENSITA_MINIMA, configuration.SFONDO_INTENSITA_MASSIMA
    )
    try:
        mondo.use_nodes = True
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        pass
    albero = getattr(mondo, "node_tree", None)
    nodo = None
    if albero is not None:
        nodo = next(
            (n for n in albero.nodes if n.bl_idname == "ShaderNodeBackground"), None
        )
    if nodo is not None:
        for nome, valore in (("Color", (colore[0], colore[1], colore[2], 1.0)), ("Strength", intensita)):
            try:
                ingresso = nodo.inputs.get(nome)
                if ingresso is not None:
                    ingresso.default_value = valore
            except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
                continue
    try:
        mondo.color = (colore[0], colore[1], colore[2])
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        pass
    return True


def applica(context, chiave: str):
    """Crea le luci dell'illuminazione indicata e sistema lo sfondo.

    Restituisce il preset applicato e l'elenco delle luci create, oppure None se
    non è stato possibile creare nulla.
    """
    scena = getattr(context, "scene", None)
    if scena is None:
        return None
    preset = aspetto.illuminazione(chiave)
    raccolta = _raccolta(scena)
    if raccolta is None:
        return None

    rimuovi_luci(scena)
    fattore = _fattore_adattamento(context, preset)
    bersaglio = centro_scena(context)
    create = []
    for descrizione in preset.luci:
        luce = _crea_luce(raccolta, descrizione, bersaglio, fattore, preset.chiave)
        if luce is not None:
            create.append(luce)
    if not create:
        return None
    imposta_sfondo(context, preset.sfondo, preset.sfondo_intensita)
    return preset, tuple(create)


def cambia_intensita(scena, intensita: float, preset: str = "") -> int:
    """Moltiplica la potenza delle luci create da FormaFacile.

    La potenza di partenza resta scritta su ogni luce: cambiando l'intensità si
    torna sempre al valore del preset invece di accumulare moltiplicazioni.
    """
    intensita = aspetto.limita(
        intensita, configuration.INTENSITA_LUCE_MINIMA, configuration.INTENSITA_LUCE_MASSIMA
    )
    cambiate = 0
    for oggetto in luci_formafacile(scena):
        dati = getattr(oggetto, "data", None)
        if dati is None:
            continue
        try:
            base = float(oggetto[configuration.CHIAVE_ENERGIA_BASE])
        except (AttributeError, KeyError, ReferenceError, RuntimeError, TypeError, ValueError):
            try:
                base = float(dati.energy)
                oggetto[configuration.CHIAVE_ENERGIA_BASE] = base
            except (AttributeError, KeyError, ReferenceError, RuntimeError, TypeError, ValueError):
                continue
        try:
            dati.energy = max(base * intensita, configuration.POTENZA_LUCE_MINIMA)
            cambiate += 1
        except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
            continue
    return cambiate


def descrizione_attuale(scena) -> tuple[str, int]:
    """Chiave dell'illuminazione applicata e numero di luci, per l'interfaccia."""
    luci = luci_formafacile(scena)
    if not luci:
        return "", 0
    chiave = ""
    for oggetto in luci:
        try:
            valore = str(oggetto[configuration.CHIAVE_MARCATORE_LUCI])
        except (AttributeError, KeyError, ReferenceError, RuntimeError, TypeError, ValueError):
            continue
        if valore:
            chiave = valore
            break
    return chiave, len(luci)
