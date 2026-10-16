# Licenze e distribuzione

## Codice FormaFacile 3D

Il codice del componente aggiuntivo e il pacchetto iniziale dichiarano **GNU GPL versione 2 o successiva** (`GPL-2.0-or-later`). Il testo completo è nel file `LICENSE`. La scelta è coerente con l'esempio ufficiale di estensione Blender consultato per questa base; va riconfermata prima di pubblicare un prodotto completo o accettare contributi con condizioni differenti.

## Blender e componenti esterni

Blender non è incluso nel repository né nell'archivio ZIP: l'utente installa una distribuzione ufficiale separata. Il programma di avvio non scarica né modifica Blender.

Il codice dell'applicazione non dipende da pacchetti Python aggiuntivi. Durante l'analisi è stato scaricato solo nell'area temporanea di sviluppo un pacchetto `bpy==4.5.14` da PyPI per valutare i test delle interfacce di programmazione; non è incluso nei file del progetto, non viene impacchettato e non è necessario per l'utente finale.

## Modelli della libreria iniziale

I modelli sono generati da codice scritto nel progetto usando vertici, facce, curve di testo, materiali e luci creati tramite le API di Blender. Non sono inclusi modelli 3D, immagini, texture o font di terzi. L'insegna usa il font predefinito già fornito da Blender; non vengono distribuiti file di font separati. Il codice che genera la libreria resta coperto dalla licenza del progetto.

Prima di ogni distribuzione andranno controllati e documentati la licenza della specifica distribuzione Blender, le licenze di eventuali componenti aggiunti, i pesi di qualsiasi modello locale e gli obblighi di attribuzione e disponibilità del codice sorgente. Non distribuire pesi o binari di terzi senza averne verificato i termini.
