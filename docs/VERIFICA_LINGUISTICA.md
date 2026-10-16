# Verifica della lingua italiana

## Dove stanno i testi

La risorsa `addon/formafacile_3d/localization.py` contiene tutti i testi visibili: etichette e
suggerimenti dei comandi, titoli dei pannelli, messaggi di stato, avvisi di errore, testi del
programma di avvio e dei controlli. I moduli dei pannelli e degli operatori non contengono etichette
scritte a mano. Il numero di testi centrali è controllato dalle prove e cresce con le funzioni: nella
versione attuale sono oltre 300.

La revisione dei termini — quali parole tecniche sono state sostituite da parole italiane più
semplici, quali restano e perché — è in `docs/REVISIONE_UX.md`.

## Controlli automatici

```sh
python3 scripts/controlla.py            # include le prove di localizzazione
python3 scripts/controlla.py --test-bpy # include i testi dei comandi veri, dentro bpy
```

Che cosa viene controllato:

- **completezza**: ogni testo è presente, non vuoto e senza spazi esterni; ogni chiave usata nel
  codice esiste davvero (nessun refuso nascosto) e ogni chiave dichiarata è nominata da qualche parte
  (nessun testo dimenticato dopo una rinomina);
- **niente inglese di ripiego**: né i testi centrali né la documentazione contengono le parole
  inglesi di comodo usate di solito come promemoria (l'elenco è nel controllo automatico: comandi di
  salvataggio, annullamento, messaggi di guasto generici e inviti generici di benvenuto);
- **centralizzazione**: i moduli dei pannelli non contengono etichette visibili scritte a mano e
  ogni comando registrato ha etichetta e descrizione che provengono dalla mappa centrale, anche
  quando contengono numeri formattati (per esempio "Sposta di 0,5 m verso destra, lungo l'asse X.");
- **tabelle**: le tabelle dei comandi (direzioni, versi di rotazione, versi della dimensione, tipi di
  oggetto) puntano a chiavi esistenti;
- **lunghezza**: le etichette e i pulsanti rispettano i limiti pensati per la barra laterale
  (`LUNGHEZZA_MASSIMA_ETICHETTA`, `LUNGHEZZA_MASSIMA_AZIONE`, `LUNGHEZZA_MASSIMA_AZIONE_SINGOLA`);
- **disegno vero**: dentro `bpy` le prove disegnano i quattro pannelli sui dati reali della scena e
  controllano che ogni testo disegnato sia italiano e che ogni icona usata sia fra quelle verificate.

Il controllo automatico è un filtro, non una prova completa della qualità linguistica.

## Revisione manuale

Quando Blender 4.5.x è disponibile, controllare:

- i quattro pannelli della scheda **FormaFacile** nella Vista 3D e il pulsante nella testata;
- i suggerimenti che compaiono passando il mouse su ogni pulsante;
- i messaggi che seguono le azioni: "Aggiunto: Cubo", "Nome cambiato in Albero", "Nascosto: Sfera",
  "Vista su Albero.", "Non ci sono oggetti visibili da scegliere.", "Scelto e di nuovo visibile: …";
- i messaggi di avviso: nome vuoto rifiutato, oggetto bloccato, oggetto nascosto, disposizione senza
  Vista 3D, storia non disponibile;
- i messaggi del programma di avvio quando Blender manca, il percorso è errato o la versione non è
  supportata;
- l'interfaccia standard di Blender dopo l'attivazione della lingua italiana;
- leggibilità e taglio delle etichette a finestre piccole e con ingrandimento del sistema.

La revisione visiva non è stata ancora eseguita perché nell'ambiente corrente manca una distribuzione
Blender grafica: i testi sono stati verificati sui dati veri ma disegnati su un blocco di interfaccia
finto. Le traduzioni dell'interfaccia standard dipendono dai file lingua forniti dalla distribuzione
ufficiale di Blender.
