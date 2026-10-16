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

# Strumenti guidati di modellazione (pannello "Dai forma").
ID_AMMORBIDISCI_SPIGOLI = "formafacile.ammorbidisci_spigoli"
ID_SUPERFICIE_LISCIA = "formafacile.superficie_liscia"
ID_SUPERFICIE_A_FACCE = "formafacile.superficie_a_facce"
ID_FORMA_PIU_LISCIA = "formafacile.forma_piu_liscia"
ID_SPECCHIA = "formafacile.specchia"
ID_RIPETI_COPIE = "formafacile.ripeti_copie"
ID_SPESSORE_PARETE = "formafacile.spessore_parete"
ID_UNISCI_FORME = "formafacile.unisci_forme"
ID_CONVERTI_IN_FORMA = "formafacile.converti_in_forma"
ID_ALLINEA = "formafacile.allinea"
ID_SPAZIA = "formafacile.spazia"
ID_RAGGRUPPA = "formafacile.raggruppa"
ID_SCEGLI_GRUPPO = "formafacile.scegli_gruppo"
ID_ALTERNA_GRUPPO = "formafacile.alterna_gruppo"
ID_TOGLI_DAL_GRUPPO = "formafacile.togli_dal_gruppo"
ID_TOGLI_MODIFICHE = "formafacile.togli_modifiche"

# Guida passo passo.
ID_GUIDA_APRI = "formafacile.guida_apri"
ID_GUIDA_ESEGUI = "formafacile.guida_esegui"
ID_GUIDA_NAVIGA = "formafacile.guida_naviga"

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

# Assi su cui si specchia o si ripete una forma.
ASSI = ("x", "y", "z")
TESTI_ASSE = {"x": "ASSE_X", "y": "ASSE_Y", "z": "ASSE_Z"}
AIUTI_ASSE = {"x": "AIUTO_ASSE_X", "y": "AIUTO_ASSE_Y", "z": "AIUTO_ASSE_Z"}

# Modi della ripetizione: in fila oppure in cerchio.
MODO_RIPETI_FILA = "fila"
MODO_RIPETI_CERCHIO = "cerchio"
MODI_RIPETIZIONE = (MODO_RIPETI_FILA, MODO_RIPETI_CERCHIO)
TESTI_RIPETIZIONE = {
    MODO_RIPETI_FILA: "AZIONE_RIPETI_FILA",
    MODO_RIPETI_CERCHIO: "AZIONE_RIPETI_CERCHIO",
}
AIUTI_RIPETIZIONE = {
    MODO_RIPETI_FILA: "AIUTO_RIPETI_FILA",
    MODO_RIPETI_CERCHIO: "AIUTO_RIPETI_CERCHIO",
}

# Centro del giro: il cursore 3D oppure il centro della scena.
CENTRO_CURSORE = "cursore"
CENTRO_SCENA = "scena"
CENTRI_RIPETIZIONE = (CENTRO_CURSORE, CENTRO_SCENA)
TESTI_CENTRO = {CENTRO_CURSORE: "AZIONE_CENTRO_CURSORE", CENTRO_SCENA: "AZIONE_CENTRO_SCENA"}

# Verso dello spessore: verso l'interno oppure verso l'esterno della forma.
VERSO_DENTRO = "dentro"
VERSO_FUORI = "fuori"
VERSI_SPESSORE = (VERSO_DENTRO, VERSO_FUORI)
TESTI_SPESSORE = {VERSO_DENTRO: "AZIONE_SPESSORE_DENTRO", VERSO_FUORI: "AZIONE_SPESSORE_FUORI"}

# Operazioni fra forme: i nomi sono quelli semplici del pannello, i valori
# tecnici sono quelli accettati da Blender.
OPERAZIONE_UNIONE = "unione"
OPERAZIONE_DIFFERENZA = "differenza"
OPERAZIONE_INTERSEZIONE = "intersezione"
OPERAZIONI_BOOLEANE = (OPERAZIONE_UNIONE, OPERAZIONE_DIFFERENZA, OPERAZIONE_INTERSEZIONE)
OPERAZIONI_BLENDER = {
    OPERAZIONE_UNIONE: "UNION",
    OPERAZIONE_DIFFERENZA: "DIFFERENCE",
    OPERAZIONE_INTERSEZIONE: "INTERSECT",
}
TESTI_OPERAZIONE = {
    OPERAZIONE_UNIONE: "AZIONE_UNISCI",
    OPERAZIONE_DIFFERENZA: "AZIONE_TAGLIA",
    OPERAZIONE_INTERSEZIONE: "AZIONE_INCROCIA",
}
AIUTI_OPERAZIONE = {
    OPERAZIONE_UNIONE: "AIUTO_UNISCI",
    OPERAZIONE_DIFFERENZA: "AIUTO_TAGLIA",
    OPERAZIONE_INTERSEZIONE: "AIUTO_INCROCIA",
}
ICONE_OPERAZIONE = {
    OPERAZIONE_UNIONE: "MOD_BOOLEAN",
    OPERAZIONE_DIFFERENZA: "MOD_BOOLEAN",
    OPERAZIONE_INTERSEZIONE: "MOD_BOOLEAN",
}

# Modi dell'allineamento: dove si attaccano gli oggetti scelti.
MODO_ALLINEA_INIZIO = "inizio"
MODO_ALLINEA_CENTRO = "centro"
MODO_ALLINEA_FINE = "fine"
MODI_ALLINEAMENTO = (MODO_ALLINEA_INIZIO, MODO_ALLINEA_CENTRO, MODO_ALLINEA_FINE)
TESTI_ALLINEAMENTO = {
    MODO_ALLINEA_INIZIO: "AZIONE_ALLINEA_INIZIO",
    MODO_ALLINEA_CENTRO: "AZIONE_ALLINEA_CENTRO",
    MODO_ALLINEA_FINE: "AZIONE_ALLINEA_FINE",
}

# Riferimento dell'allineamento: il bordo della forma oppure il suo punto di
# riferimento (quello che Blender chiama origine).
RIFERIMENTO_BORDO = "bordo"
RIFERIMENTO_PUNTO = "punto"
RIFERIMENTI_ALLINEAMENTO = (RIFERIMENTO_BORDO, RIFERIMENTO_PUNTO)
TESTI_RIFERIMENTO = {RIFERIMENTO_BORDO: "AZIONE_RIFERIMENTO_BORDO", RIFERIMENTO_PUNTO: "AZIONE_RIFERIMENTO_PUNTO"}

# Navigazione della guida passo passo.
MODO_GUIDA_AVANTI = "avanti"
MODO_GUIDA_INDIETRO = "indietro"
MODO_GUIDA_CHIUDI = "chiudi"
MODI_GUIDA = (MODO_GUIDA_AVANTI, MODO_GUIDA_INDIETRO, MODO_GUIDA_CHIUDI)
TESTI_GUIDA = {
    MODO_GUIDA_AVANTI: "AZIONE_GUIDA_AVANTI",
    MODO_GUIDA_INDIETRO: "AZIONE_GUIDA_INDIETRO",
    MODO_GUIDA_CHIUDI: "AZIONE_GUIDA_CHIUDI",
}

# Strumenti guidati, nell'ordine in cui compaiono nel pannello: servono ai
# controlli automatici.
ID_STRUMENTI_GUIDATI = (
    ID_AMMORBIDISCI_SPIGOLI,
    ID_SUPERFICIE_LISCIA,
    ID_SUPERFICIE_A_FACCE,
    ID_FORMA_PIU_LISCIA,
    ID_SPECCHIA,
    ID_RIPETI_COPIE,
    ID_SPESSORE_PARETE,
    ID_UNISCI_FORME,
    ID_CONVERTI_IN_FORMA,
    ID_ALLINEA,
    ID_SPAZIA,
    ID_RAGGRUPPA,
    ID_SCEGLI_GRUPPO,
    ID_ALTERNA_GRUPPO,
    ID_TOGLI_DAL_GRUPPO,
    ID_TOGLI_MODIFICHE,
)

# Comandi della guida, nell'ordine in cui compaiono nel pannello.
ID_GUIDA = (ID_GUIDA_APRI, ID_GUIDA_ESEGUI, ID_GUIDA_NAVIGA)

# Comandi dei gruppi e delle modifiche non applicate, nell'ordine del pannello.
ID_GRUPPI = (
    ID_RAGGRUPPA,
    ID_SCEGLI_GRUPPO,
    ID_ALTERNA_GRUPPO,
    ID_TOGLI_DAL_GRUPPO,
    ID_TOGLI_MODIFICHE,
)

# Icona di ogni strumento guidato: sono nomi di icone verificate su Blender.
ICONE_STRUMENTI_GUIDATI = {
    ID_AMMORBIDISCI_SPIGOLI: "MOD_BEVEL",
    ID_SUPERFICIE_LISCIA: "MOD_SMOOTH",
    ID_SUPERFICIE_A_FACCE: "NORMALS_FACE",
    ID_FORMA_PIU_LISCIA: "MOD_SUBSURF",
    ID_SPECCHIA: "MOD_MIRROR",
    ID_RIPETI_COPIE: "MOD_ARRAY",
    ID_SPESSORE_PARETE: "MOD_SOLIDIFY",
    ID_UNISCI_FORME: "MOD_BOOLEAN",
    ID_CONVERTI_IN_FORMA: "MESH_DATA",
    ID_ALLINEA: "ALIGN_LEFT",
    ID_SPAZIA: "SORT_ASC",
    ID_RAGGRUPPA: "GROUP",
    ID_SCEGLI_GRUPPO: "OUTLINER_COLLECTION",
    ID_ALTERNA_GRUPPO: "HIDE_OFF",
    ID_TOGLI_DAL_GRUPPO: "UNLINKED",
    ID_TOGLI_MODIFICHE: "MODIFIER",
}

# Comando nativo richiamato da ogni strumento con le maniglie, e messaggio
# mostrato quando le frecce sono attive.
STRUMENTI = {
    ID_STRUMENTO_SPOSTA: ("builtin.move", "MESSAGGIO_STRUMENTO_SPOSTA"),
    ID_STRUMENTO_RUOTA: ("builtin.rotate", "MESSAGGIO_STRUMENTO_RUOTA"),
    ID_STRUMENTO_SCALA: ("builtin.scale", "MESSAGGIO_STRUMENTO_SCALA"),
}
