# Architettura e piano della prima versione utilizzabile

## Scelta tecnica

FormaFacile 3D è un componente aggiuntivo nativo di Blender, avviabile direttamente dal repository con un piccolo programma di avvio scritto in Python. Blender resta responsabile della vista 3D interattiva, della scena, dei dati, dell'annullamento e dei file `.blend`; FormaFacile aggiunge un livello d'uso più semplice. Questa scelta riutilizza un motore 3D reale e mantiene la compatibilità con gli strumenti e i formati Blender, invece di tentare di ricostruire geometria, materiali, animazione e creazione delle immagini finali.

L'interfaccia usa il tipo di pannello pubblico `bpy.types.Panel` nella barra laterale della Vista 3D: sei pannelli in modalità Semplice (azioni principali, elenco della scena, libreria di oggetti, oggetto scelto, strumenti guidati, aspetto della scena) e un settimo pannello con i comandi tecnici in modalità Completa. Un pulsante aggiunto alla testata apre la barra laterale. Un operatore è un comando registrato in Blender che esegue un'azione e può essere annullato; qui viene registrato con `bpy.utils.register_class` e dichiara `bl_options = {"REGISTER", "UNDO"}` quando cambia i dati. Il programma di avvio usa solo la libreria standard di Python; il componente aggiuntivo non introduce dipendenze Python esterne.

Le regole su *che cosa* mostrare (nessuna scelta, una scelta, più scelte, modalità semplice o completa, elenco lungo, oggetti nascosti) sono separate dal disegno: `ui/modello.py` descrive i dati, `ui/piano.py` decide il contenuto dei pannelli senza dipendere da Blender, `ui/renderer.py` disegna il piano su `bpy.types.UILayout`. Questa separazione rende verificabili senza Blender le parti che sbagliano più spesso. Vale anche per gli strumenti guidati di modellazione: le regole che non dipendono da Blender (smusso, suddivisione, simmetria, posizioni in cerchio, spessore, spaziatura, nomi dei gruppi) stanno in `scene/regole_modellazione.py` e i passi della guida in `scene/guide.py`, mentre le chiamate a Blender restano in `blender/`. I comandi guidati non applicano mai una modifica: la forma di partenza resta quella creata e ogni ritocco si può togliere.

L'aspetto della scena segue la stessa separazione: `scene/aspetto.py` dichiara i sei materiali pronti con i loro valori veri, la tavolozza dei colori, le cinque illuminazioni, le tre qualità dell'immagine con percentuale e campioni, i nomi dei file e le stime di memoria; `blender/materiali.py`, `blender/illuminazione.py`, `blender/telecamera.py` e `blender/rendering.py` sono gli unici moduli che toccano i dati di Blender. Le regole si verificano quindi senza Blender (`tests/unit/test_aspetto.py`) e le prove dentro Blender si limitano a controllare che i dati creati siano quelli dichiarati e che l'immagine finale esista davvero.

La libreria iniziale dichiara dieci schede in `scene/libreria.py`; selezione, descrizione e campi della scena si disegnano senza dipendenze da Blender. `blender/asset_library.py` genera le mesh, le curve di testo e le luci direttamente con i datablock pubblici di Blender, creando una raccolta e un materiale indipendenti per ogni inserimento. La creazione è annullabile e, se fallisce, la procedura di ripristino elimina solo i dati appena creati. Le descrizioni dichiarano che le misure sono parametri di generazione: le mesh risultanti sono modificabili in Modalità Modifica, ma le misure iniziali non restano collegate ai controlli. Nessun modello o immagine di terzi è incluso.

## Versione scelta e riferimenti verificati

- Versione da supportare: **Blender 4.5.x LTS**, cioè una versione con supporto a lungo termine.
- Versione di riferimento: **4.5.14**.
- Blender 5.2.2 risulta più recente, ma per il primo rilascio si preferisce la linea LTS 4.5: limita le variabili e offre una base di compatibilità più prudente. Il programma di avvio controlla il numero effettivo e rifiuta le altre serie; il manifesto dell'estensione dichiara l'intervallo compatibile da 4.5.0 incluso a 4.6.0 escluso.
- Nell'ambiente di sviluppo non è presente il comando `blender`. È disponibile su PyPI il pacchetto `bpy==4.5.14` per Python 3.11, che non è l'applicazione grafica completa ma contiene la stessa interfaccia di programmazione: le prove di `tests/blender/test_addon.py` vengono eseguite con quel modulo, senza finestre, usando librerie grafiche fittizie preparate da `scripts/ambiente_bpy_locale.py` (comando `python3 scripts/controlla.py --test-bpy`).
- Restano da provare con una distribuzione Blender completa soltanto le cose che hanno bisogno di una finestra vera: disegno dei pannelli sullo schermo, passaggio del mouse sui suggerimenti, ridimensionamento, navigazione con il mouse, cambio di disposizione dei pannelli e annullamento interattivo.

Riferimenti ufficiali consultati, fissati al sorgente Blender 4.5.14:

- [Sorgenti ufficiali Blender 4.5.14](https://github.com/blender/blender/tree/v4.5.14) e [pacchetto `bpy` 4.5.14 su PyPI](https://pypi.org/project/bpy/4.5.14/): verifica delle versioni reperibili nell'ambiente.
- [Panoramica dell’interfaccia di programmazione Python di Blender](https://github.com/blender/blender/blob/v4.5.14/doc/python_api/rst/info_overview.rst): distingue gli script dai componenti aggiuntivi e descrive pannelli, operatori e registrazione delle classi.
- [Guida rapida all’interfaccia di programmazione Python di Blender](https://github.com/blender/blender/blob/v4.5.14/doc/python_api/rst/info_quickstart.rst): riassume le capacità e i limiti d'integrazione dell’interfaccia.
- [Esempio ufficiale di manifesto di un'estensione](https://github.com/blender/blender/blob/v4.5.14/scripts/addons_core/bl_pkg/example_extension/blender_manifest.toml): riferimento per il formato del manifesto e i metadati.
- [Codice ufficiale del sistema di estensioni](https://github.com/blender/blender/tree/v4.5.14/scripts/addons_core/bl_pkg): riferimento per il sistema introdotto nelle versioni recenti.
- [Validazione di manifesti e archivi ZIP](https://github.com/blender/blender/blob/v4.5.14/scripts/addons_core/bl_pkg/cli/blender_ext.py): verifica dell'intervallo di versioni e del formato di un archivio con una sola cartella principale.
- [Versioni LTS di Blender](https://www.blender.org/download/lts/): pagina ufficiale per ottenere la distribuzione completa.

## Moduli

- `scripts/avvia_formafacile.py`: individua Blender tramite opzione, variabile `FORMAFACILE_BLENDER`, file di configurazione, `PATH` e posizioni standard; verifica che la versione sia 4.5.x e avvia la sessione.
- `scripts/bootstrap_blender.py`: importa e registra il componente aggiuntivo dalla cartella del repository. Non installa codice nel sistema dell'utente.
- `addon/formafacile_3d/localization.py`: unica risorsa dei testi italiani usati dall'interfaccia, dal programma di avvio e dai messaggi dei controlli.
- `addon/formafacile_3d/configuration.py`: valori predefiniti (passo, angolo, fattori, limiti dell'elenco, dimensioni minime, vista iniziale) e scelta della lingua italiana nella sessione corrente, senza salvare le preferenze globali.
- `addon/formafacile_3d/comandi.py`: unico punto in cui sono scritti gli identificatori dei comandi e i valori degli enumerati (direzioni, versi di rotazione, versi della dimensione, modi di scelta).
- `addon/formafacile_3d/operators/`: traduce le interazioni dell'interfaccia in operatori Blender annullabili: `assets.py` (inserimento dei modelli della libreria), `scene.py` (creazione e strumenti con le maniglie), `selezione.py` (scelta), `oggetti.py` (rinomina, duplica, elimina, visibilità, blocco della scelta, copia e incolla, telecamera), `trasformazioni.py` (passi, centramento e appoggio), `vista.py` (vista iniziale, inquadrature, annulla e ripeti, ricerca), `modellazione.py` (strumenti guidati: smusso, superfici, specchio, ripetizione, spessore, unione e taglio, conversione in forma), `insiemi.py` (allineamento, spaziatura, gruppi, rimozione delle modifiche), `guide.py` (esecuzione dei passi della guida), `base.py` (parti comuni, fra cui il ripristino dell'oggetto attivo).
- `addon/formafacile_3d/scene/`: servizi di scena: `aspetto.py` (materiali pronti, tavolozza, illuminazioni, qualità, nomi dei file, percorsi e stima della memoria, senza Blender), `libreria.py` (catalogo dei dieci modelli e campi mostrati), `primitives.py` (forme e nomi italiani), `misure.py` (unità, conversioni e regole dei blocchi, senza Blender), `nomi.py` (pulizia dei nomi scritti a mano), `stato.py` (modalità, passo, grandezza, parametri della libreria, ricerca e messaggio salvati nella scena), `messaggi.py` (messaggi brevi e barra di stato), `regole_modellazione.py` (regole pure di modellazione), `guide.py` (passi della guida passo passo, senza Blender), `testi.py` (a capo e accorciamento dei testi lunghi).
- `addon/formafacile_3d/blender/`: adattatore minimo che invoca le API pubbliche di Blender, isolandole dai servizi e dall'interfaccia: `adapter.py` (creazione nativa), `asset_library.py` (mesh, testo estruso, materiali, raccolte e luci generati dal codice), `selezione.py` (regole della scelta), `oggetti.py` (dati degli oggetti e blocco della scelta), `trasformazioni.py` (formule dei passi e delle posizioni precise, con il rispetto dei blocchi), `vista.py` (vista iniziale, inquadrature, esecuzione di comandi nativi nel contesto di una Vista 3D e attivazione degli strumenti con le maniglie), `modificatori.py` (modifiche non applicate: creazione, lettura, rimozione, spigoli vivi e bordi aperti, simmetria, superficie liscia, conversione in forma), `allineamento.py` (allineamento e spaziatura calcolati sui riquadri veri degli oggetti), `raccolte.py` (gruppi di oggetti come raccolte di Blender), `materiali.py` (materiali veri dai valori scelti, con un materiale nuovo per ogni applicazione e la copia per la variazione), `illuminazione.py` (luci dei preset in una raccolta dedicata, lettura della grandezza della scena, sfondo e intensità), `telecamera.py` (creazione, inquadratura calcolata sull'apertura della telecamera, ripristino e modi di guardare la scena), `rendering.py` (controlli prima di iniziare, qualità, motore e formato, disegno con avanzamento, salvataggio e riapertura del file creato).
- `addon/formafacile_3d/ui/`: pannelli Blender e regole dell'interfaccia: `modello.py`, `piano.py`, `renderer.py`, `vista.py` (lettura della scena), `icone.py` (nomi delle icone verificate), `panel.py` (sei pannelli in modalità Semplice, un pannello aggiuntivo in modalità Completa e il pulsante nella testata).
- `addon/formafacile_3d/logging_service.py`: messaggi diagnostici essenziali sulla console; non registra prompt, nomi di file o contenuti della scena.
- `scripts/controlla.py`: verifica file, sintassi, manifesto e test unitari; con `--test-bpy` esegue le prove con il modulo `bpy` senza schermo e con `--test-blender` le esegue con una distribuzione Blender completa.
- `scripts/ambiente_bpy_locale.py`: esegue i test con il modulo `bpy` preparando librerie grafiche fittizie nella cartella `.cache`, senza installare nulla nel sistema.
- `scripts/crea_pacchetto.py`: prepara un archivio installabile dell'estensione usando la libreria standard.
- `tests/supporto_finto.py`: blocco di interfaccia finto; registra le chiamate che i pannelli farebbero a `bpy.types.UILayout`, così le regole dell'interfaccia si verificano anche senza Blender.
- `docs/REVISIONE_UX.md`: revisione dei termini italiani sostituiti e di quelli mantenuti, con le ragioni e le verifiche manuali richieste.
- `docs/VERIFICA_MANUALE.md`: checklist della verifica a mano con Blender grafico: pannelli, maniglie, mouse, campi numerici e annullamento interattivo.

## Ciclo di vita previsto

1. **Avvio:** il programma di avvio cerca l'eseguibile configurato e legge `blender --version`. Se non trova Blender o la serie è diversa da 4.5, mostra un messaggio in italiano con la procedura corretta.
2. **Preparazione:** Blender viene avviato con uno script di bootstrap che registra il pannello FormaFacile e attiva la lingua italiana nella sessione, senza salvare automaticamente le preferenze globali.
3. **Apertura del progetto:** l'utente può aprire un file `.blend` con i comandi nativi di Blender oppure passare opzioni a Blender dopo `--` nel programma di avvio. Questa base non crea né sostituisce automaticamente un progetto.
4. **Lavoro sulla scena:** i pannelli compaiono nella barra laterale della Vista 3D, scheda FormaFacile. Si aggiungono forme e luci, si sceglie e si rinomina dall'elenco, oppure si seleziona un modello della libreria, si regolano i suoi campi e lo si inserisce come raccolta di geometrie. Si sposta, si ruota e si ingrandisce a passi; le azioni di creazione sono annullabili con la storia standard di Blender.
5. **Salvataggio e riapertura:** si usano i comandi nativi di Blender per salvare e riaprire `.blend`; non viene introdotto un formato di progetto proprietario.
6. **Chiusura:** si chiude Blender normalmente. La copia avviata dal repository non resta installata e non richiede servizi in background.

## Sequenza della prima versione utilizzabile

1. **Scheletro iniziale (fatto):** programma di avvio con controllo della versione, metadati dell'estensione, interfaccia italiana iniziale, diagnostica e un'azione verificabile.
2. **Creazione e modifica (fatto):** forme affidabili (cubo, sfera, cilindro, cono, piano, ciambella, testo e luce) con grandezza regolabile, selezione, spostamento, rotazione e scala a passi e con campi numerici, maniglie per il mouse, centramento, appoggio sul piano, blocco della scelta, copia e incolla, duplicazione, rinomina, visibilità, eliminazione, rispetto dei blocchi di Blender e annullamento.
3. **Risultato visivo (fatto):** pannello **Dai un bell'aspetto alla scena** con sei materiali pronti e anteprima, tavolozza dei colori, valori di superficie, illuminazione automatica e quattro situazioni tipiche, sfondo e intensità, telecamera con inquadratura, centratura e ripristino, distinzione fra vista di lavoro e anteprima dell'immagine, e **Crea immagine finale** con qualità prudenti, controlli prima di iniziare, avanzamento con interruzione nella finestra di Blender, messaggi comprensibili e rilettura del file creato. Resta da fare un flusso dedicato per il progetto `.blend`.
4. **Apprendimento guidato (parziale):** ci sono i controlli contestuali, la modalità principiante/avanzata, gli strumenti guidati di modellazione e la prima guida passo passo (la casetta); mancano altre guide, flussi brevi e gerarchia semplificata.
5. **Scambio di file:** importazione ed esportazione solo per formati effettivamente provati sulla versione supportata.
6. **Assistente facoltativo basato su intelligenza artificiale locale:** solo dopo le azioni reali, lo schema strutturato, la validazione, l'anteprima delle modifiche e l'annullamento. Nessun servizio a pagamento o collegamento di rete obbligatorio.

## Cosa rimandare

Non si introduce un'applicazione desktop separata, un motore 3D alternativo, un modello locale, scaricamento dei pesi dei modelli, elaborazione distribuita per creare le immagini finali, importatori non verificati o uno spazio di lavoro Blender personalizzato prima che i flussi nativi siano stabili. In questa base non si sostituisce la schermata iniziale di Blender: il pannello della Vista 3D è l'alternativa semplice e mantenibile.

## Rischi principali

- **Compatibilità delle API (interfacce di programmazione):** pannelli, operatori, traduzioni e sistema delle estensioni possono cambiare. Il progetto blocca l'avvio alla serie 4.5.x e usa API pubbliche; ogni aggiornamento di versione richiede test d'integrazione e revisione delle note ufficiali.
- **Distribuzione e licenze:** Blender non è incluso. Il codice iniziale dichiara GPL-2.0-or-later; prima di una distribuzione pubblica vanno controllate la forma concreta dell'integrazione, gli obblighi applicabili e le licenze di ogni componente o risorsa aggiunta.
- **Memoria e carico:** scene e immagini finali possono richiedere molta memoria di sistema (RAM) o memoria grafica e spazio su disco. I valori predefiniti sono quelli della scena (di solito 1920×1080) con i campioni consigliati dalla qualità scelta, mai i 4096 campioni predefiniti di Blender; prima di iniziare si controllano telecamera, cartella, spazio su disco, stima della memoria e numero di pixel, e in una finestra vera Blender mostra l'avanzamento e accetta `Esc`. Restano da provare a mano il disegno dell'avanzamento e l'interruzione con `Esc`.
- **Prestazioni dell'intelligenza artificiale (IA) locale:** i modelli con pesi ridotti (quantizzati) occupano meno memoria ma possono essere lenti soprattutto usando il processore (CPU). L'assistente sarà facoltativo, con stima hardware, scaricamento esplicito, provenienza e licenza; gli strumenti normali resteranno disponibili senza modello.

## Piano delle verifiche

| Livello | Controllo | Stato |
| --- | --- | --- |
| Unitario | Analisi versione Blender, precedenza delle impostazioni e percorso di configurazione | Automatizzato con `unittest` |
| Struttura e sintassi | File richiesti, manifesto TOML e compilazione sintattica dei file Python | Automatizzato con `scripts/controlla.py` |
| Localizzazione | Risorsa italiana centrale, assenza di segnaposto inglesi noti e testi UI non incorporati nel codice dei pannelli | Automatizzato; resta necessaria revisione umana |
| Integrazione Blender | Registrazione, chiamata dell'operatore, creazione della mesh e rinomina dell'oggetto | `python3 scripts/controlla.py --test-blender`; richiede Blender 4.5.x completo |
| Immagine finale | Materiali veri e indipendenti, luci dei preset, inquadratura della telecamera, immagine scritta, riaperta e controllata (grandezza, formato, luminosità), errori comprensibili per cartella, memoria, risoluzione e salvataggio fallito | Automatizzato con `--test-bpy`, che crea immagini vere; il disegno dell'avanzamento e `Esc` restano manuali |
| Interfaccia manuale | Avvio, lingua italiana, pannello, pulsante, maniglie, mouse, campi numerici, annullamento, ridimensionamento e lettura a diverse scale | Da eseguire in Blender grafico 4.5.x, con la checklist di `docs/VERIFICA_MANUALE.md` |
| Pacchetto | Creazione dell’archivio ZIP e inclusione manifesto/licenze; installazione da disco, attivazione e disinstallazione | Creazione verificata con test unitario; installazione grafica ancora da provare |

## Decisioni

- Interfaccia nella barra laterale della Vista 3D, non uno spazio di lavoro personalizzato: le funzioni native restano dove sono.
- Nessuna scorciatoia di navigazione rimappata; annulla e ripeti richiamano la storia di Blender.
- Stato dell'interfaccia (modalità, passo, ricerca, messaggio) salvato nella scena, così si ritrova riaprendo il progetto.
- Blender non tiene scelto un oggetto che non si vede: nessun comando promette il contrario.
- Termini tecnici tradotti solo quando esiste una parola italiana altrettanto precisa; il resto resta nel pannello avanzato. Il dettaglio è in `docs/REVISIONE_UX.md`.
- Si assume Blender 4.5.x LTS, interfaccia italiana, componente aggiuntivo GPL-2.0-or-later e assistente IA non incluso finché non esiste un'integrazione reale. Prima di distribuire l'applicazione completa andranno confermate la licenza del prodotto e le licenze di ogni componente aggiunto.
