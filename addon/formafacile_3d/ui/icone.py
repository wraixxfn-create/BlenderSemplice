"""Icone e parole italiane per i tipi di oggetto.

I nomi delle icone sono quelli ufficiali di Blender 4.5 LTS (elenco
`UI_icons.hh` alla versione 4.5.14): un nome inesistente farebbe fallire il
disegno del pannello, quindi l'elenco è chiuso e verificato dai test.
"""

from __future__ import annotations

from ..localization import TESTI


# Solo queste icone sono usate dall'interfaccia: modificarle richiede di
# aggiornare anche l'elenco di controllo nei test automatici.
ICONE_USATE = frozenset(
    {
        "ADD",
        "ARMATURE_DATA",
        "BACK",
        "CAMERA_DATA",
        "CHECKBOX_DEHLT",
        "CHECKBOX_HLT",
        "CHECKMARK",
        "COPYDOWN",
        "CURVE_DATA",
        "DUPLICATE",
        "EMPTY_DATA",
        "FONT_DATA",
        "FORWARD",
        "FULLSCREEN_ENTER",
        "GREASEPENCIL",
        "HIDE_OFF",
        "HIDE_ON",
        "HOME",
        "INFO",
        "LATTICE_DATA",
        "LIGHT",
        "LOCKED",
        "LOOP_BACK",
        "LOOP_FORWARDS",
        "MESH_CONE",
        "MESH_CUBE",
        "MESH_CYLINDER",
        "MESH_DATA",
        "MESH_PLANE",
        "MESH_TORUS",
        "MESH_UVSPHERE",
        "OBJECT_DATA",
        "OBJECT_ORIGIN",
        "ORIENTATION_GIMBAL",
        "PASTEDOWN",
        "PIVOT_BOUNDBOX",
        "REMOVE",
        "SNAP_FACE",
        "SPEAKER",
        "TRASH",
        "UNLOCKED",
        "VIEWZOOM",
        "VOLUME_DATA",
        "X",
        "ZOOM_SELECTED",
    }
)

# Icone usate per il confine tecnico fra oggetti di tipo diverso.
_ICONE_TIPO = {
    "MESH": "MESH_DATA",
    "LIGHT": "LIGHT",
    "CAMERA": "CAMERA_DATA",
    "EMPTY": "EMPTY_DATA",
    "CURVE": "CURVE_DATA",
    "SURFACE": "CURVE_DATA",
    "FONT": "FONT_DATA",
    "META": "CURVE_DATA",
    "ARMATURE": "ARMATURE_DATA",
    "LATTICE": "LATTICE_DATA",
    "VOLUME": "VOLUME_DATA",
    "SPEAKER": "SPEAKER",
    "GREASEPENCIL": "GREASEPENCIL",
}

# Parole semplici per il tipo di oggetto; il tipo tecnico resta nella modalità completa.
_PAROLE_TIPO = {
    "MESH": "TIPO_FORMA",
    "LIGHT": "TIPO_LUCE",
    "CAMERA": "TIPO_TELECAMERA",
    "EMPTY": "TIPO_SEGNAPOSTO",
    "CURVE": "TIPO_CURVA",
    "SURFACE": "TIPO_CURVA",
    "FONT": "TIPO_TESTO",
    "META": "TIPO_CURVA",
    "ARMATURE": "TIPO_STRUTTURA",
    "LATTICE": "TIPO_STRUTTURA",
    "VOLUME": "TIPO_VOLUME",
    "SPEAKER": "TIPO_ALTRO",
    "GREASEPENCIL": "TIPO_DISEGNO",
}

# Gruppi usati per riassumere una scelta multipla in parole semplici.
_GRUPPI_PLURALE = {
    "MESH": "TIPO_FORMA_PLURALE",
    "LIGHT": "TIPO_LUCE_PLURALE",
    "CAMERA": "TIPO_TELECAMERA_PLURALE",
}


def icona_tipo(tipo: str) -> str:
    """Icona della barra laterale per un tipo di oggetto di Blender."""
    return _ICONE_TIPO.get(tipo, "OBJECT_DATA")


def parola_tipo(tipo: str) -> str:
    """Parola italiana semplice per un tipo di oggetto di Blender."""
    return TESTI[_PAROLE_TIPO.get(tipo, "TIPO_ALTRO")]


def chiave_plurale_tipo(tipo: str) -> str:
    """Chiave del testo usato per contare più oggetti dello stesso tipo."""
    return _GRUPPI_PLURALE.get(tipo, "TIPO_ALTRO_PLURALE")
