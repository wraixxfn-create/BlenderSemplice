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

All'avvio viene registrato il componente aggiuntivo dalla copia del repository. Nella Vista 3D apri la barra laterale con `N` e scegli la scheda **FormaFacile**. Il pulsante **Aggiungi cubo** crea un cubo reale, rinominato **Cubo**, e consente di annullare l'azione con Blender.

## Installazione del componente aggiuntivo

Per installare una copia indipendente dal programma di avvio:

1. Crea il pacchetto con `python3 scripts/crea_pacchetto.py`.
2. In Blender apri **Modifica → Preferenze → Estensioni** e usa il comando **Installa da disco** per selezionare `dist/formafacile_3d-0.1.0.zip`.
3. Attiva **FormaFacile 3D**, se Blender non l'ha già attivato.
4. Nella Vista 3D apri la barra laterale con `N` e seleziona **FormaFacile**.

I nomi dei menu possono variare leggermente in base alla traduzione installata di Blender. Il componente aggiuntivo usa etichette e messaggi propri in italiano e imposta l'italiano come lingua dell'interfaccia durante l'attivazione.

## Sviluppo e controlli

Non sono richieste librerie Python aggiuntive per i controlli di base:

```sh
python3 scripts/controlla.py
```

Per eseguire anche il test reale dell'operatore in Blender 4.5.x:

```sh
python3 scripts/controlla.py --test-blender
```

Il secondo comando individua Blender con le stesse regole del programma di avvio e avvia Blender senza finestre con il test `tests/blender/test_addon.py`. È anche possibile eseguire direttamente:

```sh
blender --background --factory-startup --python tests/blender/test_addon.py
```

Su Windows, se Python è installato tramite Python Launcher, usa `py -3` al posto di `python3`.

## Disinstallazione

- Se avvii la copia di sviluppo dal programma di avvio, chiudi Blender: non viene installato un componente aggiuntivo permanente.
- Se hai installato l'archivio ZIP, apri **Modifica → Preferenze → Estensioni → Installate**, seleziona **FormaFacile 3D** e usa **Disinstalla**; quindi riavvia Blender se richiesto.
- Per rimuovere la configurazione locale del programma di avvio, elimina il file `config.ini` dalla cartella di configurazione di FormaFacile 3D. Questa operazione non elimina i progetti `.blend`.

## Stato e limiti

Questa è una base tecnica iniziale, non una versione completa né ancora verificata con Blender grafico: include il pannello italiano e un'azione che usa le funzioni reali di Blender per aggiungere un cubo. Materiali, procedure guidate, luci, camera, creazione dell’immagine finale, gestione del progetto e assistente locale non sono ancora implementati. Il pannello del componente aggiuntivo è il punto di benvenuto; per ora non rimpiazza la schermata iniziale o la disposizione standard di Blender.

Consulta `docs/ARCHITETTURA.md`, `docs/LIMITAZIONI.md` e `docs/LICENZE.md` per il piano, i limiti verificati e le note sulle licenze.
