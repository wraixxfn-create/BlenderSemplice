"""Identificatori e valori condivisi fra interfaccia e comandi.

Questo modulo non dipende da Blender: è l'unico punto in cui sono scritti i
nomi dei comandi e i valori degli enumerati. Interfaccia, operatori e test
leggono tutti da qui, così un refuso viene individuato subito.
"""

from __future__ import annotations

# Creazione di oggetti.
ID_AGGIUNGI_CUBO = "formafacile.aggiungi_cubo"
ID_AGGIUNGI_SFERA = "formafacile.aggiungi_sfera"
ID_AGGIUNGI_CILINDRO = "formafacile.aggiungi_cilindro"
ID_AGGIUNGI_CONO = "formafacile.aggiungi_cono"
ID_AGGIUNGI_PIANO = "formafacile.aggiungi_piano"
ID_AGGIUNGI_TORO = "formafacile.aggiungi_toro"
ID_AGGIUNGI_TESTO = "formafacile.aggiungi_testo"
ID_AGGIUNGI_LUCE = "formafacile.aggiungi_luce"

# Scelta degli oggetti.
ID_SCEGLI_TUTTO = "formafacile.scegli_tutto"
ID_DESCEGLI_TUTTO = "formafacile.descegli_tutto"
ID_INVERTI_SCELTA = "formafacile.inverti_scelta"
ID_SCEGLI_STESSO_TIPO = "formafacile.scegli_stesso_tipo"
ID_SCEGLI_OGGETTO = "formafacile.scegli_oggetto"
ID_ALTERNA_SCELTA = "formafacile.alterna_scelta"

# Azioni sugli oggetti.
ID_RINOMINA = "formafacile.rinomina"
ID_DUPLICA = "formafacile.duplica"
ID_ELIMINA = "formafacile.elimina"
ID_ALTERNA_VISIBILITA = "formafacile.alterna_visibilita"
ID_MOSTRA_TUTTI = "formafacile.mostra_tutti"
ID_INQUADRA_OGGETTO = "formafacile.inquadra_oggetto"
ID_INQUADRA_SCELTI = "formafacile.inquadra_scelti"
ID_CENTRA = "formafacile.centra"
ID_APPOGGIA_SUL_PIANO = "formafacile.appoggia_sul_piano"
ID_BLOCCA_SCELTA = "formafacile.blocca_scelta"
ID_COPIA = "formafacile.copia"
ID_INCOLLA = "formafacile.incolla"

# Strumenti con le maniglie nella Vista 3D (frecce, archi e cubetti).
ID_STRUMENTO_SPOSTA = "formafacile.strumento_sposta"
ID_STRUMENTO_RUOTA = "formafacile.strumento_ruota"
ID_STRUMENTO_SCALA = "formafacile.strumento_scala"

# Trasformazioni a passi.
ID_SPOSTA_PASSO = "formafacile.sposta_passo"
ID_RUOTA_PASSO = "formafacile.ruota_passo"
ID_SCALA_PASSO = "formafacile.scala_passo"

# Comandi nativi di Blender usati per muovere con il mouse.
ID_MOUSE_SPOSTA = "transform.translate"
ID_MOUSE_RUOTA = "transform.rotate"
ID_MOUSE_INGRANDISCI = "transform.resize"

# Luce e telecamera.
ID_LUCE_PIU = "formafacile.luce_piu"
ID_LUCE_MENO = "formafacile.luce_meno"
ID_GUARDA_DA_CAMERA = "formafacile.guarda_da_camera"
ID_TELECAMERA_PRINCIPALE = "formafacile.telecamera_principale"

# Storia e vista.
ID_ANNULLA = "formafacile.annulla"
ID_RIPETI = "formafacile.ripeti"
ID_VISTA_INIZIALE = "formafacile.vista_iniziale"
ID_INQUADRA_TUTTO = "formafacile.inquadra_tutto"
ID_PULISCI_FILTRO = "formafacile.pulisci_filtro"
ID_APRI_BARRA = "formafacile.apri_barra"

# Nomi dei comandi nativi richiamati dagli operatori.
ID_NATIVO_VIEW_ALL = "view3d.view_all"
ID_NATIVO_VIEW_SELECTED = "view3d.view_selected"
ID_NATIVO_VIEW_CAMERA = "view3d.view_camera"
ID_NATIVO_VIEW_CENTER_CAMERA = "view3d.view_center_camera"
ID_NATIVO_ANNULLA = "ed.undo"
ID_NATIVO_RIPETI = "ed.redo"
ID_NATIVO_STRUMENTO = "wm.tool_set_by_id"
ID_NATIVO_COPIA = "view3d.copybuffer"
ID_NATIVO_INCOLLA = "view3d.pastebuffer"
ID_NATIVO_ANNULLA_SPINTA = "ed.undo_push"

# Direzioni dei passi: valori, etichette e spostamenti sugli assi.
DIREZIONI = ("sinistra", "destra", "su", "giu", "avanti", "indietro")
VETTORI_DIREZIONE = {
    "sinistra": (-1.0, 0.0, 0.0),
    "destra": (1.0, 0.0, 0.0),
    "su": (0.0, 0.0, 1.0),
    "giu": (0.0, 0.0, -1.0),
    "avanti": (0.0, -1.0, 0.0),
    "indietro": (0.0, 1.0, 0.0),
}
TESTI_DIREZIONE = {
    "sinistra": "AZIONE_VERSO_SINISTRA",
    "destra": "AZIONE_VERSO_DESTRA",
    "su": "AZIONE_VERSO_SU",
    "giu": "AZIONE_VERSO_GIU",
    "avanti": "AZIONE_VERSO_AVANTI",
    "indietro": "AZIONE_VERSO_INDIETRO",
}
AIUTI_DIREZIONE = {
    "sinistra": "AIUTO_VERSO_SINISTRA",
    "destra": "AIUTO_VERSO_DESTRA",
    "su": "AIUTO_VERSO_SU",
    "giu": "AIUTO_VERSO_GIU",
    "avanti": "AIUTO_VERSO_AVANTI",
    "indietro": "AIUTO_VERSO_INDIETRO",
}

# Versi di rotazione (senso antiorario oppure orario).
VERSI_ROTAZIONE = ("sinistra", "destra")
SEGNI_ROTAZIONE = {"sinistra": 1.0, "destra": -1.0}
TESTI_ROTAZIONE = {"sinistra": "AZIONE_RUOTA_SINISTRA", "destra": "AZIONE_RUOTA_DESTRA"}
AIUTI_ROTAZIONE = {"sinistra": "AIUTO_RUOTA_SINISTRA", "destra": "AIUTO_RUOTA_DESTRA"}

# Versi della dimensione.
VERSI_DIMENSIONE = ("grande", "piccolo")
TESTI_DIMENSIONE = {"grande": "AZIONE_PIU_GRANDE", "piccolo": "AZIONE_PIU_PICCOLO"}
AIUTI_DIMENSIONE = {"grande": "AIUTO_PIU_GRANDE", "piccolo": "AIUTO_PIU_PICCOLO"}

# Modi di scelta di un singolo oggetto dall'elenco.
MODI_SCELTA = ("sostituisci", "aggiungi", "rimuovi")

# Nomi dei comandi di creazione, nell'ordine in cui compaiono nel pannello.
# Servono ai controlli automatici: ogni forma promessa deve esistere davvero.
ID_FORME = (
    ID_AGGIUNGI_CUBO,
    ID_AGGIUNGI_SFERA,
    ID_AGGIUNGI_CILINDRO,
    ID_AGGIUNGI_CONO,
    ID_AGGIUNGI_PIANO,
    ID_AGGIUNGI_TORO,
    ID_AGGIUNGI_TESTO,
)

# Comando nativo richiamato da ogni strumento con le maniglie, e messaggio
# mostrato quando le frecce sono attive.
STRUMENTI = {
    ID_STRUMENTO_SPOSTA: ("builtin.move", "MESSAGGIO_STRUMENTO_SPOSTA"),
    ID_STRUMENTO_RUOTA: ("builtin.rotate", "MESSAGGIO_STRUMENTO_RUOTA"),
    ID_STRUMENTO_SCALA: ("builtin.scale", "MESSAGGIO_STRUMENTO_SCALA"),
}
