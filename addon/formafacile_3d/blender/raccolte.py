"""Gruppi di oggetti: raccolte di Blender usate in modo semplice.

Un gruppo è una raccolta (`bpy.types.Collection`) con un nome in italiano: si
sceglie tutto insieme, si nasconde tutto insieme. Gli oggetti raggruppati
vengono spostati nella raccolta, così l'occhio del gruppo funziona come
l'utente se lo aspetta; "Togli dal gruppo" li riporta nella raccolta
principale della scena.

Nessun oggetto viene mai eliminato insieme al gruppo: il gruppo è
un'organizzazione, non un contenitore che cancella.
"""

from __future__ import annotations

from dataclasses import dataclass

import bpy

from .. import configuration
from ..localization import TESTI
from ..scene import regole_modellazione as regole
from . import selezione


class ErroreGruppo(RuntimeError):
    """Errore gestibile dei gruppi: messaggio già in italiano."""


@dataclass(frozen=True)
class Gruppo:
    """Fotografia di un gruppo della scena, per l'interfaccia."""

    chiave: str
    nome: str
    quanti: int = 0
    scelti: int = 0
    nascosto: bool = False


def _raccolta_principale(scena):
    """Raccolta principale della scena: quella che contiene tutto il resto."""
    return getattr(scena, "collection", None)


def raccolte(scena) -> list:
    """Raccolte della scena che non sono la raccolta principale."""
    if scena is None:
        return []
    principale = _raccolta_principale(scena)
    trovate = []
    for raccolta in getattr(bpy.data, "collections", ()) or ():
        if raccolta is principale:
            continue
        trovate.append(raccolta)
    return sorted(trovate, key=lambda raccolta: str(getattr(raccolta, "name", "")).casefold())


def gruppi(scena) -> tuple[Gruppo, ...]:
    """Fotografia dei gruppi, pronta per l'interfaccia."""
    risultato: list[Gruppo] = []
    for raccolta in raccolte(scena)[: configuration.GRUPPO_LIMITE_ELENCO + 1]:
        oggetti = list(getattr(raccolta, "objects", ()) or ())
        scelti = 0
        for oggetto in oggetti:
            try:
                scelti += 1 if oggetto.select_get() else 0
            except (AttributeError, ReferenceError, RuntimeError):
                continue
        risultato.append(
            Gruppo(
                chiave=str(raccolta.name),
                nome=str(raccolta.name),
                quanti=len(oggetti),
                scelti=scelti,
                nascosto=bool(getattr(raccolta, "hide_viewport", False)),
            )
        )
    return tuple(risultato)


def nome_libero(scena, base: str) -> str:
    """Primo nome di gruppo non ancora usato nella scena."""
    return regole.nome_gruppo_libero(
        (str(getattr(raccolta, "name", "")) for raccolta in raccolte(scena)), base
    )


def _scollega_da(raccolta, oggetto) -> None:
    """Toglie l'oggetto da una raccolta, se ci sta."""
    try:
        raccolta.objects.unlink(oggetto)
    except (AttributeError, ReferenceError, RuntimeError):
        return


def crea(scena, nome: str, oggetti) -> str:
    """Crea un gruppo con gli oggetti indicati e restituisce il nome usato.

    Gli oggetti vengono spostati nella raccolta nuova: restando anche nella
    raccolta principale, l'interruttore del gruppo non li nasconderebbe e il
    gruppo sarebbe una promessa a metà.
    """
    elenco = [oggetto for oggetto in oggetti if oggetto is not None]
    if not elenco:
        raise ErroreGruppo(TESTI["ERRORE_GRUPPO_SENZA_OGGETTI"])
    if scena is None:
        raise ErroreGruppo(TESTI["ERRORE_GRUPPO"])

    principale = _raccolta_principale(scena)
    try:
        raccolta = bpy.data.collections.new(str(nome) or nome_libero(scena, configuration.GRUPPO_NOME_BASE))
    except (AttributeError, RuntimeError, TypeError) as errore:
        raise ErroreGruppo(TESTI["ERRORE_GRUPPO"]) from errore
    try:
        if principale is not None:
            principale.children.link(raccolta)
        else:
            scena.collection.children.link(raccolta)
    except (AttributeError, ReferenceError, RuntimeError) as errore:
        raise ErroreGruppo(TESTI["ERRORE_GRUPPO"]) from errore

    for oggetto in elenco:
        try:
            raccolta.objects.link(oggetto)
        except (AttributeError, ReferenceError, RuntimeError):
            continue
        for altra in list(getattr(oggetto, "users_collection", ()) or ()):
            if altra is raccolta:
                continue
            _scollega_da(altra, oggetto)
    return str(raccolta.name)


def trova(scena, nome: str):
    """Raccolta con il nome indicato, se esiste."""
    for raccolta in raccolte(scena):
        if str(raccolta.name) == str(nome):
            return raccolta
    return None


def alterna_visibilita(scena, nome: str) -> bool | None:
    """Mostra o nasconde tutto il gruppo; restituisce il nuovo stato."""
    raccolta = trova(scena, nome)
    if raccolta is None:
        raise ErroreGruppo(TESTI["ERRORE_GRUPPO_ASSENTE"])
    nuovo = not bool(getattr(raccolta, "hide_viewport", False))
    try:
        raccolta.hide_viewport = nuovo
    except (AttributeError, ReferenceError, RuntimeError) as errore:
        raise ErroreGruppo(TESTI["ERRORE_GRUPPO"]) from errore
    return nuovo


def scegli(scena, nome: str, view_layer) -> selezione.EsitoSelezione:
    """Sceglie tutti gli oggetti del gruppo, con le regole della scelta normale."""
    raccolta = trova(scena, nome)
    if raccolta is None:
        raise ErroreGruppo(TESTI["ERRORE_GRUPPO_ASSENTE"])
    if view_layer is None:
        return selezione.EsitoSelezione()

    oggetti = list(getattr(raccolta, "objects", ()) or ())
    scelti = saltati = 0
    primo = None
    for oggetto in view_layer.objects:
        try:
            scelto = oggetto.select_get()
        except (AttributeError, ReferenceError, RuntimeError):
            scelto = False
        if scelto:
            oggetto.select_set(False)
    for oggetto in oggetti:
        if not selezione.scegliibile_in_gruppo(oggetto):
            saltati += 1
            continue
        try:
            oggetto.select_set(True)
        except (AttributeError, ReferenceError, RuntimeError):
            saltati += 1
            continue
        scelti += 1
        primo = primo or oggetto
    if primo is not None:
        try:
            view_layer.objects.active = primo
        except (AttributeError, ReferenceError, RuntimeError):
            pass
    return selezione.EsitoSelezione(scelti, saltati)


def gruppo_di(oggetto) -> str:
    """Nome del gruppo dell'oggetto, se appartiene a un gruppo."""
    for raccolta in getattr(oggetto, "users_collection", ()) or ():
        if getattr(raccolta, "name", ""):
            return str(raccolta.name)
    return ""


def togli(scena, oggetti) -> int:
    """Riporta gli oggetti nella raccolta principale e restituisce quanti ne ha spostati."""
    principale = _raccolta_principale(scena)
    if principale is None:
        return 0
    spostati = 0
    for oggetto in oggetti:
        if oggetto is None:
            continue
        if principale in list(getattr(oggetto, "users_collection", ()) or ()):
            continue
        try:
            principale.objects.link(oggetto)
        except (AttributeError, ReferenceError, RuntimeError):
            continue
        for altra in list(getattr(oggetto, "users_collection", ()) or ()):
            if altra is principale:
                continue
            _scollega_da(altra, oggetto)
        spostati += 1
    return spostati
