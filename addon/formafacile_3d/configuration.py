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

# Dimensione minima di un oggetto: sotto questa soglia le forme diventano
# invisibili e difficili da riprendere, quindi il comando avvisa e non applica.
SCALA_MINIMA = 0.01

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
RIFERIMENTO_SCENA = "scena"
RIFERIMENTO_OGGETTO = "oggetto"
RIFERIMENTO_DATI = "dati"

# Nomi dei campi dello stato della scena usati dall'interfaccia.
GRUPPO_STATO_SCENA = "formafacile"
CAMPO_MODALITA = "formafacile.modalita"
CAMPO_FILTRO = "formafacile.filtro"
CAMPO_PASSO = "formafacile.passo"
CAMPO_MESSAGGIO = "formafacile.messaggio"
CAMPO_TEMPO_MESSAGGIO = "formafacile.tempo_messaggio"

# Limiti di comodo per i testi: la barra laterale è stretta.
# I pulsanti che stanno da soli nella loro riga possono essere più lunghi.
LUNGHEZZA_MASSIMA_ETICHETTA = 60
LUNGHEZZA_MASSIMA_AZIONE = 26
LUNGHEZZA_MASSIMA_AZIONE_SINGOLA = 34


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
