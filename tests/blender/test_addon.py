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
from formafacile_3d.blender import oggetti as servizio_oggetti  # noqa: E402
from formafacile_3d.blender import selezione, vista as servizio_vista  # noqa: E402
from formafacile_3d.localization import TESTI  # noqa: E402
from formafacile_3d.scene import messaggi, nomi, primitives, stato  # noqa: E402
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
        pezzi = re.split(r"\{[a-z_]+\}", re.escape(valore))
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
    verifica(len(pannelli) == 4, f"pannelli registrati: {len(pannelli)}")
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
        (comandi.ID_AGGIUNGI_PIANO, TESTI["NOME_PIANO"], TESTI["NOME_MESH_PIANO"]),
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
        ("oggetto", panel.FORMAFACILE_PT_oggetto),
    ):
        registro = disegna_pannello(classe)
        verifica(bool(registro), f"il pannello {chiave} disegna contenuti")
        controlla_registro(registro, chiave)

    # I titoli dei pannelli sono quelli italiani previsti.
    for classe, chiave_testo in (
        (panel.FORMAFACILE_PT_principale, "TITOLO_PANNELLO_PRINCIPALE"),
        (panel.FORMAFACILE_PT_scena, "TITOLO_PANNELLO_SCENA"),
        (panel.FORMAFACILE_PT_oggetto, "TITOLO_PANNELLO_OGGETTO"),
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

    # Modalità Semplice: niente campi tecnici sull'oggetto.
    bpy.context.scene.formafacile.modalita = configuration.MODALITA_SEMPLICE
    verifica(
        panel.FORMAFACILE_PT_completo.poll(bpy.context) is False,
        "in modalità Semplice i comandi tecnici sono nascosti",
    )
    registro = disegna_pannello(panel.FORMAFACILE_PT_oggetto)
    controlla_registro(registro, "oggetto (semplice)")
    campi = [proprieta for _tipo, proprieta in supporto_finto.campi(registro)]
    verifica(
        all(nome not in campi for nome in ("location", "scale", "display_type", "hide_render")),
        f"in modalità Semplice non compaiono campi tecnici: {campi}",
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


def main() -> int:
    azzera_scena()
    try:
        prova_registrazione()
        prova_creazione()
        prova_scelta()
        prova_rinomina()
        prova_visibilita()
        prova_trasformazioni()
        prova_duplica_elimina()
        prova_vista()
        prova_disposizioni()
        prova_pannelli()
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
