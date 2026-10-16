"""Disegno del piano dell'interfaccia su un pannello di Blender.

Il disegno non decide nulla: riceve un piano già pronto e lo traduce in
elementi di `bpy.types.UILayout`. Se un dato non è più disponibile, il campo
viene sostituito da una riga disattivata invece di far fallire tutto il
pannello: il pannello deve restare utilizzabile in ogni situazione.
"""

from __future__ import annotations

from .. import configuration
from ..localization import TESTI
from .modello import Anteprima, Azione, Campo, Etichetta, Gruppo, Pannello, Riga


def disegna_pannello(layout, pannello: Pannello, risolutore: dict[str, object]) -> None:
    """Disegna tutti i gruppi di un pannello."""
    for gruppo in pannello.gruppi:
        disegna_gruppo(layout, gruppo, risolutore)


def disegna_gruppo(layout, gruppo: Gruppo, risolutore: dict[str, object]) -> None:
    """Disegna un riquadro con il suo titolo e le sue righe."""
    riquadro = layout.box()
    if gruppo.titolo:
        riquadro.label(text=gruppo.titolo)
    for riga in gruppo.righe:
        disegna_riga(riquadro, riga, risolutore)


def disegna_riga(contenitore, riga: Riga, risolutore: dict[str, object]) -> None:
    """Disegna una riga orizzontale di elementi."""
    blocco = contenitore.row(align=not riga.distanziata)
    if riga.disabilitata:
        blocco.enabled = False
    for elemento in riga.elementi:
        if isinstance(elemento, Azione):
            disegna_azione(blocco, elemento)
        elif isinstance(elemento, Campo):
            disegna_campo(blocco, elemento, risolutore)
        elif isinstance(elemento, Anteprima):
            disegna_anteprima(blocco, elemento, risolutore)
        else:
            disegna_etichetta(blocco, elemento)


def disegna_azione(contenitore, azione: Azione) -> None:
    """Disegna un pulsante che richiama un comando."""
    parametri: dict[str, object] = {"text": "" if azione.solo_icona else azione.testo}
    if azione.icona:
        parametri["icon"] = azione.icona
    if azione.premuto:
        parametri["depress"] = True

    try:
        proprieta = contenitore.operator(azione.idname, **parametri)
    except (TypeError, ValueError, AttributeError):
        contenitore.label(text=azione.testo[: configuration.LUNGHEZZA_MASSIMA_AZIONE], icon="ERROR")
        return

    for chiave, valore in azione.parametri:
        try:
            setattr(proprieta, chiave, valore)
        except (AttributeError, TypeError, ValueError):
            continue


def disegna_campo(contenitore, campo: Campo, risolutore: dict[str, object]) -> None:
    """Disegna un campo collegato a un dato reale, con controllo di disponibilità."""
    datablock = risolutore.get(campo.chiave)
    if campo.riferimento == configuration.RIFERIMENTO_DATI:
        datablock = getattr(datablock, "data", None)

    if datablock is None or not _percorso_disponibile(datablock, campo.proprieta):
        blocco = contenitore.row(align=True)
        blocco.enabled = False
        blocco.label(text=campo.testo or campo.proprieta)
        return

    parametri: dict[str, object] = {"text": "" if campo.solo_icona else campo.testo}
    if campo.icona:
        parametri["icon"] = campo.icona
    if campo.espanso:
        parametri["expand"] = True
    if campo.interruttore:
        parametri["toggle"] = True
    if campo.indice is not None:
        parametri["index"] = campo.indice

    try:
        contenitore.prop(datablock, campo.proprieta, **parametri)
    except (TypeError, ValueError, AttributeError, RuntimeError):
        contenitore.label(text=TESTI["ETICHETTA_CAMPO_NON_DISPONIBILE"], icon="ERROR")


def disegna_anteprima(contenitore, anteprima: Anteprima, risolutore: dict[str, object]) -> None:
    """Disegna l'anteprima di un dato di Blender, con ripiego sul testo.

    L'anteprima del materiale è un disegno di Blender (`template_preview`): se
    il dato non c'è, o se Blender non sa disegnarlo, resta il testo, così il
    pannello non si rompe e non promette un'anteprima che non c'è.
    """
    datablock = risolutore.get(anteprima.chiave)
    disegna = getattr(contenitore, "template_preview", None)
    if datablock is None or disegna is None:
        contenitore.label(text=anteprima.testo, icon="INFO")
        return
    try:
        disegna(datablock)
    except (TypeError, ValueError, AttributeError, RuntimeError):
        contenitore.label(text=anteprima.testo, icon="INFO")


def disegna_etichetta(contenitore, etichetta: Etichetta) -> None:
    """Disegna un testo semplice; gli avvisi sono evidenziati."""
    blocco = contenitore.row(align=True)
    if etichetta.avviso:
        blocco.alert = True
    parametri: dict[str, object] = {"text": etichetta.testo}
    if etichetta.icona:
        parametri["icon"] = etichetta.icona
    blocco.label(**parametri)


def _percorso_disponibile(datablock: object, proprieta: str) -> bool:
    """Verifica che la proprietà esista, anche se è un percorso annidato."""
    attuale = datablock
    for pezzo in proprieta.split("."):
        if attuale is None or not hasattr(attuale, pezzo):
            return False
        attuale = getattr(attuale, pezzo)
    return True
