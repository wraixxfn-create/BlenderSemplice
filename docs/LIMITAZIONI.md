# Limiti verificati della base attuale

Questa versione contiene lo scheletro necessario per avviare il pannello su Blender 4.5.x, ma non è ancora stata verificata con una distribuzione grafica completa; non è una prima versione completa.

## Funzioni presenti

- Programma di avvio configurabile, con controllo della serie Blender 4.5.x.
- Estensione Blender con metadati e registrazione/disattivazione pulite.
- Pannello italiano **FormaFacile 3D** nella barra laterale della Vista 3D.
- Un'azione reale: aggiunge un cubo, rinomina oggetto e geometria e consente l'annullamento tramite Blender.
- Controlli automatici senza dipendenze esterne e test d'integrazione predisposto per Blender.

## Funzioni non ancora presenti

Non sono ancora implementati un flusso di nuovo progetto, scene iniziali, forme ulteriori, trasformazioni semplificate, gerarchia, materiali, luce, camera, immagine finale, animazione, importazione/esportazione, procedure guidate o assistente di intelligenza artificiale. Non ci sono pulsanti fittizi per tali funzioni.

Il programma di avvio apre la scena iniziale di Blender e non sostituisce la schermata iniziale né crea uno spazio di lavoro personalizzato. Il punto di ingresso FormaFacile è il pannello della Vista 3D. Il salvataggio e la riapertura sono disponibili tramite i normali comandi di Blender, non attraverso un flusso FormaFacile dedicato.

## Verifica nell'ambiente di sviluppo

- Sistema rilevato: Debian GNU/Linux 12, Python 3.11.2.
- Il comando `blender` non è presente nel `PATH` e non è stata rilevata una distribuzione Blender grafica.
- Il pacchetto `bpy==4.5.14` è disponibile per Python 3.11, ma non è il programma Blender completo. Il tentativo di importarlo si ferma perché l'ambiente non contiene alcune librerie di sistema richieste (`libXrender`, `libXfixes`, `libXi`, `libxkbcommon`, `libSM`, `libICE` e `libGL`).
- Di conseguenza i controlli Python, struttura, manifesto e localizzazione possono essere eseguiti qui; l'operatore e la grafica devono ancora essere eseguiti con una distribuzione Blender completa.

## Verifiche manuali richieste

Dopo aver installato Blender 4.5.x LTS (supporto a lungo termine):

1. Avvia `python3 scripts/avvia_formafacile.py` (oppure indica `--blender`).
2. Controlla che Blender mostri l'interfaccia italiana e che la barra laterale della Vista 3D contenga la scheda **FormaFacile**.
3. Premi **Aggiungi cubo**, verifica il nome **Cubo**, poi prova **Annulla** e **Ripeti** con i comandi Blender.
4. Ridimensiona la finestra e controlla che pannello e testo restino leggibili.
5. Crea l'archivio ZIP, installalo da disco, disattivalo e disinstallalo dalle preferenze.
6. Esegui `python3 scripts/controlla.py --test-blender` e conserva l'esito reale.
