# Verifica manuale: vista, maniglie e mouse

Questa checklist copre le cose che **non si possono provare senza uno schermo**:
il disegno dei pannelli nella barra laterale, le maniglie (frecce, archi e
cubetti) nella Vista 3D, il mouse e l'annullamento interattivo. Le prove
automatiche (`python3 scripts/controlla.py --test-bpy`) verificano già la logica
dei comandi; qui si verifica quello che si vede e che si tocca.

Ambito: Blender **4.5.x LTS** con FormaFacile 3D attivo, interfaccia in
italiano. Apri la barra laterale della Vista 3D con `N` e scegli la scheda
**FormaFacile**.

Come registrare l'esito: ogni riga ha una casella da spuntare. Se una riga non
passa, annota il numero della prova, il pannello e il messaggio comparso nella
barra di stato.

## 1. Aggiungi forma

| # | Prova | Esito |
| --- | --- | --- |
| 1.1 | Premi **Cubo**, **Sfera**, **Cilindro**, **Cono**, **Piano**, **Ciambella**, **Testo** e **Luce**: ogni pulsante crea un oggetto e lo sceglie (contorno arancione). | ☐ |
| 1.2 | Ogni nuovo oggetto ha un nome italiano nell'elenco "La mia scena". | ☐ |
| 1.3 | Le forme non nascono una dentro l'altra: ogni nuova forma compare accanto alle esistenti. | ☐ |
| 1.4 | Il campo **Grandezza** mostra l'unità della scena fra parentesi (per esempio "Grandezza (m)"); scrivi `4` e premi di nuovo **Cubo**: il cubo nuovo è più grande. | ☐ |
| 1.5 | **Testo** crea una scritta in piedi (leggibile dalla vista iniziale), con il testo di esempio "Testo"; il campo **Scritta** nel pannello la modifica subito. | ☐ |
| 1.6 | In modalità Modifica (premi `Tab` su un oggetto) i pulsanti di creazione sono disattivati e il pannello invita a tornare con `Tab`. | ☐ |

## 2. Libreria di oggetti

| # | Prova | Esito |
| --- | --- | --- |
| 2.1 | Apri **Libreria di oggetti**, scorri l'elenco e seleziona ogni modello: descrizione, nomi e campi sono in italiano e cambiano in base al modello. | ☐ |
| 2.2 | Seleziona **Tavolino**, cambia larghezza, altezza, spessore, spessore delle gambe e colore; premi **Aggiungi alla scena** e controlla il piano e le quattro gambe nell'elenco. | ☐ |
| 2.3 | Seleziona **Scaffale** e cambia **Ripiani interni** da 1 a 5: il numero di ripiani creati deve seguire il valore scelto. | ☐ |
| 2.4 | Prova **Sedia stilizzata**, **Piedistallo**, **Vaso cavo**, **Stanza semplice** e **Pedana circolare**; cambia almeno una misura e controlla che le parti siano geometrie selezionabili. | ☐ |
| 2.5 | Seleziona **Insegna con scritta**, inserisci una parola, aggiungila e modifica poi il testo dalla modalità Modifica del testo; la scritta deve avere estrusione. | ☐ |
| 2.6 | Seleziona **Set fotografico** e **Forme per stampa 3D**: il primo deve includere un fondale curvo e tre luci di area, il secondo quattro forme separate. | ☐ |
| 2.7 | Tieni nella scena un oggetto creato prima, inserisci un modello, seleziona le sue parti dall'elenco e usa **Elimina**: l'oggetto preesistente deve restare invariato. | ☐ |
| 2.8 | Regola uno spessore in modo che non possa stare nella misura disponibile: l'inserimento deve fermarsi con un messaggio italiano e senza lasciare parti a metà. | ☐ |
| 2.9 | Controlla le descrizioni: indicano che le mesh sono statiche dopo l'inserimento e modificabili in Modalità Modifica; le misure iniziali non restano collegate ai controlli dopo l'inserimento. | ☐ |

## 3. Maniglie e trasformazioni con il mouse

| # | Prova | Esito |
| --- | --- | --- |
| 3.1 | Scegli un oggetto e premi **Frecce per spostare**: compaiono le frecce colorate sull'oggetto. | ☐ |
| 3.2 | Trascina una freccia: l'oggetto si muove lungo quell'asse; clicca (o premi Invio) per confermare, premi Esc per annullare. | ☐ |
| 3.3 | Premi **Frecce per ruotare**: compaiono gli archi; trascinane uno per ruotare l'oggetto. | ☐ |
| 3.4 | Premi **Frecce per ingrandire**: compaiono i cubetti e le linee; trascina per cambiare la dimensione. | ☐ |
| 3.5 | Se prima avevi spento le maniglie (menu a cascata **Overlays → Gizmo**), i tre pulsanti le riaccendono da sole. | ☐ |
| 3.6 | Dopo aver attivato una maniglia, la barra degli strumenti in alto a sinistra della Vista 3D mostra lo strumento attivo (Sposta, Ruota o Scala). | ☐ |
| 3.7 | I pulsanti **Sposta**, **Ruota**, **Ingrandisci** del gruppo "Muovi con il mouse" aprono gli stessi comandi con il mouse. | ☐ |

## 4. Campi numerici

| # | Prova | Esito |
| --- | --- | --- |
| 4.1 | Con un oggetto scelto, il pannello "Oggetto scelto" mostra **Posizione (m)** con tre campi X, Y e Z. | ☐ |
| 4.2 | Scrivi un numero in un campo e conferma con Invio: l'oggetto si sposta subito nella vista. | ☐ |
| 4.3 | **Rotazione (°)** mostra tre angoli in gradi; scrivere `45` in Z gira l'oggetto di 45 gradi. | ☐ |
| 4.4 | **Dimensione (m)** mostra la misura reale dell'oggetto sui tre assi. | ☐ |
| 4.5 | Cambia l'unità della scena in **Proprietà scena → Unità** (per esempio Centimetri): le etichette dei campi diventano "(cm)". | ☐ |
| 4.6 | Con l'oggetto in rotazione "Quaternione" o "Asse e angolo" (proprietà dell'oggetto), il pannello mostra il campo giusto invece dei tre angoli. | ☐ |
| 4.7 | Scegli due oggetti insieme (Maiusc + clic): i campi numerici scompaiono, perché vargono per un solo oggetto. | ☐ |
| 4.8 | Trascina il mouse sopra i campi: i suggerimenti (tooltip) sono in italiano. | ☐ |

## 5. Posizioni precise

| # | Prova | Esito |
| --- | --- | --- |
| 5.1 | Sposta un oggetto lontano e premi **Porta al centro**: torna a coordinate 0, 0, 0. | ☐ |
| 5.2 | Solleva un oggetto e premi **Appoggia sul piano**: la sua parte più bassa tocca la griglia. | ☐ |
| 5.3 | **Appoggia sul piano** non sposta l'oggetto in orizzontale. | ☐ |
| 5.4 | Scegli più oggetti: **Porta al centro** e **Appoggia sul piano** valgono per tutti. | ☐ |
| 5.5 | Blocca un asse in Proprietà oggetto → Sposta/Ruota/Scala (lucchetto): i comandi rispettano il blocco e il messaggio avvisa. | ☐ |

## 6. Blocco della scelta

| # | Prova | Esito |
| --- | --- | --- |
| 6.1 | Nell'elenco "La mia scena" ogni riga ha il lucchetto: premi quello di un oggetto e diventa chiuso. | ☐ |
| 6.2 | Un oggetto bloccato non si sceglie più cliccandolo nella Vista 3D. | ☐ |
| 6.3 | Premi di nuovo il lucchetto: l'oggetto torna scegliibile. | ☐ |
| 6.4 | Il pannello "Oggetto scelto" mostra **Sblocca la scelta** quando l'oggetto è bloccato. | ☐ |

## 7. Copia e incolla

| # | Prova | Esito |
| --- | --- | --- |
| 7.1 | Scegli un oggetto e premi **Copia**: il messaggio dice quanti oggetti sono stati copiati. | ☐ |
| 7.2 | Premi **Incolla**: compare una copia dell'oggetto e il messaggio lo dice. | ☐ |
| 7.3 | Dopo aver svuotato la scena (o in un nuovo file), premi **Incolla** senza aver copiato: compare "Non c'è nulla da incollare: prima usa Copia." | ☐ |
| 7.4 | Ciò che copi con FormaFacile si incolla anche con Ctrl+V di Blender, e viceversa. | ☐ |

## 8. Annullamento interattivo

| # | Prova | Esito |
| --- | --- | --- |
| 8.1 | Crea un oggetto, poi premi `Ctrl+Z`: l'oggetto sparisce; `Ctrl+Maiusc+Z` lo rimette. | ☐ |
| 8.2 | Sposta con i pulsanti di passo, poi `Ctrl+Z`: la posizione torna. | ☐ |
| 8.3 | Annulla funziona anche dopo **Porta al centro**, **Appoggia sul piano**, **Duplica**, **Rinomina**, **Nascondi** e **Blocca la scelta**. | ☐ |
| 8.4 | Annulla dopo un incolla toglie l'oggetto incollato. | ☐ |
| 8.5 | I pulsanti **Annulla** e **Ripeti** del pannello si comportano come `Ctrl+Z` e `Ctrl+Maiusc+Z`. | ☐ |
| 8.6 | Attivare le frecce (sezione 3) NON compare nella storia: `Ctrl+Z` dopo una maniglia non "annulla" le frecce. | ☐ |

## 9. Rispetto degli oggetti non scelti

| # | Prova | Esito |
| --- | --- | --- |
| 9.1 | Metti due oggetti nella scena, scegline uno: sposta, ruota, ingrandisci, centra, appoggia, duplica, nascondi e blocca. L'altro oggetto non cambia mai. | ☐ |
| 9.2 | Con più oggetti scelti, l'oggetto attivo (evidenziato nel pannello) resta lo stesso dopo ogni comando di trasformazione. | ☐ |
| 9.3 | Elimina con più oggetti scelti chiede conferma prima di eliminare. | ☐ |

## 10. Ridimensionamento della barra

| # | Prova | Esito |
| --- | --- | --- |
| 10.1 | Allarga e restringi la barra laterale: i campi numerici restano leggibili e le righe non si spezzano. | ☐ |
| 10.2 | Ripeti le sezioni 1, 2 e 3 con la barra stretta al minimo. | ☐ |

## 11. Strumenti guidati, gruppi e guida della casetta

| # | Prova | Esito |
| --- | --- | --- |
| 11.1 | Con un cubo scelto premi **Ammorbidisci gli spigoli**: compare la finestrella con la spiegazione e i campi essenziali; conferma e guarda gli spigoli arrotondati. | ☐ |
| 11.2 | Sulla stessa forma premi **Superficie liscia** e poi **Superficie a facce**: cambia solo l'aspetto, il contorno non si muove. | ☐ |
| 11.3 | Premi **Specchia** e sposta nella vista l'oggetto **Specchio** (un segnaposto vuoto): il lato rispecchiato si sposta con lui. | ☐ |
| 11.4 | Premi **Ripeti le copie** in fila: le copie sono una serie regolabile; in cerchio: le copie si possono scegliere una per una. | ☐ |
| 11.5 | Scegli due forme che si sovrappongono e premi **Unisci o taglia** con **Unisci** e poi con **Taglia**: l'attrezzo sparisce dalla vista ma resta nell'elenco. | ☐ |
| 11.6 | Con una sola forma scelta (o con tre) premi **Unisci o taglia**: compare la spiegazione, non un errore tecnico. | ☐ |
| 11.7 | Dopo uno degli strumenti premi **Togli le modifiche**: la forma torna esattamente com'era, senza usare `Ctrl+Z`. | ☐ |
| 11.8 | Scegli tre forme sparse e premi **Spazia in modo uguale**: la distanza fra loro diventa la stessa; cambia **Asse** e **Bordo** e riprova con **Allinea**. | ☐ |
| 11.9 | Scegli due forme e premi **Raggruppa**: il gruppo compare nell'elenco e con **Scegli il gruppo** si scelgono tutte insieme. | ☐ |
| 11.10 | Premi **Inizia la guida** e poi **Esegui il passo** tredici volte: la casetta viene costruita e il pannello arriva a **Guida completata** senza proporre altri passi. | ☐ |
| 11.11 | Durante la guida premi **Indietro** e **Avanti** per rileggere i passi, poi **Chiudi**: la scena resta com'è. | ☐ |
| 11.12 | Premi **Esegui il passo** con la guida chiusa: compare un avviso in italiano, non un errore tecnico. | ☐ |

## Riferimenti delle prove automatiche

Le stesse funzionalità sono verificate senza schermo da
`tests/blender/test_addon.py` (esecuzione: `python3 scripts/controlla.py
--test-bpy`), che controlla la logica dei comandi, i blocchi degli assi, la
scelta, i messaggi in italiano e il disegno dei pannelli su un blocco finto.
Questa checklist copre il resto: ciò che si vede e che si tocca.
