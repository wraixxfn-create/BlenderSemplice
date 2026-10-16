"""Impostazioni sicure e compatte del componente aggiuntivo."""

from __future__ import annotations

LINGUA_PREDEFINITA = "it_IT"

# Modalità di lavoro mostrate all'utente.
MODALITA_SEMPLICE = "semplice"
MODALITA_COMPLETA = "completa"

# Durata dei messaggi di stato brevi, in secondi.
DURATA_MESSAGGIO = 8.0

# Valori dei comandi a passi: metri, gradi e fattore di ingrandimento.
PASSO_PREDEFINITO = 0.5
PASSO_MINIMO = 0.01
PASSO_MASSIMO = 100.0
ANGOLO_PREDEFINITO_GRADI = 15.0
FATTORE_SCALA_PREDEFINITO = 1.1
FATTORE_LUCE = 1.5
POTENZA_LUCE_MINIMA = 0.01

# Grandezza delle nuove forme, in metri: il lato più lungo dell'oggetto.
# Con 2 metri un cubo, una sfera, un cilindro e un cono nuovi sono larghi
# esattamente come quelli di Blender, quindi chi conosce già Blender non trova
# sorprese e chi inizia ha subito qualcosa di ben visibile.
DIMENSIONE_FORMA_PREDEFINITA = 2.0
DIMENSIONE_FORMA_MINIMA = 0.05
DIMENSIONE_FORMA_MASSIMA = 100.0

# Il testo usa metà della grandezza come altezza della scritta: con il valore
# predefinito si ottiene l'altezza standard di Blender, un metro.
FATTORE_ALTEZZA_TESTO = 0.5

# Altezza a cui viene messa una nuova luce, sopra il cursore 3D.
ALTEZZA_LUCE = 4.0

# Strumenti nativi di Blender che mostrano le frecce nella Vista 3D.
# Sono gli stessi della barra degli strumenti: attivarli è il modo pubblico per
# far comparire le maniglie di spostamento, rotazione e dimensione.
STRUMENTO_SPOSTA = "builtin.move"
STRUMENTO_RUOTA = "builtin.rotate"
STRUMENTO_SCALA = "builtin.scale"

# Interruttori della Vista 3D che rendono visibili le maniglie. Vengono accesi
# insieme allo strumento: se l'utente li aveva spenti, le frecce non si vedono.
MOSTRA_MANIGLIE = (
    "show_gizmo",
    "show_gizmo_context",
    "show_gizmo_object_translate",
    "show_gizmo_object_rotate",
    "show_gizmo_object_scale",
)

# Dimensione minima di un oggetto: sotto questa soglia le forme diventano
# invisibili e difficili da riprendere, quindi il comando avvisa e non applica.
SCALA_MINIMA = 0.01

# Strumenti guidati di modellazione. Ogni valore ha un limite prudente: gli
# strumenti lavorano su forme appena create, non su modelli complessi, e un
# valore esagerato rovinerebbe la forma invece di migliorarla.
SMUSSO_FORZA_PREDEFINITA = 3
SMUSSO_FORZA_MINIMA = 1
SMUSSO_FORZA_MASSIMA = 5
# Raggio dello smusso: una frazione della dimensione più piccola della forma,
# mai oltre un quinto, così lo spigolo si ammorbidisce senza sparire.
SMUSSO_RAPPORTO_PER_FORZA = 0.04
SMUSSO_RAPPORTO_MASSIMO = 0.20
SMUSSO_RAGGIO_MINIMO = 0.001
SMUSSO_SEGMENTI_MASSIMI = 6
SMUSSO_ANGOLO_PREDEFINITO_GRADI = 30.0

# Superficie: i livelli di suddivisione moltiplicano le facce per quattro
# ognuno, quindi oltre il terzo livello una forma semplice diventa pesante.
LISCIO_LIVELLI_PREDEFINITI = 2
LISCIO_LIVELLI_MASSIMI = 3
LISCIO_FACCE_MASSIME = 200_000
SIMIL_LISCIO_LIVELLI_PREDEFINITI = 1

# Specchio: asse predefinito e tolleranza con cui si riconosce una forma già
# simmetrica (sotto questa distanza i due lati si considerano uguali).
SPECCHIO_ASSE_PREDEFINITO = "x"
SPECCHIO_TOLLERANZA = 1e-4

# Ripetizione: quante copie e a che distanza.
RIPETI_COPIE_PREDEFINITE = 4
RIPETI_COPIE_MINIME = 2
RIPETI_COPIE_MASSIME = 50
RIPETI_SPAZIATURA_MINIMA = 0.01
RIPETI_SPAZIATURA_MASSIMA = 100.0
RIPETI_DISTANZA_PREDEFINITA = 1.0
RIPETI_MODO_PREDEFINITO = "fila"
RIPETI_ASSE_PREDEFINITO = "y"
# Centro del giro: il cursore 3D è il punto di riferimento che FormaFacile usa
# già per creare gli oggetti; il centro della scena resta come alternativa.
RIPETI_CENTRO_PREDEFINITO = "cursore"

# Spessore della parete: una frazione della dimensione più piccola, per non
# far collassare la forma su se stessa.
SPESSORE_RAPPORTO_PREDEFINITO = 0.10
SPESSORE_RAPPORTO_MASSIMO = 0.40
SPESSORE_MINIMO = 0.005
SPESSORE_VERSO_PREDEFINITO = "dentro"

# Unione e taglio: il risolutore esatto è quello che gestisce i casi normali
# (forme che si toccano, si sovrappongono o si attraversano).
BOOLEANA_SOLVER = "EXACT"
# Quante facce può avere al massimo il risultato di un'unione o di un taglio:
# oltre questa soglia il comando si ferma invece di bloccare Blender.
BOOLEANA_FACCE_MASSIME = 500_000

# Allineamento e spaziatura.
ALLINEA_ASSE_PREDEFINITO = "x"
ALLINEA_BORDO_PREDEFINITO = "inizio"
ALLINEA_RIFERIMENTO_PREDEFINITO = "bordo"
ALLINEA_OGGETTI_MINIMI = 2
# Unione e taglio lavorano su due forme: la principale (l'attiva) e l'attrezzo.
UNISCI_OGGETTI_ESATTI = 2
SPAZIA_OGGETTI_MINIMI = 3
# Tolleranza con cui due bordi si considerano già allineati o già spaziati.
ALLINEA_TOLLERANZA = 1e-6

# Gruppi: prefisso dei nomi creati e numero massimo di gruppi mostrati.
GRUPPO_NOME_BASE = "Gruppo"
GRUPPO_LIMITE_ELENCO = 8
GRUPPO_OGGETTI_MINIMI = 1

# Guida passo passo.
GUIDA_PRINCIPALE = "casetta"

# Dimensioni dell'elenco oggetti: evita pannelli lentissimi con scene grandi.
LIMITE_ELENCO_SEMPLICE = 12
LIMITE_ELENCO_COMPLETA = 24
SOGLIA_FILTRO = 8

# Lunghezza massima del nome di un oggetto accettata da Blender.
LUNGHEZZA_MASSIMA_NOME = 63

# Inquadratura: quanto spazio lasciare intorno all'oggetto e distanza minima
# per non finire dentro la geometria.
FATTORE_INQUADRATURA = 2.2
DISTANZA_MINIMA_VISTA = 0.05
DISTANZA_VUOTA_PREDEFINITA = 12.0

# Vista iniziale di Blender 4.5 LTS: prospettiva dall'alto a destra.
VISTA_INIZIALE_ROTAZIONE = (0.712376, 0.441062, 0.287358, 0.464123)
VISTA_INIZIALE_DISTANZA = 17.9866

# Chiavi riservate del risolutore di dati dell'interfaccia.
CHIAVE_SCENA = "scena"
CHIAVE_STATO = "stato_formafacile"
RIFERIMENTO_SCENA = "scena"
RIFERIMENTO_OGGETTO = "oggetto"
RIFERIMENTO_DATI = "dati"

# Nomi dei campi dello stato della scena usati dall'interfaccia.
GRUPPO_STATO_SCENA = "formafacile"
CAMPO_MODALITA = "formafacile.modalita"
CAMPO_FILTRO = "formafacile.filtro"
CAMPO_PASSO = "formafacile.passo"
CAMPO_GRANDEZZA_FORMA = "formafacile.grandezza_forma"
CAMPO_ASSE_ALLINEA = "formafacile.asse_allinea"
CAMPO_BORDO_ALLINEA = "formafacile.bordo_allinea"
CAMPO_RIFERIMENTO_ALLINEA = "formafacile.riferimento_allinea"
CAMPO_MESSAGGIO = "formafacile.messaggio"
CAMPO_TEMPO_MESSAGGIO = "formafacile.tempo_messaggio"

# Limiti di comodo per i testi: la barra laterale è stretta.
# I pulsanti che stanno da soli nella loro riga possono essere più lunghi.
LUNGHEZZA_MASSIMA_ETICHETTA = 60
LUNGHEZZA_MASSIMA_AZIONE = 26
LUNGHEZZA_MASSIMA_AZIONE_SINGOLA = 34
# Le finestrelle di conferma sono più strette della barra laterale: le
# spiegazioni si spezzano prima, altrimenti verrebbero tagliate.
LUNGHEZZA_MASSIMA_FINESTRA = 42


def imposta_interfaccia_italiana(bpy_module: object) -> bool:
    """Imposta l'italiano nella sessione corrente senza salvare preferenze globali.

    Ogni impostazione viene provata da sola: in alcune installazioni mancano i
    file di traduzione e la lingua non è disponibile, ma le altre opzioni di
    traduzione restano comunque utili.
    """
    try:
        vista = bpy_module.context.preferences.view
    except (AttributeError, KeyError, RuntimeError, TypeError, ValueError):
        return False

    italiano = False
    try:
        vista.language = LINGUA_PREDEFINITA
        italiano = True
    except (AttributeError, KeyError, RuntimeError, TypeError, ValueError):
        italiano = getattr(vista, "language", "") == LINGUA_PREDEFINITA

    for nome in (
        "use_translate_interface",
        "use_translate_tooltips",
        "use_translate_reports",
        "use_translate_new_dataname",
    ):
        if hasattr(vista, nome):
            try:
                setattr(vista, nome, True)
            except (AttributeError, RuntimeError, TypeError, ValueError):
                continue
    # Non viene chiamato bpy.ops.wm.save_userpref(): la modifica non viene
    # salvata deliberatamente nelle preferenze globali dell'utente.
    return italiano
