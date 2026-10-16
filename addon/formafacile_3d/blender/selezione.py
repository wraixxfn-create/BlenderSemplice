"""Scelta degli oggetti tramite i dati di Blender.

La scelta è fatta sui dati (e non con gli operatori della Vista 3D) perché
funziona allo stesso modo da qualsiasi pannello, anche in modalità senza
finestre.

Due regole diverse, come nell'elenco di Blender:

* le scelte di gruppo (Tutti, Inverti, Stesso tipo) prendono solo gli oggetti
  visibili e non bloccati: nessuno si ritrova scelto un oggetto che non vede;
* il singolo oggetto si può scegliere anche se è nascosto: chi comanda dall'elenco
  lo fa prima ricomparire (Blender non tiene scelto un oggetto che non si vede).
  Resta rifiutato solo un oggetto bloccato con "Blocca la scelta".

Il conteggio degli oggetti saltati torna all'utente come messaggio breve.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EsitoSelezione:
    """Risultato di una scelta, usato per i messaggi di stato."""

    scelti: int = 0
    saltati: int = 0


def _visibile(oggetto) -> bool:
    try:
        return bool(oggetto.visible_get())
    except (AttributeError, ReferenceError, RuntimeError):
        return False


def bloccato(oggetto) -> bool:
    """Indica se l'oggetto è protetto dalle scelte fatte nella Vista 3D."""
    return bool(getattr(oggetto, "hide_select", False))


def nascosto(oggetto) -> bool:
    """Indica se l'oggetto non si vede nella Vista 3D."""
    if getattr(oggetto, "hide_viewport", False):
        return True
    return not _visibile(oggetto)


def scegliibile(oggetto) -> bool:
    """Indica se l'oggetto si può scegliere da solo dall'elenco per nome.

    Un oggetto nascosto si può scegliere: serve a ritrovarlo nell'elenco e a
    farlo ricomparire. Solo un oggetto bloccato ("Blocca la scelta") rifiuta.
    """
    return not bloccato(oggetto)


def scegliibile_in_gruppo(oggetto) -> bool:
    """Indica se l'oggetto entra nelle scelte di gruppo (Tutti, Inverti, tipo).

    Gli oggetti nascosti restano fuori: chi preme "Tutti" non deve ritrovarsi
    scelto qualcosa che non vede.
    """
    return not bloccato(oggetto) and not nascosto(oggetto)


def motivo_rifiuto(oggetto) -> str:
    """Spiega perché un oggetto non si può scegliere: "bloccato", "nascosto" o vuoto."""
    if bloccato(oggetto):
        return "bloccato"
    if nascosto(oggetto):
        return "nascosto"
    return ""


def oggetti_della_scena(view_layer) -> list:
    """Oggetti della scena corrente, in ordine alfabetico per nome."""
    oggetti = list(view_layer.objects)
    return sorted(oggetti, key=lambda oggetto: oggetto.name.casefold())


def _attiva(view_layer, oggetto) -> None:
    view_layer.objects.active = oggetto


def scegli_tutto(view_layer) -> EsitoSelezione:
    """Sceglie tutti gli oggetti visibili e scegliibili."""
    scelti = saltati = 0
    attivo = None
    for oggetto in view_layer.objects:
        if scegliibile_in_gruppo(oggetto):
            oggetto.select_set(True)
            scelti += 1
            attivo = attivo or oggetto
        else:
            if oggetto.select_get():
                oggetto.select_set(False)
            saltati += 1
    if attivo is not None and view_layer.objects.active is None:
        _attiva(view_layer, attivo)
    return EsitoSelezione(scelti, saltati)


def descegli_tutto(view_layer) -> EsitoSelezione:
    """Toglie la scelta da tutti gli oggetti."""
    for oggetto in view_layer.objects:
        if oggetto.select_get():
            oggetto.select_set(False)
    _attiva(view_layer, None)
    return EsitoSelezione(0, 0)


def inverti_scelta(view_layer) -> EsitoSelezione:
    """Sceglie gli oggetti non scelti e toglie la scelta agli altri."""
    scelti = saltati = 0
    for oggetto in view_layer.objects:
        if not scegliibile_in_gruppo(oggetto):
            if oggetto.select_get():
                oggetto.select_set(False)
            saltati += 1
            continue
        nuovo = not oggetto.select_get()
        oggetto.select_set(nuovo)
        if nuovo:
            scelti += 1
    if scelti and getattr(view_layer.objects, "active", None) is None:
        for oggetto in view_layer.objects:
            if oggetto.select_get():
                _attiva(view_layer, oggetto)
                break
    return EsitoSelezione(scelti, saltati)


def scegli_stesso_tipo(view_layer, riferimento) -> EsitoSelezione:
    """Sceglie tutti gli oggetti dello stesso tipo dell'oggetto indicato."""
    if riferimento is None:
        return EsitoSelezione()
    scelti = saltati = 0
    for oggetto in view_layer.objects:
        if oggetto.type != riferimento.type:
            continue
        if scegliibile_in_gruppo(oggetto):
            oggetto.select_set(True)
            scelti += 1
        else:
            saltati += 1
    if scegliibile_in_gruppo(riferimento):
        _attiva(view_layer, riferimento)
    return EsitoSelezione(scelti, saltati)


def scegli_oggetto(view_layer, oggetto, modo: str) -> EsitoSelezione:
    """Sceglie un singolo oggetto: sostituendo la scelta, aggiungendo o togliendo."""
    if not scegliibile(oggetto):
        return EsitoSelezione(0, 1)

    if modo == "rimuovi":
        oggetto.select_set(False)
        if view_layer.objects.active == oggetto:
            nuovo_attivo = next(
                (
                    altro
                    for altro in view_layer.objects
                    if altro != oggetto and altro.select_get()
                ),
                None,
            )
            _attiva(view_layer, nuovo_attivo)
        return EsitoSelezione(0, 0)

    if modo == "sostituisci":
        for altro in view_layer.objects:
            if altro.select_get():
                altro.select_set(False)

    oggetto.select_set(True)
    _attiva(view_layer, oggetto)
    return EsitoSelezione(1, 0)


def alterna_scelta(view_layer, oggetto) -> EsitoSelezione:
    """Aggiunge o toglie l'oggetto dalla scelta, senza toccare gli altri."""
    if not scegliibile(oggetto):
        return EsitoSelezione(0, 1)
    if oggetto.select_get():
        return scegli_oggetto(view_layer, oggetto, "rimuovi")
    return scegli_oggetto(view_layer, oggetto, "aggiungi")
