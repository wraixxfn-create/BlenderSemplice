"""Testi italiani del componente aggiuntivo e degli strumenti di avvio."""

from __future__ import annotations

from types import MappingProxyType


TESTI = MappingProxyType(
    {
        # Interfaccia del componente aggiuntivo.
        "NOME_ESTENSIONE": "FormaFacile 3D",
        "AUTORE_ESTENSIONE": "Contributori di FormaFacile 3D",
        "POSIZIONE_ESTENSIONE": "Vista 3D > Barra laterale > FormaFacile",
        "DESCRIZIONE_ESTENSIONE": "Strumenti essenziali in italiano per iniziare con le scene 3D.",
        "TITOLO_PANNELLO": "FormaFacile 3D",
        "CATEGORIA_PANNELLO": "FormaFacile",
        "DESCRIZIONE_PANNELLO": "Crea la tua scena con strumenti semplici.",
        "AZIONE_AGGIUNGI_CUBO": "Aggiungi cubo",
        "AIUTO_AGGIUNGI_CUBO": "Aggiunge un cubo modificabile alla scena.",
        "NOME_CUBO": "Cubo",
        "NOME_MESH_CUBO": "Geometria del cubo",
        "CUBO_AGGIUNTO": "Cubo aggiunto alla scena.",
        "ERRORE_AGGIUNTA_CUBO": "Non è stato possibile aggiungere il cubo.",
        "LOG_ERRORE_CUBO": "L'operazione di aggiunta del cubo non è riuscita.",
        "ERRORE_REGISTRAZIONE": "Registrazione del componente aggiuntivo non riuscita.",
        "LOG_COMPONENTE_REGISTRATO": "Componente aggiuntivo registrato.",
        "LOG_COMPONENTE_DISATTIVATO": "Componente aggiuntivo disattivato.",
        "ERRORE_LINGUA_ITALIANA": "Non è stato possibile attivare l'interfaccia italiana di Blender.",
        "AVVIO_COMPONENTE_RIUSCITO": "FormaFacile è pronto. Apri la scheda FormaFacile nella barra laterale della Vista 3D.",
        "AVVIO_COMPONENTE_FALLITO": "FormaFacile non è stato caricato. Controlla la console di Blender per i dettagli.",
        # Avvio e diagnostica.
        "DESCRIZIONE_AVVIO": "Avvia FormaFacile 3D con una versione compatibile di Blender.",
        "USO_LAUNCHER": "python3 scripts/avvia_formafacile.py [--blender PERCORSO] [-- OPZIONI_BLENDER]",
        "AIUTO_PERCORSO_BLENDER": "Percorso dell'eseguibile Blender da usare.",
        "AIUTO_ARGOMENTI_BLENDER": "Opzioni da inoltrare a Blender dopo il separatore --.",
        "BLENDER_NON_TROVATO": (
            "Non trovo Blender 4.5 LTS. Installa Blender 4.5.x dalla pagina ufficiale "
            "https://www.blender.org/download/lts/ oppure indica il suo percorso con "
            "--blender o con la variabile FORMAFACILE_BLENDER."
        ),
        "PERCORSO_BLENDER_NON_VALIDO": "Il percorso indicato non contiene un eseguibile Blender valido.",
        "VERSIONE_BLENDER_NON_LEGGIBILE": "Non riesco a verificare la versione di Blender. Controlla l'installazione.",
        "VERSIONE_BLENDER_NON_SUPPORTATA": (
            "La versione rilevata è {versione}. FormaFacile supporta Blender 4.5.x LTS. "
            "Installa una versione compatibile oppure indica il percorso corretto."
        ),
        "AVVIO_BLENDER": "Avvio Blender 4.5 LTS con FormaFacile 3D.",
        "ERRORE_AVVIO_BLENDER": "Blender non è riuscito ad avviarsi.",
        # Controllo e pacchetto.
        "CONTROLLO_FILE_RIUSCITO": "Controllo dei file richiesti superato.",
        "CONTROLLO_SINTASSI_RIUSCITO": "Controllo della sintassi Python superato.",
        "CONTROLLO_MANIFEST_RIUSCITO": "Metadati del componente aggiuntivo validi.",
        "TEST_UNITA_RIUSCITI": "Test automatici superati.",
        "TEST_BLENDER_NON_TROVATO": "Per il test in Blender serve Blender 4.5.x installato e individuabile.",
        "AVVIO_TEST_BLENDER": "Esecuzione del test dell'operatore in Blender.",
        "TEST_BLENDER_RIUSCITO": "Test dell'operatore in Blender superato.",
        "DESCRIZIONE_CONTROLLI": "Controlla file, sintassi, traduzioni e prove di FormaFacile 3D.",
        "ARGPARSE_ERRORE": "Errore: {messaggio}\n",
        "ARGPARSE_USO": "Uso: ",
        "ARGPARSE_POSIZIONALI": "argomenti posizionali",
        "ARGPARSE_OPZIONI": "opzioni",
        "ARGPARSE_AIUTO": "mostra questo messaggio di aiuto ed esce",
        "ARGPARSE_NON_RICONOSCIUTI": "argomenti non riconosciuti: %s",
        "ARGPARSE_OBBLIGATORI": "mancano gli argomenti obbligatori: %s",
        "ARGPARSE_UN_VALORE": "è richiesto un valore",
        "ARGPARSE_UNO_MINIMO": "è richiesto almeno un valore",
        "ARGPARSE_UNO_MASSIMO": "è ammesso un solo valore",
        "ARGPARSE_N_VALORI": "sono richiesti %s valori",
        "ARGPARSE_SCELTA_ERRATA": "valore non valido: %(value)r (valori ammessi: %(choices)s)",
        "ARGPARSE_PARAMETRO_PREFISSO": "parametro ",
        "ARGPARSE_NON_RICONOSCIUTI_PREFISSO": "argomenti non riconosciuti: ",
        "ARGPARSE_OBBLIGATORI_PREFISSO": "mancano gli argomenti obbligatori: ",
        "ARGPARSE_SCELTA_PREFISSO": "valore non valido: ",
        "ARGPARSE_VALORI_AMMESSI_PREFISSO": " (valori ammessi: ",

        "AIUTO_TEST_BLENDER": "Esegue anche la prova reale con Blender 4.5.x.",
        "AIUTO_PERCORSO_TEST_BLENDER": "Percorso dell'eseguibile Blender da usare per la prova reale.",
        "FILE_RICHIESTI_ASSENTI": "Controllo non superato: mancano i file richiesti.",
        "ERRORE_SINTASSI": "Controllo della sintassi non superato nel file {file}, riga {riga}.",
        "ERRORE_MANIFEST": "Metadati non validi: controlla il manifesto e il supporto Blender 4.5.x.",
        "ERRORE_TEST_BLENDER": "Test Blender non superato (versione {versione}).",
        "PACCHETTO_CREATO": "Pacchetto creato: {percorso}",
    }
)


def testo(chiave: str, **valori: object) -> str:
    """Restituisce un testo italiano, applicando se necessario i valori indicati."""
    return TESTI[chiave].format(**valori) if valori else TESTI[chiave]

