"""Modificatori non distruttivi: smusso, suddivisione, specchio, serie, spessore, taglio.

Un modificatore è la strada giusta per questi strumenti: la forma originale
resta quella che l'utente ha creato, il risultato si vede subito nella Vista 3D
e si toglie con un clic o con `Ctrl+Z`. Qui ci sono **tutte** le chiamate a
Blender che riguardano i modificatori, così le regole restano leggibili altrove.

Ogni funzione controlla la risposta di Blender e solleva `ErroreModellazione`
con un messaggio già in italiano quando qualcosa non è possibile: un
modificatore che non nasce, una forma senza facce, un risultato vuoto. Un
comando che non riesce non deve mai sembrare riuscito.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import bpy

from ..localization import TESTI
from ..scene import regole_modellazione as regole


class ErroreModellazione(RuntimeError):
    """Errore gestibile di uno strumento guidato: messaggio già in italiano."""


@dataclass(frozen=True)
class Forma:
    """Misure di una forma così come si vede adesso, modificatori compresi."""

    vertici: int = 0
    facce: int = 0
    minimo: tuple[float, float, float] = (0.0, 0.0, 0.0)
    massimo: tuple[float, float, float] = (0.0, 0.0, 0.0)

    @property
    def dimensione_minima(self) -> float:
        """Lato più corto della forma: decide quanto si può smussare o assottigliare."""
        misure = [self.massimo[asse] - self.minimo[asse] for asse in range(3)]
        return min(misure) if misure else 0.0

    @property
    def dimensione_massima(self) -> float:
        """Lato più lungo della forma, usato per le distanze predefinite."""
        misure = [self.massimo[asse] - self.minimo[asse] for asse in range(3)]
        return max(misure) if misure else 0.0


# ------------------------------------------------------------------- lettura


def facce_e_vertici(oggetto) -> tuple[int, int]:
    """Numero di facce e di vertici della geometria vera (senza modificatori).

    L'ordine è quello del nome: prima le facce, poi i vertici, come in
    `_conteggio_sicuro`. Chi legge il risultato non deve indovinare.
    """
    dati = getattr(oggetto, "data", None)
    if dati is None or getattr(oggetto, "type", "") != "MESH":
        return 0, 0
    try:
        return len(dati.polygons), len(dati.vertices)
    except (AttributeError, ReferenceError, RuntimeError):
        return 0, 0


def e_forma(oggetto) -> bool:
    """Indica se l'oggetto è una forma lavorabile (una mesh con almeno una faccia)."""
    facce, vertici = _conteggio_sicuro(oggetto)
    if vertici == 0:
        return False
    return facce > 0


def _conteggio_sicuro(oggetto) -> tuple[int, int]:
    dati = getattr(oggetto, "data", None)
    if dati is None or getattr(oggetto, "type", "") != "MESH":
        return 0, 0
    try:
        return len(dati.polygons), len(dati.vertices)
    except (AttributeError, ReferenceError, RuntimeError):
        return 0, 0


def puo_diventare_forma(oggetto) -> bool:
    """Indica se l'oggetto si può convertire in una forma (testo, curva, superficie)."""
    return getattr(oggetto, "type", "") in TIPI_CONVERTIBILI


# I tipi convertibili sono una regola, non una chiamata a Blender: l'elenco
# vive in `scene/regole_modellazione.py` perché serve anche all'interfaccia.
TIPI_CONVERTIBILI = regole.TIPI_CONVERTIBILI


def _facce_e_normali(oggetto) -> tuple[tuple[tuple[int, ...], ...], tuple[tuple[float, ...], ...]]:
    """Anelli di vertici e normali delle facce della geometria vera."""
    dati = getattr(oggetto, "data", None)
    if dati is None:
        return (), ()
    try:
        facce = tuple(tuple(int(v) for v in poligono.vertices) for poligono in dati.polygons)
        normali = tuple(
            (float(poligono.normal[0]), float(poligono.normal[1]), float(poligono.normal[2]))
            for poligono in dati.polygons
        )
    except (AttributeError, ReferenceError, RuntimeError):
        return (), ()
    return facce, normali


def spigoli_vivi(oggetto, soglia_gradi: float) -> int:
    """Spigoli con un angolo vivo, quelli che ha senso ammorbidire."""
    facce, normali = _facce_e_normali(oggetto)
    if not facce:
        return 0
    return regole.spigoli_vivi(facce, normali, soglia_gradi)


def bordi_aperti(oggetto) -> int:
    """Bordi di una superficie non chiusa: un piano è tutto bordo, un cubo nessuno."""
    facce, _normali = _facce_e_normali(oggetto)
    return regole.bordi_aperti(facce)


def simmetrica(oggetto, asse: str, posizione_piano: float, tolleranza: float) -> bool:
    """Indica se la geometria è già uguale al suo specchio rispetto a un piano.

    Il piano è perpendicolare all'asse indicato e passa per `posizione_piano`
    (coordinate del mondo): è lo stesso piano che usa il modificatore, quindi
    il giudizio parla del risultato che l'utente vedrebbe davvero.
    """
    dati = getattr(oggetto, "data", None)
    if dati is None or getattr(oggetto, "type", "") != "MESH":
        return False
    matrice = getattr(oggetto, "matrix_world", None)
    try:
        coordinate = tuple(
            tuple(float(valore) for valore in (matrice @ vertice.co))
            for vertice in dati.vertices
        )
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        return False
    return regole.simmetrica(coordinate, asse, tolleranza, posizione_piano)


def unita_lunghezza(scena) -> str:
    """Abbreviazione dell'unità di lunghezza della scena, con ripiego sui metri.

    I messaggi degli strumenti scrivono le misure con l'unità che l'utente ha
    scelto in Blender: "8 cm" invece di "0,08", che per chi inizia è la
    differenza fra capire e non capire.
    """
    from ..scene import misure

    impostazioni = getattr(scena, "unit_settings", None)
    if impostazioni is None:
        return "m"
    return misure.unita_lunghezza(
        str(getattr(impostazioni, "system", "NONE")),
        str(getattr(impostazioni, "length_unit", "METERS")),
    )


def aggiorna(context) -> None:
    """Aggiorna le matrici della scena prima di leggere misure o risultati."""
    vettore = getattr(context, "view_layer", None)
    aggiorna_vista = getattr(vettore, "update", None)
    if aggiorna_vista is None:
        return
    try:
        aggiorna_vista()
    except (AttributeError, ReferenceError, RuntimeError):
        return


def forma_valutata(context, oggetto) -> Forma:
    """Misure della forma come appare adesso, con tutti i modificatori applicati."""
    aggiorna(context)
    valutato = None
    mesh = None
    try:
        valutato = oggetto.evaluated_get(context.evaluated_depsgraph_get())
        mesh = valutato.to_mesh()
        vertici = tuple(
            oggetto.matrix_world @ vertice.co for vertice in mesh.vertices
        )
        conteggio_vertici = len(mesh.vertices)
        conteggio_facce = len(mesh.polygons)
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        raise ErroreModellazione(TESTI["ERRORE_FORMA_NON_LEGGIBILE"]) from None
    finally:
        if valutato is not None and mesh is not None:
            try:
                valutato.to_mesh_clear()
            except (AttributeError, ReferenceError, RuntimeError):
                pass

    if not vertici:
        return Forma(vertici=0, facce=conteggio_facce)
    minimo = tuple(min(float(punto[asse]) for punto in vertici) for asse in range(3))
    massimo = tuple(max(float(punto[asse]) for punto in vertici) for asse in range(3))
    return Forma(conteggio_vertici, conteggio_facce, minimo, massimo)


def dimensioni_oggetto(context, oggetto) -> tuple[float, float]:
    """Lato più corto e lato più lungo della forma, modificatori compresi."""
    forma = forma_valutata(context, oggetto)
    return forma.dimensione_minima, forma.dimensione_massima


# -------------------------------------------------------------- modificatori


def elenca(oggetto) -> list:
    """Modificatori dell'oggetto, nell'ordine in cui Blender li applica."""
    try:
        return list(getattr(oggetto, "modifiers", ()) or ())
    except (AttributeError, ReferenceError, RuntimeError):
        return []


def tipo_di(modificatore) -> str:
    """Tipo tecnico del modificatore ("BEVEL", "SUBSURF", ...)."""
    return str(getattr(modificatore, "type", ""))


def nome_di(modificatore) -> str:
    """Nome del modificatore, quello mostrato nell'elenco di Blender."""
    return str(getattr(modificatore, "name", ""))


def trova(oggetto, tipo: str):
    """Primo modificatore del tipo indicato, se l'oggetto ne ha già uno."""
    for modificatore in elenca(oggetto):
        if tipo_di(modificatore) == str(tipo):
            return modificatore
    return None


def aggiungi(oggetto, tipo: str, nome: str):
    """Aggiunge un modificatore e si ferma se Blender non lo crea.

    Blender rifiuta alcuni modificatori su certi tipi di oggetto: in quel caso
    `modifiers.new` restituisce `None` invece di sollevare un errore, quindi il
    controllo va fatto qui.
    """
    try:
        modificatore = oggetto.modifiers.new(name=nome, type=tipo)
    except (AttributeError, ReferenceError, RuntimeError, TypeError) as errore:
        raise ErroreModellazione(TESTI["ERRORE_MODIFICATORE_NON_AGGIUNTO"]) from errore
    if modificatore is None:
        raise ErroreModellazione(TESTI["ERRORE_MODIFICATORE_NON_AGGIUNTO"])
    # Un modificatore appena creato deve vedersi subito nella Vista 3D: senza
    # anteprima l'utente non saprebbe che cosa è successo.
    modificatore.show_viewport = True
    modificatore.show_render = True
    return modificatore


def imposta(modificatore, **valori: object) -> list[str]:
    """Imposta solo le proprietà che esistono in questa versione di Blender.

    Restituisce i nomi delle proprietà non disponibili: le versioni di Blender
    cambiano i nomi delle opzioni dei modificatori, e un nome sbagliato non deve
    far fallire tutto il comando.
    """
    mancanti: list[str] = []
    for proprieta, valore in valori.items():
        if not hasattr(modificatore, proprieta):
            mancanti.append(proprieta)
            continue
        try:
            setattr(modificatore, proprieta, valore)
        except (AttributeError, TypeError, ValueError):
            mancanti.append(proprieta)
    return mancanti


def rimuovi(oggetto, modificatore) -> bool:
    """Toglie un modificatore e riferisce se è stato tolto davvero."""
    try:
        for indice, candidato in enumerate(oggetto.modifiers):
            if candidato is modificatore or nome_di(candidato) == nome_di(modificatore):
                oggetto.modifiers.remove(oggetto.modifiers[indice])
                return True
    except (AttributeError, ReferenceError, RuntimeError, IndexError):
        return False
    return False


def rimuovi_tutti(oggetto) -> int:
    """Toglie tutti i modificatori dell'oggetto; restituisce quanti ne ha tolti."""
    tolti = 0
    for modificatore in elenca(oggetto):
        if rimuovi(oggetto, modificatore):
            tolti += 1
    return tolti


def segnaposto(context, posizione, nome: str):
    """Crea o ritrova un segnaposto vuoto nella posizione indicata.

    Serve allo specchio: il modificatore specchia la forma rispetto a un altro
    oggetto, e un segnaposto sul cursore 3D tiene il piano dello specchio dove
    l'utente lo vede. È un oggetto vero della scena: si può spostare, rinominare
    o eliminare come tutti gli altri, e se sparisce il pannello lo segnala.
    """
    for oggetto in list(getattr(bpy.data, "objects", ()) or ()):
        if str(getattr(oggetto, "name", "")) != str(nome):
            continue
        if getattr(oggetto, "type", "") != "EMPTY":
            continue
        try:
            oggetto.location = tuple(posizione)
        except (AttributeError, ReferenceError, RuntimeError, TypeError):
            return None
        return oggetto

    scena = getattr(context, "scene", None)
    raccolta = getattr(scena, "collection", None)
    if raccolta is None:
        return None
    try:
        vuoto = bpy.data.objects.new(name=str(nome), object_data=None)
        vuoto.empty_display_type = "PLAIN_AXES"
        raccolta.objects.link(vuoto)
        vuoto.location = tuple(posizione)
    except (AttributeError, ReferenceError, RuntimeError, TypeError):
        return None
    return vuoto


def problema_di(context, modificatore) -> str:
    """Motivo per cui una modifica non produce quello che promette, se c'è.

    Serve al pannello per avvisare senza nascondere il problema: una serie
    circolare senza il suo centro, un taglio senza l'oggetto da tagliare.
    """
    tipo = tipo_di(modificatore)
    if bool(getattr(modificatore, "use_object_offset", False)) and getattr(
        modificatore, "offset_object", None
    ) is None:
        return TESTI["AVVISO_SERIE_SENZA_CENTRO"]
    if tipo == "BOOLEAN" and getattr(modificatore, "object", None) is None:
        return TESTI["AVVISO_TAGLIO_SENZA_OGGETTO"]
    if tipo == "MIRROR" and getattr(modificatore, "mirror_object", None) is None:
        return TESTI["AVVISO_SPECCHIO_SENZA_CENTRO"]
    return ""


# ------------------------------------------------------------------ superfici


def superficie_liscia(oggetto, liscia: bool = True) -> bool:
    """Cambia solo l'aspetto della superficie: nessuna faccia viene aggiunta.

    È la differenza che l'interfaccia spiega all'utente: "liscia" e "a facce"
    cambiano il modo in cui la superficie viene illuminata, non la forma.
    """
    dati = getattr(oggetto, "data", None)
    if dati is None or getattr(oggetto, "type", "") != "MESH":
        return False
    try:
        if liscia:
            dati.shade_smooth()
        else:
            dati.shade_flat()
    except (AttributeError, ReferenceError, RuntimeError):
        try:
            for poligono in dati.polygons:
                poligono.use_smooth = bool(liscia)
        except (AttributeError, ReferenceError, RuntimeError):
            return False
    return True


def e_liscia(oggetto) -> bool:
    """Indica se la superficie dell'oggetto è già mostrata liscia."""
    dati = getattr(oggetto, "data", None)
    if dati is None or getattr(oggetto, "type", "") != "MESH":
        return False
    try:
        return all(bool(poligono.use_smooth) for poligono in dati.polygons)
    except (AttributeError, ReferenceError, RuntimeError):
        return False


# ---------------------------------------------------------------- conversione


def converti_in_forma(context, oggetto) -> bool:
    """Trasforma un testo, una curva o una superficie in una forma (mesh).

    Blender converte l'oggetto attivo e scelto: qui l'oggetto indicato viene
    scelto apposta, e la scelta di prima non viene toccata.
    """
    if not puo_diventare_forma(oggetto):
        return False
    tipo_prima = getattr(oggetto, "type", "")
    precedenti = _scelti_della_scena(context)
    with _solo_oggetto(context, oggetto):
        esito = _converti(context)
        aggiorna(context)
        riuscito = "FINISHED" in esito and getattr(oggetto, "type", "") == "MESH"
    if not riuscito:
        # La conversione non è riuscita: la scelta torna com'era, ma solo se
        # l'oggetto esiste ancora.
        if tipo_prima != getattr(oggetto, "type", "MESSA"):
            _ripristina_scelta(context, oggetto, precedenti)
        return False
    _ripristina_scelta(context, oggetto, precedenti)
    return True


def _converti(context):
    """Chiama il comando nativo di conversione, se è disponibile."""
    converti = getattr(getattr(bpy.ops, "object", None), "convert", None)
    if converti is None:
        return set()
    try:
        return set(converti(target="MESH"))
    except (AttributeError, ReferenceError, RuntimeError, TypeError):
        return set()


def _scelti_della_scena(context) -> list:
    vettore = getattr(context, "view_layer", None)
    if vettore is None:
        return []
    try:
        return [oggetto for oggetto in vettore.objects if oggetto.select_get()]
    except (AttributeError, ReferenceError, RuntimeError):
        return []


class _solo_oggetto:
    """Rende scelto e attivo un solo oggetto, per un comando nativo."""

    def __init__(self, context, oggetto) -> None:
        self._context = context
        self._oggetto = oggetto
        self._vettore = getattr(context, "view_layer", None)

    def __enter__(self):
        if self._vettore is None:
            return self
        try:
            for altro in self._vettore.objects:
                if altro.select_get():
                    altro.select_set(False)
            self._oggetto.select_set(True)
            self._vettore.objects.active = self._oggetto
        except (AttributeError, ReferenceError, RuntimeError):
            pass
        return self

    def __exit__(self, tipo, valore, traccia) -> bool:
        return False


def _ripristina_scelta(context, oggetto, precedenti: Sequence[object]) -> None:
    """Rimette la scelta com'era, senza rifiutare oggetti bloccati."""
    vettore = getattr(context, "view_layer", None)
    if vettore is None:
        return
    try:
        for altro in vettore.objects:
            if altro.select_get():
                altro.select_set(False)
        for altro in precedenti:
            try:
                if altro.name in bpy.data.objects and not getattr(altro, "hide_select", False):
                    altro.select_set(True)
            except (AttributeError, ReferenceError, RuntimeError):
                continue
        if precedenti and getattr(precedenti[0], "name", "") in bpy.data.objects:
            vettore.objects.active = precedenti[0]
    except (AttributeError, ReferenceError, RuntimeError):
        return


# -------------------------------------------------------------------- nascosto


def nascondi_attrezzo(oggetto, nascosto: bool) -> bool:
    """Nasconde l'oggetto usato per tagliare, senza toglierlo dalla scena.

    Un taglio non distruttivo lascia l'oggetto che taglia dov'è: nasconderlo lo
    toglie dalla vista, e resta recuperabile con il pulsante Mostra.
    """
    try:
        oggetto.hide_viewport = bool(nascosto)
        if nascosto:
            oggetto.hide_set(True)
        else:
            oggetto.hide_set(False)
    except (AttributeError, ReferenceError, RuntimeError):
        return False
    return True
