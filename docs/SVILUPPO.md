# Sviluppo e prova manuale

## Requisiti

- Python 3.11 o successivo per il programma di avvio e i controlli.
- Blender 4.5.x LTS (supporto a lungo termine) per avviare la vista grafica e i test d'integrazione.
- Nessuna dipendenza Python di terze parti per l'applicazione o i test unitari.

## Comandi

Dalla cartella principale del repository:

```sh
python3 scripts/controlla.py
python3 scripts/crea_pacchetto.py
python3 scripts/avvia_formafacile.py
```

Per usare un eseguibile Blender non presente nel `PATH`:

```sh
python3 scripts/avvia_formafacile.py --blender "/percorso/al/programma/blender"
```

In alternativa, imposta `FORMAFACILE_BLENDER` oppure il valore `executable` nel file `config.ini`, sezione `[blender]`:

```ini
[blender]
executable=/percorso/all/eseguibile/blender
```

Il percorso del file di configurazione si adatta alle convenzioni del sistema operativo; su Linux rispetta `XDG_CONFIG_HOME`.

Per i test Blender reali:

```sh
python3 scripts/controlla.py --test-blender
```

Il test diretto equivalente è:

```sh
blender --background --factory-startup --python tests/blender/test_addon.py
```

## Prova visiva

Avvia il programma, apri la barra laterale della Vista 3D con `N`, seleziona **FormaFacile** e premi **Aggiungi cubo**. Verifica la selezione e il nome del cubo; annulla e ripeti l'azione con i controlli di Blender. Chiudi e riapri Blender per verificare che l'avvio non abbia installato un servizio o alterato un progetto.

## Installazione e rimozione

Per provare il pacchetto indipendente, crea l'archivio ZIP e installalo dalla sezione Estensioni delle preferenze di Blender. Per rimuoverlo, disinstalla **FormaFacile 3D** dalla stessa sezione. Il programma di avvio per lo sviluppo importa invece il codice direttamente dal repository e non modifica l'installazione di Blender.
