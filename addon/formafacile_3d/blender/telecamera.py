"""Telecamera e modi di guardare la scena.

Tre cose diverse, tenute qui perché parlano dello stesso argomento:

* creare una telecamera e farla inquadrare gli oggetti scelti, calcolando la
  distanza sulla forma vera degli oggetti (non su un numero fisso);
* riportare la telecamera dove l'aveva messa FormaFacile all'inizio;
* scegliere che cosa mostra la Vista 3D: la vista di lavoro (colori semplici,
  disegno veloce) oppure l'anteprima dell'immagine finale (materiali, luci e
  ombre), così i due modi si distinguono a colpo d'occhio.

La telecamera creata qui ricorda la sua posizione iniziale: "Ripristina la
telecamera" è quindi una promessa mantenibile, non un comando che indovina.
"""

from __future__ import annotations

import math

import bpy
import mathutils

from .. import comandi, configuration
from ..localization import TESTI
from . import vista as servizio_vista

# Direzione da cui guarda la scena una telecamera nuova: davanti, a destra e
# un po' in alto, come la vista di partenza di Blender.
DIREZIONE_PREDEFINITA = (0.85, -1.0, 0.45)
# Margine intorno agli oggetti inquadrati: si vede un po' d'aria, non il bordo.
MARGINE_INQUADRATURA = 1.15


def _riquadro(oggetti) -> tuple[object, float]:
    """Centro e raggio della forma vera degli oggetti, angoli compresi."""
    punti: list = []
    for oggetto in oggetti:
        try:
            matrice = oggetto.matrix_world
            punti.extend(matrice @ mathutils.Vector(angolo) for angolo in oggetto.bound_box)
        except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
            continue
    if not punti:
        return mathutils.Vector((0.0, 0.0, 0.0)), 0.0
    minimo = mathutils.Vector(tuple(min(punto[i] for punto in punti) for i in range(3)))
    massimo = mathutils.Vector(tuple(max(punto[i] for punto in punti) for i in range(3)))
    centro = (minimo + massimo) * 0.5
    return centro, max((punto - centro).length for punto in punti)


def _distanza_per_raggio(telecamera, raggio: float) -> float:
    """Distanza a cui un oggetto di quel raggio entra tutto nell'inquadratura.

    Si usa la più stretta fra le due aperture della telecamera: è il caso
    peggiore, quello che garantisce che nulla resti fuori.
    """
    if raggio <= 0.0:
        return configuration.DISTANZA_VUOTA_PREDEFINITA
    dati = getattr(telecamera, "data", None)
    aperture = []
    for nome in ("angle_x", "angle_y"):
        try:
            valore = float(getattr(dati, nome))
        except (AttributeError, ReferenceError, TypeError, ValueError):
            continue
        if 0.0 < valore < math.pi:
            aperture.append(valore)
    apertura = min(aperture) if aperture else math.radians(50.0)
    distanza = raggio / max(math.tan(apertura * 0.5), 1e-4)
    return max(distanza * MARGINE_INQUADRATURA, configuration.DISTANZA_MINIMA_VISTA)


def _guarda(oggetto_telecamera, centro) -> None:
    """Gira la telecamera verso il centro: l'obiettivo è l'asse -Z."""
    try:
        direzione = mathutils.Vector(centro) - mathutils.Vector(oggetto_telecamera.location)
        if direzione.length <= 0.0:
            return
        oggetto_telecamera.rotation_euler = direzione.to_track_quat("-Z", "Y").to_euler()
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        return


def _posiziona(oggetto_telecamera, centro, raggio: float, direzione=DIREZIONE_PREDEFINITA) -> None:
    """Mette la telecamera intorno al centro, a distanza utile."""
    versore = mathutils.Vector(direzione)
    if versore.length <= 0.0:
        versore = mathutils.Vector(DIREZIONE_PREDEFINITA)
    versore.normalize()
    distanza = _distanza_per_raggio(oggetto_telecamera, float(raggio))
    try:
        oggetto_telecamera.location = mathutils.Vector(centro) + versore * distanza
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        return
    _guarda(oggetto_telecamera, centro)


def _ricorda_posizione_iniziale(oggetto_telecamera) -> None:
    """Scrive sulla telecamera la posizione a cui tornare."""
    try:
        dati = [float(valore) for valore in oggetto_telecamera.location]
        dati.extend(float(valore) for valore in oggetto_telecamera.rotation_euler)
        oggetto_telecamera[configuration.CHIAVE_TELECAMERA_INIZIALE] = dati
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        return


def ha_posizione_iniziale(oggetto_telecamera) -> bool:
    """Indica se la telecamera sa dove tornare."""
    try:
        return len(oggetto_telecamera[configuration.CHIAVE_TELECAMERA_INIZIALE]) == 6
    except (AttributeError, KeyError, ReferenceError, RuntimeError, TypeError, ValueError):
        return False


def oggetti_da_inquadrare(context, scelti) -> tuple[list, bool]:
    """Oggetti da inquadrare e se sono quelli scelti o tutta la scena.

    Restituisce la scelta dell'utente quando c'è; altrimenti tutti gli oggetti
    visibili tranne telecamere e luci, che non hanno una forma da inquadrare.
    """
    scelti = [oggetto for oggetto in scelti if getattr(oggetto, "type", "") != "CAMERA"]
    if scelti:
        return scelti, True
    scena = getattr(context, "scene", None)
    visibili = [
        oggetto
        for oggetto in getattr(scena, "objects", ()) or ()
        if getattr(oggetto, "type", "") not in {"CAMERA", "LIGHT"}
    ]
    return visibili, False


def aggiungi(context):
    """Crea una telecamera che inquadra la scena e la usa per l'immagine finale."""
    scena = getattr(context, "scene", None)
    if scena is None:
        return None
    try:
        dati = bpy.data.cameras.new(name=TESTI["NOME_TELECAMERA"])
        oggetto = bpy.data.objects.new(name=TESTI["NOME_TELECAMERA"], object_data=dati)
        scena.collection.objects.link(oggetto)
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        return None

    servizio_vista.aggiorna_scena(context)
    oggetti, _scelti = oggetti_da_inquadrare(context, [])
    centro, raggio = _riquadro(oggetti)
    _posiziona(oggetto, centro, raggio)
    _ricorda_posizione_iniziale(oggetto)
    try:
        scena.camera = oggetto
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        pass
    # La telecamera appena creata resta scelta: chi preme il pulsante la vede
    # comparire e può subito spostarla con gli strumenti di Blender.
    try:
        oggetto.select_set(True)
        context.view_layer.objects.active = oggetto
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        pass
    return oggetto


def inquadra(context, oggetto_telecamera, scelti) -> tuple[bool, bool]:
    """Fa inquadrare alla telecamera gli oggetti indicati.

    Restituisce (riuscito, erano_scelti): il secondo valore permette al
    messaggio di dire con onestà che cosa è stato inquadrato.
    """
    if oggetto_telecamera is None or getattr(oggetto_telecamera, "type", "") != "CAMERA":
        return False, False
    oggetti, erano_scelti = oggetti_da_inquadrare(context, scelti)
    if not oggetti:
        return False, erano_scelti
    servizio_vista.aggiorna_scena(context)
    centro, raggio = _riquadro(oggetti)
    # La telecamera resta dalla stessa parte da cui guarda adesso: cambiare
    # inquadratura non deve spostare il punto di vista attorno alla scena.
    try:
        direzione = mathutils.Vector(oggetto_telecamera.location) - mathutils.Vector(centro)
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        direzione = mathutils.Vector(DIREZIONE_PREDEFINITA)
    _posiziona(oggetto_telecamera, centro, raggio, direzione if direzione.length > 0 else DIREZIONE_PREDEFINITA)
    return True, erano_scelti


def ripristina(oggetto_telecamera) -> bool:
    """Riporta la telecamera alla posizione iniziale registrata."""
    if oggetto_telecamera is None or getattr(oggetto_telecamera, "type", "") != "CAMERA":
        return False
    try:
        dati = [float(valore) for valore in oggetto_telecamera[configuration.CHIAVE_TELECAMERA_INIZIALE]]
    except (AttributeError, KeyError, ReferenceError, RuntimeError, TypeError, ValueError):
        return False
    if len(dati) != 6:
        return False
    try:
        oggetto_telecamera.location = dati[:3]
        oggetto_telecamera.rotation_euler = dati[3:]
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        return False
    return True


def centra_vista(context, oggetti) -> bool:
    """Porta al centro della vista gli oggetti indicati, senza cambiare lo zoom.

    Blender centra la vista sul cursore 3D: il cursore viene spostato per un
    istante sul centro degli oggetti e poi rimesso dov'era, così la scena non
    cambia e l'inquadratura sì.
    """
    oggetti = [oggetto for oggetto in oggetti if getattr(oggetto, "type", "") != "CAMERA"]
    if not oggetti:
        return False
    servizio_vista.aggiorna_scena(context)
    centro, raggio = _riquadro(oggetti)
    if raggio <= 0.0:
        return False
    scena = getattr(context, "scene", None)
    cursore = getattr(scena, "cursor", None)
    if cursore is None:
        return False
    prima = tuple(float(valore) for valore in cursore.location)
    try:
        cursore.location = centro
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        return False
    riuscito = servizio_vista.esegui_in_vista(context, comandi.ID_NATIVO_CENTRA_VISTA) is not None
    try:
        cursore.location = prima
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        pass
    return riuscito


def _spazi_vista(context):
    """Spazi delle Viste 3D disponibili adesso."""
    schermi = []
    for finestra in getattr(getattr(context, "window_manager", None), "windows", ()) or ():
        schermo = getattr(finestra, "screen", None)
        if schermo is not None:
            schermi.append(schermo)
    for schermo in schermi:
        for area in getattr(schermo, "areas", ()) or ():
            if getattr(area, "type", "") != "VIEW_3D":
                continue
            spazio = getattr(getattr(area, "spaces", None), "active", None)
            if spazio is not None:
                yield spazio


def imposta_ombreggiatura(context, tipo: str) -> int:
    """Sceglie come mostra la scena la Vista 3D: lavoro oppure anteprima."""
    cambiate = 0
    for spazio in _spazi_vista(context):
        ombreggiatura = getattr(spazio, "shading", None)
        if ombreggiatura is None or not hasattr(ombreggiatura, "type"):
            continue
        try:
            ombreggiatura.type = tipo
            cambiate += 1
        except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
            continue
    return cambiate


def in_anteprima(context) -> bool:
    """Indica se la Vista 3D sta mostrando l'anteprima dell'immagine finale."""
    for spazio in _spazi_vista(context):
        ombreggiatura = getattr(spazio, "shading", None)
        if str(getattr(ombreggiatura, "type", "")) == configuration.OMBREGGIATURA_ANTEPRIMA:
            return True
    return False


def modo_attuale(context) -> str:
    """Chiave del testo del modo di guardare la scena attivo adesso."""
    if in_anteprima(context):
        return "ETICHETTA_MODO_VISTA_ANTEPRIMA"
    return "ETICHETTA_MODO_VISTA_LAVORO"
