# FormaFacile 3D

FormaFacile 3D è un componente aggiuntivo per Blender pensato per offrire un punto di partenza più semplice, senza sostituire il motore 3D o la vista interattiva di Blender.

## Versioni supportate

- **Blender 4.5.x LTS (supporto a lungo termine)**; il riferimento di sviluppo è Blender **4.5.14**.
- **Python 3.11 o successivo** per il programma di avvio e i controlli del repository.
- Il programma richiede l'eseguibile completo di Blender. Il pacchetto Python `bpy` da solo non offre l'interfaccia grafica necessaria per usare l'applicazione.
- Per scaricare Blender, usa la pagina ufficiale delle versioni con supporto a lungo termine: <https://www.blender.org/download/lts/>.

## Avvio rapido

Con Blender 4.5.x installato e il comando `blender` disponibile nel `PATH` (l'elenco di cartelle in cui il sistema cerca i programmi):

```sh
python3 scripts/avvia_formafacile.py
```

Se Blender non è nel `PATH`, indica il percorso dell'eseguibile:

```sh
python3 scripts/avvia_formafacile.py --blender "/percorso/al/programma/blender"
```

In alternativa imposta la variabile d'ambiente `FORMAFACILE_BLENDER` oppure configura il file `config.ini` nella cartella di configurazione utente di FormaFacile 3D. Il programma di avvio cerca Blender nel `PATH`, nelle posizioni standard del sistema e nelle impostazioni esplicite; non dipende da un percorso personale fissato nel codice.

All'avvio viene registrato il componente aggiuntivo dalla copia del repository. Nella Vista 3D apri la barra laterale con `N` e scegli la scheda **FormaFacile**: trovi sei pannelli in modalità Semplice — **Azioni principali**, **La mia scena**, **Libreria di oggetti**, **Oggetto scelto**, **Dai forma** e **Dai un bell'aspetto alla scena** — e un settimo pannello tecnico, **Comandi di Blender**, nella modalità completa.

Nelle **Azioni principali** si creano **Cubo**, **Sfera**, **Cilindro**, **Cono**, **Piano**, **Ciambella**, **Testo** e **Luce**, con la grandezza regolabile da un solo campo; si annulla e si ripete, si torna alla vista iniziale e si inquadra la scena. In **La mia scena** c'è l'elenco degli oggetti: si sceglie per nome (anche con più oggetti), si rinomina, si nasconde, si blocca la scelta con il lucchetto e si cerca. Il pannello **Oggetto scelto** cambia con la scelta: sposta, ruota e ingrandisce a passi oppure con i campi numerici di posizione, rotazione e dimensione (con l'unità della scena); attiva le frecce, gli archi e i cubetti per lavorare con il mouse; porta al centro, appoggia sul piano, copia, incolla, duplica, elimina, inquadra l'oggetto, cambia la potenza della luce o guarda la scena dalla telecamera. Ogni azione lascia un messaggio breve in italiano e tutte le azioni che cambiano i dati si annullano con `Ctrl+Z`, perché usano la storia di Blender; i blocchi messi in Blender (asse bloccato, scelta bloccata) vengono sempre rispettati.

La **Libreria di oggetti** parte con dieci modelli costruiti da geometria Blender, non da immagini: **Tavolino**, **Scaffale**, **Sedia stilizzata**, **Piedistallo**, **Vaso cavo**, **Insegna con scritta**, **Stanza semplice**, **Pedana circolare**, **Set fotografico** e **Forme per stampa 3D**. Scegli il modello per leggere la descrizione, regola le misure e il colore e premi **Aggiungi alla scena**. Ogni inserimento crea una raccolta indipendente con parti dai nomi italiani; il testo dell'insegna resta modificabile come testo estruso. Le descrizioni spiegano quali parti sono mesh statiche: le misure configurano la geometria iniziale, poi i pezzi si modificano in Modalità Modifica ma le misure non restano collegate ai controlli. La generazione usa solo codice e risorse già incluse in Blender, senza modelli di terzi. La libreria è stata verificata con prove automatiche in modalità senza schermo, non è ancora stata provata visivamente nella Vista 3D o con un'immagine finale.

Nel pannello **Dai forma** ci sono gli strumenti guidati per ritoccare una forma senza parolone: **Ammorbidisci gli spigoli**, **Superficie liscia**, **Superficie a facce**, **Forma più arrotondata**, **Specchia**, **Ripeti le copie** (in fila o in cerchio), **Spessore della parete**, **Unisci o taglia** e **Trasforma in forma**. Ogni comando spiega prima che cosa farà, chiede solo i valori indispensabili (gli altri restano nella modalità completa), non cambia mai la forma di partenza — usa modifiche non applicate, che si tolgono tutte insieme con **Togli le modifiche** — e quando non può fare qualcosa lo dice, invece di fingere che sia riuscito. Accanto ci sono **Allinea**, **Spazia in modo uguale**, i **gruppi** (gli oggetti raccolti insieme si scelgono, si nascondono e si sciolgono con un clic) e la **guida passo passo**: **Inizia la guida** costruisce una casetta in 13 passi, dalla prima forma al gruppo finito, con **Indietro**, **Avanti**, **Esegui il passo** e **Chiudi**.

Nel pannello **Dai un bell'aspetto alla scena** la scena diventa bella da vedere, senza sapere come funziona un motore di creazione delle immagini. Ci sono **sei materiali pronti** con nomi italiani — plastica opaca, metallo, legno stilizzato, vetro, ceramica e gomma — un'**anteprima del materiale applicato**, una **tavolozza di colori** con il nome scritto accanto al campione e i campi **Colore**, **Ruvidità**, **Metallico** e **Trasparenza** (la trasparenza compare solo sui materiali che la prevedono, come il vetro). **Applica il materiale** dà il materiale agli oggetti scelti; siccome ogni oggetto riceve un materiale suo, cambiare l'aspetto di un oggetto non tocca gli altri. Se un materiale è usato da più oggetti il pannello lo dice e propone **Crea variazione**, che ne fa una copia indipendente prima di modificarlo.

**Illuminazione automatica** sistema luci e sfondo con valori prudenti, regolati sulla grandezza della scena; accanto ci sono le situazioni tipiche **Prodotto**, **Interno semplice**, **Esterno semplice** e **Studio neutro**, i campi **Colore di sfondo**, **Luminosità dello sfondo** e **Potenza delle luci**, e il pulsante **Applica sfondo e intensità**. Le luci create da FormaFacile stanno in una raccolta dedicata e vengono sostituite cambiando illuminazione: **le luci messe da te non vengono mai toccate**. **Aggiungi telecamera** crea una telecamera che inquadra la scena e diventa quella principale; **Inquadra con la telecamera** la avvicina agli oggetti scelti, **Centra la vista** porta al centro quello che hai scelto e **Ripristina la telecamera** la riporta dov'era. **Vista di lavoro** e **Anteprima dell'immagine** distinguono a colpo d'occhio i due modi di guardare la scena: colori semplici e disegno veloce, oppure materiali, luci e ombre.

**Crea immagine finale** salva un'immagine vera nella cartella scelta. La qualità si sceglie fra **Anteprima**, **Standard** e **Alta qualità** (la percentuale di risoluzione e i campioni sono scritti in chiaro nel pannello); nella modalità completa compaiono la percentuale di risoluzione, i campioni, il motore (**Come in Blender**, **EEVEE**, **Cycles**) e il formato (**PNG** o **JPEG**). Prima di iniziare il comando controlla che ci sia una telecamera, che la cartella esista e si possa scrivere, che la memoria libera basti e che l'immagine non sia enorme; poi in una finestra vera Blender mostra l'avanzamento e si può interrompere con `Esc`. Se qualcosa non va — memoria insufficiente, cartella non valida, motore non disponibile, errore di Blender — il messaggio è in italiano e dice che cosa fare. Il file creato viene riaperto da Blender per controllare che sia un'immagine vera: se non lo è, il comando lo dice invece di dichiarare un successo.

## Installazione del componente aggiuntivo

Per installare una copia indipendente dal programma di avvio:

1. Crea il pacchetto con `python3 scripts/crea_pacchetto.py`.
2. In Blender apri **Modifica → Preferenze → Estensioni** e usa il comando **Installa da disco** per selezionare `dist/formafacile_3d-0.4.0.zip`.
3. Attiva **FormaFacile 3D**, se Blender non l'ha già attivato.
4. Nella Vista 3D apri la barra laterale con `N` e seleziona **FormaFacile**.

I nomi dei menu possono variare leggermente in base alla traduzione installata di Blender. Il componente aggiuntivo usa etichette e messaggi propri in italiano e imposta l'italiano come lingua dell'interfaccia durante l'attivazione.

## Sviluppo e controlli

Non sono richieste librerie Python aggiuntive per i controlli di base:

```sh
python3 scripts/controlla.py
```

Per eseguire anche le prove del componente aggiuntivo con il modulo `bpy`, senza che serva Blender
grafico e senza installare nulla nel sistema:

```sh
python3 scripts/controlla.py --test-bpy
```

Il comando usa l'ambiente virtuale `.venv` se esiste e prepara nella cartella `.cache` alcune
librerie grafiche fittizie, necessarie soltanto per avviare il modulo senza schermo (vedi
`docs/SVILUPPO.md`).

Per eseguire le stesse prove con una distribuzione Blender 4.5.x completa:

```sh
python3 scripts/controlla.py --test-blender
```

Quel comando individua Blender con le stesse regole del programma di avvio e avvia Blender senza
finestre con il test `tests/blender/test_addon.py`. È anche possibile eseguire direttamente:

```sh
blender --background --factory-startup --python tests/blender/test_addon.py
```

Su Windows, se Python è installato tramite Python Launcher, usa `py -3` al posto di `python3`.

## Disinstallazione

- Se avvii la copia di sviluppo dal programma di avvio, chiudi Blender: non viene installato un componente aggiuntivo permanente.
- Se hai installato l'archivio ZIP, apri **Modifica → Preferenze → Estensioni → Installate**, seleziona **FormaFacile 3D** e usa **Disinstalla**; quindi riavvia Blender se richiesto.
- Per rimuovere la configurazione locale del programma di avvio, elimina il file `config.ini` dalla cartella di configurazione di FormaFacile 3D. Questa operazione non elimina i progetti `.blend`.

## Stato e limiti

Questa è la prima interfaccia utilizzabile, verificata automaticamente con il modulo `bpy` senza
schermo (5767 controlli) e con 269 prove di unità; **non è ancora stata provata su uno schermo**,
perché nell'ambiente di sviluppo non è installata una distribuzione Blender grafica. Restano da
provare a mano disegno dei pannelli, suggerimenti, ridimensionamento, navigazione con il mouse,
trascinamento delle maniglie e annullamento interattivo: la checklist da seguire è in
`docs/VERIFICA_MANUALE.md` e l'elenco dei limiti in `docs/LIMITAZIONI.md`.

La creazione dell'immagine finale è stata provata davvero, senza schermo: il file viene scritto,
riaperto da Blender e controllato (grandezza, formato e luminosità), anche nel caso in cui il
salvataggio fallisca. Restano da provare a mano soltanto il disegno dell'avanzamento nella finestra
di Blender e l'interruzione con `Esc`.

Non sono ancora presenti animazione, gerarchia fra oggetti, salvataggio e riapertura con un flusso
FormaFacile dedicato, importazione ed esportazione, altre guide passo passo oltre a quella della
casetta e assistente locale. Non ci sono pulsanti fittizi per queste funzioni. I pannelli non
rimpiazzano la schermata iniziale né la disposizione standard di Blender.

Consulta `docs/ARCHITETTURA.md` per il piano, `docs/LIMITAZIONI.md` per i limiti verificati,
`docs/REVISIONE_UX.md` per la revisione dei termini italiani e `docs/LICENZE.md` per le licenze.
