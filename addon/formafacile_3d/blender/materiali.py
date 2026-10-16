"""Materiali veri di Blender, costruiti dai valori scelti dall'utente.

Un materiale pronto diventa un *nuovo* materiale di Blender: applicandolo due
volte su oggetti diversi nascono due materiali indipendenti, quindi cambiare
l'aspetto a un oggetto non cambia quello degli altri. Per lo stesso motivo la
variazione è una copia: chi vuole ritoccare un materiale condiviso non tocca
quello di partenza.

I nodi usati sono quelli pubblici di Blender (`Principled BSDF`); i nomi degli
ingressi sono quelli della versione supportata (4.5 LTS) e le proprietà che non
esistono vengono saltate invece di far fallire il comando.
"""

from __future__ import annotations

import bpy

from .. import configuration
from ..scene import aspetto


def _ingresso(nodo, nome: str, valore) -> bool:
    """Scrive un ingresso del nodo principale, se esiste davvero."""
    ingressi = getattr(nodo, "inputs", None)
    if ingressi is None:
        return False
    try:
        ingresso = ingressi.get(nome)
    except (AttributeError, ReferenceError, RuntimeError, TypeError):
        return False
    if ingresso is None:
        return False
    try:
        ingresso.default_value = valore
        return True
    except (AttributeError, ReferenceError, TypeError, ValueError):
        return False


def nodo_principale(materiale):
    """Nodo principale del materiale, quello che decide come appare la superficie."""
    albero = getattr(materiale, "node_tree", None)
    if albero is None:
        return None
    for nodo in albero.nodes:
        if nodo.bl_idname == "ShaderNodeBsdfPrincipled":
            return nodo
    return None


def imposta_valori(materiale, colore, ruvidita: float, metallico: float, trasparenza: float,
                   indice_rifrazione: float = 1.45) -> bool:
    """Scrive colore, ruvidità, metallico e trasparenza su un materiale esistente.

    Il colore viene scritto anche sull'anteprima del materiale
    (`diffuse_color`), così il campione dell'interfaccia e la Vista 3D in
    modalità "Materiale" mostrano subito il colore giusto.
    """
    colore = tuple(float(valore) for valore in colore[:3])
    if len(colore) < 3:
        return False

    materiale.use_nodes = True
    nodo = nodo_principale(materiale)
    riuscito = False
    if nodo is not None:
        riuscito = _ingresso(nodo, "Base Color", (colore[0], colore[1], colore[2], 1.0))
        _ingresso(nodo, "Roughness", float(ruvidita))
        _ingresso(nodo, "Metallic", float(metallico))
        _ingresso(nodo, "Transmission Weight", float(trasparenza))
        if indice_rifrazione:
            _ingresso(nodo, "IOR", float(indice_rifrazione))
    try:
        materiale.diffuse_color = (colore[0], colore[1], colore[2], 1.0)
    except (AttributeError, ReferenceError, TypeError, ValueError):
        pass

    _imposta_trasparenza(materiale, float(trasparenza))
    return riuscito


def _imposta_trasparenza(materiale, trasparenza: float) -> None:
    """Regola i metodi di fusione per la trasparenza, solo dove esistono.

    Blender 4.5 LTS accetta sia `blend_method` (usato dai motori precedenti)
    sia `surface_render_method` (motore EEVEE attuale): si impostano tutti
    quelli disponibili, e se una proprietà manca non succede nulla.
    """
    vetro = trasparenza >= configuration.MATERIALE_TRASPARENZA_VETRO
    for nome, valore in (
        ("blend_method", "BLEND" if vetro else "OPAQUE"),
        ("surface_render_method", "BLENDED" if vetro else "DITHERED"),
        ("use_raytrace_refraction", bool(vetro)),
        ("use_transparent_shadow", True),
    ):
        if not hasattr(materiale, nome):
            continue
        try:
            setattr(materiale, nome, valore)
        except (AttributeError, ReferenceError, TypeError, ValueError):
            continue


def crea(nome: str, valori: aspetto.Materiale):
    """Crea un materiale nuovo con i valori indicati.

    Restituisce `None` se Blender non riesce a creare il dato: chi chiama deve
    avvisare l'utente, non fingere che il materiale esista.
    """
    try:
        materiale = bpy.data.materials.new(name=str(nome))
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        return None
    imposta_valori(
        materiale,
        valori.colore,
        valori.ruvidita,
        valori.metallico,
        valori.trasparenza,
        valori.indice_rifrazione,
    )
    return materiale


def crea_con_valori(valori: aspetto.Materiale):
    """Crea un materiale nuovo con i valori indicati e un nome libero."""
    nome = aspetto.nome_materiale(valori, n_nomi_esistenti())
    materiale = crea(nome, valori)
    if materiale is None:
        return None
    # Il materiale ricorda da quale ricetta nasce: serve a riconoscere un
    # materiale di FormaFacile e a sapere se la sua trasparenza si regola.
    try:
        materiale[configuration.CHIAVE_MATERIALE_RICETTA] = valori.chiave
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        pass
    return materiale


def n_nomi_esistenti() -> tuple[str, ...]:
    """Nomi dei materiali già presenti nella scena corrente."""
    try:
        return tuple(materiale.name for materiale in bpy.data.materials)
    except (AttributeError, ReferenceError, RuntimeError, TypeError):
        return ()


def ricetta(materiale) -> str:
    """Chiave della ricetta di un materiale creato da FormaFacile, se nota."""
    try:
        return str(materiale.get(configuration.CHIAVE_MATERIALE_RICETTA, ""))
    except (AttributeError, ReferenceError, RuntimeError, TypeError):
        return ""


def materiali_di(oggetto) -> list:
    """Materiali presenti negli spazi del materiale di un oggetto, senza doppioni."""
    dati = getattr(oggetto, "data", None)
    spazi = getattr(dati, "materials", None)
    if spazi is None:
        return []
    trovati = []
    for indice in range(len(spazi)):
        materiale = spazi[indice]
        if materiale is not None and materiale not in trovati:
            trovati.append(materiale)
    return trovati


def materiale_principale(oggetto):
    """Materiale mostrato dall'oggetto, oppure None se non ne ha."""
    trovati = materiali_di(oggetto)
    return trovati[0] if trovati else None


def quanti_oggetti_usano(scena, materiale) -> int:
    """Quanti oggetti della scena usano quel materiale.

    Si contano gli oggetti, non gli spazi del materiale: due spazi dello stesso
    oggetto restano un oggetto solo, ed è quello che interessa all'utente quando
    legge "questo materiale è usato da tre oggetti".
    """
    quanti = 0
    for oggetto in getattr(scena, "objects", ()) or ():
        if materiale in materiali_di(oggetto):
            quanti += 1
    return quanti


def assegna(oggetto, materiale) -> bool:
    """Dà il materiale all'oggetto, in tutti i suoi spazi del materiale.

    Sostituire ogni spazio (e crearne uno se non c'è) evita il caso peggiore per
    chi inizia: mezza forma con il materiale nuovo e mezza con quello vecchio.
    """
    dati = getattr(oggetto, "data", None)
    spazi = getattr(dati, "materials", None)
    if spazi is None:
        return False
    try:
        if len(spazi) == 0:
            spazi.append(materiale)
            return True
        for indice in range(len(spazi)):
            spazi[indice] = materiale
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        return False
    return True


def sostituisci(oggetto, vecchio, nuovo) -> bool:
    """Sostituisce un materiale con un altro solo dove serve.

    Serve alla variazione: gli spazi del materiale che usano il materiale di
    partenza passano alla copia, gli altri restano come sono. È il modo per non
    cambiare l'aspetto di tutto il resto dell'oggetto.
    """
    dati = getattr(oggetto, "data", None)
    spazi = getattr(dati, "materials", None)
    if spazi is None:
        return False
    cambiati = 0
    try:
        for indice in range(len(spazi)):
            if spazi[indice] is vecchio:
                spazi[indice] = nuovo
                cambiati += 1
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        return False
    return cambiati > 0


def copia(materiale, nome: str | None = None):
    """Copia indipendente di un materiale: la variazione."""
    try:
        nuovo = materiale.copy()
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        return None
    if nuovo is None:
        return None
    nuovo.name = str(nome) if nome else aspetto.nome_variazione(materiale.name, n_nomi_esistenti())
    return nuovo


def nome_per_variazione(materiale) -> str:
    """Nome libero per la variazione di un materiale."""
    return aspetto.nome_variazione(str(getattr(materiale, "name", "")), n_nomi_esistenti())
