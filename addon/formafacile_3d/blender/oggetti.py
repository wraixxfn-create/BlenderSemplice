"""Azioni sui dati degli oggetti: rinominare, duplicare, eliminare, nascondere."""

from __future__ import annotations

from dataclasses import dataclass

import bpy

from ..localization import TESTI
from ..logging_service import ottieni_logger
from ..scene.nomi import pulisci_nome


def aggiorna_vista() -> None:
    """Aggiorna la scena dopo un cambio di visibilità.

    Blender ricalcola da solo dopo ogni comando, ma l'aggiornamento esplicito
    evita che il pannello mostri per un istante lo stato precedente.
    """
    vettore = getattr(bpy.context, "view_layer", None)
    if vettore is None:
        return
    try:
        vettore.update()
    except (AttributeError, ReferenceError, RuntimeError):
        return


def rinomina(oggetto, nome: str) -> tuple[str, bool]:
    """Rinomina oggetto e, se i dati non sono condivisi, anche la sua geometria.

    Restituisce il nome finale e se qualcosa è cambiato davvero.
    """
    nome_pulito = pulisci_nome(nome)
    if not nome_pulito:
        raise ValueError(TESTI["ERRORE_NOME_VUOTO"])
    if nome_pulito == oggetto.name:
        return oggetto.name, False

    precedente = oggetto.name
    oggetto.name = nome_pulito
    nome_finale = oggetto.name

    dati = getattr(oggetto, "data", None)
    if dati is not None and getattr(dati, "users", 0) == 1:
        if nome_finale != precedente or dati.name.startswith("Geometria"):
            try:
                dati.name = f"{TESTI['PREFISSO_GEOMETRIA']} {nome_finale}"
            except (TypeError, ValueError, RuntimeError):
                ottieni_logger().info(TESTI["LOG_ERRORE_NOME_DATI"])
    return nome_finale, True


def duplica(oggetto, spostamento: tuple[float, float, float]):
    """Crea una copia indipendente dell'oggetto, spostata di poco.

    La copia riceve una propria geometria e viene collegata alle stesse
    raccolte dell'originale: si comporta come la duplicazione di Blender, ma
    senza dipendere dalla posizione del mouse.
    """
    copia = oggetto.copy()
    if getattr(oggetto, "data", None) is not None:
        copia.data = oggetto.data.copy()

    raccolte = list(oggetto.users_collection)
    if not raccolte:
        raccolte = [bpy.context.scene.collection]
    for raccolta in raccolte:
        raccolta.objects.link(copia)

    copia.name = f"{oggetto.name} {TESTI['SUFFISSO_COPIA']}"
    copia.location = (
        oggetto.location[0] + spostamento[0],
        oggetto.location[1] + spostamento[1],
        oggetto.location[2] + spostamento[2],
    )
    return copia


def elimina(oggetti) -> int:
    """Elimina gli oggetti indicati e restituisce quanti ne sono stati tolti."""
    eliminati = 0
    for oggetto in list(oggetti):
        try:
            bpy.data.objects.remove(oggetto, do_unlink=True)
            eliminati += 1
        except (ReferenceError, RuntimeError):
            continue
    return eliminati


def imposta_visibilita(oggetto, visibile: bool) -> bool:
    """Mostra o nasconde l'oggetto nella Vista 3D, come l'icona a occhio.

    Vengono usati gli stessi due interruttori di Blender ("Nascondi nella
    vista" e l'occhio della Vista 3D), così il comando funziona anche su un
    oggetto nascosto da Blender stesso.
    """
    oggetto.hide_viewport = not visibile
    if not visibile:
        try:
            oggetto.hide_set(True)
        except (AttributeError, ReferenceError, RuntimeError):
            pass
        if oggetto.select_get():
            oggetto.select_set(False)
    else:
        try:
            oggetto.hide_set(False)
        except (AttributeError, ReferenceError, RuntimeError):
            pass
    aggiorna_vista()
    return bool(oggetto.hide_viewport)


def mostra_tutti(view_layer) -> int:
    """Fa ricomparire tutti gli oggetti nascosti della scena."""
    mostrati = 0
    for oggetto in view_layer.objects:
        nascosto = bool(oggetto.hide_viewport)
        try:
            nascosto = nascosto or bool(oggetto.hide_get())
        except (AttributeError, ReferenceError, RuntimeError):
            pass
        if not nascosto:
            continue
        oggetto.hide_viewport = False
        try:
            oggetto.hide_set(False)
        except (AttributeError, ReferenceError, RuntimeError):
            pass
        mostrati += 1
    aggiorna_vista()
    return mostrati


def imposta_telecamera_principale(scena, oggetto) -> bool:
    """Usa una telecamera per l'immagine finale."""
    if oggetto.type != "CAMERA":
        return False
    scena.camera = oggetto
    return True


@dataclass(frozen=True)
class EsitoBlocco:
    """Quanti oggetti sono stati bloccati o sbloccati davvero."""

    applicati: int = 0
    saltati: int = 0


def blocca_scelta(oggetti, blocca: bool, view_layer=None) -> EsitoBlocco:
    """Blocca o sblocca la scelta degli oggetti indicati.

    Blender non tiene scelto un oggetto che non si può scegliere: quando si
    blocca, l'oggetto viene tolto dalla scelta e, se era quello attivo, il
    ruolo passa a un altro oggetto ancora scelto. Lo scambio è fatto qui per
    non lasciare l'interfaccia senza un oggetto attivo.
    """
    applicati = saltati = 0
    for oggetto in list(oggetti):
        if oggetto is None:
            continue
        if not hasattr(oggetto, "hide_select"):
            saltati += 1
            continue
        try:
            oggetto.hide_select = bool(blocca)
        except (AttributeError, ReferenceError, RuntimeError, TypeError):
            saltati += 1
            continue
        if blocca and view_layer is not None:
            _togli_dalla_scelta(oggetto, view_layer)
        applicati += 1
    aggiorna_vista()
    return EsitoBlocco(applicati, saltati)


def _togli_dalla_scelta(oggetto, view_layer) -> None:
    """Toglie un oggetto dalla scelta e sistema l'oggetto attivo.

    Bloccare la scelta in Blender toglie già l'oggetto dalla scelta da solo, ma
    lo lascia attivo: un oggetto che non si può scegliere non deve restare
    attivo, perché i pannelli continuerebbero a mostrarlo. Se ci sono altri
    oggetti scelti, il ruolo passa al primo di loro.

    Il confronto con l'oggetto attivo è fatto per nome: i riferimenti Python
    degli oggetti Blender non si possono paragonare con `is`, perché lo stesso
    oggetto può avere più involucri Python vivi nello stesso momento.
    """
    try:
        if oggetto.select_get():
            oggetto.select_set(False)
    except (AttributeError, ReferenceError, RuntimeError):
        pass
    attivo = view_layer.objects.active
    if attivo is None or attivo.name != oggetto.name:
        return
    rimasti = [
        altro
        for altro in view_layer.objects
        if altro.name != oggetto.name and _scelto(altro)
    ]
    try:
        view_layer.objects.active = rimasti[0] if rimasti else None
    except (AttributeError, ReferenceError, RuntimeError, TypeError):
        return


def _scelto(oggetto) -> bool:
    try:
        return bool(oggetto.select_get())
    except (AttributeError, ReferenceError, RuntimeError):
        return False
