# Sviluppo e prova manuale

## Requisiti

- Python 3.11 o successivo per il programma di avvio e i controlli.
- Blender 4.5.x LTS (supporto a lungo termine) per avviare la vista grafica e per le prove
  d'integrazione con l'applicazione completa.
- Nessuna dipendenza Python di terze parti per l'applicazione, per il programma di avvio o per le
  prove di unità.

## Comandi

Dalla cartella principale del repository:

```sh
python3 scripts/controlla.py                 # file, sintassi, manifesto, prove di unità
python3 scripts/crea_pacchetto.py            # archivio installabile in dist/
python3 scripts/avvia_formafacile.py         # avvia Blender con FormaFacile registrato
```

Per usare un eseguibile Blender non presente nel `PATH`:

```sh
python3 scripts/avvia_formafacile.py --blender "/percorso/al/programma/blender"
```

In alternativa, imposta `FORMAFACILE_BLENDER` oppure il valore `executable` nel file `config.ini`,
sezione `[blender]`:

```ini
[blender]
executable=/percorso/all/eseguibile/blender
```

Il percorso del file di configurazione si adatta alle convenzioni del sistema operativo; su Linux
rispetta `XDG_CONFIG_HOME`.

## Prove dentro Blender o con il modulo bpy

Le prove d'integrazione stanno in `tests/blender/test_addon.py` e si eseguono in due modi.

Con una distribuzione Blender 4.5.x completa:

```sh
python3 scripts/controlla.py --test-blender
blender --background --factory-startup --python tests/blender/test_addon.py
```

Senza Blender grafico, usando il pacchetto `bpy` da PyPI:

```sh
python3 scripts/controlla.py --test-bpy
python3 scripts/ambiente_bpy_locale.py --python .venv/bin/python
python3 scripts/ambiente_bpy_locale.py --prepara     # ricostruisce solo le librerie fittizie
```

Che cosa fa il secondo percorso:

1. l'ambiente virtuale `.venv` (escluso dal repository) contiene `bpy` versione 4.5.14. Le prove
   d'integrazione non hanno bisogno di installare una distribuzione Blender completa, ma il modulo
   richiede alcune librerie grafiche di sistema che su un server possono mancare;
2. `scripts/ambiente_bpy_locale.py` legge i simboli richiesti dalle librerie di `bpy` e costruisce in
   `.cache/librerie_bpy` alcune librerie fittizie (sette file) con il compilatore di sistema. Servono
   **solo** a far partire il modulo in modalità senza finestre: non disegnano nulla, non vengono
   installate nel sistema e si possono cancellare in qualsiasi momento (vengono ricostruite in pochi
   secondi);
3. il file di prova viene eseguito con `LD_LIBRARY_PATH` che punta a quella cartella. Alla fine il
   test stampa una riga di riepilogo (`Test Blender superato: … verifiche.`) e il processo chiude il
   componente aggiuntivo con `unregister()`, altrimenti Blender non termina.

`scripts/controlla.py --test-bpy` controlla sia il codice di uscita sia la riga di riepilogo e
rifiuta l'esito se nell'uscita compare una traccia di errore Python: un comando che solleva
un'eccezione non deve passare inosservato.

## Come sono organizzate le prove

| File | Che cosa verifica | Serve Blender? |
| --- | --- | --- |
| `tests/unit/test_configuration.py` | lingua italiana di sessione e valori predefiniti | no |
| `tests/unit/test_launcher.py` | ricerca di Blender, versione, configurazione utente | no |
| `tests/unit/test_localization.py` | testi centrali, segnaposto inglesi, chiavi usate inesistenti e chiavi mai nominate | no |
| `tests/unit/test_packaging.py` | contenuto dell'archivio installabile | no |
| `tests/unit/test_piano.py` | regole dei pannelli: nessuna scelta, una, molte, modalità semplice/completa, elenco lungo, ricerca, messaggi | no |
| `tests/unit/test_renderer.py` | disegno del piano con un blocco di interfaccia finto, campi mancanti, dati guasti | no |
| `tests/unit/test_selezione.py` | regole della scelta con oggetti finti: visibili, nascosti, bloccati, singoli e di gruppo | no |
| `tests/blender/test_addon.py` | registrazione, comandi, dati veri della scena, vista, disposizioni dei pannelli e disegno dei pannelli | sì (Blender o modulo `bpy`) |

`tests/supporto_finto.py` è il blocco di interfaccia finto: riceve le stesse chiamate che i pannelli
farebbero a `bpy.types.UILayout`, le annota in un registro e non disegna nulla. Dentro Blender le
prove usano lo stesso blocco insieme ai dati reali della scena, così si controlla in una volta sola
che cosa il pannello mostrerebbe e se i comandi, i campi e le icone esistono davvero.

## Prova visiva

Avvia il programma, apri la barra laterale della Vista 3D con `N`, scegli **FormaFacile** e prova i
cinque pannelli: crea una forma, sceglila e rinominala dall'elenco, nascondila e falla ricomparire,
arrotondala e rispecchiala con gli strumenti guidati del pannello **Dai forma**, raggruppala e prova
la guida della casetta,
spostala a passi, annulla e ripeti. Prova poi il cambio di modalità (Semplice/Completa), il
ridimensionamento della finestra e un cambio di disposizione dei pannelli. L'elenco completo delle
verifiche manuali è in `docs/LIMITAZIONI.md` e in `docs/REVISIONE_UX.md`.

## Installazione e rimozione

Per provare il pacchetto indipendente, crea l'archivio ZIP e installalo dalla sezione Estensioni
delle preferenze di Blender. Per rimuoverlo, disinstalla **FormaFacile 3D** dalla stessa sezione. Il
programma di avvio per lo sviluppo importa invece il codice direttamente dal repository e non
modifica l'installazione di Blender.

## Convenzioni di scrittura

- Tutto ciò che l'utente legge sta in `addon/formafacile_3d/localization.py`: i moduli dei pannelli e
  degli operatori non contengono etichette visibili scritte a mano (le prove lo controllano).
- Gli identificatori dei comandi e i valori degli enumerati stanno in `addon/formafacile_3d/comandi.py`.
- Le regole dell'interfaccia stanno in moduli senza dipendenze da Blender (`ui/piano.py`,
  `scene/nomi.py`, `blender/selezione.py`, `blender/trasformazioni.py`): si possono provare in fretta
  con `unittest`.
- Ogni comando che cambia i dati dichiara `bl_options = {"REGISTER", "UNDO"}`; i comandi che non
  cambiano i dati (inquadrature, apertura della barra) non lo dichiarano.
