# Revisione dell'esperienza d'uso e dei termini

Questa revisione riguarda la prima interfaccia utilizzabile di FormaFacile 3D: quella
descritta come "Spazio di lavoro per principianti e interfaccia di base". Serve a spiegare,
in modo verificabile, **quali termini tecnici sono stati sostituiti da parole italiane più
semplici e quali invece restano**, con la ragione di ogni scelta.

## Che cosa vede un principiante

Nella barra laterale della Vista 3D (tasto `N`) compare la scheda **FormaFacile**, con cinque
pannelli in modalità Semplice e il sesto pannello tecnico nella modalità Completa:

| Pannello | Che cosa contiene | Perché è lì |
| --- | --- | --- |
| **Azioni principali** | gruppi *Costruisci* (Cubo, Sfera, Cilindro, Cono, Piano, Ciambella, Testo, Luce, con il campo *Grandezza*), *Annulla e ripeti*, *Guarda la scena* (Torna alla vista iniziale, Inquadra tutto), *Consigli*, e la riga del messaggio appena successo | sono le azioni che si cercano per prime; Undo e Redo stanno sempre a portata, anche a scena vuota |
| **La mia scena** | conteggio in parole ("3 oggetti, 1 scelto"), ricerca per nome quando gli oggetti sono più di otto, *Tutti*, *Nessuno*, *Inverti*, *Stesso tipo*, elenco con una riga per oggetto | sostituisce l'elenco oggetti di Blender senza la sua gerarchia tecnica: qui si sceglie, si rinomina e si nasconde |
| **Libreria di oggetti** | dieci modelli geometrici; selezione, descrizione, campi di misura e colore, pulsante per inserire una raccolta nuova | mostra prima le dimensioni e il tipo di geometria; dichiara quali parti sono geometrie statiche dopo la creazione |
| **Dai forma** | strumenti guidati, modifiche non applicate, gruppi e guida passo passo | presenta i comandi di ritocco in parole semplici |
| **Oggetto scelto** | si adatta alla scelta: nessuna scelta, un oggetto, più oggetti | è il pannello che risponde alla domanda "che cosa posso fare adesso?" |
| **Comandi di Blender** | solo nella modalità **Completa**: nome dei dati, posizione, rotazione, dimensione, aspetto, blocco della scelta, nascondi nell'immagine finale, potenza della luce | chi vuole il controllo fine lo trova, ma non lo incontra per caso |

La testata della Vista 3D riceve un solo pulsante in più, **FormaFacile**, che apre la barra
laterale. La testata nativa non viene sostituita: FormaFacile si aggiunge.

Ogni azione lascia un **messaggio breve** nel pannello e, quando la disposizione dei pannelli lo
permette, nella barra di stato: "Aggiunto: Cubo", "Nascosto: Sfera", "Vista su Albero.",
"Non ci sono oggetti visibili da scegliere." I messaggi non contengono numeri di errore né
nomi di funzioni.

## Parole tecniche sostituite

| In Blender o nel codice | In FormaFacile | Perché |
| --- | --- | --- |
| `Add Mesh` → `Cube`, `UV Sphere`, `Cylinder`, `Cone`, `Plane`, `Torus`; `Add Text`; `Add Light` | **Cubo**, **Sfera**, **Cilindro**, **Cono**, **Piano**, **Ciambella**, **Testo**, **Luce** | il nome della forma basta: "primitive" e "mesh" non aggiungono nulla a chi comincia; "Ciambella" è più immediata di "toro", che in italiano dice altro |
| `Object`, `Empty` (come *tipo* di oggetto) | **Forma**, **Oggetto** | "Forma" è la parola che un principiante usa; il tipo tecnico compare solo nel pannello dei comandi di Blender |
| `Object Mode` / `Edit Mode` | **modalità Oggetto** / **modalità Modifica** | sono due parole già italiane: cambiano solo l'ordine, e la frase "Prima torna alla modalità Oggetto con Tab." dice cosa fare |
| `Hide in Viewport` / `Unhide` / icona a occhio | **Nascondi** / **Mostra** / **Mostra tutti gli oggetti** | l'occhio si capisce solo dopo averlo imparato; il verbo no |
| `Select All`, `Deselect All`, `Invert Selection` | **Tutti**, **Nessuno**, **Inverti** | verbi brevi, nessun "select" da sciogliere |
| `Select Grouped by Type` / `Select Same Type` | **Stesso tipo** | dice l'effetto, non il meccanismo |
| `Frame All`, `Frame Selected`, `Zoom to Object` | **Inquadra tutto**, **Inquadra la scelta**, **Inquadra l'oggetto** | "frame" e "zoom to" non sono italiani e non dicono che cosa succede |
| `Align View to Selected`, `Set Active Object as Camera`, `Camera View` | **Guarda dalla telecamera**, **Usa come telecamera principale** | "Guarda dalla telecamera" è l'effetto voluto; la seconda dice quando serve |
| `Move` (`G`), `Rotate` (`R`), `Scale` (`S`) | **Sposta di poco**, **Ruota di poco**, **Ingrandisci o rimpicciolisci** con i pulsanti **Sinistra**, **Destra**, **Su**, **Giù**, **Avanti**, **Indietro**, **Gira a sinistra**, **Gira a destra**, **Più grande**, **Più piccolo**; e i campi **Posizione**, **Rotazione**, **Dimensione** con l'unità della scena | niente lettere da memorizzare: ogni clic fa un passo definito, e chi vuole il numero esatto lo scrive, con l'unità scritta accanto |
| `Axis X/Y/Z` | **Sinistra, destra, su, giù, avanti, indietro** | "asse X" richiede di immaginare gli assi; i punti di vista della stanza no |
| `Outliner`, `Collection`, `Scene Collection` | **Oggetti della scena**, conteggio in parole, **gruppo** solo dove serve | l'elenco piatto è una scelta precisa: la gerarchia si aggiungerà quando ci sarà un motivo |
| `Undo History`, `Redo` | **Annulla**, **Ripeti** (con il promemoria `Ctrl+Z` e `Ctrl+Maiusc+Z` nei suggerimenti) | due parole già italiane e già usate da ogni programma |
| `Mesh data`, `Object data`, `energy`, `location`, `rotation_mode`, `scale`, `display_type`, `hide_select`, `hide_render` | **Geometria di …**, **Dati dell'oggetto**, **Potenza**, **Posizione**, **Modo di rotazione**, **Rotazione**, **Dimensione**, **Aspetto**, **Blocca la scelta**, **Nascondi nell'immagine finale** | sono i nomi dei campi del pannello avanzato: restano tradotti perché anche lì la parola descrive il risultato |
| `Item` (scheda laterale di Blender) | **le schede di Blender** | il nome della scheda cambia con la traduzione installata: meglio non citarlo |
| `Bevel` | **Ammorbidisci gli spigoli** | dice l'effetto su una forma di tutti i giorni; "smusso" e "bevel" non aiutano chi comincia |
| `Shade Smooth`, `Shade Flat`, `Subdivision Surface` | **Superficie liscia**, **Superficie a facce**, **Forma più arrotondata** | distingue l'aspetto (illuminazione) dall'aggiunta di geometria, che è la confusione più frequente |
| `Mirror` | **Specchia**, con il segnaposto **Specchio** | verbo italiano; il piano è un oggetto che si vede e si sposta, non un numero da ricordare |
| `Array` | **Ripeti le copie** in **fila** o in **cerchio**, con **Quante copie** e **Distanza** | "array" è gergo di programmazione |
| `Solidify` | **Spessore della parete** | descrive il risultato su una superficie sottile |
| `Boolean` con `Difference`, `Union`, `Intersect` | **Unisci o taglia**, con **forma principale** e **attrezzo** | toglie "booleana", "differenza" e "intersezione" dalla scelta e dice chi fa cosa |
| `Modifier`, `Apply` | **modifica** (non applicata) e **Togli le modifiche** | si toglie una modifica invece di applicarla: la forma di partenza resta sempre disponibile |
| `Workspace`, `Screen`, `Area` | **disposizione dei pannelli** | compare solo nella documentazione, dove "spazio di lavoro" sarebbe ambiguo con il nostro "spazio di lavoro per principianti" |

## Parole tecniche che restano, e perché

- **Blender**: FormaFacile è un componente aggiuntivo di Blender e non lo nasconde. Fingere che
  Blender non esista renderebbe impossibile spiegare i file `.blend`, la barra laterale o i tasti.
- **Vista 3D, scena, oggetto, luce, telecamera, forma, modalità**: parole italiane di uso comune
  nel settore, già presenti nell'interfaccia tradotta di Blender; sostituirle creerebbe un
  vocabolario isolato.
- **Annulla, Ripeti, Passo, Cerca, Elimina, Duplica, Visibilità, Copia, Incolla**: termini brevi
  e comprensibili.
- **Maniglie, frecce, archi, cubetti**: sono le parole con cui la documentazione di Blender
  descrive i gizmo; "maniglia" dice subito che cosa si trascina, e i pulsanti spiegano comunque
  l'effetto (**Frecce per spostare**, **Frecce per ruotare**, **Frecce per ingrandire**).
- **Piano di lavoro**: la griglia su cui poggiano gli oggetti; **Appoggia sul piano** dice
  l'effetto meglio di "snap to ground" o "allinea al suolo".
- **Tipo tecnico: `MESH`, `LIGHT`, `CAMERA`** e i campi tecnici dell'oggetto: compaiono **solo**
  nella modalità **Completa**, con un promemoria che lo dice ("Modalità completa: compaiono anche
  i comandi tecnici."). Chi vuole un ponte verso la documentazione di Blender lo trova; chi non lo
  vuole non lo vede.
- **Tasti e scorciatoie** (`Ctrl+Z`, `Ctrl+Maiusc+Z`, `N`, `Tab`) e il tasto centrale del mouse:
  restano nella forma in cui appaiono su tastiera, perché tradurli li renderebbe irriconoscibili.
- **`Geometria di …`** per il blocco dei dati: è un nome, non un'etichetta di comando; dà un'idea
  di che cosa viene rinominato insieme all'oggetto.

## Che cosa è stato evitato per non perdere affidabilità

Le stesse regole del progetto dicono di preferire l'affidabilità a un'interfaccia personalizzata
quando una semplificazione darebbe fastidio a una funzione importante. Qui la scelta è stata:

1. **Nessuna scorciatoia rimappata.** Rotellina, tasto centrale, `Ctrl+Z`, `Tab`, `N` e la
   navigazione nativa restano quelli di Blender (le prove verificano che gli operatori nativi di
   navigazione esistono ancora e funzionano).
2. **Annulla e Ripeti richiamano la storia di Blender**, non una storia interna: ogni comando che
   cambia i dati dichiara `bl_options = {"REGISTER", "UNDO"}` e le prove lo controllano comando
   per comando.
3. **Nessun pulsante finto.** Il pannello mostra solo comandi che esistono e che hanno effetto:
   per esempio "Mostra" compare solo quando il nascondimento dipende dall'oggetto, mentre se è il
   gruppo a nasconderlo compare una spiegazione invece di un pulsante che non funzionerebbe.
4. **Pannelli nella barra laterale, non uno spazio di lavoro sostitutivo**: la scena, la vista e le
   funzioni native restano esattamente dove sono. "Torna alla vista iniziale" usa prima gli
   operatori nativi (`view3d.view_all`, `view3d.view_selected`) e solo se non sono disponibili
   ricalcola gli stessi valori dai dati della scena.
5. **La vista iniziale è un insieme di numeri** (rotazione, distanza, tipo di vista) registrato per
   ogni disposizione dei pannelli: nessun riferimento a finestre che potrebbero sparire, quindi
   nessun errore quando si cambia disposizione o si chiude una finestra.
6. **Blender non tiene scelto un oggetto che non si vede.** Comportamento verificato: nascondendo
   un oggetto (con l'occhio, con "Nascondi nella vista" o nascondendo il suo gruppo) Blender toglie
   anche la scelta. FormaFacile lo rispetta e non promette il contrario: le scelte di gruppo
   lasciano fuori gli oggetti nascosti e il messaggio dice quanti ne ha saltati
   ("… Non scegliabili: 2."). Scegliendo un oggetto nascosto **per nome dall'elenco**, FormaFacile
   lo fa prima ricomparire e lo dice nel messaggio ("Scelto e di nuovo visibile: Cubo"): è l'unico
   modo perché quel clic abbia un effetto.
7. **Elenco limitato e ricerca**: con molti oggetti l'elenco si ferma al limite dichiarato e lo
   scrive ("Mostrati 12 di 16 oggetti: usa Cerca."), così il pannello non diventa lento né
   inutilizzabile.

## Parole scelte per l'aspetto della scena e l'immagine finale

| Termine tecnico | Parola usata nel pannello | Perché |
| --- | --- | --- |
| Materiale di esempio / preset | **Materiale pronto** | Dice che è già configurato e che non serve sapere che cos'è un nodo. |
| Base Color | **Colore** | Il colore si vede: non serve il nome tecnico dell'ingresso. |
| Roughness | **Ruvidità** | Parola italiana comune, con il suggerimento che spiega i due estremi. |
| Metallic | **Metallico** | Aggettivo italiano; il suggerimento dice che cosa cambia. |
| Transmission / Alpha | **Trasparenza** | Una parola sola per due dati tecnici, spiegata dal suggerimento. |
| HDRI / Environment | **Colore di sfondo** e **Luminosità dello sfondo** | Si sceglie un colore e quanto illumina, non un'immagine da scaricare. |
| Light / Sun / Area Light | **Luce**, **Sole**, **Luce dal soffitto**, **Luce dalla finestra** | I nomi delle luci dei preset dicono da dove arrivano. |
| Nome del comando di Blender per creare l'immagine | **Immagine finale** | È quello che l'utente vuole ottenere: un'immagine. La parola inglese resta solo nel codice e nei nomi dei comandi nativi. |
| Samples | **Campioni** | Parola italiana del linguaggio tecnico, mostrata solo in modalità Completa con la spiegazione. |
| Resolution % | **Risoluzione** | Con il simbolo di percentuale di Blender accanto al campo. |
| Engine | **Motore** | Parola italiana, spiegata dai nomi **Come in Blender**, **EEVEE (veloce)**, **Cycles (preciso)**. |
| File Format | **Formato** | Con i nomi **PNG** e **JPEG**, che sono nomi propri di formato. |
| Denoise | (non mostrato) | Il disturbo si toglie da solo con la qualità scelta: non è una scelta da principianti. |
| Working viewport / Rendered preview | **Vista di lavoro** e **Anteprima dell'immagine** | I due pulsanti si escludono a vicenda e il pannello scrive che cosa si sta guardando. |

I nomi dei motori (**EEVEE**, **Cycles**), dei formati (**PNG**, **JPEG**) e delle funzioni della
tastiera (`Esc`) restano come sono: sono nomi propri di Blender e tradurli confonderebbe chi cerca la
stessa voce altrove.

## Termini inglesi ancora presenti nel codice (non nell'interfaccia)

Restano in inglese solo i nomi interni che Blender stesso usa e che l'utente non vede:
`bpy.ops.mesh.primitive_uv_sphere_add`, `hide_viewport`, `matrix_basis`, `bl_space_type`,
`REGISTER`/`UNDO`, i nomi dei file `.blend`. Scriverli tradotti renderebbe il codice incompatibile
con Blender e con la sua documentazione.

## Verifica automatica di queste scelte

- `tests/unit/test_piano.py` controlla che i pannelli contengano i gruppi e le parole previste, che
  le etichette rispettino i limiti di lunghezza e che i nomi tecnici compaiano **solo** nella
  modalità Completa.
- `tests/unit/test_localization.py` controlla che i testi provengano dalla mappa centrale, che non
  contengano segnaposto inglesi e che ogni chiave dichiarata sia nominata da qualche parte.
- `tests/blender/test_addon.py` (eseguibile con `python3 scripts/controlla.py --test-bpy`) disegna i
  pannelli sui dati veri della scena, controlla che ogni pulsante esista davvero, che ogni icona sia
  fra quelle verificate, che ogni suggerimento provenga dalla mappa centrale e che il
  comportamento promesso (Mostra, Annulla, inquadrature, modalità) avvenga per davvero.

## Verifica manuale ancora necessaria

Nessun controllo automatico può guardare uno schermo. La checklist completa, divisa per
argomento, sta in `docs/VERIFICA_MANUALE.md`. In sintesi, in Blender 4.5.x grafico vanno ancora
provati a mano:

1. la scheda **FormaFacile** nella barra laterale, con i sei pannelli semplici e il pannello tecnico visibile solo in modalità Completa;
2. il passaggio fra **Semplice** e **Completa** e la chiusura del pannello tecnico;
3. il passaggio del mouse sui pulsanti per leggere i suggerimenti;
4. `Ctrl+Z` e `Ctrl+Maiusc+Z` dopo una creazione, una rinomina e un nascondimento;
5. il ridimensionamento della finestra e della barra laterale, con il testo del sistema ingrandito;
6. la navigazione con il tasto centrale e la rotellina, per confermare che nulla è stato rimappato;
7. il cambio di disposizione dei pannelli (per esempio *Modeling* o *Rendering*) e il ritorno alla
   vista iniziale in una disposizione che non ha una Vista 3D (deve comparire l'avviso, non un
   errore);
8. un oggetto nascosto scelto dall'elenco **di Blender** (Outliner) mentre è nascosto: in quel caso
   il pannello contestuale deve spiegare che l'oggetto è nascosto e proporre **Mostra**;
9. l'anteprima del materiale dentro il pannello (disegnata da Blender), il vetro visto in **Anteprima
   dell'immagine** e la differenza a colpo d'occhio fra **Vista di lavoro** e **Anteprima**;
10. la creazione dell'immagine finale dalla finestra, con l'avanzamento di Blender, l'interruzione con
    `Esc` e il messaggio di fine lavoro nella barra di stato.
