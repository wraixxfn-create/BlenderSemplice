# Limiti verificati della versione attuale

Questa versione è la prima interfaccia utilizzabile: creare forme, scegliere, rinominare,
nascondere, spostare a passi e con numeri esatti, ruotare, ingrandire, centrare, appoggiare sul
piano, bloccare la scelta, copiare e incollare, duplicare, eliminare, inquadrare, annullare e
ripetere. Le cose che seguono dicono che cosa non c'è, che cosa è stato verificato e che cosa va
ancora provato a mano.

## Funzioni presenti

- Programma di avvio configurabile, con controllo della serie Blender 4.5.x.
- Estensione Blender con metadati e registrazione/disattivazione pulite e ripetibili.
- Cinque pannelli italiani in modalità Semplice (**Azioni principali**, **La mia scena**,
  **Libreria di oggetti**, **Oggetto scelto**, **Dai forma**) e un sesto pannello (**Comandi di
  Blender**) nella modalità Completa; un pulsante nella testata apre la barra.
- Creazione di **Cubo**, **Sfera**, **Cilindro**, **Cono**, **Piano**, **Ciambella**, **Testo**
  e **Luce**, con nomi italiani per oggetto e geometria e posizione libera vicino al cursore 3D;
  la grandezza delle nuove forme si regola da un solo campo, che porta l'unità della scena.
- **Libreria di oggetti**: tavolino, scaffale con numero di ripiani regolabile, sedia stilizzata,
  piedistallo, vaso cavo con spessore della parete, insegna con testo estruso modificabile, stanza,
  pedana circolare, set fotografico con fondale e tre luci di area, e quattro forme solide per la
  stampa 3D. La selezione mostra descrizione e campi italiani prima dell'inserimento. Ogni modello
  viene generato da mesh o curve reali in una raccolta nuova con materiale indipendente; le parti
  mesh sono statiche dopo la creazione ma modificabili in Modalità Modifica. Le prove verificano
  dimensioni, oggetti, messaggi, annullamento degli errori e rimozione senza danneggiare geometrie
  preesistenti. Non è stata eseguita una prova visiva in Vista 3D o con un'immagine finale.
- Scelta degli oggetti: **Tutti**, **Nessuno**, **Inverti**, **Stesso tipo**, scelta per nome
  dall'elenco (anche con più oggetti), casella di scelta su ogni riga.
- Elenco della scena con conteggio in parole, ricerca per nome quando serve, oggetti nascosti
  segnalati e **Mostra tutti gli oggetti**.
- Azioni sull'oggetto scelto: **Rinomina**, **Nascondi**/**Mostra**, **Inquadra l'oggetto**,
  **Duplica**, **Elimina**; con più oggetti scelti: inquadra, nascondi, duplica, elimina.
- Trasformazioni a passi: **Sposta di poco** (sei direzioni), **Ruota di poco** (due versi),
  **Ingrandisci o rimpicciolisci** (due versi), con campo **Passo** regolabile.
- Campi numerici con unità per l'oggetto scelto: **Posizione**, **Rotazione** e **Dimensione** con
  un campo per asse; la rotazione segue il modo dell'oggetto (Euleri, quaternione, asse-angolo) e
  con più oggetti scelti i numeri non compaiono, perché vargono per un solo oggetto.
- Maniglie nella Vista 3D: **Frecce per spostare**, **Frecce per ruotare** e **Frecce per
  ingrandire** attivano gli strumenti nativi di Blender e riaccendono gli interruttori delle
  maniglie se erano spenti.
- Posizioni precise: **Porta al centro** e **Appoggia sul piano** (la parte più bassa tocca il piano
  di lavoro, senza scivolare in orizzontale; per luci, telecamere e segnaposti finisce sul piano il
  punto di riferimento e il messaggio lo dice).
- **Blocca la scelta** e **Sblocca la scelta** (lucchetto nell'elenco e nel pannello dell'oggetto):
  un oggetto bloccato non si sceglie più per sbaglio, e l'oggetto attivo non resta mai un oggetto
  bloccato.
- **Copia** e **Incolla** con gli appunti di Blender: ciò che si copia qui si incolla anche con
  `Ctrl+V` e viceversa; incollare a vuoto avvisa in italiano, senza errori tecnici.
- Rispetto dei blocchi di Blender: un asse bloccato in posizione, rotazione o dimensione non viene
  toccato; il comando avvisa e gli assi liberi si muovono comunque.
- Luce (**Più luminosa**, **Meno luminosa**, con minimo di sicurezza) e telecamera
  (**Guarda dalla telecamera**, **Usa come telecamera principale**).
- **Torna alla vista iniziale**, **Inquadra tutto**, **Annulla**, **Ripeti**.
- Modalità **Semplice** e **Completa**; messaggi brevi in italiano nel pannello e nella barra di
  stato; suggerimenti (descrizioni dei comandi) presi dalla mappa centrale dei testi.
- Strumenti guidati nel pannello **Dai forma**: **Ammorbidisci gli spigoli** (smusso con forza e
  segmenti), **Superficie liscia** e **Superficie a facce** (cambiano solo l'aspetto, senza aggiungere
  facce), **Forma più arrotondata** (suddivisione a livelli, riusando un solo modificatore),
  **Specchia** (modificatore specchio con il piano segnato dal segnaposto **Specchio**),
  **Ripeti le copie** (in fila con una serie regolabile, in cerchio con copie vere attorno al cursore
  3D o al centro della scena), **Spessore della parete**, **Unisci o taglia** (unione, differenza e
  intersezione fra due forme) e **Trasforma in forma** (scritte, curve e superfici diventano forme).
- **Allinea** e **Spazia in modo uguale** sugli oggetti scelti, con **Asse**, **Bordo** e
  **Riferimento** scelti nel pannello.
- **Gruppi**: **Raggruppa**, **Scegli il gruppo**, **Nascondi/Mostra il gruppo**, **Togli dal
  gruppo**; **Togli le modifiche** riporta la forma a com'era senza usare `Ctrl+Z`.
- **Guida passo passo**: **Inizia la guida** costruisce una casetta in 13 passi verificati, con
  **Indietro**, **Avanti**, **Esegui il passo** e **Chiudi**; ogni passo spiega che cosa sta per fare
  e usa solo comandi che esistono davvero.
- **Dai un bell'aspetto alla scena**: sei **materiali pronti** (plastica opaca, metallo, legno
  stilizzato, vetro, ceramica, gomma) con i valori veri dichiarati nel codice, **anteprima** del
  materiale applicato disegnata da Blender, **tavolozza di colori** con il nome accanto al campione e
  campi **Colore**, **Ruvidità**, **Metallico** e **Trasparenza** (solo per i materiali che la
  prevedono). **Applica il materiale** crea un materiale nuovo per ogni oggetto, quindi cambiare un
  oggetto non cambia gli altri; quando un materiale è condiviso il pannello lo dice e **Crea
  variazione** ne fa una copia indipendente.
- **Illuminazione automatica** con valori regolati sulla grandezza della scena e quattro situazioni
  tipiche (**Prodotto**, **Interno semplice**, **Esterno semplice**, **Studio neutro**), campi per
  **Colore di sfondo**, **Luminosità dello sfondo** e **Potenza delle luci**, e **Applica sfondo e
  intensità**. Le luci di FormaFacile stanno in una raccolta dedicata e vengono sostituite cambiando
  illuminazione; le luci create dall'utente non vengono toccate.
- **Telecamera**: **Aggiungi telecamera** (inquadra la scena e diventa quella principale),
  **Inquadra con la telecamera** (distanza calcolata sull'apertura della telecamera e sulla forma vera
  degli oggetti), **Centra la vista** e **Ripristina la telecamera**. La distinzione fra **Vista di
  lavoro** e **Anteprima dell'immagine** è scritta nel pannello e si vede nella Vista 3D.
- **Crea immagine finale**: qualità **Anteprima**, **Standard** e **Alta qualità** con percentuale di
  risoluzione e campioni in chiaro; nella modalità completa percentuale, campioni, motore (**Come in
  Blender**, **EEVEE**, **Cycles**) e formato (**PNG**, **JPEG**). Controlli prima di iniziare
  (telecamera, cartella, spazio su disco, stima della memoria, numero di pixel), avanzamento di Blender
  con interruzione con `Esc` quando c'è una finestra, e rilettura del file creato: se l'immagine non si
  apre, il comando lo dice invece di dichiarare un successo.

### Limiti dell'aspetto della scena e dell'immagine finale, verificati

- I materiali pronti sono sei e tutti realistici solo per i valori dichiarati: nessuno finge un aspetto
  che Blender non sappia riprodurre (per esempio il legno non ha venature disegnate, perché non c'è
  una texture inclusa).
- La **trasparenza** si regola solo sui materiali che la prevedono (il vetro): sugli altri il campo non
  compare e il valore resta a zero, così un materiale opaco non diventa una superficie "trasparente"
  per errore.
- Cambiare **Colore**, **Ruvidità**, **Metallico** o **Trasparenza** non cambia da solo l'oggetto:
  serve **Applica il materiale**. Il pannello lo scrive accanto ai campi.
- **Illuminazione** e le altre azioni di FormaFacile non spostano le luci dell'utente: la nuova
  illuminazione sostituisce solo le luci con il segno di FormaFacile.
- **Inquadra con la telecamera** e **Centra la vista** non fanno nulla se non c'è niente da inquadrare:
  il messaggio lo dice. **Ripristina la telecamera** funziona solo sulle telecamere create da
  FormaFacile (le altre non hanno una posizione iniziale registrata) e il messaggio lo spiega.
- La **creazione dell'immagine** è l'unica operazione lenta: l'avanzamento di Blender e l'interruzione
  con `Esc` funzionano nella finestra grafica, mentre senza finestra il comando aspetta la fine del
  lavoro. Il disegno dell'avanzamento e `Esc` non sono stati provati a mano.
- Il **motore EEVEE** ha bisogno di una scheda grafica funzionante: se la creazione fallisce, il
  messaggio è in italiano e suggerisce una qualità più bassa; in questo ambiente senza schermo il
  motore EEVEE non è stato provato (la prova dell'immagine vera usa **Cycles**).
- Il file creato viene salvato nella cartella scelta con un nome che contiene data e ora: immagini
  create nello stesso secondo si distinguono solo grazie ai secondi nel nome.

### Limiti degli strumenti guidati, verificati

- **Unisci o taglia** lavora su due forme scelte: l'oggetto attivo è la **forma principale**, l'altro
  è l'**attrezzo**, che resta nella scena ma non si vede. Con una sola forma scelta o con più di due
  il comando si ferma e lo spiega; l'attrezzo deve essere una forma chiusa (un piano aperto viene
  rifiutato).
- Lo **specchio** ha per piano il **cursore 3D**: una forma già a cavallo del piano viene rifiutata,
  perché rispecchiarla non aggiungerebbe nulla. Il segnaposto **Specchio** si può spostare o
  eliminare; se manca, il pannello avvisa che la modifica specchia la forma su se stessa.
- La **ripetizione in fila** è un modificatore regolabile e resta un oggetto solo; quella **in
  cerchio** crea copie vere, che si possono scegliere e spostare una per una.
- **Ammorbidisci gli spigoli** è rifiutato sulle forme senza spigoli vivi (per esempio la sfera) e
  sugli oggetti che non sono forme (scritte, luci): il messaggio dice quale comando usare al posto suo.
- La **guida passo passo** è una sola (la casetta) e i passi non si saltano: si percorrono con
  **Esegui il passo**, **Indietro** e **Avanti**.

## Funzioni non ancora presenti

Non ci sono ancora animazione, gerarchia fra oggetti, salvataggio e riapertura con un flusso FormaFacile
dedicato, importazione ed esportazione, altre guide passo passo oltre a quella della casetta e
assistente di intelligenza artificiale. **Non esistono pulsanti fittizi per queste funzioni**: i
pannelli mostrano solo comandi che hanno un effetto reale. Non ci sono materiali con texture o
immagini esterne: i sei materiali pronti nascono dai valori dei nodi di Blender, quindi nel file `.blend`
restano leggeri e senza risorse da scaricare.

Il programma di avvio apre la scena iniziale di Blender e non sostituisce la schermata iniziale né
crea uno spazio di lavoro personalizzato. Il punto di ingresso di FormaFacile è la barra laterale
della Vista 3D. Salvataggio e riapertura usano i normali comandi di Blender.

## Verifica nell'ambiente di sviluppo

- Sistema rilevato: Debian GNU/Linux 12, Python 3.11.
- Il comando `blender` non è presente nel `PATH`: non c'è una distribuzione Blender grafica.
- Il pacchetto `bpy==4.5.14` è installato in un ambiente virtuale separato (`.venv`, escluso dal
  repository). Non è l'applicazione completa, ma espone la stessa interfaccia di programmazione,
  quindi le prove di `tests/blender/test_addon.py` sono state **eseguite davvero**:
  `python3 scripts/controlla.py --test-bpy` (5767 controlli superati, più 269 prove di unità).
  Le librerie grafiche di sistema mancanti (`libXrender`, `libXfixes`, `libXi`, `libxkbcommon`,
  `libSM`, `libICE`, `libGL`) vengono sostituite da librerie fittizie preparate da
  `scripts/ambiente_bpy_locale.py` nella cartella `.cache/librerie_bpy`: servono solo ad avviare il
  modulo senza schermo e non disegnano nulla.

Verificato automaticamente senza finestre:

- registrazione e disattivazione ripetute, elenco dei comandi registrati, opzioni
  `REGISTER`/`UNDO` di ogni comando che cambia i dati;
- creazione delle otto forme (cubo, sfera, cilindro, cono, piano, ciambella, testo, luce), nomi
  italiani, geometrie non sovrapposte, grandezza regolabile, scritta in piedi con testo di esempio,
  messaggio dopo ogni azione;
- scelta: nessuna scelta, una scelta, più scelte, scelta per nome nei tre modi, inverti, stesso tipo,
  conteggio degli oggetti saltati, rifiuto di un oggetto bloccato;
- rinomina con spazi, ritorni a capo, nomi lunghi (troncati a 63 caratteri), nome vuoto rifiutato,
  nomi doppi sistemati da Blender e riportati nel messaggio;
- visibilità, **Mostra tutti**, e il comportamento verificato di Blender per cui un oggetto nascosto
  non resta scelto (scelto per nome dall'elenco, viene prima fatto ricomparire);
- trasformazioni a passi con i tre modi di rotazione di Blender (Euleri, quaternioni, asse-angolo),
  passo regolabile, limite di dimensione minima e minimo di potenza della luce;
- rispetto dei blocchi degli assi (posizione, rotazione, dimensione): l'asse bloccato resta fermo,
  il messaggio avvisa e l'oggetto non scelto non viene mai toccato; l'oggetto attivo resta lo stesso
  dopo i comandi a passi;
- posizioni precise: centramento (anche con assi bloccati, muovendo solo i liberi), appoggio sul
  piano calcolato sul riquadro reale dell'oggetto, avviso per gli oggetti senza forma propria;
- blocco della scelta: l'oggetto bloccato esce dalla scelta, non resta attivo, si può sbloccare
  dall'elenco e dal pannello;
- copia e incolla con gli appunti di Blender: conteggio degli oggetti copiati e incollati, avviso
  chiaro quando non c'è nulla da incollare;
- strumenti con le maniglie: attivazione degli strumenti nativi `builtin.move`, `builtin.rotate`,
  `builtin.scale` e riaccensione degli interruttori `show_gizmo` della Vista 3D;
- campi numerici: un campo per asse con l'indice giusto, etichette con l'unità della scena (metri,
  centimetri, gradi, radianti), campo di rotazione coerente con il modo dell'oggetto, campo della
  scritta collegato ai dati del testo;
- duplicazione (geometria indipendente, stessa raccolta, copia scelta) ed eliminazione singola e
  multipla, fino alla scena vuota;
- vista iniziale (rotazione, distanza e tipo di vista ripristinati), inquadratura di un oggetto di
  cui si conoscono centro e raggio, inquadratura di tutta la scena e degli oggetti scelti, rifiuto di
  inquadrare un oggetto nascosto, vista dalla telecamera (e permanenza nella vista della telecamera);
- esistenza e funzionamento dei comandi nativi di navigazione (`view_all`, `view_axis`, …);
- cambio di disposizione dei pannelli (divisione di un'area in due Viste 3D), registrazione delle
  viste iniziali di tutte le disposizioni disponibili, avviso chiaro quando non esiste una Vista 3D;
- disegno dei sette pannelli (sei in modalità Semplice) e della testata sui dati veri: ogni pulsante esiste, ogni icona è fra
  quelle verificate, ogni campo è collegato a un dato esistente, nessun testo inglese di ripiego,
  nessun nome tecnico nella modalità Semplice;
- materiali veri creati dai valori dichiarati (colore, ruvidità, metallico, trasparenza e indice di
  rifrazione del vetro), un materiale indipendente per ogni applicazione, variazione che copia il
  materiale senza toccare quello di partenza, rifiuto di applicare un materiale a luci e telecamere;
- illuminazioni dei preset: numero di luci, potenza, direzione verso il centro della scena, sfondo
  impostato, sostituzione delle luci di FormaFacile e rispetto delle luci dell'utente, adattamento
  automatico alla grandezza della scena e limiti dell'intensità;
- telecamera: creazione, inquadratura calcolata, centratura senza spostare il cursore 3D, ripristino
  della posizione iniziale e rifiuto comprensibile per una telecamera senza posizione registrata;
- **immagine finale vera**: la qualità di anteprima usata per la prova scrive un PNG e un JPEG che
  vengono riaperti da Blender, con grandezza, formato e luminosità controllati; il nome del file
  contiene data e ora e finisce nella cartella scelta; i controlli precedenti rifiutano una cartella
  inesistente, un file al posto della cartella, una risoluzione esagerata e (dove la misura è
  disponibile) una richiesta di memoria impossibile; un salvataggio impossibile produce un errore in
  italiano e nessun file a metà; il file viene riletto per riconoscere un finto PNG;
- segnali di fine disegno: registrazione, rimozione, nessun accumulo e messaggio giusto per un lavoro
  finito o interrotto;
- elenco lungo (limite e avviso), ricerca per nome (con e senza risultati), messaggio recente e
  messaggio scaduto.

Non verificabile senza finestre (serve Blender grafico):

- il disegno vero dei pannelli sullo schermo e l'aspetto dei pulsanti;
- i suggerimenti al passaggio del mouse, il ridimensionamento della barra laterale e del testo;
- la navigazione con il mouse (rotellina, tasto centrale) e le scorciatoie da tastiera;
- il trascinamento delle maniglie con il mouse (le prove senza schermo verificano che lo strumento
  si attivi e che gli interruttori delle maniglie si riaccendano, non il movimento a schermo);
- l'annullamento interattivo: in modalità senza finestre la storia di Blender non è disponibile
  (`Undo disabled at startup in background-mode`), quindi le prove controllano che ogni comando che
  cambia i dati dichiari `REGISTER` e `UNDO` e che **Annulla**/**Ripeti** avvisino senza danni quando
  la storia non c'è;
- il cambio di spazio di lavoro con l'evento vero della finestra e la coesistenza con la testata
  nativa;
- la creazione dell'immagine dal pulsante con l'avanzamento di Blender nella finestra, l'interruzione
  con `Esc` e il messaggio di fine lavoro nella barra di stato (senza finestra il comando aspetta la
  fine del lavoro, ed è così che è stato verificato);
- l'anteprima del materiale disegnata da Blender dentro il pannello (`template_preview`) e il vetro
  visto davvero in modalità "Anteprima dell'immagine": i valori del materiale sono verificati, il
  disegno no;
- il motore EEVEE, che in questo ambiente senza schermo non si avvia.

## Verifiche manuali richieste

Dopo aver installato Blender 4.5.x LTS:

0. Apri `docs/VERIFICA_MANUALE.md`: è la checklist completa della vista, delle maniglie e del
   mouse, divisa per argomento (forme, maniglie, campi numerici, posizioni, blocco, copia e
   incolla, annullamento, oggetti non scelti, ridimensionamento).
1. Avvia `python3 scripts/avvia_formafacile.py` (oppure indica `--blender PERCORSO`).
2. Controlla la lingua italiana e la scheda **FormaFacile** nella barra laterale della Vista 3D.
3. Crea un cubo, una sfera e una luce; scegli, rinomina e nascondi un oggetto dall'elenco.
4. Premi **Annulla** e **Ripeti**, poi ripeti con `Ctrl+Z` e `Ctrl+Maiusc+Z`.
5. Passa da **Semplice** a **Completa** e controlla che i campi tecnici compaiano solo nella
   modalità completa.
6. Ridimensiona la finestra e la barra laterale e ingrandisci il testo del sistema.
7. Gira la vista con il tasto centrale, usa la rotellina e premi **Torna alla vista iniziale**.
8. Cambia disposizione dei pannelli (per esempio *Modeling* e *Rendering*) e riprova **Inquadra
   tutto**: nella disposizione senza Vista 3D deve comparire un avviso, non un errore.
9. Crea l'archivio ZIP con `python3 scripts/crea_pacchetto.py`, installalo da disco, attivalo,
   disattivalo e disinstallalo dalle preferenze.
10. Esegui `python3 scripts/controlla.py --test-blender` e conserva l'esito reale.
