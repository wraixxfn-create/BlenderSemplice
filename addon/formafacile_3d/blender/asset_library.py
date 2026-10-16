"""Costruzione di modelli reali per la libreria di FormaFacile.

Ogni inserimento crea una raccolta nuova con mesh indipendenti e un materiale
proprio. La creazione è una piccola transazione: in caso di errore vengono
rimossi soltanto i dati appena creati, mai gli oggetti già presenti nella scena.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import bpy
from mathutils import Vector

from ..localization import TESTI
from ..scene import libreria


SEGMENTI_CILINDRO = 48
SEGMENTI_VASO = 48
ANELLI_SFERA = 16


class ErroreAsset(RuntimeError):
    """Errore comprensibile della libreria, già scritto in italiano."""


@dataclass(frozen=True)
class IstanzaAsset:
    """Risultato dell'inserimento: raccolta e oggetti creati."""

    identificatore: str
    nome: str
    raccolta: object
    oggetti: tuple[object, ...]


class _Costruttore:
    """Raccoglie i dati creati e offre forme base con coordinate locali."""

    def __init__(self, raccolta, materiale, origine: tuple[float, float, float]):
        self.raccolta = raccolta
        self.materiale = materiale
        self.origine = origine
        self.oggetti: list[object] = []
        self.dati: list[object] = []

    def mesh(self, nome: str, vertici, facce, centro=(0.0, 0.0, 0.0), *, liscio=False):
        """Crea un oggetto mesh nella raccolta, con origine sulla sua parte."""
        nome_completo = f"{self.raccolta.name} - {nome}"
        mesh = bpy.data.meshes.new(TESTI["ASSET_NOME_GEOMETRIA"].format(nome=nome_completo))
        self.dati.append(mesh)
        mesh.from_pydata(list(vertici), [], list(facce))
        mesh.update()
        if liscio:
            for poligono in mesh.polygons:
                poligono.use_smooth = True
        _ricalcola_normali(mesh)

        oggetto = bpy.data.objects.new(nome_completo, mesh)
        self.oggetti.append(oggetto)
        self.raccolta.objects.link(oggetto)
        oggetto.location = tuple(self.origine[i] + centro[i] for i in range(3))
        mesh.materials.append(self.materiale)
        return oggetto

    def scatola(self, nome: str, centro, dimensioni):
        """Crea una scatola chiusa, centrata sul proprio punto di origine."""
        x, y, z = (float(v) / 2.0 for v in dimensioni)
        vertici = (
            (-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
            (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z),
        )
        facce = (
            (0, 3, 2, 1), (4, 5, 6, 7),
            (0, 1, 5, 4), (1, 2, 6, 5),
            (2, 3, 7, 6), (3, 0, 4, 7),
        )
        return self.mesh(nome, vertici, facce, centro)

    def cilindro(self, nome: str, centro, raggio: float, altezza: float, segmenti=SEGMENTI_CILINDRO):
        """Cilindro chiuso, con superfici laterali e due basi."""
        vertici = []
        z_basso, z_alto = -altezza / 2.0, altezza / 2.0
        for z in (z_basso, z_alto):
            vertici.extend(
                (raggio * math.cos(2.0 * math.pi * indice / segmenti),
                 raggio * math.sin(2.0 * math.pi * indice / segmenti), z)
                for indice in range(segmenti)
            )
        indice_centro_basso = len(vertici)
        vertici.append((0.0, 0.0, z_basso))
        indice_centro_alto = len(vertici)
        vertici.append((0.0, 0.0, z_alto))

        facce = []
        for indice in range(segmenti):
            successivo = (indice + 1) % segmenti
            facce.append((indice, successivo, segmenti + successivo, segmenti + indice))
            facce.append((indice_centro_basso, successivo, indice))
            facce.append((indice_centro_alto, segmenti + indice, segmenti + successivo))
        return self.mesh(nome, vertici, facce, centro)

    def cono(self, nome: str, centro, raggio: float, altezza: float, segmenti=SEGMENTI_CILINDRO):
        """Cono chiuso con base piana."""
        vertici = [
            (raggio * math.cos(2.0 * math.pi * indice / segmenti),
             raggio * math.sin(2.0 * math.pi * indice / segmenti), -altezza / 2.0)
            for indice in range(segmenti)
        ]
        vertici.append((0.0, 0.0, -altezza / 2.0))
        vertici.append((0.0, 0.0, altezza / 2.0))
        indice_centro = segmenti
        indice_punta = segmenti + 1
        facce = []
        for indice in range(segmenti):
            successivo = (indice + 1) % segmenti
            facce.append((indice_centro, successivo, indice))
            facce.append((indice, successivo, indice_punta))
        return self.mesh(nome, vertici, facce, centro)

    def sfera(self, nome: str, centro, raggio: float, segmenti=SEGMENTI_CILINDRO, anelli=ANELLI_SFERA):
        """Sfera UV chiusa, adatta a essere modificata in Modalità Modifica."""
        vertici = [(0.0, 0.0, raggio)]
        for indice_anello in range(1, anelli):
            latitudine = math.pi / 2.0 - math.pi * indice_anello / anelli
            raggio_anello = raggio * math.cos(latitudine)
            quota = raggio * math.sin(latitudine)
            vertici.extend(
                (raggio_anello * math.cos(2.0 * math.pi * indice / segmenti),
                 raggio_anello * math.sin(2.0 * math.pi * indice / segmenti), quota)
                for indice in range(segmenti)
            )
        indice_polo_basso = len(vertici)
        vertici.append((0.0, 0.0, -raggio))
        facce = []
        for indice in range(segmenti):
            successivo = (indice + 1) % segmenti
            facce.append((0, 1 + indice, 1 + successivo))
        for anello in range(anelli - 2):
            inizio = 1 + anello * segmenti
            successivo_anello = inizio + segmenti
            for indice in range(segmenti):
                prossimo = (indice + 1) % segmenti
                facce.append((inizio + indice, successivo_anello + indice,
                              successivo_anello + prossimo, inizio + prossimo))
        inizio_ultimo = 1 + (anelli - 2) * segmenti
        for indice in range(segmenti):
            successivo = (indice + 1) % segmenti
            facce.append((inizio_ultimo + indice, indice_polo_basso, inizio_ultimo + successivo))
        return self.mesh(nome, vertici, facce, centro, liscio=True)

    def vaso(self, nome: str, altezza: float, raggio: float, spessore: float):
        """Vaso cavo chiuso, con profilo interno ed esterno in un'unica mesh."""
        profilo_esterno = (
            (raggio * 0.52, 0.0),
            (raggio * 0.72, altezza * 0.08),
            (raggio * 0.91, altezza * 0.25),
            (raggio, altezza * 0.48),
            (raggio * 0.91, altezza * 0.70),
            (raggio * 0.67, altezza * 0.86),
            (raggio * 0.54, altezza * 0.93),
            (raggio * 0.56, altezza),
        )
        profilo_interno = tuple(
            (max(raggio * 0.08, r - spessore), max(spessore, z))
            for r, z in reversed(profilo_esterno)
        )
        profilo = ((0.0, 0.0), *profilo_esterno, *profilo_interno, (0.0, spessore))
        vertici: list[tuple[float, float, float]] = []
        anelli: list[tuple[int, int, float]] = []
        for r, z in profilo:
            inizio = len(vertici)
            if r <= 1e-8:
                vertici.append((0.0, 0.0, z))
                anelli.append((inizio, 1, r))
            else:
                vertici.extend(
                    (r * math.cos(2.0 * math.pi * indice / SEGMENTI_VASO),
                     r * math.sin(2.0 * math.pi * indice / SEGMENTI_VASO), z)
                    for indice in range(SEGMENTI_VASO)
                )
                anelli.append((inizio, SEGMENTI_VASO, r))

        facce = []
        for (inizio_a, quanti_a, _), (inizio_b, quanti_b, _) in zip(anelli, anelli[1:]):
            if quanti_a == 1:
                for indice in range(SEGMENTI_VASO):
                    successivo = (indice + 1) % SEGMENTI_VASO
                    facce.append((inizio_a, inizio_b + successivo, inizio_b + indice))
            elif quanti_b == 1:
                for indice in range(SEGMENTI_VASO):
                    successivo = (indice + 1) % SEGMENTI_VASO
                    facce.append((inizio_a + indice, inizio_a + successivo, inizio_b))
            else:
                for indice in range(SEGMENTI_VASO):
                    successivo = (indice + 1) % SEGMENTI_VASO
                    facce.append((inizio_a + indice, inizio_a + successivo,
                                  inizio_b + successivo, inizio_b + indice))
        return self.mesh(nome, vertici, facce, liscio=True)

    def fondale(self, nome: str, larghezza: float, profondita: float, altezza: float, spessore: float):
        """Superficie curva del fondale, estrusa in larghezza come mesh."""
        raggio = min(altezza * 0.25, profondita * 0.22)
        parete_y = profondita / 2.0 - spessore
        centro_y = parete_y - raggio
        profilo = [(-profondita / 2.0, spessore), (centro_y, spessore)]
        for indice in range(1, 9):
            angolo = -math.pi / 2.0 + (math.pi / 2.0) * indice / 8.0
            profilo.append((centro_y + raggio * math.cos(angolo),
                            spessore + raggio + raggio * math.sin(angolo)))
        profilo.append((parete_y, altezza))
        vertici = []
        for y, z in profilo:
            vertici.extend(((-larghezza / 2.0, y, z), (larghezza / 2.0, y, z)))
        facce = [
            (indice * 2, indice * 2 + 1, (indice + 1) * 2 + 1, (indice + 1) * 2)
            for indice in range(len(profilo) - 1)
        ]
        return self.mesh(nome, vertici, facce, liscio=True)

    def testo_estruso(self, nome: str, corpo: str, larghezza: float, altezza: float, spessore: float):
        """Crea testo estruso modificabile come curva di testo di Blender."""
        nome_completo = f"{self.raccolta.name} - {nome}"
        curva = bpy.data.curves.new(TESTI["ASSET_NOME_GEOMETRIA"].format(nome=nome_completo), type="FONT")
        self.dati.append(curva)
        curva.body = corpo
        curva.align_x = "CENTER"
        curva.align_y = "CENTER"
        curva.size = max(0.05, min(altezza * 0.42, larghezza / (max(len(corpo), 1) * 0.78)))
        curva.extrude = max(0.003, spessore * 0.16)
        curva.bevel_depth = min(curva.extrude * 0.15, curva.size * 0.015)
        curva.resolution_u = 8
        curva.materials.append(self.materiale)
        oggetto = bpy.data.objects.new(nome_completo, curva)
        self.oggetti.append(oggetto)
        self.raccolta.objects.link(oggetto)
        oggetto.location = (
            self.origine[0],
            self.origine[1] - spessore / 2.0,
            self.origine[2] + altezza / 2.0,
        )
        oggetto.rotation_euler = (math.pi / 2.0, 0.0, 0.0)
        return oggetto

    def luce_area(self, nome: str, numero: int, posizione, bersaglio, potenza: float, dimensione: float):
        """Crea una luce di area separata, orientata verso il centro del set."""
        nome_completo = f"{self.raccolta.name} - {nome}"
        dati = bpy.data.lights.new(name=nome_completo, type="AREA")
        self.dati.append(dati)
        dati.energy = potenza
        dati.shape = "DISK"
        dati.size = dimensione
        oggetto = bpy.data.objects.new(nome_completo, dati)
        self.oggetti.append(oggetto)
        self.raccolta.objects.link(oggetto)
        oggetto.location = tuple(self.origine[i] + posizione[i] for i in range(3))
        direzione = Vector(tuple(self.origine[i] + bersaglio[i] for i in range(3))) - oggetto.location
        if direzione.length > 1e-8:
            oggetto.rotation_euler = direzione.to_track_quat("-Z", "Y").to_euler()
        return oggetto


def crea_asset(context, identificatore: str, stato) -> IstanzaAsset:
    """Genera il modello scelto, senza modificare gli oggetti preesistenti."""
    if not libreria.identificatore_valido(identificatore):
        raise ErroreAsset(TESTI["ERRORE_ASSET_NON_VALIDO"])
    scena = getattr(context, "scene", None)
    view_layer = getattr(context, "view_layer", None)
    if scena is None or view_layer is None or getattr(scena, "collection", None) is None:
        raise ErroreAsset(TESTI["ERRORE_ASSET_SCENA"])

    voce = libreria.scheda(identificatore)
    try:
        valori = libreria.parametri(stato, identificatore)
    except (AttributeError, KeyError, TypeError) as errore:
        raise ErroreAsset(TESTI["ERRORE_ASSET_PARAMETRI"]) from errore
    _verifica_parametri(identificatore, valori)

    origine = _posizione_libera(context, valori)
    raccolta = materiale = None
    costruttore = None
    try:
        nome_raccolta = TESTI["ASSET_NOME_RACCOLTA"].format(nome=voce.nome)
        raccolta = bpy.data.collections.new(nome_raccolta)
        scena.collection.children.link(raccolta)
        materiale = _crea_materiale(raccolta.name, valori[libreria.CAMPO_COLORE])
        costruttore = _Costruttore(raccolta, materiale, origine)
        _costruisci(costruttore, identificatore, valori)
        raccolta[TESTI["ASSET_PROPRIETA_MODELLO"]] = voce.nome
        raccolta[TESTI["ASSET_PROPRIETA_PARAMETRI"]] = _testo_parametri(valori)
        _seleziona_nuovi(context, costruttore.oggetti)
    except ErroreAsset:
        _annulla_creazione(raccolta, materiale, costruttore)
        raise
    except Exception as errore:  # noqa: BLE001 - non lascia dati parziali nella scena
        _annulla_creazione(raccolta, materiale, costruttore)
        raise ErroreAsset(TESTI["ERRORE_ASSET_CREAZIONE"]) from errore

    return IstanzaAsset(
        identificatore=identificatore,
        nome=voce.nome,
        raccolta=raccolta,
        oggetti=tuple(costruttore.oggetti),
    )


def _crea_materiale(nome: str, colore) :
    """Materiale nuovo, così cambiare un modello non altera gli altri."""
    materiale = bpy.data.materials.new(TESTI["ASSET_NOME_MATERIALE"].format(nome=nome))
    rgba = tuple(float(valore) for valore in colore)
    materiale.diffuse_color = rgba
    materiale.use_nodes = True
    nodo = materiale.node_tree.nodes.get("Principled BSDF") if materiale.node_tree else None
    if nodo is not None:
        ingresso = nodo.inputs.get("Base Color")
        if ingresso is not None:
            ingresso.default_value = rgba
    return materiale


def _testo_parametri(valori: dict[str, object]) -> str:
    """Salva sulla raccolta una sintesi leggibile dei valori iniziali."""
    parti = []
    for chiave, valore in valori.items():
        if isinstance(valore, (tuple, list)):
            rappresentazione = ", ".join(f"{float(v):.3g}" for v in valore)
        elif isinstance(valore, float):
            rappresentazione = f"{valore:.3g}"
        else:
            rappresentazione = str(valore)
        parti.append(f"{libreria.nome_campo(chiave)}: {rappresentazione}")
    return "; ".join(parti)


def _verifica_parametri(identificatore: str, valori: dict[str, object]) -> None:
    """Controlla i limiti geometrici prima di creare il primo datablock."""
    for chiave, valore in valori.items():
        if chiave == libreria.CAMPO_TESTO:
            if not str(valore).strip():
                raise ErroreAsset(TESTI["ERRORE_ASSET_TESTO_VUOTO"])
        elif chiave == libreria.CAMPO_COLORE:
            if len(valore) != 4 or any(not math.isfinite(float(v)) or not 0.0 <= float(v) <= 1.0 for v in valore):
                raise ErroreAsset(TESTI["ERRORE_ASSET_PARAMETRI"])
        elif chiave == libreria.CAMPO_NUMERO_RIPIANI:
            if not 1 <= int(valore) <= 8:
                raise ErroreAsset(TESTI["ERRORE_ASSET_PARAMETRI"])
        else:
            try:
                numero = float(valore)
            except (TypeError, ValueError) as errore:
                raise ErroreAsset(TESTI["ERRORE_ASSET_PARAMETRI"]) from errore
            if not math.isfinite(numero) or numero <= 0.0:
                raise ErroreAsset(TESTI["ERRORE_ASSET_PARAMETRI"])

    larghezza = float(valori.get(libreria.CAMPO_LARGHEZZA, 1.0))
    profondita = float(valori.get(libreria.CAMPO_PROFONDITA, 1.0))
    altezza = float(valori.get(libreria.CAMPO_ALTEZZA, 1.0))
    spessore = float(valori.get(libreria.CAMPO_SPESSORE, 0.0))
    spessore_gamba = float(valori.get(libreria.CAMPO_SPESSORE_GAMBA, 0.0))
    raggio = float(valori.get(libreria.CAMPO_RAGGIO, 1.0))
    parete = float(valori.get(libreria.CAMPO_SPESSORE_PARETE, 0.0))
    diametro = float(valori.get(libreria.CAMPO_DIAMETRO, 1.0))
    grandezza = float(valori.get(libreria.CAMPO_GRANDEZZA, 1.0))

    if identificatore == libreria.ASSET_TAVOLINO:
        valido = spessore < min(larghezza, profondita, altezza)
        valido = valido and spessore_gamba < min(larghezza, profondita) / 2.0
    elif identificatore == libreria.ASSET_SCAFFALE:
        valido = 2.0 * spessore < min(larghezza, altezza, profondita)
    elif identificatore == libreria.ASSET_SEDIA:
        valido = spessore < min(larghezza, profondita, altezza * 0.3)
        valido = valido and spessore_gamba < min(larghezza, profondita) / 2.0
    elif identificatore == libreria.ASSET_PIEDISTALLO:
        valido = 2.0 * spessore < min(larghezza, profondita, altezza)
    elif identificatore == libreria.ASSET_VASO:
        valido = parete < min(raggio * 0.35, altezza * 0.15)
    elif identificatore == libreria.ASSET_INSEGNA:
        valido = spessore < min(larghezza, altezza) / 3.0
    elif identificatore == libreria.ASSET_STANZA:
        valido = spessore < min(larghezza, profondita, altezza) / 3.0
    elif identificatore == libreria.ASSET_PEDANA:
        valido = float(valori[libreria.CAMPO_ALTEZZA]) < diametro
    elif identificatore == libreria.ASSET_SET_FOTOGRAFICO:
        valido = spessore < min(larghezza, profondita, altezza) / 3.0
        valido = valido and float(valori[libreria.CAMPO_POTENZA_LUCE]) > 0.0
    elif identificatore == libreria.ASSET_FORMA_STAMPA:
        valido = grandezza > 0.0
    else:
        valido = False
    if not valido:
        raise ErroreAsset(TESTI["ERRORE_ASSET_PARAMETRI"])


def _posizione_libera(context, valori: dict[str, object]) -> tuple[float, float, float]:
    """Usa il cursore 3D e sposta il nuovo modello se collide con oggetti vicini."""
    cursore = getattr(getattr(context.scene, "cursor", None), "location", (0.0, 0.0, 0.0))
    candidato = [float(cursore[i]) for i in range(3)]
    grandezze = [
        float(valori[chiave])
        for chiave in (
            libreria.CAMPO_LARGHEZZA,
            libreria.CAMPO_PROFONDITA,
            libreria.CAMPO_ALTEZZA,
            libreria.CAMPO_DIAMETRO,
            libreria.CAMPO_GRANDEZZA,
        )
        if chiave in valori
    ]
    estensione = max(grandezze, default=1.0)
    passo = estensione + 1.0
    oggetti = list(getattr(context.view_layer, "objects", ()) or ())
    for _ in range(64):
        occupato = False
        for oggetto in oggetti:
            try:
                centro = oggetto.location
                dimensioni = oggetto.dimensions
                raggi = tuple(max(float(dimensioni[i]) / 2.0, 0.25) for i in range(3))
                if all(abs(candidato[i] - float(centro[i])) < raggi[i] + estensione * 0.5 + 0.25 for i in range(3)):
                    occupato = True
                    break
            except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
                continue
        if not occupato:
            return tuple(candidato)
        candidato[0] += passo
    return tuple(candidato)


def _costruisci(c: _Costruttore, identificatore: str, valori: dict[str, object]) -> None:
    """Instrada il modello selezionato verso il generatore di geometria."""
    costruttori = {
        libreria.ASSET_TAVOLINO: _tavolino,
        libreria.ASSET_SCAFFALE: _scaffale,
        libreria.ASSET_SEDIA: _sedia,
        libreria.ASSET_PIEDISTALLO: _piedistallo,
        libreria.ASSET_VASO: _vaso,
        libreria.ASSET_INSEGNA: _insegna,
        libreria.ASSET_STANZA: _stanza,
        libreria.ASSET_PEDANA: _pedana,
        libreria.ASSET_SET_FOTOGRAFICO: _set_fotografico,
        libreria.ASSET_FORMA_STAMPA: _forme_stampa,
    }
    costruttori[identificatore](c, valori)


def _tavolino(c: _Costruttore, p: dict[str, object]) -> None:
    larghezza, profondita, altezza = (float(p[k]) for k in (libreria.CAMPO_LARGHEZZA, libreria.CAMPO_PROFONDITA, libreria.CAMPO_ALTEZZA))
    spessore = float(p[libreria.CAMPO_SPESSORE])
    gamba = float(p[libreria.CAMPO_SPESSORE_GAMBA])
    c.scatola(TESTI["ASSET_PARTE_PIANO"], (0, 0, altezza - spessore / 2), (larghezza, profondita, spessore))
    altezza_gamba = altezza - spessore
    for numero, (x, y) in enumerate((
        (-larghezza / 2 + gamba / 2, -profondita / 2 + gamba / 2),
        (larghezza / 2 - gamba / 2, -profondita / 2 + gamba / 2),
        (-larghezza / 2 + gamba / 2, profondita / 2 - gamba / 2),
        (larghezza / 2 - gamba / 2, profondita / 2 - gamba / 2),
    ), 1):
        c.scatola(TESTI["ASSET_PARTE_GAMBA"].format(numero=numero),
                  (x, y, altezza_gamba / 2), (gamba, gamba, altezza_gamba))


def _scaffale(c: _Costruttore, p: dict[str, object]) -> None:
    larghezza, profondita, altezza = (float(p[k]) for k in (libreria.CAMPO_LARGHEZZA, libreria.CAMPO_PROFONDITA, libreria.CAMPO_ALTEZZA))
    spessore = float(p[libreria.CAMPO_SPESSORE])
    quanti = int(p[libreria.CAMPO_NUMERO_RIPIANI])
    interno = larghezza - 2.0 * spessore
    c.scatola(TESTI["ASSET_PARTE_FIANCO_SINISTRO"], (-larghezza / 2 + spessore / 2, 0, altezza / 2), (spessore, profondita, altezza))
    c.scatola(TESTI["ASSET_PARTE_FIANCO_DESTRO"], (larghezza / 2 - spessore / 2, 0, altezza / 2), (spessore, profondita, altezza))
    c.scatola(TESTI["ASSET_PARTE_SCHIENALE"], (0, profondita / 2 - spessore / 2, altezza / 2), (interno, spessore, altezza))
    c.scatola(TESTI["ASSET_PARTE_BASE"], (0, 0, spessore / 2), (interno, profondita, spessore))
    c.scatola(TESTI["ASSET_PARTE_TOP"], (0, 0, altezza - spessore / 2), (interno, profondita, spessore))
    for numero in range(1, quanti + 1):
        quota = spessore + numero * (altezza - 2.0 * spessore) / (quanti + 1)
        c.scatola(TESTI["ASSET_PARTE_RIPIANO"].format(numero=numero), (0, 0, quota), (interno, profondita, spessore))


def _sedia(c: _Costruttore, p: dict[str, object]) -> None:
    larghezza, profondita, altezza = (float(p[k]) for k in (libreria.CAMPO_LARGHEZZA, libreria.CAMPO_PROFONDITA, libreria.CAMPO_ALTEZZA))
    seduta = float(p[libreria.CAMPO_SPESSORE])
    gamba = float(p[libreria.CAMPO_SPESSORE_GAMBA])
    quota_seduta = altezza * 0.46
    c.scatola(TESTI["ASSET_PARTE_SEDUTA"], (0, 0, quota_seduta - seduta / 2), (larghezza, profondita, seduta))
    schienale_altezza = altezza * 0.32
    c.scatola(TESTI["ASSET_PARTE_SCHIENALE"],
              (0, profondita / 2 - seduta / 2, quota_seduta + schienale_altezza / 2),
              (larghezza, seduta, schienale_altezza))
    altezza_gamba = quota_seduta - seduta
    for numero, (x, y, quota) in enumerate((
        (-larghezza / 2 + gamba / 2, -profondita / 2 + gamba / 2, altezza_gamba),
        (larghezza / 2 - gamba / 2, -profondita / 2 + gamba / 2, altezza_gamba),
        (-larghezza / 2 + gamba / 2, profondita / 2 - gamba / 2, altezza),
        (larghezza / 2 - gamba / 2, profondita / 2 - gamba / 2, altezza),
    ), 1):
        c.scatola(TESTI["ASSET_PARTE_SOSTEGNO"].format(numero=numero),
                  (x, y, quota / 2), (gamba, gamba, quota))


def _piedistallo(c: _Costruttore, p: dict[str, object]) -> None:
    larghezza, profondita, altezza = (float(p[k]) for k in (libreria.CAMPO_LARGHEZZA, libreria.CAMPO_PROFONDITA, libreria.CAMPO_ALTEZZA))
    spessore = float(p[libreria.CAMPO_SPESSORE])
    c.scatola(TESTI["ASSET_PARTE_BASE"], (0, 0, spessore / 2), (larghezza, profondita, spessore))
    c.scatola(TESTI["ASSET_PARTE_PANNELLO"], (0, 0, altezza / 2),
              (larghezza * 0.52, profondita * 0.52, altezza - 2.0 * spessore))
    c.scatola(TESTI["ASSET_PARTE_TOP"], (0, 0, altezza - spessore / 2),
              (larghezza, profondita, spessore))


def _vaso(c: _Costruttore, p: dict[str, object]) -> None:
    c.vaso(TESTI["ASSET_PARTE_CONTENITORE"],
           float(p[libreria.CAMPO_ALTEZZA]), float(p[libreria.CAMPO_RAGGIO]),
           float(p[libreria.CAMPO_SPESSORE_PARETE]))


def _insegna(c: _Costruttore, p: dict[str, object]) -> None:
    larghezza = float(p[libreria.CAMPO_LARGHEZZA])
    altezza = float(p[libreria.CAMPO_ALTEZZA])
    spessore = float(p[libreria.CAMPO_SPESSORE])
    c.scatola(TESTI["ASSET_PARTE_PANNELLO"], (0, 0, altezza / 2), (larghezza, spessore, altezza))
    c.testo_estruso(TESTI["ASSET_PARTE_TESTO"], str(p[libreria.CAMPO_TESTO]).strip(),
                    larghezza, altezza, spessore)


def _stanza(c: _Costruttore, p: dict[str, object]) -> None:
    larghezza, profondita, altezza = (float(p[k]) for k in (libreria.CAMPO_LARGHEZZA, libreria.CAMPO_PROFONDITA, libreria.CAMPO_ALTEZZA))
    spessore = float(p[libreria.CAMPO_SPESSORE])
    c.scatola(TESTI["ASSET_PARTE_PAVIMENTO"], (0, 0, spessore / 2), (larghezza, profondita, spessore))
    c.scatola(TESTI["ASSET_PARTE_PARETE"].format(numero=1),
              (-larghezza / 2 + spessore / 2, 0, altezza / 2), (spessore, profondita, altezza))
    c.scatola(TESTI["ASSET_PARTE_PARETE"].format(numero=2),
              (0, profondita / 2 - spessore / 2, altezza / 2), (larghezza, spessore, altezza))


def _pedana(c: _Costruttore, p: dict[str, object]) -> None:
    diametro = float(p[libreria.CAMPO_DIAMETRO])
    altezza = float(p[libreria.CAMPO_ALTEZZA])
    c.cilindro(TESTI["ASSET_PARTE_PEDANA"], (0, 0, altezza * 0.38), diametro / 2, altezza * 0.76)
    c.cilindro(TESTI["ASSET_PARTE_BORDO"], (0, 0, altezza * 0.88), diametro * 0.91 / 2, altezza * 0.24)


def _set_fotografico(c: _Costruttore, p: dict[str, object]) -> None:
    larghezza, profondita, altezza = (float(p[k]) for k in (libreria.CAMPO_LARGHEZZA, libreria.CAMPO_PROFONDITA, libreria.CAMPO_ALTEZZA))
    spessore = float(p[libreria.CAMPO_SPESSORE])
    potenza = float(p[libreria.CAMPO_POTENZA_LUCE])
    c.scatola(TESTI["ASSET_PARTE_PAVIMENTO"], (0, 0, spessore / 2), (larghezza, profondita, spessore))
    c.fondale(TESTI["ASSET_PARTE_FONDALE"], larghezza, profondita, altezza, spessore)
    bersaglio = (0.0, 0.0, altezza * 0.38)
    c.luce_area(TESTI["ASSET_PARTE_LUCE"].format(numero=1), 1,
                (-larghezza * 0.32, -profondita * 0.22, altezza * 0.78), bersaglio,
                potenza, larghezza * 0.34)
    c.luce_area(TESTI["ASSET_PARTE_LUCE"].format(numero=2), 2,
                (larghezza * 0.32, -profondita * 0.18, altezza * 0.64), bersaglio,
                potenza * 0.65, larghezza * 0.30)
    c.luce_area(TESTI["ASSET_PARTE_LUCE"].format(numero=3), 3,
                (0.0, profondita * 0.20, altezza * 0.80), bersaglio,
                potenza * 0.8, larghezza * 0.32)


def _forme_stampa(c: _Costruttore, p: dict[str, object]) -> None:
    grandezza = float(p[libreria.CAMPO_GRANDEZZA])
    c.scatola(TESTI["ASSET_PARTE_CUBO"], (-1.5 * grandezza, 0, grandezza / 2),
              (grandezza, grandezza, grandezza))
    c.cilindro(TESTI["ASSET_PARTE_CILINDRO"], (-0.5 * grandezza, 0, grandezza / 2),
               grandezza * 0.42, grandezza)
    c.sfera(TESTI["ASSET_PARTE_SFERA"], (0.5 * grandezza, 0, grandezza / 2),
            grandezza * 0.44)
    c.cono(TESTI["ASSET_PARTE_CONO"], (1.5 * grandezza, 0, grandezza / 2),
           grandezza * 0.42, grandezza)


def _seleziona_nuovi(context, oggetti) -> None:
    """Sceglie tutte le parti create, lasciando intatti i dati degli altri."""
    view_layer = context.view_layer
    for oggetto in view_layer.objects:
        try:
            if oggetto.select_get():
                oggetto.select_set(False)
        except (AttributeError, ReferenceError, RuntimeError):
            continue
    primo = None
    for oggetto in oggetti:
        try:
            oggetto.select_set(True)
            primo = primo or oggetto
        except (AttributeError, ReferenceError, RuntimeError):
            continue
    if primo is not None:
        try:
            view_layer.objects.active = primo
        except (AttributeError, ReferenceError, RuntimeError, TypeError):
            pass


def _ricalcola_normali(mesh) -> None:
    """Rende coerenti le normali delle superfici procedurali."""
    import bmesh

    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(mesh)
    finally:
        bm.free()
    mesh.update()


def _annulla_creazione(raccolta, materiale, costruttore) -> None:
    """Rimuove solo i datablock creati durante un inserimento fallito."""
    if costruttore is not None:
        for oggetto in reversed(costruttore.oggetti):
            try:
                if oggetto.name in bpy.data.objects:
                    bpy.data.objects.remove(oggetto, do_unlink=True)
            except (ReferenceError, RuntimeError, TypeError):
                continue
        for dato in reversed(costruttore.dati):
            try:
                if dato.users == 0:
                    if isinstance(dato, bpy.types.Mesh):
                        bpy.data.meshes.remove(dato)
                    elif isinstance(dato, bpy.types.Curve):
                        bpy.data.curves.remove(dato)
                    elif isinstance(dato, bpy.types.Light):
                        bpy.data.lights.remove(dato)
            except (AttributeError, ReferenceError, RuntimeError, TypeError):
                continue
    if raccolta is not None:
        try:
            if raccolta.name in bpy.data.collections:
                bpy.data.collections.remove(raccolta, do_unlink=True)
        except (ReferenceError, RuntimeError, TypeError):
            pass
    if materiale is not None:
        try:
            if materiale.name in bpy.data.materials and materiale.users == 0:
                bpy.data.materials.remove(materiale)
        except (ReferenceError, RuntimeError, TypeError):
            pass
