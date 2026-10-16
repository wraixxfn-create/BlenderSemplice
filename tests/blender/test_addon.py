"""Prove di FormaFacile 3D dentro Blender (o dentro il modulo bpy).

Si eseguono in due modi:

    blender --background --factory-startup --python tests/blender/test_addon.py
    python3 scripts/ambiente_bpy_locale.py

Coprono le cose che si possono verificare senza finestre: registrazione,
creazione, scelta (nessuna, una, molte), nomi modificati, visibilità,
trasformazioni a passi, duplicazione ed eliminazione, vista iniziale e
inquadrature, cambi di disposizione dei pannelli e disegno dei pannelli con un
blocco di interfaccia finto. I pannelli veri, il mouse e i ridimensionamenti
con il mouse restano da provare a mano in Blender grafico: le prove lo dicono
esplicitamente quando un controllo non è possibile senza finestre.
"""

from __future__ import annotations

import contextlib
import math
import re
import sys
from pathlib import Path


RADICE = Path(__file__).resolve().parents[2]
for _percorso in (RADICE / "addon", RADICE / "tests"):
    if str(_percorso) not in sys.path:
        sys.path.insert(0, str(_percorso))

import bpy  # noqa: E402
import mathutils  # noqa: E402
import formafacile_3d as componente  # noqa: E402
import supporto_finto  # noqa: E402
from formafacile_3d import comandi, configuration  # noqa: E402
from formafacile_3d.blender import allineamento  # noqa: E402
from formafacile_3d.blender import asset_library as servizio_libreria  # noqa: E402
from formafacile_3d.blender import modificatori  # noqa: E402
from formafacile_3d.blender import oggetti as servizio_oggetti  # noqa: E402
from formafacile_3d.blender import raccolte  # noqa: E402
from formafacile_3d.blender import selezione, vista as servizio_vista  # noqa: E402
from formafacile_3d.localization import TESTI  # noqa: E402
from formafacile_3d.scene import guide, libreria, messaggi, nomi, primitives, stato  # noqa: E402
from formafacile_3d.ui import icone, panel, piano as piano_ui, renderer, vista as vista_ui  # noqa: E402


ESITI: list[str] = []

# Testi inglesi che non devono mai comparire nell'interfaccia italiana.
SEGNAPOSTO_INGLESE = re.compile(
    r"\b(?:TODO|Click here|Save|Cancel|Render|Error|Welcome)\b", re.IGNORECASE
)

# Tutti gli identificatori di comando dichiarati nella tabella centrale.
IDENTIFICATORI_DICHIARATI = frozenset(
    valore for valore in vars(comandi).values() if isinstance(valore, str)
)

# Comandi che non cambiano i dati della scena: non hanno bisogno di UNDO.
# Gli altri devono essere annullabili con Ctrl+Z, come i comandi di Blender.
SENZA_UNDO = frozenset(
    {
        comandi.ID_VISTA_INIZIALE,
        comandi.ID_INQUADRA_TUTTO,
        comandi.ID_INQUADRA_SCELTI,
        comandi.ID_INQUADRA_OGGETTO,
        comandi.ID_APRI_BARRA,
        comandi.ID_ANNULLA,
        comandi.ID_RIPETI,
        comandi.ID_PULISCI_FILTRO,
        comandi.ID_STRUMENTO_SPOSTA,
        comandi.ID_STRUMENTO_RUOTA,
        comandi.ID_STRUMENTO_SCALA,
    }
)

# Tipi di comando disegnati dai pannelli: come si chiamano nell'API di Blender.
FUNZIONI_DI_DISEGNO = {
    "riga": "row",
    "colonna": "column",
    "riquadro": "box",
    "divisione": "split",
    "separatore": "separator",
    "etichetta": "label",
    "comando": "operator",
    "campo": "prop",
}


# ---------------------------------------------------------------- aiutanti


def verifica(condizione: object, descrizione: str) -> None:
    """Controllo con messaggio chiaro; interrompe subito se non è soddisfatto."""
    if not condizione:
        raise AssertionError(f"Verifica non superata: {descrizione}")
    ESITI.append(descrizione)


def azzera_scena() -> None:
    """Riparte da una scena vuota, come un principiante che apre Blender."""
    bpy.ops.wm.read_factory_settings(use_empty=True)


def svuota_appunti() -> None:
    """Toglie il file temporaneo degli appunti di Blender, se esiste.

    Il copia e incolla della Vista 3D passa da un file `copybuffer.blend`
    nella cartella temporanea, che sopravvive al processo: senza questo
    passaggio la prova di "incolla senza aver copiato" dipenderebbe da quello
    che era rimasto sul disco da un'esecuzione precedente.
    """
    import tempfile

    try:
        (Path(tempfile.gettempdir()) / "copybuffer.blend").unlink(missing_ok=True)
    except OSError:
        pass


def comando(idname: str):
    modulo, _, nome = idname.partition(".")
    return getattr(getattr(bpy.ops, modulo), nome)


def esegui(idname: str, **parametri: object):
    """Esegue un comando se è disponibile; altrimenti restituisce None."""
    operatore = comando(idname)
    try:
        if not operatore.poll():
            return None
    except RuntimeError:
        return None
    return operatore(**parametri)


def scelti() -> list[str]:
    return sorted(o.name for o in bpy.context.view_layer.objects if o.select_get())


def nomi_scena() -> list[str]:
    return sorted(o.name for o in bpy.context.scene.objects)


def messaggio() -> str:
    return str(bpy.context.scene.formafacile.messaggio)


def area_vista():
    """La prima area Vista 3D disponibile, se c'è."""
    for finestra in bpy.data.window_managers[0].windows if bpy.data.window_managers else ():
        schermo = getattr(finestra, "screen", None)
        if schermo is None:
            continue
        for area in schermo.areas:
            if area.type == "VIEW_3D":
                return area
    return None


def regione_di(area):
    return next((r for r in area.regions if r.type == "WINDOW"), None)


@contextlib.contextmanager
def contesto_area(area):
    """Contesto di una Vista 3D, come quando si preme un pulsante del pannello."""
    with bpy.context.temp_override(
        window=bpy.context.window, area=area, region=regione_di(area)
    ):
        yield


def regione_3d(area):
    return area.spaces.active.region_3d


def contesto_interfaccia():
    return vista_ui.raccogli_contesto(bpy.context)


def pannello_di(chiave: str):
    contesto, risolutore = contesto_interfaccia()
    for pannello_ui in piano_ui.costruisci_piano(contesto):
        if pannello_ui.chiave == chiave:
            return pannello_ui, risolutore
    raise AssertionError(f"Pannello assente: {chiave}")


def disegna_pannello(classe_pannello) -> list[dict]:
    """Disegna un pannello con il blocco finto: se fallisce, la prova si ferma."""
    return supporto_finto.disegna(classe_pannello, bpy.context)


def classi_registrate(tipo) -> list:
    return [
        classe
        for classe in componente._CLASSI_REGISTRATE
        if isinstance(classe, type) and issubclass(classe, tipo)
    ]


def schemi_dei_testi() -> list[re.Pattern]:
    """Espressioni regolari dei testi centrali, con i segnaposto al posto dei valori."""

    def schema(valore: str) -> re.Pattern:
        # Prima si separano i segnaposto, poi si proteggono i pezzi: proteggere
        # prima nasconderebbe le graffe e nessun testo con i valori dentro
        # risulterebbe centralizzato.
        pezzi = [re.escape(pezzo) for pezzo in re.split(r"\{[a-z_]+\}", valore)]
        return re.compile("^" + ".+?".join(pezzi) + "$", re.DOTALL)

    return [schema(valore) for valore in TESTI.values()]


def testo_centralizzato(testo: str) -> bool:
    """Indica se un testo visibile proviene dalla mappa centrale dei testi."""
    if not testo:
        return True
    return any(schema.match(testo) for schema in schemi_dei_testi())


# ---------------------------------------------------------------- registrazione


def prova_registrazione() -> None:
    componente.register()
    componente.register()  # seconda chiamata senza effetti
    verifica(True, "registrazione ripetibile senza errori")

    dichiarati = {
        valore
        for nome, valore in vars(comandi).items()
        if nome.startswith("ID_") and isinstance(valore, str) and valore.startswith("formafacile.")
    }
    disponibili = {f"formafacile.{nome}" for nome in dir(bpy.ops.formafacile)}
    verifica(
        dichiarati == disponibili,
        f"i comandi registrati corrispondono a quelli dichiarati ({len(dichiarati)})",
    )

    verifica(
        bpy.context.scene.formafacile.modalita == configuration.MODALITA_SEMPLICE,
        "la modalità iniziale è Semplice",
    )
    verifica(
        stato.modalita_della_scena(bpy.context.scene) == configuration.MODALITA_SEMPLICE,
        "lo stato della scena è collegato alla scena vera",
    )

    viste = servizio_vista._VISTE_INIZIALI
    verifica(len(viste) >= 5, f"viste iniziali registrate per {len(viste)} schermi")
    for _chiave, elenco in viste.items():
        for voce in elenco:
            verifica(
                set(voce) == {"rotazione", "distanza", "prospettiva", "punto_di_vista"},
                "ogni vista registrata ha i dati attesi",
            )
            lunghezza = math.sqrt(sum(float(v) ** 2 for v in voce["rotazione"]))
            verifica(abs(lunghezza - 1.0) < 1e-3, "la rotazione registrata è un quaternione valido")
            verifica(
                voce["punto_di_vista"] in servizio_vista.PUNTI_DI_VISTA,
                f"tipo di vista registrato: {voce['punto_di_vista']}",
            )

    pannelli = classi_registrate(bpy.types.Panel)
    testate = classi_registrate(bpy.types.Header)
    verifica(len(pannelli) == 6, f"pannelli registrati: {len(pannelli)}")
    verifica(len(testate) == 1, "la testata con il pulsante FormaFacile è registrata")
    for classe in (*pannelli, *testate):
        verifica(classe.bl_space_type == "VIEW_3D", f"{classe.__name__} vive nella Vista 3D")

    for classe in classi_registrate(bpy.types.Operator):
        opzioni = set(classe.bl_options)
        with_errore = "REGISTER" not in opzioni or (
            classe.bl_idname not in SENZA_UNDO and "UNDO" not in opzioni
        )
        verifica(not with_errore, f"{classe.bl_idname} è annullabile (REGISTER/UNDO)")


# --------------------------------------------------------------------- creazione


def prova_creazione() -> None:
    azzera_scena()
    attesi = [
        (comandi.ID_AGGIUNGI_CUBO, TESTI["NOME_CUBO"], TESTI["NOME_MESH_CUBO"]),
        (comandi.ID_AGGIUNGI_SFERA, TESTI["NOME_SFERA"], TESTI["NOME_MESH_SFERA"]),
        (comandi.ID_AGGIUNGI_CILINDRO, TESTI["NOME_CILINDRO"], TESTI["NOME_MESH_CILINDRO"]),
        (comandi.ID_AGGIUNGI_CONO, TESTI["NOME_CONO"], TESTI["NOME_MESH_CONO"]),
        (comandi.ID_AGGIUNGI_PIANO, TESTI["NOME_PIANO"], TESTI["NOME_MESH_PIANO"]),
        (comandi.ID_AGGIUNGI_TORO, TESTI["NOME_TORO"], TESTI["NOME_MESH_TORO"]),
        (comandi.ID_AGGIUNGI_TESTO, TESTI["NOME_TESTO"], TESTI["NOME_DATI_TESTO"]),
    ]
    for idname, nome_atteso, nome_dati in attesi:
        esito = esegui(idname)
        verifica(esito is not None and "FINISHED" in esito, f"comando eseguito: {idname}")
        oggetto = bpy.data.objects.get(nome_atteso)
        verifica(oggetto is not None, f"l'oggetto è chiamato {nome_atteso} in italiano")
        verifica(oggetto.data.name == nome_dati, f"la geometria si chiama {nome_dati}")
        verifica(
            messaggio() == TESTI["MESSAGGIO_OGGETTO_CREATO"].format(nome=nome_atteso),
            f"messaggio breve dopo la creazione: {messaggio()}",
        )

    # Ogni forma promessa esiste davvero: l'elenco dei comandi è completo.
    verifica(
        tuple(idname for idname, _n, _d in attesi) == comandi.ID_FORME,
        "l'elenco delle forme corrisponde alla tabella dei comandi",
    )

    # Il cono, la ciambella e la scritta sono forme vere, con geometria propria.
    cono = bpy.data.objects[TESTI["NOME_CONO"]]
    verifica(cono.type == "MESH" and len(cono.data.polygons) > 0, "il cono ha una geometria vera")
    toro = bpy.data.objects[TESTI["NOME_TORO"]]
    verifica(
        toro.type == "MESH" and len(toro.data.polygons) > 0, "la ciambella ha una geometria vera"
    )
    verifica(
        max(abs(v) for v in toro.dimensions) < 2.1,
        f"la ciambella rispetta la grandezza scelta: {tuple(round(v, 2) for v in toro.dimensions)}",
    )

    testo = bpy.data.objects[TESTI["NOME_TESTO"]]
    verifica(testo.type == "FONT", "la scritta è un oggetto Testo di Blender")
    verifica(testo.data.body == TESTI["TESTO_INIZIALE"], "la scritta parte con un testo di esempio")
    verifica(
        abs(testo.data.size - configuration.DIMENSIONE_FORMA_PREDEFINITA / 2.0) < 1e-6,
        f"l'altezza della scritta è mezza grandezza: {testo.data.size}",
    )
    verifica(
        abs(testo.rotation_euler.x - math.pi / 2.0) < 1e-5,
        "la scritta nasce in piedi, non distesa per terra",
    )

    # La grandezza delle nuove forme si cambia da un solo campo.
    azzera_scena()
    bpy.context.scene.formafacile.grandezza_forma = 4.0
    esegui(comandi.ID_AGGIUNGI_CUBO)
    cubo_grande = bpy.data.objects[TESTI["NOME_CUBO"]]
    verifica(
        max(abs(v) for v in cubo_grande.dimensions) > 3.9,
        f"la grandezza scelta cambia davvero il cubo: {tuple(round(v, 2) for v in cubo_grande.dimensions)}",
    )
    bpy.context.scene.formafacile.grandezza_forma = configuration.DIMENSIONE_FORMA_PREDEFINITA

    azzera_scena()
    esegui(comandi.ID_AGGIUNGI_LUCE)
    luce = bpy.data.objects.get(TESTI["NOME_LUCE"])
    verifica(luce is not None and luce.type == "LIGHT", "il comando Luce crea una luce")
    verifica(
        abs(luce.location.z - 4.0) < 1e-6,
        "la luce compare sopra il cursore 3D, quindi illumina la scena",
    )

    posizioni = [tuple(round(v, 3) for v in o.location) for o in bpy.context.scene.objects]
    verifica(
        len(set(posizioni)) == len(posizioni),
        f"le forme non finiscono una dentro l'altra: {posizioni}",
    )
    verifica(
        scelti() == [TESTI["NOME_LUCE"]]
        and bpy.context.view_layer.objects.active.name == TESTI["NOME_LUCE"],
        "dopo la creazione è scelto solo l'ultimo oggetto",
    )

    # La creazione funziona anche in modalità completa, che mostra più comandi.
    azzera_scena()
    bpy.context.scene.formafacile.modalita = configuration.MODALITA_COMPLETA
    esito = esegui(comandi.ID_AGGIUNGI_CUBO)
    verifica("FINISHED" in esito, "in modalità completa la creazione funziona ugualmente")
    bpy.context.scene.formafacile.modalita = configuration.MODALITA_SEMPLICE


# ---------------------------------------------------------- libreria di modelli


def _asset_oggetto(raccolta_asset, finale: str):
    """Trova una parte della raccolta per il finale del suo nome italiano."""
    return next(
        (oggetto for oggetto in raccolta_asset.objects if oggetto.name.endswith(f" - {finale}")),
        None,
    )


def _controlla_dimensioni_asset(oggetto, attese, descrizione: str) -> None:
    """Controlla le dimensioni geometriche dopo aver aggiornato la scena."""
    bpy.context.view_layer.update()
    ottenute = tuple(float(valore) for valore in oggetto.dimensions)
    verifica(
        all(abs(ottenuta - attesa) < 0.015 for ottenuta, attesa in zip(ottenute, attese)),
        f"{descrizione}: dimensioni {tuple(round(v, 3) for v in ottenute)}",
    )


def prova_libreria_asset() -> None:
    """Genera, misura, seleziona e rimuove ogni modello con geometria reale."""
    conteggi = {
        libreria.ASSET_TAVOLINO: 5,
        libreria.ASSET_SCAFFALE: 8,
        libreria.ASSET_SEDIA: 6,
        libreria.ASSET_PIEDISTALLO: 3,
        libreria.ASSET_VASO: 1,
        libreria.ASSET_INSEGNA: 2,
        libreria.ASSET_STANZA: 3,
        libreria.ASSET_PEDANA: 2,
        libreria.ASSET_SET_FOTOGRAFICO: 5,
        libreria.ASSET_FORMA_STAMPA: 4,
    }
    for scheda in libreria.SCHEDE:
        azzera_scena()
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(100.0, 100.0, 0.0))
        preesistente = bpy.context.object
        preesistente.name = "Cubo preesistente"
        posizione_precedente = tuple(float(v) for v in preesistente.location)
        dimensioni_precedenti = tuple(float(v) for v in preesistente.dimensions)
        geometria_precedente = preesistente.data
        materiale_preesistente = bpy.data.materials.new("Materiale preesistente")
        materiale_preesistente.diffuse_color = (0.1, 0.2, 0.3, 1.0)
        preesistente.data.materials.append(materiale_preesistente)
        colore_precedente = tuple(float(v) for v in materiale_preesistente.diffuse_color)

        stato_asset = bpy.context.scene.formafacile
        stato_asset.asset_selezionato = scheda.identificatore
        if scheda.identificatore == libreria.ASSET_TAVOLINO:
            stato_asset.asset_colore = (0.2, 0.4, 0.6, 1.0)
        esito = esegui(comandi.ID_AGGIUNGI_ASSET)
        verifica(
            esito is not None and "FINISHED" in esito,
            f"il modello {scheda.nome} viene inserito senza errori",
        )
        raccolta_asset = next(
            (voce for voce in bpy.data.collections
             if voce.get(TESTI["ASSET_PROPRIETA_MODELLO"]) == scheda.nome),
            None,
        )
        verifica(raccolta_asset is not None, f"{scheda.nome}: raccolta dedicata presente")
        parti = tuple(raccolta_asset.objects)
        verifica(
            len(parti) == conteggi[scheda.identificatore],
            f"{scheda.nome}: numero di parti previsto ({len(parti)})",
        )
        verifica(
            all(oggetto.data is not None and oggetto.type in {"MESH", "FONT", "LIGHT"} for oggetto in parti),
            f"{scheda.nome}: la raccolta contiene oggetti Blender reali",
        )
        verifica(
            all(len(oggetto.data.vertices) > 0 and len(oggetto.data.polygons) > 0
                for oggetto in parti if oggetto.type == "MESH"),
            f"{scheda.nome}: ogni parte mesh ha vertici e facce",
        )
        verifica(
            all(oggetto.data.materials for oggetto in parti if oggetto.type == "MESH"),
            f"{scheda.nome}: ogni parte mesh ha il materiale regolabile scelto",
        )
        verifica(
            all(oggetto.data.materials[0] is not materiale_preesistente
                for oggetto in parti if oggetto.type == "MESH"),
            f"{scheda.nome}: il colore usa un materiale indipendente dagli oggetti precedenti",
        )
        verifica(
            bool(raccolta_asset.get(TESTI["ASSET_PROPRIETA_PARAMETRI"])),
            f"{scheda.nome}: i parametri di partenza restano leggibili sulla raccolta",
        )
        if scheda.identificatore == libreria.ASSET_TAVOLINO:
            colore_creato = tuple(float(v) for v in parti[0].data.materials[0].diffuse_color)
            verifica(
                all(abs(a - b) < 1e-5 for a, b in zip(colore_creato, (0.2, 0.4, 0.6, 1.0))),
                "il colore scelto viene applicato al materiale del tavolino",
            )
        verifica(
            all(oggetto.name.startswith(raccolta_asset.name + " - ") for oggetto in parti),
            f"{scheda.nome}: i nomi delle parti sono chiari e raggruppati",
        )
        verifica(
            sorted(scelti()) == sorted(oggetto.name for oggetto in parti),
            f"{scheda.nome}: dopo l'inserimento sono scelte tutte e sole le sue parti",
        )
        messaggio_asset = (
            TESTI["MESSAGGIO_ASSET_AGGIUNTO_UNO"].format(nome=scheda.nome)
            if len(parti) == 1
            else TESTI["MESSAGGIO_ASSET_AGGIUNTO"].format(
                nome=scheda.nome, numero=len(parti)
            )
        )
        verifica(
            bpy.context.scene.formafacile.messaggio == messaggio_asset,
            f"{scheda.nome}: messaggio di inserimento in italiano",
        )

        if scheda.identificatore == libreria.ASSET_TAVOLINO:
            _controlla_dimensioni_asset(_asset_oggetto(raccolta_asset, TESTI["ASSET_PARTE_PIANO"]),
                                        (1.2, 0.7, 0.06), "Piano del tavolino")
        elif scheda.identificatore == libreria.ASSET_SCAFFALE:
            _controlla_dimensioni_asset(_asset_oggetto(raccolta_asset, TESTI["ASSET_PARTE_FIANCO_SINISTRO"]),
                                        (0.04, 0.35, 2.0), "Fianco dello scaffale")
        elif scheda.identificatore == libreria.ASSET_SEDIA:
            _controlla_dimensioni_asset(_asset_oggetto(raccolta_asset, TESTI["ASSET_PARTE_SEDUTA"]),
                                        (0.45, 0.5, 0.045), "Seduta della sedia")
        elif scheda.identificatore == libreria.ASSET_PIEDISTALLO:
            _controlla_dimensioni_asset(_asset_oggetto(raccolta_asset, TESTI["ASSET_PARTE_TOP"]),
                                        (0.8, 0.8, 0.08), "Piano del piedistallo")
        elif scheda.identificatore == libreria.ASSET_VASO:
            _controlla_dimensioni_asset(parti[0], (0.4, 0.4, 0.5), "Vaso cavo")
            verifica(
                len(parti[0].data.polygons) >= 48 * 10,
                "il vaso è una superficie cava a profilo, non un'immagine o un segnaposto",
            )
        elif scheda.identificatore == libreria.ASSET_INSEGNA:
            pannello_asset = _asset_oggetto(raccolta_asset, TESTI["ASSET_PARTE_PANNELLO"])
            scritta_asset = _asset_oggetto(raccolta_asset, TESTI["ASSET_PARTE_TESTO"])
            _controlla_dimensioni_asset(pannello_asset, (1.2, 0.06, 0.6), "Pannello dell'insegna")
            verifica(scritta_asset.type == "FONT" and scritta_asset.data.extrude > 0.0,
                     "la scritta è testo 3D estruso e resta modificabile")
            verifica(scritta_asset.data.body == "CIAO", "l'insegna usa il testo scelto")
        elif scheda.identificatore == libreria.ASSET_STANZA:
            _controlla_dimensioni_asset(_asset_oggetto(raccolta_asset, TESTI["ASSET_PARTE_PAVIMENTO"]),
                                        (4.0, 4.0, 0.12), "Pavimento della stanza")
        elif scheda.identificatore == libreria.ASSET_PEDANA:
            verifica(all(oggetto.type == "MESH" for oggetto in parti), "la pedana è fatta di mesh solide")
            _controlla_dimensioni_asset(_asset_oggetto(raccolta_asset, TESTI["ASSET_PARTE_PEDANA"]),
                                        (1.2, 1.2, 0.0912), "Base della pedana")
        elif scheda.identificatore == libreria.ASSET_SET_FOTOGRAFICO:
            verifica(sum(oggetto.type == "LIGHT" for oggetto in parti) == 3,
                     "il set fotografico crea tre luci di area reali")
            verifica(all(oggetto.data.type == "AREA" for oggetto in parti if oggetto.type == "LIGHT"),
                     "le luci del set sono regolabili come luci di area")
            _controlla_dimensioni_asset(_asset_oggetto(raccolta_asset, TESTI["ASSET_PARTE_PAVIMENTO"]),
                                        (4.0, 3.5, 0.08), "Pavimento del set fotografico")
        elif scheda.identificatore == libreria.ASSET_FORMA_STAMPA:
            _controlla_dimensioni_asset(_asset_oggetto(raccolta_asset, TESTI["ASSET_PARTE_CUBO"]),
                                        (0.5, 0.5, 0.5), "Cubo del set di stampa 3D")

        verifica(
            bpy.data.objects.get(preesistente.name) is preesistente
            and tuple(float(v) for v in preesistente.location) == posizione_precedente
            and tuple(float(v) for v in preesistente.dimensions) == dimensioni_precedenti
            and preesistente.data is geometria_precedente
            and preesistente.data.materials[0] is materiale_preesistente
            and tuple(float(v) for v in materiale_preesistente.diffuse_color) == colore_precedente,
            f"{scheda.nome}: oggetto e materiale preesistenti non vengono toccati",
        )
        verifica(
            "FINISHED" in esegui("object.delete", use_global=False),
            f"{scheda.nome}: le parti aggiunte si possono rimuovere con il comando normale",
        )
        verifica(
            bpy.data.objects.get(preesistente.name) is preesistente
            and preesistente.data is geometria_precedente
            and preesistente.data.materials[0] is materiale_preesistente
            and tuple(float(v) for v in materiale_preesistente.diffuse_color) == colore_precedente,
            f"{scheda.nome}: la rimozione non danneggia gli oggetti precedenti",
        )

    # Una combinazione di misure incompatibile deve fallire prima di creare geometrie.
    azzera_scena()
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(50.0, 50.0, 0.0))
    preesistente = bpy.context.object
    stato_asset = bpy.context.scene.formafacile
    stato_asset.asset_selezionato = libreria.ASSET_TAVOLINO
    stato_asset.asset_larghezza = 0.05
    stato_asset.asset_profondita = 0.05
    stato_asset.asset_spessore = 0.2
    nomi_precedenti = set(nomi_scena())
    esito = esegui(comandi.ID_AGGIUNGI_ASSET)
    verifica(esito is not None and "CANCELLED" in esito,
             "misure incompatibili fermano la creazione senza eccezioni")
    verifica(set(nomi_scena()) == nomi_precedenti and preesistente.name in nomi_scena(),
             "un errore di misura non aggiunge né rimuove oggetti")
    verifica(messaggio() == TESTI["ERRORE_ASSET_PARAMETRI"],
             "l'errore delle misure è spiegato in italiano")

    stato_asset.asset_selezionato = libreria.ASSET_INSEGNA
    stato_asset.asset_testo = ""
    esito = esegui(comandi.ID_AGGIUNGI_ASSET)
    verifica(esito is not None and "CANCELLED" in esito,
             "l'insegna non viene creata con il testo vuoto")
    verifica(messaggio() == TESTI["ERRORE_ASSET_TESTO_VUOTO"],
             "l'errore del testo vuoto è chiaro e in italiano")


# --------------------------------------------------------------------- scelta


def prova_scelta() -> None:
    azzera_scena()
    for idname in (
        comandi.ID_AGGIUNGI_CUBO,
        comandi.ID_AGGIUNGI_SFERA,
        comandi.ID_AGGIUNGI_CILINDRO,
    ):
        esegui(idname)

    esegui(comandi.ID_DESCEGLI_TUTTO)
    verifica(scelti() == [], "Nessuno toglie la scelta da tutti gli oggetti")
    verifica(
        bpy.context.view_layer.objects.active is None,
        "dopo Nessuno non resta un oggetto attivo, come in Blender",
    )
    verifica(messaggio() == TESTI["MESSAGGIO_DESELEZIONA_TUTTO"], "messaggio di scelta azzerata")

    contesto, _ = contesto_interfaccia()
    verifica(contesto.scelti == (), "il pannello contestuale vede che non c'è nulla di scelto")
    verifica(contesto.attivo is None, "senza scelta non c'è un oggetto attivo")
    verifica(
        not comando(comandi.ID_SPOSTA_PASSO).poll(),
        "senza scelta i comandi di spostamento non sono disponibili",
    )

    esito = esegui(comandi.ID_SCEGLI_TUTTO)
    verifica("FINISHED" in esito and len(scelti()) == 3, "Tutti sceglie i tre oggetti visibili")
    verifica(
        messaggio() == TESTI["MESSAGGIO_SELEZIONA_TUTTO"].format(numero=3),
        f"messaggio di scelta multipla: {messaggio()}",
    )

    cubo, sfera, cilindro = (TESTI["NOME_CUBO"], TESTI["NOME_SFERA"], TESTI["NOME_CILINDRO"])
    esegui(comandi.ID_SCEGLI_OGGETTO, oggetto=cubo, modo="sostituisci")
    verifica(scelti() == [cubo], "Scegli sostituisce la scelta con un solo oggetto")
    verifica(
        bpy.context.view_layer.objects.active.name == cubo,
        "l'oggetto scelto diventa anche l'attivo",
    )

    esegui(comandi.ID_SCEGLI_OGGETTO, oggetto=sfera, modo="aggiungi")
    verifica(len(scelti()) == 2, "con Maiusc la scelta si allarga")
    verifica(
        messaggio() == TESTI["MESSAGGIO_AGGIUNTO_ALLA_SCELTA"].format(nome=sfera),
        "messaggio di oggetto aggiunto alla scelta",
    )

    contesto, _ = contesto_interfaccia()
    verifica(len(contesto.scelti) == 2, "il pannello contestuale vede i due oggetti scelti")
    verifica(
        contesto.attivo is not None and contesto.attivo.nome == sfera,
        "l'ultimo oggetto scelto è anche quello attivo, come in Blender",
    )
    pannello_oggetto, _ = pannello_di("oggetto")
    testi = [
        elemento.testo
        for gruppo in pannello_oggetto.gruppi
        for riga in gruppo.righe
        for elemento in riga.elementi
        if hasattr(elemento, "testo")
    ]
    verifica(
        TESTI["ETICHETTA_MULTI_SELEZIONE"].format(numero=2) in testi,
        "il pannello contestuale riassume la scelta multipla",
    )
    verifica(
        TESTI["TIPO_FORMA_PLURALE"].format(numero=2) in testi,
        "il riassunto conta le forme in parole semplici",
    )

    esegui(comandi.ID_SCEGLI_OGGETTO, oggetto=cubo, modo="rimuovi")
    verifica(scelti() == [sfera], "con Ctrl la scelta si stringe")
    verifica(
        messaggio() == TESTI["MESSAGGIO_TOLTO_DALLA_SCELTA"].format(nome=cubo),
        "messaggio di oggetto tolto dalla scelta",
    )

    esegui(comandi.ID_INVERTI_SCELTA)
    verifica(
        sorted(scelti()) == sorted([cubo, cilindro]),
        f"Inverti sceglie gli oggetti non scelti: {scelti()}",
    )

    esegui(comandi.ID_SCEGLI_OGGETTO, oggetto=cilindro, modo="sostituisci")
    esito = esegui(comandi.ID_SCEGLI_STESSO_TIPO)
    verifica("FINISHED" in esito and len(scelti()) == 3, "Stesso tipo sceglie le tre forme")
    verifica(
        messaggio() == TESTI["MESSAGGIO_SELEZIONA_TIPO"].format(numero=3),
        f"messaggio di scelta per tipo: {messaggio()}",
    )

    # Un oggetto nascosto non entra mai nella scelta di gruppo.
    oggetto_nascosto = bpy.data.objects[TESTI["NOME_CILINDRO"]]
    oggetto_nascosto.hide_viewport = True
    esegui(comandi.ID_SCEGLI_TUTTO)
    verifica(
        TESTI["NOME_CILINDRO"] not in scelti(),
        "un oggetto nascosto non viene scelto da Tutti",
    )
    verifica(
        TESTI["MESSAGGIO_SALTATI"].format(numero=1) in messaggio(),
        f"il messaggio dice quanti oggetti sono stati saltati: {messaggio()}",
    )
    contesto, _ = contesto_interfaccia()
    verifica(
        any(o.nascosto and o.nome == TESTI["NOME_CILINDRO"] for o in contesto.oggetti),
        "il pannello segnala l'oggetto nascosto",
    )
    oggetto_nascosto.hide_viewport = False

    # Un oggetto bloccato viene rifiutato con una spiegazione.
    oggetto_nascosto.hide_select = True
    esito = esegui(comandi.ID_SCEGLI_OGGETTO, oggetto=TESTI["NOME_CILINDRO"], modo="sostituisci")
    verifica(esito is not None and "CANCELLED" in esito, "un oggetto bloccato non si sceglie")
    verifica(
        messaggio()
        == TESTI["ERRORE_OGGETTO_NON_SELEZIONABILE"].format(nome=TESTI["NOME_CILINDRO"]),
        "il messaggio spiega perché non si può scegliere",
    )
    oggetto_nascosto.hide_select = False

    verifica(
        [o.name for o in selezione.oggetti_della_scena(bpy.context.view_layer)]
        == sorted(nomi_scena(), key=str.casefold),
        "l'elenco degli oggetti è in ordine alfabetico",
    )


# -------------------------------------------------------------------- rinomina


def prova_rinomina() -> None:
    azzera_scena()
    esegui(comandi.ID_AGGIUNGI_CUBO)
    esito = esegui(comandi.ID_RINOMINA, oggetto=TESTI["NOME_CUBO"], nome="  Albero  ")
    verifica("FINISHED" in esito, "rinomina eseguita")
    verifica("Albero" in bpy.data.objects, "gli spazi esterni vengono tolti dal nome")
    albero = bpy.data.objects["Albero"]
    verifica(
        albero.data.name == f"{TESTI['PREFISSO_GEOMETRIA']} Albero",
        f"la geometria segue il nuovo nome: {albero.data.name}",
    )
    verifica(
        messaggio() == TESTI["MESSAGGIO_RINOMINATO"].format(nome="Albero"),
        f"messaggio con il nuovo nome: {messaggio()}",
    )
    contesto, _ = contesto_interfaccia()
    verifica(
        [o.nome for o in contesto.oggetti] == ["Albero"],
        "il pannello mostra subito il nome nuovo",
    )

    esito = esegui(comandi.ID_RINOMINA, oggetto="Albero", nome="Tavolo\ncon\nritorni")
    verifica(
        "FINISHED" in esito and "Tavolo con ritorni" in bpy.data.objects,
        "ritorni a capo rimossi",
    )

    esito = esegui(comandi.ID_RINOMINA, oggetto="Tavolo con ritorni", nome="x" * 90)
    verifica("FINISHED" in esito, "un nome lunghissimo viene accettato")
    nome_lungo = next(n for n in bpy.data.objects.keys() if n.startswith("x"))
    verifica(
        len(nome_lungo) == configuration.LUNGHEZZA_MASSIMA_NOME,
        f"il nome è troncato al limite di Blender: {len(nome_lungo)} caratteri",
    )

    esito = esegui(comandi.ID_RINOMINA, oggetto=nome_lungo, nome="   ")
    verifica(esito is not None and "CANCELLED" in esito, "un nome vuoto viene rifiutato")
    verifica(
        nome_lungo in bpy.data.objects,
        "dopo il rifiuto l'oggetto mantiene il nome di prima",
    )
    verifica(
        messaggio() == TESTI["ERRORE_NOME_VUOTO"],
        f"il motivo del rifiuto si legge nel pannello: {messaggio()}",
    )

    esegui(comandi.ID_AGGIUNGI_SFERA)
    esito = esegui(comandi.ID_RINOMINA, oggetto=TESTI["NOME_SFERA"], nome=nome_lungo)
    nome_finale = next(n for n in bpy.data.objects.keys() if n != nome_lungo)
    verifica("FINISHED" in esito, "si può rinominare con un nome già usato")
    verifica(
        nome_finale != nome_lungo,
        f"Blender sistema il nome doppio e il messaggio lo riporta: {nome_finale}",
    )
    verifica(
        messaggio() == TESTI["MESSAGGIO_RINOMINATO"].format(nome=nome_finale),
        "il messaggio mostra il nome davvero assegnato",
    )


# ------------------------------------------------------------------ visibilità


def prova_visibilita() -> None:
    azzera_scena()
    esegui(comandi.ID_AGGIUNGI_CUBO)
    esegui(comandi.ID_AGGIUNGI_SFERA)
    cubo = bpy.data.objects[TESTI["NOME_CUBO"]]

    esegui(comandi.ID_ALTERNA_VISIBILITA, oggetto=cubo.name)
    verifica(cubo.hide_viewport, "Nascondi toglie l'oggetto dalla Vista 3D")
    verifica(cubo.name not in scelti(), "un oggetto nascosto non resta scelto")
    verifica(
        messaggio() == TESTI["MESSAGGIO_NASCOSTO"].format(nome=cubo.name),
        f"messaggio di oggetto nascosto: {messaggio()}",
    )

    pannello_scena, _ = pannello_di("scena")
    identificatori = [
        elemento.idname
        for gruppo in pannello_scena.gruppi
        for riga in gruppo.righe
        for elemento in riga.elementi
        if hasattr(elemento, "idname")
    ]
    verifica(
        comandi.ID_MOSTRA_TUTTI in identificatori,
        "con un oggetto nascosto compare Mostra tutti gli oggetti",
    )

    esegui(comandi.ID_ALTERNA_VISIBILITA, oggetto=cubo.name)
    verifica(not cubo.hide_viewport, "la seconda pressione fa ricomparire l'oggetto")
    verifica(
        messaggio() == TESTI["MESSAGGIO_MOSTRATO"].format(nome=cubo.name),
        "messaggio di oggetto di nuovo visibile",
    )

    esegui(comandi.ID_SCEGLI_TUTTO)
    esegui(comandi.ID_ALTERNA_VISIBILITA)
    verifica(
        cubo.hide_viewport and bpy.data.objects[TESTI["NOME_SFERA"]].hide_viewport,
        "Nascondi vale per tutti gli oggetti scelti",
    )
    verifica(
        messaggio() == TESTI["MESSAGGIO_NASCOSTI"].format(numero=2),
        f"nascondendo più oggetti il messaggio è al plurale: {messaggio()}",
    )
    esito = esegui(comandi.ID_MOSTRA_TUTTI)
    verifica("FINISHED" in esito, "Mostra tutti gli oggetti funziona")
    verifica(
        not cubo.hide_viewport and not bpy.data.objects[TESTI["NOME_SFERA"]].hide_viewport,
        "tutti gli oggetti tornano visibili",
    )
    verifica(
        messaggio() == TESTI["MESSAGGIO_MOSTRATI_TUTTI"],
        "messaggio di ripristino della visibilità",
    )


# --------------------------------------------------------------- trasformazioni


def prova_trasformazioni() -> None:
    azzera_scena()
    esegui(comandi.ID_AGGIUNGI_CUBO)
    cubo = bpy.data.objects[TESTI["NOME_CUBO"]]
    passo = configuration.PASSO_PREDEFINITO

    attesi = {
        "destra": (passo, 0.0, 0.0),
        "sinistra": (-passo, 0.0, 0.0),
        "su": (0.0, 0.0, passo),
        "giu": (0.0, 0.0, -passo),
        "avanti": (0.0, -passo, 0.0),
        "indietro": (0.0, passo, 0.0),
    }
    for direzione, spostamento in attesi.items():
        partenza = tuple(cubo.location)
        esito = esegui(comandi.ID_SPOSTA_PASSO, direzione=direzione)
        with_errore = "FINISHED" not in esito
        for asse in range(3):
            atteso = partenza[asse] + spostamento[asse]
            with_errore = with_errore or abs(cubo.location[asse] - atteso) > 1e-6
        verifica(not with_errore, f"spostamento verso {direzione}: {spostamento}")
        verso = TESTI[comandi.TESTI_DIREZIONE[direzione]].lower()
        verifica(
            messaggio() == TESTI["MESSAGGIO_MOSSO"].format(nome=cubo.name, verso=verso),
            f"messaggio di spostamento verso {direzione}",
        )

    bpy.context.scene.formafacile.passo = 2.0
    partenza = cubo.location.x
    esegui(comandi.ID_SPOSTA_PASSO, direzione="destra")
    verifica(
        abs(cubo.location.x - partenza - 2.0) < 1e-6,
        "il campo Passo cambia davvero la misura dello spostamento",
    )
    bpy.context.scene.formafacile.passo = passo

    # La rotazione funziona con i tre modi di Blender e dà lo stesso risultato.
    for modo in ("XYZ", "QUATERNION", "AXIS_ANGLE"):
        azzera_scena()
        esegui(comandi.ID_AGGIUNGI_CUBO)
        oggetto = bpy.data.objects[TESTI["NOME_CUBO"]]
        oggetto.rotation_mode = modo
        prima = oggetto.matrix_basis.copy()
        esito = esegui(comandi.ID_RUOTA_PASSO, verso="destra")
        attesa = mathutils.Matrix.Rotation(
            math.radians(-configuration.ANGOLO_PREDEFINITO_GRADI), 4, "Z"
        ) @ prima
        differenza = max(
            abs(oggetto.matrix_basis[r][c] - attesa[r][c]) for r in range(4) for c in range(4)
        )
        verifica(
            "FINISHED" in esito and differenza < 1e-4,
            f"Gira a destra di {configuration.ANGOLO_PREDEFINITO_GRADI} gradi nel modo {modo}",
        )
        verifica(
            messaggio() == TESTI["MESSAGGIO_RUOTATO"].format(nome=oggetto.name),
            "messaggio di rotazione eseguita",
        )

    # Più oggetti scelti: un solo passo vale per tutti.
    azzera_scena()
    esegui(comandi.ID_AGGIUNGI_CUBO)
    esegui(comandi.ID_AGGIUNGI_SFERA)
    esegui(comandi.ID_SCEGLI_TUTTO)
    prima = {o.name: tuple(o.location) for o in bpy.context.scene.objects}
    esito = esegui(comandi.ID_SPOSTA_PASSO, direzione="su")
    verifica("FINISHED" in esito, "lo spostamento vale per tutti gli oggetti scelti")
    for oggetto in bpy.context.scene.objects:
        with_errore = (
            abs(oggetto.location.z - prima[oggetto.name][2] - configuration.PASSO_PREDEFINITO)
            > 1e-6
        )
        verifica(not with_errore, f"{oggetto.name} si è spostato verso l'alto")
    verifica(
        messaggio()
        == TESTI["MESSAGGIO_MOSSI"].format(
            numero=len(bpy.context.scene.objects), verso=TESTI["AZIONE_VERSO_SU"].lower()
        ),
        f"messaggio al plurale: {messaggio()}",
    )

    # Dimensione: su, giù e limite minimo.
    azzera_scena()
    esegui(comandi.ID_AGGIUNGI_SFERA)
    sfera = bpy.data.objects[TESTI["NOME_SFERA"]]
    esegui(comandi.ID_SCALA_PASSO, verso="grande")
    verifica(
        abs(sfera.scale.x - configuration.FATTORE_SCALA_PREDEFINITO) < 1e-6,
        "Più grande applica il fattore previsto",
    )
    esegui(comandi.ID_SCALA_PASSO, verso="piccolo")
    verifica(abs(sfera.scale.x - 1.0) < 1e-6, "Più piccolo riporta alla dimensione iniziale")
    verifica(
        messaggio() == TESTI["MESSAGGIO_SCALATO"].format(nome=sfera.name),
        "messaggio di dimensione cambiata",
    )

    piccolissima = configuration.SCALA_MINIMA / 2.0
    sfera.scale = (piccolissima, piccolissima, piccolissima)
    esito = esegui(comandi.ID_SCALA_PASSO, verso="piccolo")
    verifica(esito is not None and "CANCELLED" in esito, "non si scende sotto la dimensione minima")
    verifica(
        abs(sfera.scale.x - piccolissima) < 1e-9,
        "dopo il rifiuto la dimensione resta quella di prima",
    )
    verifica(
        messaggio() == TESTI["MESSAGGIO_DIMENSIONE_MINIMA"],
        f"il messaggio spiega perché non si rimpicciolisce: {messaggio()}",
    )

    # I blocchi di Blender vengono rispettati: un asse bloccato non si tocca.
    azzera_scena()
    esegui(comandi.ID_AGGIUNGI_CUBO)
    bloccato_poco = bpy.data.objects[TESTI["NOME_CUBO"]]
    bloccato_poco.lock_location = (True, False, False)
    partenza = tuple(bloccato_poco.location)
    esito = esegui(comandi.ID_SPOSTA_PASSO, direzione="destra")
    verifica(esito is not None and "CANCELLED" in esito, "spostare un asse bloccato non fa nulla")
    verifica(
        tuple(bloccato_poco.location) == partenza,
        "l'asse X bloccato resta fermo, e con lui tutto l'oggetto",
    )
    verifica(
        messaggio() == TESTI["ERRORE_TRASFORMAZIONE_BLOCCATA"],
        f"il messaggio spiega il blocco in italiano: {messaggio()}",
    )

    esito = esegui(comandi.ID_SPOSTA_PASSO, direzione="su")
    verifica("FINISHED" in esito, "un asse libero si muove anche se un altro è bloccato")
    verifica(
        abs(bloccato_poco.location.z - partenza[2] - passo) < 1e-6
        and abs(bloccato_poco.location.x - partenza[0]) < 1e-9,
        "si muove solo l'asse libero (Z), l'asse bloccato (X) resta fermo",
    )

    bloccato_poco.lock_rotation = (False, False, True)
    esito = esegui(comandi.ID_RUOTA_PASSO, verso="sinistra")
    verifica("CANCELLED" in esito, "ruotare con l'asse Z bloccato non fa nulla")

    bloccato_poco.lock_scale = (True, True, True)
    esito = esegui(comandi.ID_SCALA_PASSO, verso="grande")
    verifica("CANCELLED" in esito, "ingrandire con la dimensione bloccata non fa nulla")
    verifica(
        tuple(bloccato_poco.scale) == (1.0, 1.0, 1.0),
        "la dimensione bloccata non cambia",
    )

    # Un oggetto non scelto non viene mai toccato.
    azzera_scena()
    esegui(comandi.ID_AGGIUNGI_CUBO)
    esegui(comandi.ID_AGGIUNGI_SFERA)
    cubo = bpy.data.objects[TESTI["NOME_CUBO"]]
    sfera = bpy.data.objects[TESTI["NOME_SFERA"]]
    esegui(comandi.ID_SCEGLI_OGGETTO, oggetto=cubo.name, modo="sostituisci")
    prima_sfera = tuple(sfera.location)
    prima_cubo = tuple(cubo.location)
    esegui(comandi.ID_SPOSTA_PASSO, direzione="destra")
    esegui(comandi.ID_RUOTA_PASSO, verso="destra")
    esegui(comandi.ID_SCALA_PASSO, verso="grande")
    verifica(
        tuple(sfera.location) == prima_sfera and tuple(sfera.scale) == (1.0, 1.0, 1.0),
        "l'oggetto non scelto non si muove e non cambia dimensione",
    )
    verifica(
        cubo.location.x > prima_cubo[0],
        "l'oggetto scelto si è mosso: la scelta comanda",
    )
    verifica(
        bpy.context.view_layer.objects.active is not None
        and bpy.context.view_layer.objects.active.name == cubo.name,
        "dopo i passi l'oggetto attivo è lo stesso di prima",
    )

    # Luci.
    azzera_scena()
    esegui(comandi.ID_AGGIUNGI_LUCE)
    luce = bpy.data.objects[TESTI["NOME_LUCE"]]
    partenza = float(luce.data.energy)
    esegui(comandi.ID_LUCE_PIU)
    verifica(
        abs(luce.data.energy - partenza * configuration.FATTORE_LUCE) < 1e-3,
        "Più luminosa aumenta la potenza della luce",
    )
    esegui(comandi.ID_LUCE_MENO)
    verifica(
        abs(luce.data.energy - partenza) < 1e-3, "Meno luminosa riporta alla potenza precedente"
    )
    luce.data.energy = configuration.POTENZA_LUCE_MINIMA / 2.0
    esegui(comandi.ID_LUCE_MENO)
    verifica(
        luce.data.energy >= configuration.POTENZA_LUCE_MINIMA - 1e-6,
        f"la potenza della luce non si azzera: {luce.data.energy}",
    )


# ------------------------------------------------------- duplicazione ed elimina


def prova_duplica_elimina() -> None:
    azzera_scena()
    esegui(comandi.ID_AGGIUNGI_CUBO)
    cubo = bpy.data.objects[TESTI["NOME_CUBO"]]
    esito = esegui(comandi.ID_DUPLICA)
    verifica("FINISHED" in esito, "Duplica crea una copia")
    copie = [o for o in bpy.context.scene.objects if o.name != cubo.name]
    verifica(len(copie) == 1, "la copia è una sola")
    copia = copie[0]
    verifica(copia.data != cubo.data, "la copia ha una geometria propria")
    verifica(copia.location.x > cubo.location.x, "la copia è spostata di fianco, quindi si vede")
    verifica(scelti() == [copia.name], "dopo la copia è scelta la copia")
    verifica(
        messaggio() == TESTI["MESSAGGIO_DUPLICATO"].format(nome=copia.name),
        f"messaggio con il nome della copia: {messaggio()}",
    )
    verifica(
        copia.users_collection[0] == cubo.users_collection[0],
        "la copia resta nella stessa raccolta dell'originale",
    )

    nome_cubo = cubo.name
    esegui(comandi.ID_DESCEGLI_TUTTO)
    esegui(comandi.ID_SCEGLI_OGGETTO, oggetto=nome_cubo, modo="sostituisci")
    esegui(comandi.ID_ELIMINA)
    verifica(len(bpy.context.scene.objects) == 1, "Elimina toglie un solo oggetto")
    verifica(
        messaggio() == TESTI["MESSAGGIO_ELIMINATO"].format(nome=nome_cubo),
        f"messaggio di oggetto eliminato: {messaggio()}",
    )

    esegui(comandi.ID_SCEGLI_TUTTO)
    esito = esegui(comandi.ID_ELIMINA)
    verifica("FINISHED" in esito, "Elimina funziona anche con più oggetti")
    verifica(len(bpy.context.scene.objects) == 0, "la scena resta vuota")
    contesto, _ = contesto_interfaccia()
    verifica(contesto.oggetti == (), "il pannello riconosce la scena vuota")
    pannello_scena, _ = pannello_di("scena")
    testi_pannello = [
        elemento.testo
        for gruppo in pannello_scena.gruppi
        for riga in gruppo.righe
        for elemento in riga.elementi
        if hasattr(elemento, "testo")
    ]
    verifica(
        TESTI["ETICHETTA_NESSUN_OGGETTO"] in testi_pannello,
        "la scena vuota mostra un invito chiaro",
    )


# ---------------------------------------------------------- posizioni precise


def prova_posizioni() -> None:
    """Porta al centro e appoggia sul piano: niente sorprese."""
    azzera_scena()
    esegui(comandi.ID_AGGIUNGI_CUBO)
    esegui(comandi.ID_AGGIUNGI_SFERA)
    cubo = bpy.data.objects[TESTI["NOME_CUBO"]]
    sfera = bpy.data.objects[TESTI["NOME_SFERA"]]
    cubo.location = (3.0, -2.0, 5.0)
    sfera.location = (-1.5, 4.0, 2.0)
    bpy.context.view_layer.update()

    esegui(comandi.ID_SCEGLI_OGGETTO, oggetto=cubo.name, modo="sostituisci")
    esito = esegui(comandi.ID_CENTRA)
    verifica("FINISHED" in esito, "Porta al centro viene eseguito")
    verifica(
        tuple(round(v, 6) for v in cubo.location) == (0.0, 0.0, 0.0),
        f"il cubo è al centro: {tuple(round(v, 3) for v in cubo.location)}",
    )
    verifica(
        tuple(sfera.location) == (-1.5, 4.0, 2.0),
        "Porta al centro non tocca gli oggetti non scelti",
    )
    verifica(
        messaggio() == TESTI["MESSAGGIO_CENTRATO"].format(nome=cubo.name),
        f"messaggio di centramento: {messaggio()}",
    )

    # Il blocco della posizione viene rispettato anche qui.
    sfera.lock_location = (False, True, True)
    esegui(comandi.ID_SCEGLI_OGGETTO, oggetto=sfera.name, modo="sostituisci")
    esito = esegui(comandi.ID_CENTRA)
    verifica("FINISHED" in esito, "il centramento con un asse bloccato riesce in parte")
    verifica(
        abs(sfera.location.x) < 1e-6 and sfera.location.y == 4.0,
        f"si centra solo l'asse libero: {tuple(round(v, 3) for v in sfera.location)}",
    )
    verifica(
        TESTI["AVVISO_TRASFORMAZIONE_PARZIALE"].format(numero=1) in messaggio()
        or TESTI["MESSAGGIO_CENTRATO"].format(nome=sfera.name) in messaggio(),
        f"il messaggio parla del risultato: {messaggio()}",
    )
    sfera.lock_location = (False, False, False)

    # Appoggia sul piano: la parte più bassa tocca lo zero.
    azzera_scena()
    esegui(comandi.ID_AGGIUNGI_SFERA)
    esegui(comandi.ID_AGGIUNGI_CONO)
    sfera2 = bpy.data.objects[TESTI["NOME_SFERA"]]
    cono = bpy.data.objects[TESTI["NOME_CONO"]]
    sfera2.location = (0.0, 0.0, 7.0)
    cono.location = (2.0, 0.0, -3.0)
    bpy.context.view_layer.update()
    esegui(comandi.ID_SCEGLI_TUTTO)
    esito = esegui(comandi.ID_APPOGGIA_SUL_PIANO)
    verifica("FINISHED" in esito, "Appoggia sul piano viene eseguito")
    bpy.context.view_layer.update()
    for oggetto in (sfera2, cono):
        angoli = [oggetto.matrix_world @ mathutils.Vector(a) for a in oggetto.bound_box]
        minimo = min(a.z for a in angoli)
        verifica(
            abs(minimo) < 1e-5,
            f"{oggetto.name} appoggia sul piano (quota più bassa {minimo:.6f})",
        )
        verifica(
            abs(oggetto.location.x - round(oggetto.location.x, 6)) < 1e-5,
            "appoggiare non sposta l'oggetto in orizzontale",
        )
    verifica(
        messaggio() == TESTI["MESSAGGIO_APPOGGIATI"].format(numero=2),
        f"messaggio di appoggio al plurale: {messaggio()}",
    )

    # Un oggetto senza forma propria si appoggia per il suo punto.
    esegui(comandi.ID_AGGIUNGI_LUCE)
    luce = bpy.data.objects[TESTI["NOME_LUCE"]]
    esegui(comandi.ID_SCEGLI_OGGETTO, oggetto=luce.name, modo="sostituisci")
    esito = esegui(comandi.ID_APPOGGIA_SUL_PIANO)
    verifica("FINISHED" in esito, "la luce si appoggia per il suo punto di riferimento")
    verifica(abs(luce.location.z) < 1e-6, "la luce finisce con il punto sul piano")
    verifica(
        TESTI["AVVISO_APPOGGIO_SENZA_FORMA"] in messaggio(),
        f"il messaggio spiega il caso senza forma: {messaggio()}",
    )


# --------------------------------------------- blocco della scelta, copia, incolla


def prova_blocco_copia() -> None:
    azzera_scena()
    esegui(comandi.ID_AGGIUNGI_CUBO)
    esegui(comandi.ID_AGGIUNGI_SFERA)
    cubo = bpy.data.objects[TESTI["NOME_CUBO"]]
    sfera = bpy.data.objects[TESTI["NOME_SFERA"]]

    esegui(comandi.ID_SCEGLI_OGGETTO, oggetto=cubo.name, modo="sostituisci")
    esito = esegui(comandi.ID_BLOCCA_SCELTA, oggetto=cubo.name, blocca=True)
    verifica("FINISHED" in esito, "Blocca la scelta viene eseguito")
    verifica(bool(cubo.hide_select), "l'oggetto è protetto dalla scelta")
    verifica(cubo.name not in scelti(), "un oggetto bloccato esce dalla scelta")
    verifica(
        bpy.context.view_layer.objects.active is None
        or bpy.context.view_layer.objects.active.name != cubo.name,
        "l'oggetto attivo non resta un oggetto bloccato",
    )
    verifica(
        messaggio() == TESTI["MESSAGGIO_SCELTA_BLOCCATA"].format(nome=cubo.name),
        f"messaggio di blocco: {messaggio()}",
    )

    esito = esegui(comandi.ID_SCEGLI_OGGETTO, oggetto=cubo.name, modo="sostituisci")
    verifica("CANCELLED" in esito, "un oggetto bloccato non si sceglie")

    esito = esegui(comandi.ID_BLOCCA_SCELTA, oggetto=cubo.name, blocca=False)
    verifica("FINISHED" in esito, "Sblocca la scelta viene eseguito")
    verifica(not bool(cubo.hide_select), "l'oggetto è di nuovo scegliibile")
    verifica(
        messaggio() == TESTI["MESSAGGIO_SCELTA_SBLOCCATA"].format(nome=cubo.name),
        f"messaggio di sblocco: {messaggio()}",
    )
    esegui(comandi.ID_SCEGLI_OGGETTO, oggetto=cubo.name, modo="sostituisci")
    verifica(cubo.name in scelti(), "dopo lo sblocco l'oggetto si sceglie di nuovo")

    # Copia e incolla usano gli appunti di Blender.
    svuota_appunti()
    esegui(comandi.ID_SCEGLI_OGGETTO, oggetto=sfera.name, modo="sostituisci")
    esito = esegui(comandi.ID_INCOLLA)
    verifica(
        esito is not None and "CANCELLED" in esito,
        "incollare senza aver copiato avvisa, in italiano",
    )
    verifica(
        messaggio() == TESTI["ERRORE_NIENTE_DA_INCOLLARE"],
        f"messaggio di appunti vuoti: {messaggio()}",
    )

    esito = esegui(comandi.ID_COPIA)
    verifica("FINISHED" in esito, "Copia viene eseguito con una Vista 3D")
    verifica(
        messaggio() == TESTI["MESSAGGIO_COPIATI"].format(numero=1),
        f"messaggio di copia: {messaggio()}",
    )

    quanti = len(bpy.context.scene.objects)
    esito = esegui(comandi.ID_INCOLLA)
    verifica("FINISHED" in esito, "Incolla viene eseguito")
    verifica(
        len(bpy.context.scene.objects) == quanti + 1,
        "l'incollato aggiunge un oggetto alla scena",
    )
    verifica(
        messaggio() == TESTI["MESSAGGIO_INCOLLATI"].format(numero=1),
        f"messaggio di incollato: {messaggio()}",
    )


# -------------------------------------------------------------------- maniglie


def prova_maniglie() -> None:
    """I pulsanti attivano gli strumenti nativi con le frecce della Vista 3D."""
    azzera_scena()
    esegui(comandi.ID_AGGIUNGI_CUBO)
    area = area_vista()
    verifica(area is not None, "il test ha una Vista 3D")

    attesi = (
        (comandi.ID_STRUMENTO_SPOSTA, configuration.STRUMENTO_SPOSTA),
        (comandi.ID_STRUMENTO_RUOTA, configuration.STRUMENTO_RUOTA),
        (comandi.ID_STRUMENTO_SCALA, configuration.STRUMENTO_SCALA),
    )
    spazio = area.spaces.active
    # Come farebbe chi aveva spento le maniglie: il comando deve riaccenderle.
    for nome in configuration.MOSTRA_MANIGLIE:
        if hasattr(spazio, nome):
            setattr(spazio, nome, False)

    for idname, strumento in attesi:
        esito = esegui(idname)
        verifica(esito is not None and "FINISHED" in esito, f"comando eseguito: {idname}")
        with contesto_area(area):
            verifica(
                bpy.context.workspace.tools.from_space_view3d_mode("OBJECT", create=False).idname
                == strumento,
                f"lo strumento attivo è {strumento}",
            )
        verifica(
            all(getattr(spazio, nome, True) for nome in configuration.MOSTRA_MANIGLIE),
            f"{idname} riaccende gli interruttori delle maniglie",
        )
    verifica(
        messaggio() == TESTI["MESSAGGIO_STRUMENTO_SCALA"],
        f"messaggio dello strumento: {messaggio()}",
    )

    # Senza una Vista 3D il comando avvisa e non fallisce.
    finto = type("ContestoFinto", (), {"window_manager": None, "window": None})()
    verifica(
        not servizio_vista.aree_vista_disponibili(finto),
        "senza finestre non ci sono viste 3D disponibili",
    )
    verifica(
        not servizio_vista.attiva_strumento(finto, configuration.STRUMENTO_SPOSTA),
        "senza Vista 3D lo strumento non si attiva, ma non cade",
    )


# --------------------------------------------------------------- campi numerici


def prova_campi_numerici() -> None:
    """I campi di posizione, rotazione e dimensione sono legati ai dati veri."""
    azzera_scena()
    esegui(comandi.ID_AGGIUNGI_CUBO)
    cubo = bpy.data.objects[TESTI["NOME_CUBO"]]

    registro = disegna_pannello(panel.FORMAFACILE_PT_oggetto)
    controlla_registro(registro, "oggetto (campi numerici)")
    campi = [prop for _tipo, prop in supporto_finto.campi(registro)]
    for previsto in ("location", "rotation_euler", "dimensions", configuration.CAMPO_PASSO):
        verifica(previsto in campi, f"il pannello mostra il campo {previsto}")
    verifica(
        supporto_finto.campi(registro).count(("Object", "location")) == 3,
        "la posizione ha tre campi, uno per asse",
    )

    # I campi sono davvero collegati: un valore scritto arriva all'oggetto.
    voci = [voce for voce in registro if voce["tipo"] == "campo" and voce["proprieta"] == "location"]
    verifica(len(voci) == 3, "tre campi posizione trovati nel disegno")
    verifica(
        all(voce["parametri"].get("index") == indice for indice, voce in enumerate(voci)),
        "ogni campo posizione porta l'indice del suo asse",
    )

    # Le etichette scrivono l'unità della scena, non una scelta fissa.
    etichette = supporto_finto.etichette(registro)
    verifica(
        TESTI["ETICHETTA_POSIZIONE"] + " (m)" in etichette,
        f"l'etichetta posizione porta i metri: {[e for e in etichette if 'Posizione' in e]}",
    )
    verifica(
        TESTI["ETICHETTA_ROTAZIONE"] + " (°)" in etichette,
        "l'etichetta rotazione porta i gradi",
    )

    bpy.context.scene.unit_settings.length_unit = "CENTIMETERS"
    registro = disegna_pannello(panel.FORMAFACILE_PT_oggetto)
    verifica(
        TESTI["ETICHETTA_POSIZIONE"] + " (cm)" in supporto_finto.etichette(registro),
        "cambiando l'unità della scena cambia l'etichetta",
    )
    bpy.context.scene.unit_settings.length_unit = "METERS"

    bpy.context.scene.unit_settings.system_rotation = "RADIANS"
    registro = disegna_pannello(panel.FORMAFACILE_PT_oggetto)
    verifica(
        TESTI["ETICHETTA_ROTAZIONE"] + " (rad)" in supporto_finto.etichette(registro),
        "con i radianti l'etichetta degli angoli cambia",
    )
    bpy.context.scene.unit_settings.system_rotation = "DEGREES"

    # La rotazione segue il modo dell'oggetto: un quaternione non ha tre angoli.
    cubo.rotation_mode = "QUATERNION"
    registro = disegna_pannello(panel.FORMAFACILE_PT_oggetto)
    proprieta = [prop for _tipo, prop in supporto_finto.campi(registro)]
    verifica(
        "rotation_quaternion" in proprieta and "rotation_euler" not in proprieta,
        "con un quaternione il campo è quello giusto",
    )
    cubo.rotation_mode = "XYZ"

    # La scritta ha i suoi campi, collegati ai dati del testo.
    azzera_scena()
    esegui(comandi.ID_AGGIUNGI_TESTO)
    testo = bpy.data.objects[TESTI["NOME_TESTO"]]
    registro = disegna_pannello(panel.FORMAFACILE_PT_oggetto)
    controlla_registro(registro, "oggetto (scritta)")
    proprieta = [prop for _tipo, prop in supporto_finto.campi(registro)]
    verifica("body" in proprieta, "il pannello mostra il campo della scritta")
    verifica("size" in proprieta, "il pannello mostra l'altezza della scritta")
    testo.data.body = "Ciao"
    bpy.context.view_layer.update()
    verifica(testo.data.body == "Ciao", "il campo della scritta è quello vero")

    # Con più oggetti scelti i numeri non compaiono: valgono per uno solo.
    azzera_scena()
    esegui(comandi.ID_AGGIUNGI_CUBO)
    esegui(comandi.ID_AGGIUNGI_SFERA)
    esegui(comandi.ID_SCEGLI_TUTTO)
    registro = disegna_pannello(panel.FORMAFACILE_PT_oggetto)
    proprieta = [prop for _tipo, prop in supporto_finto.campi(registro)]
    verifica(
        "location" not in proprieta and "dimensions" not in proprieta,
        "con più oggetti scelti i campi numerici non compaiono",
    )


# ----------------------------------------------------------------------- vista


def prova_vista() -> None:
    azzera_scena()
    esegui(comandi.ID_AGGIUNGI_CUBO)
    esegui(comandi.ID_AGGIUNGI_SFERA)
    area = area_vista()
    verifica(area is not None, "il test ha una Vista 3D")
    vista = regione_3d(area)

    # Si simula la confusione tipica: vista ruotata, ortogonale e spostata.
    vista.view_rotation = (1.0, 0.0, 0.0, 0.0)
    vista.view_perspective = "ORTHO"
    vista.view_location = (50.0, 50.0, 50.0)
    vista.view_distance = 60.0

    esito = esegui(comandi.ID_VISTA_INIZIALE)
    verifica("FINISHED" in esito, "Torna alla vista iniziale viene eseguito")
    attesa = servizio_vista.vista_iniziale(bpy.context.screen, 0)
    scarto = max(abs(vista.view_rotation[i] - attesa["rotazione"][i]) for i in range(4))
    verifica(scarto < 1e-5, f"rotazione riportata a quella di partenza (scarto {scarto:.6f})")
    verifica(
        vista.view_perspective == attesa["punto_di_vista"],
        f"tipo di vista ripristinato: {vista.view_perspective}",
    )
    verifica(
        vista.view_distance < 60.0 and abs(vista.view_location.x) < 8.0,
        f"la vista inquadra la scena: {tuple(round(v, 2) for v in vista.view_location)}",
    )
    verifica(
        messaggio() == TESTI["MESSAGGIO_VISTA_INIZIALE"],
        "messaggio dopo il ripristino della vista",
    )

    # Inquadratura di un singolo oggetto.
    cubo = bpy.data.objects[TESTI["NOME_CUBO"]]
    cubo.location = (12.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    angoli = [cubo.matrix_world @ mathutils.Vector(a) for a in cubo.bound_box]
    centro_atteso = sum(angoli, mathutils.Vector((0.0, 0.0, 0.0))) / 8.0
    raggio_atteso = max((angolo - centro_atteso).length for angolo in angoli)
    esito = esegui(comandi.ID_INQUADRA_OGGETTO, oggetto=cubo.name)
    verifica("FINISHED" in esito, "Inquadra l'oggetto viene eseguito")
    verifica(
        (vista.view_location - centro_atteso).length < 0.05,
        f"la vista si centra sull'oggetto: {tuple(round(v, 3) for v in vista.view_location)}",
    )
    verifica(
        abs(vista.view_distance - raggio_atteso * configuration.FATTORE_INQUADRATURA) < 0.05,
        f"la distanza è calcolata sull'oggetto: {vista.view_distance:.3f}",
    )
    verifica(
        messaggio() == TESTI["MESSAGGIO_INQUADRA_OGGETTO"].format(nome=cubo.name),
        "messaggio di inquadratura dell'oggetto",
    )

    esito = esegui(comandi.ID_INQUADRA_TUTTO)
    verifica("FINISHED" in esito, "Inquadra tutto viene eseguito")
    verifica(
        messaggio() == TESTI["MESSAGGIO_INQUADRA_TUTTO"],
        "messaggio di inquadratura di tutta la scena",
    )

    esegui(comandi.ID_SCEGLI_TUTTO)
    esito = esegui(comandi.ID_INQUADRA_SCELTI)
    verifica("FINISHED" in esito, "Inquadra la scelta viene eseguito")
    verifica(
        messaggio() == TESTI["MESSAGGIO_INQUADRA_SCELTI"],
        "messaggio di inquadratura degli oggetti scelti",
    )

    cubo.hide_viewport = True
    esito = esegui(comandi.ID_INQUADRA_OGGETTO, oggetto=cubo.name)
    verifica(esito is not None and "CANCELLED" in esito, "un oggetto nascosto non si inquadra")
    verifica(
        messaggio() == TESTI["ERRORE_INQUADRA_OGGETTO"],
        f"il messaggio spiega che l'oggetto è nascosto: {messaggio()}",
    )
    cubo.hide_viewport = False

    # Telecamera: la vista ci va e ci resta anche premendo due volte.
    bpy.ops.object.camera_add(location=(7.0, -7.0, 5.0))
    telecamera = bpy.context.view_layer.objects.active
    verifica(bpy.context.scene.camera is None, "all'inizio la scena non ha una telecamera principale")
    esito = esegui(comandi.ID_GUARDA_DA_CAMERA, oggetto=telecamera.name)
    verifica("FINISHED" in esito, "Guarda dalla telecamera viene eseguito")
    verifica(bpy.context.scene.camera is telecamera, "la telecamera diventa quella principale")
    verifica(vista.view_perspective == "CAMERA", "la vista passa alla telecamera")
    esito = esegui(comandi.ID_GUARDA_DA_CAMERA, oggetto=telecamera.name)
    verifica(
        "FINISHED" in esito and vista.view_perspective == "CAMERA",
        "premendo di nuovo si resta nella vista della telecamera",
    )
    verifica(
        messaggio() == TESTI["MESSAGGIO_GUARDA_DA_CAMERA"],
        "messaggio di vista dalla telecamera",
    )

    esegui(comandi.ID_VISTA_INIZIALE)
    verifica(
        vista.view_perspective == "PERSP",
        "Torna alla vista iniziale esce anche dalla vista della telecamera",
    )

    # Aprire la barra laterale con il pulsante della testata.
    with contesto_area(area):
        esito = bpy.ops.formafacile.apri_barra()
        verifica("FINISHED" in esito, "il pulsante della testata apre la barra laterale")
        verifica(area.spaces.active.show_region_ui is True, "la barra laterale è aperta")

    # La navigazione normale non è toccata: nessuna scorciatoia sostituita.
    for idname in servizio_vista.comandi_nativi_di_navigazione():
        modulo, _, nome = idname.partition(".")
        verifica(
            hasattr(getattr(bpy.ops, modulo, None), nome),
            f"il comando nativo {idname} esiste ancora",
        )
    with contesto_area(area):
        esito = bpy.ops.view3d.view_all()
        verifica("FINISHED" in esito, "la navigazione nativa view_all funziona")
        esito = bpy.ops.view3d.view_axis(type="FRONT")
        direzione = vista.view_rotation @ mathutils.Vector((0.0, 0.0, -1.0))
        verifica(
            "FINISHED" in esito and direzione.y > 0.9,
            f"la vista frontale nativa mostra la scena di fronte: {tuple(round(v, 2) for v in direzione)}",
        )

    verifica(
        servizio_vista.vista_iniziale(None, 0)["punto_di_vista"] == "PERSP",
        "senza schermo si usa la vista predefinita documentata",
    )
    verifica(
        servizio_vista.vista_iniziale(bpy.context.screen, 99) == servizio_vista._vista_predefinita(),
        "un indice fuori elenco ripiega sulla vista predefinita",
    )


# ------------------------------------------------------- disposizioni dei pannelli


def prova_disposizioni() -> None:
    """Le disposizioni dei pannelli cambiano: i comandi devono reggere."""
    azzera_scena()
    esegui(comandi.ID_AGGIUNGI_CUBO)

    registrate = servizio_vista.registra_viste_iniziali()
    attese = sum(
        1
        for disposizione in bpy.data.workspaces
        for schermo in disposizione.screens
        for area in schermo.areas
        if area.type == "VIEW_3D"
    )
    verifica(registrate >= 5, f"viste iniziali registrate per tutte le disposizioni: {registrate}")
    verifica(
        registrate == attese,
        f"viste registrate ({registrate}) e aree 3D disponibili ({attese}) coincidono",
    )

    disposizioni_senza_vista = 0
    for disposizione in bpy.data.workspaces:
        for schermo in disposizione.screens:
            aree = [area for area in schermo.areas if area.type == "VIEW_3D"]
            if not aree:
                disposizioni_senza_vista += 1
            for indice in range(len(aree)):
                valori = servizio_vista.vista_iniziale(schermo, indice)
                verifica(
                    valori["punto_di_vista"] in servizio_vista.PUNTI_DI_VISTA,
                    f"disposizione {disposizione.name}: vista valida anche per l'indice {indice}",
                )
    verifica(
        disposizioni_senza_vista >= 1,
        f"esistono disposizioni senza Vista 3D: {disposizioni_senza_vista} schermi",
    )

    # Disposizione senza Vista 3D: i comandi di vista devono solo avvisare.
    finto = type("ContestoFinto", (), {"window_manager": None, "window": None})()
    verifica(
        not servizio_vista.aree_vista_disponibili(finto),
        "senza finestre non ci sono viste 3D disponibili",
    )
    with_errore = None
    try:
        servizio_vista.torna_alla_vista_iniziale(finto)
    except servizio_vista.ErroreVista as errore:
        with_errore = str(errore)
    verifica(
        with_errore == TESTI["ERRORE_VISTA_INIZIALE"],
        f"senza Vista 3D il messaggio è chiaro: {with_errore}",
    )

    # Cambio di disposizione vero: si divide l'area in due viste 3D.
    area = area_vista()
    if area is not None and regione_di(area) is not None:
        with contesto_area(area):
            esito = bpy.ops.screen.area_split(direction="VERTICAL", factor=0.5)
        verifica("FINISHED" in esito, "la disposizione dei pannelli può cambiare")
        aree = [a for a in bpy.context.screen.areas if a.type == "VIEW_3D"]
        verifica(len(aree) >= 2, f"adesso ci sono {len(aree)} viste 3D")
        verifica(
            len(list(servizio_vista._aree_vista(bpy.context))) == len(aree),
            "il servizio di vista trova tutte le viste 3D della disposizione",
        )
        esito = esegui(comandi.ID_VISTA_INIZIALE)
        verifica("FINISHED" in esito, "Torna alla vista iniziale funziona anche con più viste 3D")
        verifica(
            servizio_vista.registra_viste_iniziali() >= len(aree),
            "le viste di partenza si possono registrare di nuovo dopo il cambio",
        )

        # Il ridimensionamento non deve dipendere dalla larghezza della barra:
        # nell'estensione non viene mai letta una misura in pixel.
        for modulo in (
            RADICE / "addon" / "formafacile_3d" / "ui" / "piano.py",
            RADICE / "addon" / "formafacile_3d" / "ui" / "panel.py",
            RADICE / "addon" / "formafacile_3d" / "ui" / "renderer.py",
            RADICE / "addon" / "formafacile_3d" / "ui" / "vista.py",
        ):
            sorgente = modulo.read_text(encoding="utf-8")
            verifica(
                "region.width" not in sorgente and "region.height" not in sorgente,
                f"{modulo.name} non dipende dalla larghezza della barra laterale",
            )


# ------------------------------------------------------------------- pannelli


def controlla_registro(registro: list[dict], nome_pannello: str) -> None:
    """Ogni chiamata al disegno deve esistere davvero nell'API di Blender."""
    for voce in registro:
        if voce["tipo"] == "proprieta":
            continue
        funzione = FUNZIONI_DI_DISEGNO[voce["tipo"]]
        ammessi = set(bpy.types.UILayout.bl_rna.functions[funzione].parameters.keys())
        for parametro in voce["parametri"]:
            verifica(
                parametro in ammessi,
                f"{nome_pannello}: UILayout.{funzione} accetta il parametro {parametro}",
            )
        if voce["tipo"] == "comando":
            idname = voce["idname"]
            modulo, _, nome = idname.partition(".")
            gruppo = getattr(bpy.ops, modulo, None)
            verifica(
                gruppo is not None and hasattr(gruppo, nome),
                f"{nome_pannello}: il comando {idname} esiste",
            )
            verifica(
                idname.startswith("formafacile.") or idname in IDENTIFICATORI_DICHIARATI,
                f"{nome_pannello}: {idname} è dichiarato nella tabella dei comandi",
            )
        if voce["tipo"] == "campo":
            verifica(
                voce["dati"] is not None,
                f"{nome_pannello}: il campo {voce['proprieta']} ha i dati collegati",
            )
            attuale = voce["dati"]
            for pezzo in str(voce["proprieta"]).split("."):
                verifica(
                    hasattr(attuale, pezzo),
                    f"{nome_pannello}: il dato {voce['proprieta']} esiste davvero",
                )
                attuale = getattr(attuale, pezzo)

    for testo in supporto_finto.etichette(registro) + supporto_finto.testi_comandi(registro):
        verifica(
            SEGNAPOSTO_INGLESE.search(testo) is None,
            f"{nome_pannello}: nessun segnaposto inglese nei testi ({testo})",
        )
    for nome_icona in supporto_finto.icone_usate(registro):
        verifica(
            nome_icona in icone.ICONE_USATE,
            f"{nome_pannello}: l'icona {nome_icona} è fra quelle verificate",
        )


def prova_pannelli() -> None:
    """I pannelli si disegnano e mostrano le cose giuste in ogni situazione."""
    azzera_scena()
    esegui(comandi.ID_AGGIUNGI_CUBO)
    esegui(comandi.ID_AGGIUNGI_SFERA)

    for chiave, classe in (
        ("principale", panel.FORMAFACILE_PT_principale),
        ("scena", panel.FORMAFACILE_PT_scena),
        ("libreria", panel.FORMAFACILE_PT_libreria),
        ("oggetto", panel.FORMAFACILE_PT_oggetto),
        ("modella", panel.FORMAFACILE_PT_modella),
    ):
        registro = disegna_pannello(classe)
        verifica(bool(registro), f"il pannello {chiave} disegna contenuti")
        controlla_registro(registro, chiave)

    # I titoli dei pannelli sono quelli italiani previsti.
    for classe, chiave_testo in (
        (panel.FORMAFACILE_PT_principale, "TITOLO_PANNELLO_PRINCIPALE"),
        (panel.FORMAFACILE_PT_scena, "TITOLO_PANNELLO_SCENA"),
        (panel.FORMAFACILE_PT_libreria, "TITOLO_PANNELLO_LIBRERIA"),
        (panel.FORMAFACILE_PT_oggetto, "TITOLO_PANNELLO_OGGETTO"),
        (panel.FORMAFACILE_PT_modella, "TITOLO_PANNELLO_MODELLA"),
        (panel.FORMAFACILE_PT_completo, "TITOLO_PANNELLO_COMPLETO"),
    ):
        verifica(
            classe.bl_label == TESTI[chiave_testo],
            f"titolo del pannello: {classe.bl_label}",
        )

    # La testata mostra un solo pulsante, quello che apre la barra.
    registro = disegna_pannello(panel.FORMAFACILE_HT_barra)
    verifica(
        supporto_finto.comandi(registro) == [comandi.ID_APRI_BARRA],
        "la testata aggiunge solo il pulsante FormaFacile",
    )

    # Modalità Semplice: i numeri sì, i campi tecnici no.
    bpy.context.scene.formafacile.modalita = configuration.MODALITA_SEMPLICE
    verifica(
        panel.FORMAFACILE_PT_completo.poll(bpy.context) is False,
        "in modalità Semplice i comandi tecnici sono nascosti",
    )
    registro = disegna_pannello(panel.FORMAFACILE_PT_oggetto)
    controlla_registro(registro, "oggetto (semplice)")
    campi = [proprieta for _tipo, proprieta in supporto_finto.campi(registro)]
    verifica(
        all(
            nome not in campi
            for nome in ("name", "scale", "display_type", "hide_render", "hide_select")
        ),
        f"in modalità Semplice non compaiono campi tecnici: {campi}",
    )
    for previsto in ("location", "rotation_euler", "dimensions"):
        verifica(
            previsto in campi,
            f"in modalità Semplice il campo numerico {previsto} resta a disposizione",
        )
    verifica(
        TESTI["GRUPPO_SPOSTA"] in supporto_finto.etichette(registro),
        "in modalità Semplice ci sono comunque i comandi di spostamento",
    )

    # Modalità Completa: compaiono i campi tecnici collegati ai dati veri.
    bpy.context.scene.formafacile.modalita = configuration.MODALITA_COMPLETA
    verifica(
        panel.FORMAFACILE_PT_completo.poll(bpy.context) is True,
        "in modalità Completa i comandi tecnici sono disponibili",
    )
    registro = disegna_pannello(panel.FORMAFACILE_PT_completo)
    controlla_registro(registro, "completo")
    campi = [proprieta for _tipo, proprieta in supporto_finto.campi(registro)]
    for proprieta in (
        "location",
        "rotation_mode",
        "rotation_euler",
        "scale",
        "display_type",
        "hide_select",
        "hide_render",
    ):
        verifica(proprieta in campi, f"il pannello tecnico mostra il campo {proprieta}")

    bpy.context.scene.formafacile.modalita = configuration.MODALITA_SEMPLICE
    registro = disegna_pannello(panel.FORMAFACILE_PT_principale)
    verifica(
        configuration.CAMPO_MODALITA
        in [proprieta for _tipo, proprieta in supporto_finto.campi(registro)],
        "il cambio di modalità è un campo del pannello principale",
    )

    # Adattamento al contesto: nessuna scelta, una scelta, più scelte.
    esegui(comandi.ID_DESCEGLI_TUTTO)
    registro = disegna_pannello(panel.FORMAFACILE_PT_oggetto)
    controlla_registro(registro, "oggetto (senza scelta)")
    verifica(
        TESTI["ETICHETTA_NESSUNA_SELEZIONE"] in supporto_finto.etichette(registro),
        "senza scelta il pannello spiega che non c'è nulla di scelto",
    )
    verifica(
        comandi.ID_SPOSTA_PASSO not in supporto_finto.comandi(registro),
        "senza scelta non compaiono i comandi di spostamento",
    )

    esegui(comandi.ID_SCEGLI_OGGETTO, oggetto=TESTI["NOME_CUBO"], modo="sostituisci")
    registro = disegna_pannello(panel.FORMAFACILE_PT_oggetto)
    controlla_registro(registro, "oggetto (una scelta)")
    verifica(
        supporto_finto.comandi(registro).count(comandi.ID_SPOSTA_PASSO) == 6,
        "con un oggetto scelto compaiono i sei spostamenti a passi",
    )
    verifica(
        TESTI["NOME_CUBO"] in supporto_finto.etichette(registro),
        "il pannello contestuale mostra il nome dell'oggetto scelto",
    )

    esegui(comandi.ID_SCEGLI_TUTTO)
    registro = disegna_pannello(panel.FORMAFACILE_PT_oggetto)
    controlla_registro(registro, "oggetto (più scelte)")
    verifica(
        TESTI["ETICHETTA_MULTI_SELEZIONE"].format(numero=2)
        in supporto_finto.etichette(registro),
        "con due oggetti scelti il pannello lo dice",
    )
    verifica(
        comandi.ID_ELIMINA in supporto_finto.comandi(registro)
        and comandi.ID_INQUADRA_SCELTI in supporto_finto.comandi(registro),
        "con più oggetti scelti compaiono i comandi di gruppo",
    )

    # Oggetto nascosto: la scelta di gruppo lo lascia fuori. Chi lo sceglie per
    # nome dall'elenco lo fa invece ricomparire, perché Blender non tiene scelto
    # un oggetto che non si vede.
    cubo = bpy.data.objects[TESTI["NOME_CUBO"]]
    nome_cubo = cubo.name
    cubo.hide_viewport = True
    bpy.context.view_layer.update()
    esegui(comandi.ID_SCEGLI_TUTTO)
    verifica(cubo.name not in scelti(), "la scelta di gruppo lascia fuori gli oggetti nascosti")
    registro = disegna_pannello(panel.FORMAFACILE_PT_scena)
    controlla_registro(registro, "scena (oggetto nascosto)")
    verifica(
        TESTI["AZIONE_MOSTRA_TUTTI"] in supporto_finto.testi_comandi(registro),
        "l'elenco propone di far ricomparire gli oggetti nascosti",
    )

    esito = esegui(comandi.ID_SCEGLI_OGGETTO, oggetto=nome_cubo, modo="sostituisci")
    verifica(
        "FINISHED" in esito and cubo.select_get(),
        "scegliere un oggetto nascosto dall'elenco lo sceglie davvero",
    )
    verifica(
        cubo.visible_get() and not cubo.hide_viewport,
        "e lo fa anche ricomparire, invece di lasciarlo invisibile",
    )
    verifica(
        messaggio() == TESTI["MESSAGGIO_SCELTO_MOSTRATO"].format(nome=nome_cubo),
        f"il messaggio dice che l'oggetto è di nuovo visibile: {messaggio()}",
    )

    # Anche un oggetto nascosto dalla sua raccolta resta fuori dalla scelta e
    # l'elenco lo segnala: il gruppo può tornare visibile in ogni momento.
    raccolta = bpy.data.collections.new("Gruppo di prova")
    bpy.context.scene.collection.children.link(raccolta)
    bpy.context.scene.collection.objects.unlink(cubo)
    raccolta.objects.link(cubo)
    raccolta.hide_viewport = True
    bpy.context.view_layer.update()
    contesto, _ = contesto_interfaccia()
    voce = next(o for o in contesto.oggetti if o.nome == nome_cubo)
    verifica(
        voce.nascosto and not voce.nascosto_direttamente,
        "il nascondimento fatto dal gruppo viene riconosciuto e distinto",
    )
    registro = disegna_pannello(panel.FORMAFACILE_PT_scena)
    controlla_registro(registro, "scena (gruppo nascosto)")
    verifica(
        TESTI["AZIONE_MOSTRA_TUTTI"] in supporto_finto.testi_comandi(registro),
        "il conteggio e l'elenco tengono conto degli oggetti nascosti dal gruppo",
    )
    raccolta.hide_viewport = False
    raccolta.objects.unlink(cubo)
    bpy.context.scene.collection.objects.link(cubo)
    bpy.context.view_layer.update()

    # Un oggetto bloccato non entra nella scelta: il pannello resta coerente.
    cubo.hide_select = True
    bpy.context.view_layer.update()
    cubo.select_set(True)
    esito = esegui(comandi.ID_SCEGLI_OGGETTO, oggetto=cubo.name, modo="sostituisci")
    verifica(
        esito is not None and "CANCELLED" in esito and not cubo.select_get(),
        "un oggetto bloccato non entra nella scelta",
    )
    cubo.hide_select = False
    bpy.context.view_layer.update()

    # Elenco lungo: limite, ricerca e conteggio.
    azzera_scena()
    for _ in range(16):
        esegui(comandi.ID_AGGIUNGI_SFERA)
    registro = disegna_pannello(panel.FORMAFACILE_PT_scena)
    controlla_registro(registro, "scena (elenco lungo)")
    campi = [proprieta for _tipo, proprieta in supporto_finto.campi(registro)]
    verifica(
        configuration.CAMPO_FILTRO in campi,
        f"con molti oggetti compare il campo di ricerca: {campi}",
    )
    quanti_scegli = supporto_finto.comandi(registro).count(comandi.ID_SCEGLI_OGGETTO)
    verifica(
        quanti_scegli == configuration.LIMITE_ELENCO_SEMPLICE,
        f"l'elenco è limitato a {configuration.LIMITE_ELENCO_SEMPLICE} righe: {quanti_scegli}",
    )
    verifica(
        TESTI["ETICHETTA_MANCANO_OGGETTI"].format(
            mostrati=configuration.LIMITE_ELENCO_SEMPLICE, totali=16
        )
        in supporto_finto.etichette(registro),
        "il pannello spiega che l'elenco è parziale",
    )

    bpy.context.scene.formafacile.filtro = "sfera.001"
    contesto, _ = contesto_interfaccia()
    verifica(len(contesto.filtrati()) == 1, "la ricerca trova un oggetto per nome, senza maiuscole")
    bpy.context.scene.formafacile.filtro = "inesistente-xyz"
    registro = disegna_pannello(panel.FORMAFACILE_PT_scena)
    controlla_registro(registro, "scena (ricerca vuota)")
    verifica(
        TESTI["ETICHETTA_FILTRO_VUOTO"] in supporto_finto.etichette(registro),
        "una ricerca senza risultati lo dice chiaramente",
    )
    esegui(comandi.ID_PULISCI_FILTRO)
    verifica(bpy.context.scene.formafacile.filtro == "", "Pulisci cancella la ricerca")

    # Messaggio recente e messaggio scaduto.
    azzera_scena()
    esegui(comandi.ID_AGGIUNGI_CUBO)
    registro = disegna_pannello(panel.FORMAFACILE_PT_principale)
    verifica(
        messaggio() in supporto_finto.etichette(registro),
        f"il messaggio recente compare nel pannello: {messaggio()}",
    )
    bpy.context.scene.formafacile.tempo_messaggio -= configuration.DURATA_MESSAGGIO + 1.0
    registro = disegna_pannello(panel.FORMAFACILE_PT_principale)
    verifica(
        messaggio() not in supporto_finto.etichette(registro),
        "un messaggio vecchio non compare più",
    )
    verifica(messaggio() != "", "il testo del messaggio resta salvato nello stato della scena")


def prova_testi_dei_comandi() -> None:
    """Etichette e descrizioni dei comandi arrivano dalla mappa centrale."""
    for classe in classi_registrate(bpy.types.Operator):
        with_errore = []
        if not classe.bl_label:
            with_errore.append("etichetta vuota")
        elif not testo_centralizzato(classe.bl_label):
            with_errore.append(f"etichetta non centralizzata: {classe.bl_label}")
        if not classe.bl_description:
            with_errore.append("descrizione vuota")
        elif not testo_centralizzato(classe.bl_description):
            with_errore.append(f"descrizione non centralizzata: {classe.bl_description}")
        if SEGNAPOSTO_INGLESE.search(classe.bl_label or ""):
            with_errore.append("etichetta in inglese")
        verifica(not with_errore, f"{classe.bl_idname}: {'; '.join(with_errore) or 'testi in italiano'}")

    for classe in classi_registrate(bpy.types.Panel):
        verifica(
            bool(getattr(classe, "bl_label", "")) and testo_centralizzato(classe.bl_label),
            f"titolo del pannello {classe.__name__}: {getattr(classe, 'bl_label', '')}",
        )


# --------------------------------------------------------------- messaggi e stato


def prova_messaggi() -> None:
    azzera_scena()
    esegui(comandi.ID_AGGIUNGI_CUBO)
    testo = messaggio()
    tempo = float(bpy.context.scene.formafacile.tempo_messaggio)
    verifica(bool(testo), "dopo un'azione c'è un messaggio di stato")
    verifica(messaggi.messaggio_attuale(testo, tempo), "il messaggio è attuale subito dopo")
    verifica(
        not messaggi.messaggio_attuale(testo, tempo, tempo + configuration.DURATA_MESSAGGIO + 1.0),
        "il messaggio scade dopo la durata prevista",
    )
    verifica(not messaggi.messaggio_attuale("", tempo), "un messaggio vuoto non è mai attuale")

    letto, recente = stato.messaggio_della_scena(bpy.context.scene)
    verifica(letto == testo and recente, "lo stato della scena riporta il messaggio appena scritto")
    verifica(
        stato.modalita_della_scena(None) == configuration.MODALITA_SEMPLICE,
        "senza scena la modalità di ripiego è Semplice",
    )
    verifica(
        stato.passo_della_scena(None) == configuration.PASSO_PREDEFINITO,
        "senza scena il passo di ripiego è quello predefinito",
    )
    verifica(
        not stato.messaggio_della_scena(None)[1],
        "senza scena non c'è nessun messaggio recente",
    )


# ------------------------------------------------------------------------ storia


def prova_storia() -> None:
    """Annulla e Ripeti richiamano la storia di Blender senza romperla."""
    azzera_scena()
    disponibile = False
    try:
        disponibile = bool(bpy.ops.ed.undo.poll())
    except RuntimeError:
        disponibile = False
    if not disponibile:
        # In modalità senza finestre la storia va inizializzata a mano.
        try:
            bpy.ops.ed.undo_push(message="prova FormaFacile")
            disponibile = bool(bpy.ops.ed.undo.poll())
        except RuntimeError:
            disponibile = False

    if disponibile:
        esegui(comandi.ID_AGGIUNGI_CUBO)
        verifica(len(bpy.context.scene.objects) == 1, "la scena ha l'oggetto appena creato")
        esito = esegui(comandi.ID_ANNULLA)
        verifica("FINISHED" in esito, "Annulla esegue l'annullamento di Blender")
        verifica(len(bpy.context.scene.objects) == 0, "Annulla toglie davvero l'oggetto")
        verifica(messaggio() == TESTI["MESSAGGIO_ANNULLA"], "messaggio di azione annullata")
        esito = esegui(comandi.ID_RIPETI)
        verifica("FINISHED" in esito, "Ripeti esegue la ripetizione di Blender")
        verifica(len(bpy.context.scene.objects) == 1, "Ripeti rimette l'oggetto annullato")
        verifica(messaggio() == TESTI["MESSAGGIO_RIPETI"], "messaggio di azione ripetuta")
    else:
        esito = esegui(comandi.ID_ANNULLA)
        verifica("CANCELLED" in esito, "senza storia disponibile Annulla non fa danni")
        verifica(
            messaggio() == TESTI["ERRORE_STORIA"],
            f"il messaggio spiega che la storia non è disponibile: {messaggio()}",
        )
        ESITI.append("storia non disponibile in questo ambiente: comportamento verificato")


# ----------------------------------------------------------------------- tabelle


def prova_tabelle() -> None:
    """Tabelle dei tipi, dei comandi e dei nomi: nessun buco."""
    for tipo in (
        "MESH",
        "LIGHT",
        "CAMERA",
        "EMPTY",
        "CURVE",
        "SURFACE",
        "FONT",
        "META",
        "ARMATURE",
        "LATTICE",
        "VOLUME",
        "SPEAKER",
        "GREASEPENCIL",
    ):
        verifica(bool(icone.icona_tipo(tipo)), f"icona definita per il tipo {tipo}")
        verifica(bool(icone.parola_tipo(tipo)), f"parola italiana definita per il tipo {tipo}")
        verifica(
            icone.icona_tipo(tipo) in icone.ICONE_USATE,
            f"l'icona del tipo {tipo} è nell'elenco verificato",
        )
    verifica(icone.parola_tipo("TIPO_INESISTENTE") == TESTI["TIPO_ALTRO"], "tipo ignoto: parola generica")
    verifica(icone.icona_tipo("TIPO_INESISTENTE") == "OBJECT_DATA", "tipo ignoto: icona generica")

    for direzione in comandi.DIREZIONI:
        verifica(
            comandi.TESTI_DIREZIONE[direzione] in TESTI
            and comandi.AIUTI_DIREZIONE[direzione] in TESTI,
            f"testi della direzione {direzione}",
        )
    for verso in comandi.VERSI_ROTAZIONE:
        verifica(
            comandi.TESTI_ROTAZIONE[verso] in TESTI and comandi.AIUTI_ROTAZIONE[verso] in TESTI,
            f"testi della rotazione {verso}",
        )
    for verso in comandi.VERSI_DIMENSIONE:
        verifica(
            comandi.TESTI_DIMENSIONE[verso] in TESTI and comandi.AIUTI_DIMENSIONE[verso] in TESTI,
            f"testi della dimensione {verso}",
        )
    verifica(
        set(comandi.VETTORI_DIREZIONE) == set(comandi.DIREZIONI),
        "ogni direzione ha il suo vettore di spostamento",
    )
    verifica(
        all(
            abs(sum(v * v for v in comandi.VETTORI_DIREZIONE[d])) - 1.0 < 1e-9
            for d in comandi.DIREZIONI
        ),
        "i vettori delle direzioni sono versori",
    )
    verifica(
        set(comandi.MODI_SCELTA) == {"sostituisci", "aggiungi", "rimuovi"},
        "i modi di scelta sono quelli usati dagli operatori",
    )
    verifica(
        set(comandi.ID_FORME) == {
            comandi.ID_AGGIUNGI_CUBO,
            comandi.ID_AGGIUNGI_SFERA,
            comandi.ID_AGGIUNGI_CILINDRO,
            comandi.ID_AGGIUNGI_CONO,
            comandi.ID_AGGIUNGI_PIANO,
            comandi.ID_AGGIUNGI_TORO,
            comandi.ID_AGGIUNGI_TESTO,
        },
        "l'elenco delle forme coincide con i comandi di creazione",
    )
    verifica(
        set(comandi.STRUMENTI)
        == {
            comandi.ID_STRUMENTO_SPOSTA,
            comandi.ID_STRUMENTO_RUOTA,
            comandi.ID_STRUMENTO_SCALA,
        },
        "la tabella degli strumenti ha i tre comandi con le maniglie",
    )
    for idname, (strumento, chiave_messaggio) in comandi.STRUMENTI.items():
        verifica(
            chiave_messaggio in TESTI and strumento.startswith("builtin."),
            f"lo strumento {idname} ha nome e messaggio validi",
        )
    # Gli interruttori delle maniglie vivono nelle proprietà RNA dello spazio
    # Vista 3D: sulla classe Python non compaiono con hasattr.
    proprieta_vista = {p.identifier for p in bpy.types.SpaceView3D.bl_rna.properties}
    for nome in configuration.MOSTRA_MANIGLIE:
        verifica(
            nome in proprieta_vista,
            f"l'interruttore delle maniglie esiste: {nome}",
        )

    verifica(nomi.pulisci_nome("  Doppio   spazio  ") == "Doppio spazio", "gli spazi doppi si stringono")
    verifica(nomi.pulisci_nome("\n\t") == "", "i soli ritorni a capo non fanno un nome")
    verifica(not nomi.nome_accettabile("   "), "un nome di soli spazi non è accettabile")
    verifica(
        len(nomi.pulisci_nome("y" * 200)) == configuration.LUNGHEZZA_MASSIMA_NOME,
        "i nomi troppo lunghi vengono troncati prima di arrivare a Blender",
    )
    verifica(
        primitives.DISTANZA_LIBERA > 0.0,
        "le forme nuove vengono messe a distanza di sicurezza dal cursore 3D",
    )


# ------------------------------------------------------------------------- avvio


# ------------------------------------------------------------ modellazione


def crea_oggetto(idname: str, **parametri: object):
    """Crea un oggetto con un comando di FormaFacile e restituisce l'attivo."""
    esegui(idname, **parametri)
    return bpy.context.view_layer.objects.active


def forma_di(oggetto):
    """Forma valutata dall'oggetto, con i modificatori non applicati."""
    return modificatori.forma_valutata(bpy.context, oggetto)


def prova_strumenti_guidati() -> None:
    """Gli strumenti guidati danno il risultato promesso o spiegano il rifiuto."""
    # ------------------------------------------------------------------ smusso
    azzera_scena()
    cubo = crea_oggetto(comandi.ID_AGGIUNGI_CUBO)
    vertici_prima = len(cubo.data.vertices)
    verifica(
        esegui(comandi.ID_AMMORBIDISCI_SPIGOLI) == {"FINISHED"},
        f"lo smusso riesce sul cubo: {messaggio()}",
    )
    verifica(
        [modificatori.tipo_di(m) for m in modificatori.elenca(cubo)] == ["BEVEL"],
        "lo smusso usa una modifica non applicata",
    )
    verifica(testo_centralizzato(messaggio()), f"messaggio dello smusso in italiano: {messaggio()}")
    verifica(
        len(cubo.data.vertices) == vertici_prima,
        "la forma di partenza resta quella creata",
    )
    verifica(forma_di(cubo).vertici > vertici_prima, "il risultato ha più vertici di prima")

    azzera_scena()
    sfera = crea_oggetto(comandi.ID_AGGIUNGI_SFERA)
    verifica(
        esegui(comandi.ID_AMMORBIDISCI_SPIGOLI) == {"CANCELLED"},
        "su una sfera senza spigoli lo smusso è rifiutato",
    )
    verifica(not modificatori.elenca(sfera), "rifiutando, non resta nessuna modifica")
    verifica(
        messaggio() == TESTI["ERRORE_SENZA_SPIGOLI"],
        f"la spiegazione dice perché: {messaggio()}",
    )

    azzera_scena()
    piano = crea_oggetto(comandi.ID_AGGIUNGI_PIANO)
    verifica(
        esegui(comandi.ID_AMMORBIDISCI_SPIGOLI) == {"CANCELLED"},
        "sul piano aperto lo smusso è rifiutato",
    )
    verifica(not modificatori.elenca(piano), "sul piano non resta nessuna modifica")

    azzera_scena()
    crea_oggetto(comandi.ID_AGGIUNGI_TESTO)
    verifica(
        esegui(comandi.ID_AMMORBIDISCI_SPIGOLI) == {"CANCELLED"},
        "su una scritta lo smusso è rifiutato",
    )
    verifica(
        messaggio() == TESTI["ERRORE_SERVE_FORMA"],
        f"per le scritte la spiegazione manda a Trasforma in forma: {messaggio()}",
    )

    azzera_scena()
    crea_oggetto(comandi.ID_AGGIUNGI_LUCE)
    verifica(
        esegui(comandi.ID_AMMORBIDISCI_SPIGOLI) == {"CANCELLED"},
        "su una luce lo smusso è rifiutato",
    )
    verifica(
        messaggio() == TESTI["ERRORE_SERVE_FORMA_ALTRO"],
        f"per gli oggetti non-forma la spiegazione è un'altra: {messaggio()}",
    )

    # --------------------------------------------------------------- superficie
    azzera_scena()
    cubo = crea_oggetto(comandi.ID_AGGIUNGI_CUBO)
    facce_prima = len(cubo.data.polygons)
    verifica(
        esegui(comandi.ID_SUPERFICIE_LISCIA) == {"FINISHED"},
        f"la superficie si mostra liscia: {messaggio()}",
    )
    verifica(modificatori.e_liscia(cubo), "dopo il comando la superficie è liscia")
    verifica(
        not modificatori.elenca(cubo),
        "mostrare liscia cambia solo l'aspetto: nessuna modifica da applicare",
    )
    verifica(
        len(cubo.data.polygons) == facce_prima,
        "mostrare liscia non aggiunge facce alla forma",
    )
    verifica(
        esegui(comandi.ID_SUPERFICIE_A_FACCE) == {"FINISHED"},
        f"la superficie torna a facce: {messaggio()}",
    )
    verifica(not modificatori.e_liscia(cubo), "dopo il comando la superficie è a facce")
    verifica(
        esegui(comandi.ID_SUPERFICIE_A_FACCE) == {"FINISHED"},
        "ripetere lo stesso aspetto non è un errore",
    )
    verifica(
        messaggio() == TESTI["MESSAGGIO_SUPERFICIE_INVARIATA"],
        f"ripetendo, il comando lo dice invece di fingere: {messaggio()}",
    )

    # ------------------------------------------------------- forma più arrotondata
    azzera_scena()
    cubo = crea_oggetto(comandi.ID_AGGIUNGI_CUBO)
    verifica(
        esegui(comandi.ID_FORMA_PIU_LISCIA, livelli=1) == {"FINISHED"},
        f"la forma diventa più arrotondata: {messaggio()}",
    )
    verifica(
        [modificatori.tipo_di(m) for m in modificatori.elenca(cubo)] == ["SUBSURF"],
        "l'arrotondamento è una modifica non applicata",
    )
    verifica(int(cubo.modifiers[0].levels) == 1, "il livello richiesto è quello applicato")
    verifica(
        esegui(comandi.ID_FORMA_PIU_LISCIA, livelli=2) == {"FINISHED"},
        "si può chiedere una forma più arrotondata",
    )
    verifica(
        len(modificatori.elenca(cubo)) == 1,
        "chiedere più arrotondato non impila due modifiche",
    )
    verifica(int(cubo.modifiers[0].levels) == 2, "il livello sale invece di raddoppiare")
    verifica(
        esegui(comandi.ID_FORMA_PIU_LISCIA, livelli=2) == {"FINISHED"},
        "chiedere lo stesso livello non è un errore",
    )
    verifica(
        messaggio() == TESTI["MESSAGGIO_FORMA_LISCIA_GIA"],
        f"se la forma è già così, il comando lo dice: {messaggio()}",
    )
    verifica(
        len(cubo.data.vertices) == 8 and len(cubo.data.polygons) == 6,
        "la forma di partenza resta il cubo di sei facce",
    )
    verifica(forma_di(cubo).facce > 6, "il risultato mostra più facce della forma di partenza")

    # ---------------------------------------------------------------- specchio
    azzera_scena()
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
    cubo = crea_oggetto(comandi.ID_AGGIUNGI_CUBO)
    cubo.location = (1.0, 0.0, 0.0)
    vertici_prima = forma_di(cubo).vertici
    verifica(
        esegui(comandi.ID_SPECCHIA, asse="x") == {"FINISHED"},
        f"la forma si rispecchia: {messaggio()}",
    )
    segnaposto = bpy.data.objects.get(TESTI["NOME_SPECCHIO"])
    verifica(
        segnaposto is not None and segnaposto.type == "EMPTY",
        "il piano dello specchio è un segnaposto visibile nella scena",
    )
    verifica(
        len(modificatori.elenca(cubo)) == 1
        and modificatori.tipo_di(cubo.modifiers[0]) == "MIRROR",
        "lo specchio è una modifica non applicata",
    )
    verifica(
        cubo.modifiers[0].mirror_object is segnaposto,
        "la modifica specchia rispetto al segnaposto, che si può spostare",
    )
    verifica(forma_di(cubo).vertici > vertici_prima, "il risultato aggiunge il lato opposto")
    verifica(
        round(float(forma_di(cubo).minimo[0]), 3) < -0.5,
        "il lato nuovo compare dall'altra parte del piano",
    )

    azzera_scena()
    cubo = crea_oggetto(comandi.ID_AGGIUNGI_CUBO)
    verifica(
        esegui(comandi.ID_SPECCHIA, asse="x") == {"CANCELLED"},
        "una forma già a cavallo dello specchio non si specchia",
    )
    verifica(not modificatori.elenca(cubo), "rifiutando, non resta nessuna modifica")
    verifica(
        messaggio() == TESTI["ERRORE_SPECCHIO_SIMMETRICA"],
        f"la spiegazione dice cosa fare: {messaggio()}",
    )

    # ------------------------------------------------------------- ripetizione
    azzera_scena()
    cubo = crea_oggetto(comandi.ID_AGGIUNGI_CUBO)
    verifica(
        esegui(comandi.ID_RIPETI_COPIE, modo="fila", quante=4, distanza=1.0, asse="y")
        == {"FINISHED"},
        f"le copie si mettono in fila: {messaggio()}",
    )
    verifica(
        [modificatori.tipo_di(m) for m in modificatori.elenca(cubo)] == ["ARRAY"],
        "la fila è una modifica non applicata, regolabile dopo",
    )
    fila = cubo.modifiers[0]
    verifica(int(fila.count) == 4, "la fila contiene le forme richieste")
    verifica(
        tuple(round(float(v), 3) for v in fila.constant_offset_displace) == (0.0, 1.0, 0.0),
        "le copie distano quanto richiesto lungo l'asse scelto",
    )
    verifica(len(bpy.data.objects) == 1, "la fila resta un oggetto solo")

    azzera_scena()
    crea_oggetto(comandi.ID_AGGIUNGI_CUBO)
    verifica(
        esegui(comandi.ID_RIPETI_COPIE, modo="cerchio", quante=4, distanza=2.0, centro="scena")
        == {"FINISHED"},
        f"le copie si mettono in cerchio: {messaggio()}",
    )
    verifica(
        len(bpy.data.objects) == 4,
        f"il giro crea le copie attorno all'originale: {nomi_scena()}",
    )
    distanze = [
        round(math.hypot(float(o.location[0]), float(o.location[1])), 3)
        for o in bpy.data.objects
    ]
    verifica(
        len(set(distanze)) == 1 and abs(distanze[0] - 2.0) < 1e-6,
        f"tutte le forme del giro stanno alla distanza richiesta dal centro: {distanze}",
    )

    # ------------------------------------------------------------------ spessore
    azzera_scena()
    piano = crea_oggetto(comandi.ID_AGGIUNGI_PIANO)
    verifica(
        esegui(comandi.ID_SPESSORE_PARETE, spessore=0.2) == {"FINISHED"},
        f"il piano diventa una parete: {messaggio()}",
    )
    verifica(
        [modificatori.tipo_di(m) for m in modificatori.elenca(piano)] == ["SOLIDIFY"],
        "lo spessore è una modifica non applicata",
    )
    verifica(forma_di(piano).vertici > 4, "il risultato ha due facce invece di una")
    verifica(
        round(float(piano.modifiers[0].thickness), 3) == 0.2,
        "lo spessore richiesto è quello applicato",
    )
    verifica(
        len(piano.data.vertices) == 4,
        "la superficie di partenza resta quella creata",
    )

    azzera_scena()
    crea_oggetto(comandi.ID_AGGIUNGI_CUBO)
    verifica(
        esegui(comandi.ID_SPESSORE_PARETE, spessore=0.2) == {"FINISHED"},
        "anche una forma chiusa accetta lo spessore",
    )
    verifica(
        TESTI["AVVISO_SPESSORE_FORMA_CHIUSA"] in messaggio(),
        f"su una forma chiusa il comando avvisa: {messaggio()}",
    )

    # -------------------------------------------------------------- unire e tagliare
    azzera_scena()
    cubo = crea_oggetto(comandi.ID_AGGIUNGI_CUBO)
    sfera = crea_oggetto(comandi.ID_AGGIUNGI_SFERA)
    sfera.location = (0.7, 0.0, 0.0)
    esegui(comandi.ID_SCEGLI_TUTTO)
    bpy.context.view_layer.objects.active = cubo
    verifica(
        esegui(comandi.ID_UNISCI_FORME, operazione=comandi.OPERAZIONE_UNIONE) == {"FINISHED"},
        f"due forme scelte si uniscono: {messaggio()}",
    )
    booleana = cubo.modifiers[0]
    verifica(
        modificatori.tipo_di(booleana) == "BOOLEAN",
        "l'unione è una modifica non applicata",
    )
    verifica(
        booleana.object is sfera,
        "l'oggetto attivo è la forma principale e l'altro è l'attrezzo",
    )
    verifica(
        str(booleana.operation) == comandi.OPERAZIONI_BLENDER[comandi.OPERAZIONE_UNIONE],
        "l'operazione applicata è quella richiesta",
    )
    verifica(
        not sfera.visible_get() and bool(sfera.hide_viewport),
        "l'attrezzo resta nella scena ma non si vede",
    )
    verifica(sfera.name in nomi_scena(), "l'attrezzo non viene eliminato")
    verifica(len(cubo.data.polygons) == 6, "la forma principale resta quella creata")

    # Tre forme scelte tutte visibili: il comando non sa quale sarebbe l'attrezzo.
    azzera_scena()
    crea_oggetto(comandi.ID_AGGIUNGI_CUBO)
    crea_oggetto(comandi.ID_AGGIUNGI_SFERA)
    crea_oggetto(comandi.ID_AGGIUNGI_CONO)
    esegui(comandi.ID_SCEGLI_TUTTO)
    verifica(
        esegui(comandi.ID_UNISCI_FORME) == {"CANCELLED"},
        "con tre forme scelte l'unione è rifiutata",
    )
    verifica(
        messaggio() == TESTI["ERRORE_UNISCI_TROPPI"],
        f"la spiegazione dice quante forme servono: {messaggio()}",
    )

    azzera_scena()
    cubo = crea_oggetto(comandi.ID_AGGIUNGI_CUBO)
    piano = crea_oggetto(comandi.ID_AGGIUNGI_PIANO)
    piano.location = (0.0, 0.0, 0.5)
    esegui(comandi.ID_SCEGLI_TUTTO)
    bpy.context.view_layer.objects.active = cubo
    verifica(
        esegui(comandi.ID_UNISCI_FORME, operazione=comandi.OPERAZIONE_DIFFERENZA)
        == {"CANCELLED"},
        "un piano aperto non può fare da attrezzo per un taglio",
    )
    verifica(
        messaggio() == TESTI["ERRORE_UNISCI_ATTREZZO_APERTO"],
        f"la spiegazione dice perché: {messaggio()}",
    )
    verifica(not modificatori.elenca(cubo), "il taglio rifiutato non lascia modifiche")

    # -------------------------------------------------------------- conversione
    azzera_scena()
    scritta = crea_oggetto(comandi.ID_AGGIUNGI_TESTO)
    verifica(
        esegui(comandi.ID_CONVERTI_IN_FORMA) == {"FINISHED"},
        f"una scritta diventa una forma: {messaggio()}",
    )
    verifica(scritta.type == "MESH", "dopo il comando l'oggetto è una forma (mesh)")
    verifica(len(scritta.data.polygons) > 0, "la forma convertita ha facce vere")
    verifica(
        esegui(comandi.ID_CONVERTI_IN_FORMA) == {"CANCELLED"},
        "una forma già pronta non si riconverte",
    )
    verifica(
        messaggio() == TESTI["ERRORE_CONVERTI_NIENTE"],
        f"la spiegazione lo dice: {messaggio()}",
    )

    # ------------------------------------------------------ allineare e spaziare
    azzera_scena()
    cubi = []
    for posizione in ((0.0, 0.0, 0.0), (2.0, 0.0, 0.0), (8.0, 0.0, 0.0)):
        cubo = crea_oggetto(comandi.ID_AGGIUNGI_CUBO)
        cubo.location = posizione
        cubi.append(cubo)
    esegui(comandi.ID_SCEGLI_TUTTO)
    verifica(esegui(comandi.ID_SPAZIA) == {"FINISHED"}, f"la spaziatura riesce: {messaggio()}")
    riquadri = allineamento.riquadri(bpy.context, cubi)
    spazi = [
        round(float(riquadri[i + 1][0][0]) - float(riquadri[i][1][0]), 3)
        for i in range(len(riquadri) - 1)
    ]
    verifica(
        len(set(spazi)) == 1 and spazi[0] > 0.0,
        f"dopo la spaziatura c'è sempre lo stesso spazio fra le forme: {spazi}",
    )

    bpy.context.scene.formafacile.asse_allinea = "z"
    bpy.context.scene.formafacile.bordo_allinea = comandi.MODO_ALLINEA_INIZIO
    for indice, cubo in enumerate(cubi):
        cubo.location = (float(indice) * 4.0, 0.0, float(indice))
    verifica(esegui(comandi.ID_ALLINEA) == {"FINISHED"}, f"l'allineamento riesce: {messaggio()}")
    basi = [
        round(float(allineamento.riquadri(bpy.context, [cubo])[0][0][2]), 3) for cubo in cubi
    ]
    verifica(
        len(set(basi)) == 1,
        f"allineando sul bordo di partenza le basi finiscono allo stesso livello: {basi}",
    )

    esegui(comandi.ID_SCEGLI_OGGETTO, oggetto=cubi[0].name, modo="sostituisci")
    verifica(
        esegui(comandi.ID_SPAZIA) == {"CANCELLED"},
        "con una sola forma scelta non si spazia",
    )
    verifica(
        messaggio() == TESTI["ERRORE_SPAZIA_POCHI"],
        f"la spiegazione dice quante forme servono: {messaggio()}",
    )


def prova_gruppi() -> None:
    """I gruppi si scelgono, si nascondono e si sciolgono; le modifiche si tolgono."""
    azzera_scena()
    cubo = crea_oggetto(comandi.ID_AGGIUNGI_CUBO)
    sfera = crea_oggetto(comandi.ID_AGGIUNGI_SFERA)
    esegui(comandi.ID_SCEGLI_TUTTO)

    nome = TESTI["NOME_CASETTA_GRUPPO"]
    verifica(esegui(comandi.ID_RAGGRUPPA, nome=nome) == {"FINISHED"}, f"il gruppo nasce: {messaggio()}")
    gruppi = raccolte.gruppi(bpy.context.scene)
    verifica(
        [gruppo.nome for gruppo in gruppi] == [nome],
        f"il gruppo compare nell'elenco: {[g.nome for g in gruppi]}",
    )
    verifica(gruppi[0].quanti == 2, f"il gruppo conta le forme raggruppate: {gruppi[0].quanti}")
    verifica(
        raccolte.gruppo_di(cubo) == nome and raccolte.gruppo_di(sfera) == nome,
        "entrambe le forme sono passate nel gruppo",
    )
    verifica(testo_centralizzato(messaggio()), f"messaggio del gruppo in italiano: {messaggio()}")

    esegui(comandi.ID_DESCEGLI_TUTTO)
    verifica(
        esegui(comandi.ID_SCEGLI_GRUPPO, gruppo=nome) == {"FINISHED"},
        f"il gruppo si sceglie tutto insieme: {messaggio()}",
    )
    verifica(
        scelti() == sorted([cubo.name, sfera.name]),
        f"la scelta del gruppo prende le sue forme: {scelti()}",
    )

    verifica(
        esegui(comandi.ID_ALTERNA_GRUPPO, gruppo=nome) == {"FINISHED"},
        f"il gruppo si nasconde: {messaggio()}",
    )
    verifica(
        not cubo.visible_get() and not sfera.visible_get(),
        "nascosto, il gruppo non si vede più",
    )
    verifica(
        esegui(comandi.ID_ALTERNA_GRUPPO, gruppo=nome) == {"FINISHED"},
        "il gruppo si rimostra",
    )
    verifica(cubo.visible_get() and sfera.visible_get(), "mostrato, il gruppo si rivede")

    esegui(comandi.ID_SCEGLI_GRUPPO, gruppo=nome)
    verifica(
        esegui(comandi.ID_TOGLI_DAL_GRUPPO) == {"FINISHED"},
        f"le forme escono dal gruppo: {messaggio()}",
    )
    verifica(raccolte.gruppo_di(cubo) != nome, "dopo il comando la forma non è più nel gruppo")

    verifica(
        esegui(comandi.ID_SCEGLI_GRUPPO, gruppo="non-esiste") == {"CANCELLED"},
        "un gruppo che non esiste non si sceglie",
    )
    verifica(
        messaggio() == TESTI["ERRORE_GRUPPO_ASSENTE"],
        f"la spiegazione dice che non c'è più: {messaggio()}",
    )

    # ------------------------------------------- modifiche non applicate nel pannello
    azzera_scena()
    cubo = crea_oggetto(comandi.ID_AGGIUNGI_CUBO)
    esegui(comandi.ID_AMMORBIDISCI_SPIGOLI)
    esegui(comandi.ID_FORMA_PIU_LISCIA, livelli=1)
    nomi_elenco = [modificatori.nome_di(m) for m in modificatori.elenca(cubo)]
    verifica(len(nomi_elenco) == 2, f"il cubo ha due modifiche non applicate: {nomi_elenco}")

    contesto, _risolutore = contesto_interfaccia()
    verifica(
        [modifica.chiave for modifica in contesto.modificatori] == nomi_elenco,
        "il pannello legge le modifiche dell'oggetto attivo",
    )
    verifica(
        all(modifica.parola and modifica.icona for modifica in contesto.modificatori),
        "ogni modifica ha una parola italiana e un'icona",
    )

    esegui(comandi.ID_SCEGLI_TUTTO)
    verifica(
        esegui(comandi.ID_TOGLI_MODIFICHE, modificatore=nomi_elenco[1]) == {"FINISHED"},
        f"si può togliere una modifica sola: {messaggio()}",
    )
    verifica(
        messaggio() == TESTI["MESSAGGIO_MODIFICA_TOLTA"],
        f"togliendo una modifica sola il messaggio è al singolare: {messaggio()}",
    )
    verifica(
        [modificatori.nome_di(m) for m in modificatori.elenca(cubo)] == [nomi_elenco[0]],
        "è sparita solo la modifica indicata",
    )
    verifica(
        esegui(comandi.ID_TOGLI_MODIFICHE) == {"FINISHED"},
        f"si tolgono tutte le modifiche rimaste: {messaggio()}",
    )
    verifica(not modificatori.elenca(cubo), "dopo il comando non resta nessuna modifica")
    verifica(
        esegui(comandi.ID_TOGLI_MODIFICHE) == {"FINISHED"},
        "togliere quando non c'è nulla non è un errore",
    )
    verifica(
        messaggio() == TESTI["MESSAGGIO_MODIFICHE_NESSUNA"],
        f"senza modifiche il comando lo dice: {messaggio()}",
    )

    azzera_scena()
    creato = crea_oggetto(comandi.ID_AGGIUNGI_CUBO)
    creato.location = (1.0, 0.0, 0.0)
    esegui(comandi.ID_SPECCHIA, asse="x")
    creato.modifiers[0].mirror_object = None
    contesto, _risolutore = contesto_interfaccia()
    verifica(
        bool(contesto.modificatori)
        and contesto.modificatori[0].problema == TESTI["AVVISO_SPECCHIO_SENZA_CENTRO"],
        "lo specchio senza segnaposto viene segnalato nel pannello",
    )


def prova_guida() -> None:
    """La guida della casetta: comandi veri, risultato in piedi, fine ordinata."""
    azzera_scena()
    stato_scena = bpy.context.scene.formafacile
    chiave = configuration.GUIDA_PRINCIPALE
    corrente = guide.guida(chiave)
    verifica(
        corrente is not None and bool(corrente.passi),
        "la guida della casetta esiste e ha dei passi",
    )

    verifica(
        esegui(comandi.ID_GUIDA_APRI, guida=chiave) == {"FINISHED"},
        f"la guida si apre: {messaggio()}",
    )
    verifica(
        stato_scena.guida == chiave and int(stato_scena.passo_guida) == 0,
        "la guida parte dal primo passo",
    )
    verifica(
        messaggio() == TESTI["MESSAGGIO_GUIDA_INIZIO"].format(totale=len(corrente.passi)),
        f"il messaggio dice quanti passi ci sono: {messaggio()}",
    )

    for indice, passo in enumerate(corrente.passi):
        verifica(
            int(stato_scena.passo_guida) == indice,
            f"prima del passo {indice + 1} l'indice è quello giusto",
        )
        verifica(
            esegui(comandi.ID_GUIDA_ESEGUI) == {"FINISHED"},
            f"il passo «{TESTI[passo.titolo]}» riesce: {messaggio()}",
        )
    verifica(
        int(stato_scena.passo_guida) == len(corrente.passi),
        "dopo l'ultimo passo la guida risulta finita",
    )
    verifica(
        messaggio() == TESTI["MESSAGGIO_GUIDA_FINE"],
        f"a fine guida il messaggio lo dice: {messaggio()}",
    )

    verifica(
        esegui(comandi.ID_GUIDA_ESEGUI) == {"CANCELLED"},
        "una guida finita non esegue altri passi",
    )
    verifica(
        messaggio() == TESTI["ERRORE_GUIDA_FINITA"],
        f"la spiegazione dice di chiuderla: {messaggio()}",
    )
    verifica(
        len(bpy.data.objects) == 3,
        f"la scena ha solo le tre forme della casetta, senza doppioni: {nomi_scena()}",
    )

    corpo = bpy.data.objects.get(TESTI["NOME_CASETTA_CORPO"])
    tetto = bpy.data.objects.get(TESTI["NOME_CASETTA_TETTO"])
    camino = bpy.data.objects.get(TESTI["NOME_CASETTA_CAMINO"])
    for oggetto, nome in ((corpo, "Corpo"), (tetto, "Tetto"), (camino, "Camino")):
        verifica(oggetto is not None, f"la guida ha creato {nome}")
        verifica(oggetto.type == "MESH", f"{nome} è una forma")

    verifica(
        [modificatori.tipo_di(m) for m in modificatori.elenca(corpo)] == ["BOOLEAN"],
        "il tetto è unito al corpo con una modifica non applicata",
    )
    verifica(corpo.modifiers[0].object is tetto, "la modifica unisce il corpo e il tetto")
    verifica(
        not tetto.visible_get(),
        "la forma usata per unire resta nella scena ma non si vede",
    )
    verifica(tetto.name in nomi_scena(), "la forma usata per unire non viene eliminata")

    riquadro_corpo = allineamento.riquadri(bpy.context, [corpo])[0]
    riquadro_tetto = allineamento.riquadri(bpy.context, [tetto])[0]
    riquadro_camino = allineamento.riquadri(bpy.context, [camino])[0]
    verifica(
        round(float(riquadro_corpo[0][2]), 2) == 0.0,
        f"la casa appoggia sul pavimento: base a {round(float(riquadro_corpo[0][2]), 2)}",
    )
    verifica(
        round(float(riquadro_corpo[1][2]), 3) > round(float(riquadro_tetto[0][2]), 3),
        "la casa unita è più alta della sola base su cui poggia il tetto",
    )
    verifica(
        float(riquadro_camino[1][2]) > float(riquadro_tetto[0][2]),
        "il camino arriva sopra la base del tetto, non resta per terra",
    )
    verifica(
        float(riquadro_camino[0][2]) >= 0.0,
        "il camino non sprofonda sotto il pavimento",
    )

    gruppi = raccolte.gruppi(bpy.context.scene)
    verifica(
        [gruppo.nome for gruppo in gruppi] == [TESTI["NOME_CASETTA_GRUPPO"]],
        f"alla fine la casetta è un gruppo solo: {[g.nome for g in gruppi]}",
    )
    verifica(
        gruppi[0].quanti == 2,
        f"il gruppo raccoglie la casa e il camino, non l'attrezzo: {gruppi[0].quanti}",
    )

    esegui(comandi.ID_GUIDA_NAVIGA, modo=comandi.MODO_GUIDA_INDIETRO)
    verifica(
        int(stato_scena.passo_guida) == len(corrente.passi) - 1,
        "Indietro torna all'ultimo passo, per rileggerlo",
    )
    esegui(comandi.ID_GUIDA_NAVIGA, modo=comandi.MODO_GUIDA_AVANTI)
    verifica(
        int(stato_scena.passo_guida) == len(corrente.passi),
        "Avanti riporta a fine guida senza duplicare nulla",
    )

    registro = disegna_pannello(panel.FORMAFACILE_PT_modella)
    controlla_registro(registro, "modella (guida finita)")
    verifica(
        TESTI["ETICHETTA_GUIDA_FINITA"] in supporto_finto.etichette(registro),
        "il pannello dice che la guida è arrivata in fondo",
    )
    verifica(
        comandi.ID_GUIDA_ESEGUI not in supporto_finto.comandi(registro),
        "a guida finita il pannello non propone di eseguire altri passi",
    )

    verifica(
        esegui(comandi.ID_GUIDA_NAVIGA, modo=comandi.MODO_GUIDA_CHIUDI) == {"FINISHED"},
        f"la guida si chiude: {messaggio()}",
    )
    verifica(
        stato_scena.guida == "" and int(stato_scena.passo_guida) == 0,
        "chiusa la guida, lo stato torna vuoto",
    )
    verifica(
        esegui(comandi.ID_GUIDA_ESEGUI) == {"CANCELLED"},
        "senza guida aperta non si esegue nessun passo",
    )
    verifica(
        esegui(comandi.ID_GUIDA_APRI, guida="non-esiste") == {"CANCELLED"},
        "una guida che non esiste non si apre",
    )
    verifica(
        messaggio() == TESTI["ERRORE_GUIDA_ASSENTE"],
        f"la spiegazione dice che non è disponibile: {messaggio()}",
    )


def main() -> int:
    azzera_scena()
    try:
        prova_registrazione()
        prova_creazione()
        prova_libreria_asset()
        prova_scelta()
        prova_rinomina()
        prova_visibilita()
        prova_trasformazioni()
        prova_duplica_elimina()
        prova_posizioni()
        prova_blocco_copia()
        prova_maniglie()
        prova_campi_numerici()
        prova_vista()
        prova_disposizioni()
        prova_pannelli()
        prova_strumenti_guidati()
        prova_gruppi()
        prova_guida()
        prova_testi_dei_comandi()
        prova_messaggi()
        prova_storia()
        prova_tabelle()
    finally:
        componente.unregister()
        componente.unregister()

    print(f"Test Blender superato: {len(ESITI)} verifiche.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
