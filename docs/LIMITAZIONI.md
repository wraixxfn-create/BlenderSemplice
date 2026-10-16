# Limiti verificati della versione attuale

Questa versione è la prima interfaccia utilizzabile: creare forme, scegliere, rinominare,
nascondere, spostare a passi e con numeri esatti, ruotare, ingrandire, centrare, appoggiare sul
piano, bloccare la scelta, copiare e incollare, duplicare, eliminare, inquadrare, annullare e
ripetere. Le cose che seguono dicono che cosa non c'è, che cosa è stato verificato e che cosa va
ancora provato a mano.

## Funzioni presenti

- Programma di avvio configurabile, con controllo della serie Blender 4.5.x.
- Estensione Blender con metadati e registrazione/disattivazione pulite e ripetibili.
- Quattro pannelli italiani nella barra laterale della Vista 3D (**Azioni principali**, **La mia
  scena**, **Oggetto scelto**, **Comandi di Blender**) e un pulsante nella testata che apre la barra.
- Creazione di **Cubo**, **Sfera**, **Cilindro**, **Cono**, **Piano**, **Ciambella**, **Testo**
  e **Luce**, con nomi italiani per oggetto e geometria e posizione libera vicino al cursore 3D;
  la grandezza delle nuove forme si regola da un solo campo, che porta l'unità della scena.
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

## Funzioni non ancora presenti

Non ci sono ancora: materiali e colori semplificati, sfondo, anteprima e immagine finale,
animazione, gerarchia fra oggetti, salvataggio e riapertura con un flusso FormaFacile dedicato,
importazione ed esportazione, scene iniziali guidate, flussi passo passo e assistente di intelligenza
artificiale. **Non esistono pulsanti fittizi per queste funzioni**: i pannelli mostrano solo comandi
che hanno un effetto reale.

Il programma di avvio apre la scena iniziale di Blender e non sostituisce la schermata iniziale né
crea uno spazio di lavoro personalizzato. Il punto di ingresso di FormaFacile è la barra laterale
della Vista 3D. Salvataggio e riapertura usano i normali comandi di Blender.

## Verifica nell'ambiente di sviluppo

- Sistema rilevato: Debian GNU/Linux 12, Python 3.11.
- Il comando `blender` non è presente nel `PATH`: non c'è una distribuzione Blender grafica.
- Il pacchetto `bpy==4.5.14` è installato in un ambiente virtuale separato (`/.venv`, escluso dal
  repository). Non è l'applicazione completa, ma espone la stessa interfaccia di programmazione,
  quindi le prove di `tests/blender/test_addon.py` sono state **eseguite davvero**:
  `python3 scripts/controlla.py --test-bpy` (2810 controlli superati, più 134 prove di unità).
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
- disegno dei quattro pannelli e della testata sui dati veri: ogni pulsante esiste, ogni icona è fra
  quelle verificate, ogni campo è collegato a un dato esistente, nessun testo inglese di ripiego,
  nessun nome tecnico nella modalità Semplice;
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
  nativa.

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
