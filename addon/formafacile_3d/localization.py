"""Testi italiani del componente aggiuntivo e degli strumenti di avvio.

Questo file è l'unica risorsa dei testi visibili all'utente: i moduli
dell'interfaccia e i comandi richiamano le chiavi, non scrivono frasi. I messaggi
sono brevi e senza accordi di genere ambigui, perché valgono per oggetti di
qualsiasi tipo.
"""

from __future__ import annotations

from types import MappingProxyType


TESTI = MappingProxyType(
    {
        # Interfaccia del componente aggiuntivo.
        "NOME_ESTENSIONE": "FormaFacile 3D",
        "AUTORE_ESTENSIONE": "Contributori di FormaFacile 3D",
        "POSIZIONE_ESTENSIONE": "Vista 3D > Barra laterale > FormaFacile",
        "DESCRIZIONE_ESTENSIONE": "Strumenti essenziali in italiano per iniziare con le scene 3D.",
        "CATEGORIA_PANNELLO": "FormaFacile",
        "ERRORE_REGISTRAZIONE": "Registrazione del componente aggiuntivo non riuscita.",
        "LOG_COMPONENTE_REGISTRATO": "Componente aggiuntivo registrato.",
        "LOG_COMPONENTE_DISATTIVATO": "Componente aggiuntivo disattivato.",
        "ERRORE_LINGUA_ITALIANA": "Non è stato possibile attivare l'interfaccia italiana di Blender.",
        "AVVIO_COMPONENTE_RIUSCITO": (
            "FormaFacile è pronto. Apri la scheda FormaFacile nella barra laterale della Vista 3D."
        ),
        "AVVIO_COMPONENTE_FALLITO": "FormaFacile non è stato caricato. Controlla la console di Blender.",
        # Titoli dei pannelli.
        "TITOLO_PANNELLO_PRINCIPALE": "Azioni principali",
        "TITOLO_PANNELLO_SCENA": "La mia scena",
        "TITOLO_PANNELLO_OGGETTO": "Oggetto scelto",
        "TITOLO_PANNELLO_COMPLETO": "Comandi di Blender",
        "TITOLO_PANNELLO_MODELLA": "Dai forma",
        # Modalità.
        "ETICHETTA_MODALITA": "Modalità",
        "MODALITA_SEMPLICE": "Semplice",
        "MODALITA_COMPLETA": "Completa",
        "AIUTO_MODALITA_SEMPLICE": "Mostra solo i comandi più comuni.",
        "AIUTO_MODALITA_COMPLETA": "Mostra anche i comandi tecnici di Blender.",
        "ETICHETTA_AVANZATO_ATTIVO": "Modalità completa: compaiono anche i comandi tecnici.",
        # Gruppi di comandi, raggruppati per risultato voluto.
        "GRUPPO_COSTRUISCI": "Costruisci",
        "GRUPPO_STORIA": "Annulla e ripeti",
        "GRUPPO_GUARDA": "Guarda la scena",
        "GRUPPO_SELEZIONE": "Scegli gli oggetti",
        "GRUPPO_ELENCO": "Oggetti della scena",
        "GRUPPO_SPOSTA": "Sposta di poco",
        "GRUPPO_RUOTA": "Ruota di poco",
        "GRUPPO_INGRANDISCI": "Ingrandisci o rimpicciolisci",
        "GRUPPO_MOUSE": "Muovi con il mouse",
        "GRUPPO_ALTRO": "Altre azioni",
        "GRUPPO_OGGETTI_SCELTI": "Più oggetti scelti",
        "GRUPPO_LUCE": "Luce",
        "GRUPPO_TELECAMERA": "Telecamera",
        "GRUPPO_TESTO": "Scritta",
        "GRUPPO_TECNICO": "Comandi tecnici",
        "GRUPPO_DATI": "Dati dell'oggetto",
        "GRUPPO_AIUTO": "Consigli",
        "GRUPPO_SPIGOLI": "Spigoli e superficie",
        "GRUPPO_ASPETTO": "Aspetto della superficie",
        "GRUPPO_SIMILE_LISCIO": "Forma più arrotondata",
        "GRUPPO_SPECCHIO": "Specchio e spessore",
        "GRUPPO_COPIE": "Ripeti la forma",
        "GRUPPO_UNISCI": "Unisci o taglia",
        "GRUPPO_ALLINEA": "Allinea e spazia",
        "GRUPPO_GRUPPI": "Gruppi",
        "GRUPPO_MODIFICHE": "Modifiche non applicate",
        "GRUPPO_GUIDA": "Impara: una casetta",
        # Campi e ricerche.
        "ETICHETTA_PASSO": "Passo",
        "AIUTO_PASSO": "Di quanto si sposta l'oggetto a ogni clic, in metri.",
        "ETICHETTA_CERCA": "Cerca",
        "AIUTO_CERCA": "Scrivi una parte del nome per trovare un oggetto.",
        "ETICHETTA_CAMPO_NON_DISPONIBILE": "Campo non disponibile",
        "ETICHETTA_GRADI_ROTAZIONE": "Ogni clic gira di {gradi} gradi.",
        "ETICHETTA_PERCENTUALE": "Ogni clic cambia del {percentuale} per cento.",
        "ETICHETTA_GRANDEZZA": "Grandezza",
        "AIUTO_GRANDEZZA": "Grandezza delle nuove forme: il lato più largo, nell'unità della scena.",
        "ETICHETTA_ROTAZIONE_QUATERNIONE": "Rotazione (quaternione)",
        "ETICHETTA_ROTAZIONE_ASSE_ANGOLO": "Rotazione (asse e angolo)",
        "ASSE_X": "X",
        "ASSE_Y": "Y",
        "ASSE_Z": "Z",
        "ETICHETTA_SCRITTA": "Scritta",
        "AIUTO_SCRITTA": "Il testo della scritta scelta.",
        "ETICHETTA_ALTEZZA_TESTO": "Altezza",
        "AIUTO_ALTEZZA_TESTO": "Altezza della scritta, in {unita}.",
        # Stato della scena.
        "ETICHETTA_NESSUN_OGGETTO": "La scena è vuota.",
        "AIUTO_NESSUN_OGGETTO": "Aggiungi un oggetto dal gruppo Costruisci qui sopra.",
        "ETICHETTA_NESSUNA_SELEZIONE": "Nessun oggetto scelto.",
        "AIUTO_NESSUNA_SELEZIONE": "Clicca un oggetto nella Vista 3D oppure il suo nome qui sopra.",
        "ETICHETTA_MULTI_SELEZIONE": "{numero} oggetti scelti",
        "ETICHETTA_NASCOSTO": "Questo oggetto è nascosto.",
        "ETICHETTA_NASCOSTO_CON_GRUPPO": "Questo oggetto è nascosto insieme al gruppo a cui appartiene.",
        "AIUTO_MULTI_SELEZIONE": "Le azioni qui sotto valgono per tutti gli oggetti scelti.",
        "ETICHETTA_OGGETTO_ATTIVO": "Attivo: {nome}",
        "ETICHETTA_MODALITA_MODIFICA": "Sei in modalità Modifica: premi Tab per uscire.",
        "ETICHETTA_MANCANO_OGGETTI": "Mostrati {mostrati} di {totali} oggetti: usa Cerca.",
        "ETICHETTA_FILTRO_VUOTO": "Nessun oggetto trovato con questo nome.",
        "ETICHETTA_OGGETTO_UNO": "1 oggetto",
        "ETICHETTA_OGGETTI": "{numero} oggetti",
        "ETICHETTA_SCELTI_NESSUNO": "nessuno scelto",
        "ETICHETTA_SCELTI_UNO": "1 scelto",
        "ETICHETTA_SCELTI": "{numero} scelti",
        "ETICHETTA_CONTEGGIO": "{oggetti}, {scelti}",
        "ETICHETTA_OGGETTI_NASCOSTI": "nascosti: {numero}",
        "ETICHETTA_TIPO_TECNICO": "Tipo tecnico: {tipo}",
        "ETICHETTA_DATI_MESH": "Vertici: {vertici}, facce: {facce}",
        "ETICHETTA_NOME_DATI": "Nome dei dati",
        "ETICHETTA_PUNTA_SCHEDA": "Per gli altri comandi premi N e scorri le schede di Blender.",
        "CONSIGLIO_ROTAZIONE": "Consiglio: gira la vista con il tasto centrale del mouse.",
        # Nomi dei tipi di oggetto in parole semplici.
        "TIPO_FORMA": "Forma",
        "TIPO_LUCE": "Luce",
        "TIPO_TELECAMERA": "Telecamera",
        "TIPO_SEGNAPOSTO": "Segnaposto",
        "TIPO_CURVA": "Curva",
        "TIPO_TESTO": "Testo",
        "TIPO_STRUTTURA": "Struttura",
        "TIPO_DISEGNO": "Disegno",
        "TIPO_VOLUME": "Volume",
        "TIPO_ALTRO": "Oggetto",
        "TIPO_FORMA_PLURALE": "{numero} forme",
        "TIPO_LUCE_PLURALE": "{numero} luci",
        "TIPO_TELECAMERA_PLURALE": "{numero} telecamere",
        "TIPO_ALTRO_PLURALE": "{numero} altri oggetti",
        # Costruzione: cubo, sfera, cilindro, piano, luce.
        "AZIONE_AGGIUNGI_CUBO": "Cubo",
        "AIUTO_AGGIUNGI_CUBO": "Aggiunge un cubo alla scena e lo sceglie.",
        "NOME_CUBO": "Cubo",
        "NOME_MESH_CUBO": "Geometria del cubo",
        "CUBO_AGGIUNTO": "Aggiunto: un cubo.",
        "AZIONE_AGGIUNGI_SFERA": "Sfera",
        "AIUTO_AGGIUNGI_SFERA": "Aggiunge una sfera alla scena e la sceglie.",
        "NOME_SFERA": "Sfera",
        "NOME_MESH_SFERA": "Geometria della sfera",
        "SFERA_AGGIUNTA": "Aggiunta: una sfera.",
        "AZIONE_AGGIUNGI_CILINDRO": "Cilindro",
        "AIUTO_AGGIUNGI_CILINDRO": "Aggiunge un cilindro alla scena e lo sceglie.",
        "NOME_CILINDRO": "Cilindro",
        "NOME_MESH_CILINDRO": "Geometria del cilindro",
        "CILINDRO_AGGIUNTO": "Aggiunto: un cilindro.",
        "AZIONE_AGGIUNGI_PIANO": "Piano",
        "AIUTO_AGGIUNGI_PIANO": "Aggiunge un piano piatto, utile come pavimento.",
        "NOME_PIANO": "Piano",
        "NOME_MESH_PIANO": "Geometria del piano",
        "PIANO_AGGIUNTO": "Aggiunto: un piano.",
        "AZIONE_AGGIUNGI_CONO": "Cono",
        "AIUTO_AGGIUNGI_CONO": "Aggiunge un cono alla scena e lo sceglie.",
        "NOME_CONO": "Cono",
        "NOME_MESH_CONO": "Geometria del cono",
        "CONO_AGGIUNTO": "Aggiunto: un cono.",
        "AZIONE_AGGIUNGI_TORO": "Ciambella",
        "AIUTO_AGGIUNGI_TORO": "Aggiunge una ciambella alla scena e la sceglie.",
        "NOME_TORO": "Ciambella",
        "NOME_MESH_TORO": "Geometria della ciambella",
        "TORO_AGGIUNTO": "Aggiunta: una ciambella.",
        "AZIONE_AGGIUNGI_TESTO": "Testo",
        "AIUTO_AGGIUNGI_TESTO": "Aggiunge una scritta in piedi, poi la modifichi qui sotto.",
        "NOME_TESTO": "Testo",
        "NOME_DATI_TESTO": "Geometria del testo",
        "TESTO_INIZIALE": "Testo",
        "TESTO_AGGIUNTO": "Aggiunto: una scritta.",
        "AZIONE_AGGIUNGI_LUCE": "Luce",
        "AIUTO_AGGIUNGI_LUCE": "Aggiunge una luce che illumina la scena.",
        "NOME_LUCE": "Luce",
        "LUCE_AGGIUNTA": "Aggiunta: una luce.",
        "MESSAGGIO_OGGETTO_CREATO": "Aggiunto: {nome}",
        "ERRORE_CREAZIONE_OGGETTO": "Non è stato possibile aggiungere l'oggetto.",
        "ERRORE_CREAZIONE_IN_MODIFICA": "Prima torna alla modalità Oggetto con Tab.",
        "LOG_ERRORE_CREAZIONE": "La creazione dell'oggetto non è riuscita.",
        "PREFISSO_GEOMETRIA": "Geometria di",
        "SUFFISSO_COPIA": "copia",
        # Vista.
        "AZIONE_VISTA_INIZIALE": "Torna alla vista iniziale",
        "AIUTO_VISTA_INIZIALE": "Rimette la vista 3D come all'avvio e inquadra la scena.",
        "MESSAGGIO_VISTA_INIZIALE": "Vista riportata all'inizio.",
        "ERRORE_VISTA_INIZIALE": "Non trovo una vista 3D da sistemare.",
        "ERRORE_VISTA_NON_DISPONIBILE": "La vista 3D non è disponibile qui.",
        "AZIONE_INQUADRA_TUTTO": "Inquadra tutto",
        "AIUTO_INQUADRA_TUTTO": "Allontana o avvicina la vista per mostrare tutti gli oggetti.",
        "MESSAGGIO_INQUADRA_TUTTO": "Vista inquadrata su tutta la scena.",
        "AZIONE_INQUADRA_OGGETTO": "Inquadra l'oggetto",
        "AIUTO_INQUADRA_OGGETTO": "Avvicina la vista all'oggetto scelto.",
        "MESSAGGIO_INQUADRA_OGGETTO": "Vista su {nome}.",
        "AZIONE_INQUADRA_SCELTI": "Inquadra la scelta",
        "AIUTO_INQUADRA_SCELTI": "Avvicina la vista agli oggetti scelti.",
        "MESSAGGIO_INQUADRA_SCELTI": "Vista sugli oggetti scelti.",
        "ERRORE_INQUADRA_OGGETTO": "L'oggetto è nascosto: usa Mostra per vederlo.",
        "LOG_ERRORE_VISTA": "La vista non è stata ripristinata.",
        "LOG_ERRORE_REGISTRAZIONE_VISTA": "Non è stato possibile registrare la vista iniziale.",
        # Storia.
        "AZIONE_ANNULLA": "Annulla",
        "AIUTO_ANNULLA": "Annulla l'ultima azione, come Ctrl+Z.",
        "MESSAGGIO_ANNULLA": "Ultima azione annullata.",
        "AZIONE_RIPETI": "Ripeti",
        "AIUTO_RIPETI": "Ripete l'azione annullata, come Ctrl+Maiusc+Z.",
        "MESSAGGIO_RIPETI": "Azione ripetuta.",
        "ERRORE_STORIA": "Non c'è nulla da annullare o ripetere.",
        "LOG_ERRORE_STORIA": "Il comando di annullamento o ripetizione non è riuscito.",
        # Scelta degli oggetti.
        "AZIONE_SELEZIONA_TUTTO": "Tutti",
        "AIUTO_SELEZIONA_TUTTO": "Sceglie tutti gli oggetti visibili della scena.",
        "MESSAGGIO_SELEZIONA_TUTTO": "Scelti {numero} oggetti.",
        "MESSAGGIO_NIENTE_DA_SCEGLIERE": "Non ci sono oggetti visibili da scegliere.",
        "AZIONE_DESCEGLI_TUTTO": "Nessuno",
        "AIUTO_DESCEGLI_TUTTO": "Toglie la scelta da tutti gli oggetti.",
        "MESSAGGIO_DESELEZIONA_TUTTO": "Nessun oggetto scelto.",
        "AZIONE_INVERTI_SCELTA": "Inverti",
        "AIUTO_INVERTI_SCELTA": "Sceglie gli oggetti non scelti e toglie gli altri.",
        "MESSAGGIO_INVERTI_SELEZIONE": "Invertita: {numero} oggetti scelti.",
        "AZIONE_SCEGLI_STESSO_TIPO": "Stesso tipo",
        "AIUTO_SCEGLI_STESSO_TIPO": "Sceglie tutti gli oggetti dello stesso tipo.",
        "MESSAGGIO_SELEZIONA_TIPO": "Scelti {numero} oggetti dello stesso tipo.",
        "MESSAGGIO_SELEZIONA_TIPO_NESSUNO": "Non ci sono altri oggetti di questo tipo.",
        "AZIONE_SCEGLI_OGGETTO": "Scegli",
        "AIUTO_SCEGLI_OGGETTO": "Sceglie questo oggetto. Con Maiusc ne aggiunge un altro.",
        "AZIONE_ALTERNA_SCELTA": "Scelta",
        "AIUTO_ALTERNA_SCELTA": "Aggiunge o toglie questo oggetto dalla scelta.",
        "MESSAGGIO_SCELTO": "Scelto: {nome}",
        "MESSAGGIO_SCELTO_MOSTRATO": "Scelto e di nuovo visibile: {nome}",
        "MESSAGGIO_AGGIUNTO_MOSTRATO": "Aggiunto alla scelta e di nuovo visibile: {nome}",
        "MESSAGGIO_AGGIUNTO_ALLA_SCELTA": "Aggiunto alla scelta: {nome}",
        "MESSAGGIO_TOLTO_DALLA_SCELTA": "Tolto dalla scelta: {nome}",
        "MESSAGGIO_SALTATI": "Non scegliibili: {numero}.",
        "ERRORE_OGGETTO_NON_SELEZIONABILE": "{nome} non si può scegliere: è bloccato.",
        "ERRORE_OGGETTO_NASCOSTO": "{nome} è nascosto: premi l'occhio qui accanto per vederlo.",
        # Azioni sugli oggetti.
        "AZIONE_RINOMINA": "Rinomina",
        "AIUTO_RINOMINA": "Cambia il nome dell'oggetto scelto.",
        "TITOLO_RINOMINA": "Rinomina oggetto",
        "ETICHETTA_NUOVO_NOME": "Nuovo nome",
        "AIUTO_NUOVO_NOME": "Scrivi il nuovo nome e conferma.",
        "MESSAGGIO_RINOMINATO": "Nome cambiato in {nome}",
        "MESSAGGIO_RINOMINA_INVARIATA": "Il nome non è cambiato.",
        "ERRORE_NOME_VUOTO": "Il nome non può essere vuoto.",
        "LOG_ERRORE_RINOMINA": "La rinomina non è riuscita.",
        "LOG_ERRORE_NOME_DATI": "Non è stato possibile rinominare i dati dell'oggetto.",
        "AZIONE_DUPLICA": "Duplica",
        "AIUTO_DUPLICA": "Crea una copia indipendente degli oggetti scelti.",
        "MESSAGGIO_DUPLICATO": "Copia creata: {nome}",
        "MESSAGGIO_DUPLICATI": "Copie create: {numero}",
        "AZIONE_ELIMINA": "Elimina",
        "AIUTO_ELIMINA": "Toglie dalla scena l'oggetto scelto.",
        "AZIONE_ELIMINA_SCELTI": "Elimina {numero} oggetti",
        "ETICHETTA_CONFERMA_ELIMINA": "Verranno eliminati {numero} oggetti.",
        "MESSAGGIO_ELIMINATO": "Eliminato: {nome}",
        "MESSAGGIO_ELIMINATI": "Eliminati {numero} oggetti",
        "ERRORE_ELIMINA": "Non è stato possibile eliminare l'oggetto.",
        "AZIONE_NASCONDI": "Nascondi",
        "AZIONE_MOSTRA": "Mostra",
        "AZIONE_NASCONDI_SCELTI": "Nascondi gli scelti",
        "AZIONE_DUPLICA_SCELTI": "Duplica gli scelti",
        "AZIONE_DESCEGLI_SCELTI": "Deseleziona tutto",
        "AZIONE_MOSTRA_TUTTI": "Mostra tutti gli oggetti",
        "AIUTO_MOSTRA_TUTTI": "Fa ricomparire tutti gli oggetti nascosti.",
        "AZIONE_ALTERNA_VISIBILITA": "Visibilità",
        "AIUTO_ALTERNA_VISIBILITA": "Mostra o nasconde questo oggetto nella Vista 3D.",
        "MESSAGGIO_NASCOSTO": "Nascosto: {nome}",
        "MESSAGGIO_NASCOSTI": "Nascosti {numero} oggetti",
        "MESSAGGIO_MOSTRATO": "Di nuovo visibile: {nome}",
        "MESSAGGIO_MOSTRATI": "Di nuovo visibili: {numero} oggetti",
        "MESSAGGIO_MOSTRATI_TUTTI": "Tutti gli oggetti sono di nuovo visibili.",
        "ERRORE_VISIBILITA": "Non è stato possibile cambiare la visibilità.",
        # Posizione: centro della scena e piano di lavoro.
        "AZIONE_CENTRA": "Porta al centro",
        "AIUTO_CENTRA": "Porta l'oggetto scelto al centro della scena.",
        "MESSAGGIO_CENTRATO": "Portato al centro: {nome}",
        "MESSAGGIO_CENTRATI": "Portati al centro {numero} oggetti",
        "AZIONE_APPOGGIA_SUL_PIANO": "Appoggia sul piano",
        "AIUTO_APPOGGIA_SUL_PIANO": "Fa toccare il piano di lavoro all'oggetto scelto.",
        "MESSAGGIO_APPOGGIATO": "Appoggiato sul piano: {nome}",
        "MESSAGGIO_APPOGGIATI": "Appoggiati sul piano {numero} oggetti",
        "AVVISO_APPOGGIO_SENZA_FORMA": "Senza una forma propria è sul piano il suo punto.",
        # Blocco della scelta.
        "AZIONE_BLOCCA_SCELTA": "Blocca la scelta",
        "AIUTO_BLOCCA_SCELTA": "Impedisce di scegliere l'oggetto per sbaglio.",
        "AZIONE_SBLOCCA_SCELTA": "Sblocca la scelta",
        "AIUTO_SBLOCCA_SCELTA": "Di nuovo possibile scegliere l'oggetto.",
        "MESSAGGIO_SCELTA_BLOCCATA": "Scelta bloccata: {nome}",
        "MESSAGGIO_SCELTA_BLOCCATE": "Scelta bloccata per {numero} oggetti",
        "MESSAGGIO_SCELTA_SBLOCCATA": "Di nuovo scegliibile: {nome}",
        "MESSAGGIO_SCELTA_SBLOCCATE": "Di nuovo scegliibili: {numero} oggetti",
        # Copia e incolla.
        "AZIONE_COPIA": "Copia",
        "AIUTO_COPIA": "Copia gli oggetti scelti, come Ctrl+C.",
        "AZIONE_INCOLLA": "Incolla",
        "AIUTO_INCOLLA": "Incolla gli oggetti copiati, come Ctrl+V.",
        "MESSAGGIO_COPIATI": "Copiati {numero} oggetti.",
        "MESSAGGIO_INCOLLATI": "Incollati {numero} oggetti.",
        "ERRORE_NIENTE_DA_INCOLLARE": "Non c'è nulla da incollare: prima usa Copia.",
        "ERRORE_COPIA_NON_RIUSCITA": "Non è stato possibile copiare: apri una Vista 3D.",
        "ERRORE_INCOLLA_NON_RIUSCITA": "Non è stato possibile incollare: apri una Vista 3D.",
        # Passi di movimento.
        "AZIONE_VERSO_SINISTRA": "Sinistra",
        "AIUTO_VERSO_SINISTRA": "Sposta di {passo} m verso sinistra, lungo l'asse X.",
        "AZIONE_VERSO_DESTRA": "Destra",
        "AIUTO_VERSO_DESTRA": "Sposta di {passo} m verso destra, lungo l'asse X.",
        "AZIONE_VERSO_SU": "Su",
        "AIUTO_VERSO_SU": "Sposta di {passo} m verso l'alto, lungo l'asse Z.",
        "AZIONE_VERSO_GIU": "Giù",
        "AIUTO_VERSO_GIU": "Sposta di {passo} m verso il basso, lungo l'asse Z.",
        "AZIONE_VERSO_AVANTI": "Avanti",
        "AIUTO_VERSO_AVANTI": "Sposta di {passo} m in avanti, lungo l'asse Y negativo.",
        "AZIONE_VERSO_INDIETRO": "Indietro",
        "AIUTO_VERSO_INDIETRO": "Sposta di {passo} m indietro, lungo l'asse Y positivo.",
        "MESSAGGIO_MOSSO": "Spostato: {nome}, verso {verso}",
        "MESSAGGIO_MOSSI": "Spostati {numero} oggetti verso {verso}",
        # Passi di rotazione.
        "AZIONE_RUOTA_SINISTRA": "Gira a sinistra",
        "AIUTO_RUOTA_SINISTRA": "Ruota di {gradi} gradi in senso antiorario.",
        "AZIONE_RUOTA_DESTRA": "Gira a destra",
        "AIUTO_RUOTA_DESTRA": "Ruota di {gradi} gradi in senso orario.",
        "MESSAGGIO_RUOTATO": "Ruotato: {nome}",
        "MESSAGGIO_RUOTATI": "Ruotati {numero} oggetti",
        # Passi di dimensione.
        "AZIONE_PIU_GRANDE": "Più grande",
        "AIUTO_PIU_GRANDE": "Ingrandisce l'oggetto del {percentuale} per cento.",
        "AZIONE_PIU_PICCOLO": "Più piccolo",
        "AIUTO_PIU_PICCOLO": "Rimpicciolisce l'oggetto del {percentuale} per cento.",
        "MESSAGGIO_SCALATO": "Dimensione cambiata: {nome}",
        "MESSAGGIO_SCALATI": "Dimensione cambiata per {numero} oggetti",
        "MESSAGGIO_DIMENSIONE_MINIMA": "L'oggetto è già molto piccolo.",
        "ERRORE_TRASFORMAZIONE": "Non è stato possibile spostare l'oggetto.",
        "ERRORE_TRASFORMAZIONE_NESSUNA_SCELTA": "Prima scegli un oggetto da spostare.",
        "ERRORE_NESSUNA_SCELTA": "Seleziona prima un oggetto.",
        "ERRORE_TRASFORMAZIONE_BLOCCATA": "Questo oggetto ha le trasformazioni bloccate.",
        "AVVISO_TRASFORMAZIONE_PARZIALE": "{numero} oggetti bloccati: non si sono mossi.",
        # Comandi nativi con il mouse.
        "AZIONE_MOUSE_SPOSTA": "Sposta",
        "AZIONE_MOUSE_RUOTA": "Ruota",
        "AZIONE_MOUSE_INGRANDISCI": "Ingrandisci",
        "ETICHETTA_CONSIGLIO_MOUSE": "Con il mouse: muovi e clicca per confermare.",
        # Maniglie nella Vista 3D (frecce, archi e cubetti).
        "AZIONE_STRUMENTO_SPOSTA": "Frecce per spostare",
        "AIUTO_STRUMENTO_SPOSTA": "Mostra le frecce: trascinale per spostare l'oggetto.",
        "AZIONE_STRUMENTO_RUOTA": "Frecce per ruotare",
        "AIUTO_STRUMENTO_RUOTA": "Mostra gli archi: trascinali per ruotare l'oggetto.",
        "AZIONE_STRUMENTO_SCALA": "Frecce per ingrandire",
        "AIUTO_STRUMENTO_SCALA": "Mostra i cubetti: trascinali per cambiare la dimensione.",
        "MESSAGGIO_STRUMENTO_SPOSTA": "Frecce di spostamento pronte: trascina una freccia.",
        "MESSAGGIO_STRUMENTO_RUOTA": "Archi di rotazione pronti: trascina un arco.",
        "MESSAGGIO_STRUMENTO_SCALA": "Maniglie di dimensione pronte: trascina un cubetto.",
        "ERRORE_STRUMENTO": "Apri una Vista 3D per usare le frecce.",
        "LOG_ERRORE_STRUMENTO": "Lo strumento con le maniglie non è disponibile.",
        # Luce e telecamera.
        "AZIONE_PIU_LUMINOSA": "Più luminosa",
        "AIUTO_PIU_LUMINOSA": "Aumenta la potenza della luce.",
        "AZIONE_MENO_LUMINOSA": "Meno luminosa",
        "AIUTO_MENO_LUMINOSA": "Riduce la potenza della luce.",
        "MESSAGGIO_LUCE_CAMBIATA": "Potenza della luce cambiata.",
        "ETICHETTA_POTENZA": "Potenza",
        "AZIONE_GUARDA_DA_CAMERA": "Guarda dalla telecamera",
        "AIUTO_GUARDA_DA_CAMERA": "Mostra la scena come la vede questa telecamera.",
        "MESSAGGIO_GUARDA_DA_CAMERA": "Vista dalla telecamera.",
        "AZIONE_TELECAMERA_PRINCIPALE": "Usa come telecamera principale",
        "AIUTO_TELECAMERA_PRINCIPALE": "Usa questa telecamera per l'immagine finale.",
        "MESSAGGIO_TELECAMERA_PRINCIPALE": "Telecamera principale: {nome}",
        "ERRORE_TELECAMERA": "Non è stato possibile usare la telecamera.",
        # Strumenti guidati di modellazione (pannello "Dai forma").
        "AZIONE_AMMORBIDISCI_SPIGOLI": "Arrotonda gli spigoli",
        "AIUTO_AMMORBIDISCI_SPIGOLI": (
            "Arrotonda gli spigoli vivi della forma con una modifica che si può togliere."
        ),
        "DIALOGO_AMMORBIDISCI_SPIGOLI": (
            "Gli spigoli vivi diventano tondi. La forma di partenza resta quella di prima: "
            "la modifica si può togliere quando vuoi."
        ),
        "ETICHETTA_FORZA": "Quanto arrotondare",
        "AIUTO_FORZA": "Da 1 (appena) a 5 (molto): quanto diventano tondi gli spigoli.",
        "ETICHETTA_SEGMENTI": "Segmenti del raccordo",
        "AIUTO_SEGMENTI": "Quanti pezzi compongono il raccordo: più pezzi, più tondo.",
        "ETICHETTA_ANGOLO_SPIGOLO": "Angolo da arrotondare",
        "AIUTO_ANGOLO_SPIGOLO": "Vengono arrotondati solo gli spigoli più vivi di questo angolo.",
        "ETICHETTA_RAGGIO": "Raggio del raccordo",
        "AIUTO_RAGGIO": "Quanto è grande l'arrotondamento, nell'unità della scena.",
        "MESSAGGIO_SPIGOLI": "Spigoli ammorbiditi: {nome}.",
        "MESSAGGIO_SPIGOLI_RAGGIO": "Spigoli ammorbiditi: {nome} (raggio {raggio} {unita}).",
        "ERRORE_SERVE_FORMA": (
            "Serve una forma (una mesh): per una scritta o una curva usa Trasforma in forma."
        ),
        "ERRORE_FORMA_VUOTA": "Questa forma è vuota: non c'è nulla da modificare.",
        "ERRORE_FORMA_NON_LEGGIBILE": "Non riesco a leggere la forma di questo oggetto.",
        "ERRORE_MODIFICATORE_NON_AGGIUNTO": (
            "Questa modifica non si può aggiungere a questo tipo di oggetto."
        ),
        "ERRORE_SENZA_SPIGOLI": "Questa forma non ha spigoli vivi: è già morbida.",
        "ERRORE_SPIGOLI_NON_RIUSCITI": "Non è stato possibile ammorbidire gli spigoli.",
        "AZIONE_SUPERFICIE_LISCIA": "Superficie liscia",
        "AIUTO_SUPERFICIE_LISCIA": (
            "Illumina la superficie come se fosse continua: non cambia la forma."
        ),
        "AZIONE_SUPERFICIE_A_FACCE": "Superficie a facce",
        "AIUTO_SUPERFICIE_A_FACCE": (
            "Rimette in evidenza le facce: è l'aspetto di prima della superficie liscia."
        ),
        "MESSAGGIO_SUPERFICIE_LISCIA": "Superficie mostrata liscia: l'aspetto cambia, le facce no.",
        "MESSAGGIO_SUPERFICIE_A_FACCE": "Superficie mostrata a facce: l'aspetto cambia, le facce no.",
        "ERRORE_SUPERFICIE": "Non è stato possibile cambiare l'aspetto della superficie.",
        "AZIONE_FORMA_PIU_LISCIA": "Forma più arrotondata",
        "AIUTO_FORMA_PIU_LISCIA": (
            "Aggiunge facce per arrotondare davvero la forma: qui si cambia la geometria."
        ),
        "DIALOGO_FORMA_PIU_LISCIA": (
            "Qui la forma cambia davvero: ogni livello aggiunge facce e arrotonda di più. "
            "Stima: da {prima} a {dopo} facce."
        ),
        "ETICHETTA_LIVELLI": "Quanto arrotondare",
        "AIUTO_LIVELLI": "Ogni livello aggiunge facce e arrotonda di più (al massimo tre).",
        "MESSAGGIO_FORMA_LISCIA": "Forma più arrotondata: {nome}, ora {facce} facce.",
        "ERRORE_FORMA_LISCIA": "Non è stato possibile arrotondare la forma.",
        "AZIONE_SPECCHIA": "Rispecchia",
        "AIUTO_SPECCHIA": "Crea il lato uguale e opposto, come uno specchio sull'asse scelto.",
        "DIALOGO_SPECCHIA": (
            "Nasce il lato uguale e opposto della forma, rispetto al cursore 3D. Il "
            "segnaposto Specchio segna il piano dello specchio e si sposta come un "
            "oggetto qualsiasi."
        ),
        "NOME_SPECCHIO": "Specchio",
        "NOTA_SPECCHIO": "Lo specchio usa il cursore 3D come piano, e il segnaposto Specchio lo segue.",
        "ERRORE_SPECCHIO_SEGNAPOSTO": "Non è stato possibile segnare il piano dello specchio.",
        "AVVISO_SPECCHIO_SENZA_CENTRO": "Manca il segnaposto dello specchio: la forma si rispecchia su se stessa.",
        "ETICHETTA_ASSE": "Asse dello specchio",
        "AIUTO_ASSE_SPECCHIO": "L'asse perpendicolare allo specchio: X, Y oppure Z.",
        "ETICHETTA_UNISCI_CENTRO": "Unisci i bordi al centro",
        "AIUTO_UNISCI_CENTRO": "Tiene ferme le facce sul piano dello specchio.",
        "ETICHETTA_DISTANZA_UNIONE": "Distanza di unione",
        "AIUTO_DISTANZA_UNIONE": "Avvicina fra loro i vertici che stanno a questa distanza.",
        "MESSAGGIO_SPECCHIATA": "Rispecchiata su {asse}: {nome}.",
        "ERRORE_SPECCHIO_SIMMETRICA": (
            "Questa forma sta a cavallo dello specchio: spostala da una parte, o porta il "
            "cursore 3D dall'altra, e riprova."
        ),
        "ERRORE_SPECCHIO": "Non è stato possibile creare lo specchio.",
        "AZIONE_RIPETI_COPIE": "Ripeti la forma",
        "AIUTO_RIPETI_COPIE": "Crea altre copie della forma, in fila oppure in cerchio.",
        "AZIONE_RIPETI_FILA": "In fila",
        "AIUTO_RIPETI_FILA": "Crea copie in fila, alla distanza scelta.",
        "AZIONE_RIPETI_CERCHIO": "In cerchio",
        "AIUTO_RIPETI_CERCHIO": "Crea copie attorno al centro scelto, alla stessa distanza.",
        "DIALOGO_RIPETI_FILA": (
            "Le copie si mettono in fila lungo l'asse scelto e restano legate all'originale: "
            "la fila si può togliere o correggere quando vuoi."
        ),
        "DIALOGO_RIPETI_CERCHIO": (
            "Le copie si mettono in cerchio attorno al centro scelto. Sono oggetti a sé, "
            "con la stessa forma dell'originale: si possono spostare uno per uno."
        ),
        "ETICHETTA_QUANTE_COPIE": "Quante forme in tutto",
        "AIUTO_QUANTE_COPIE": "Compresa l'originale: 4 vuol dire l'originale più 3 copie.",
        "ETICHETTA_SPAZIATURA": "Distanza fra le copie",
        "AIUTO_SPAZIATURA": "Quanto spazio c'è fra una copia e la successiva.",
        "ETICHETTA_DISTANZA_CENTRO": "Distanza dal centro",
        "AIUTO_DISTANZA_CENTRO": (
            "Quanto distano le copie dal centro del giro; se l'oggetto è sul centro, viene spostato lì."
        ),
        "ETICHETTA_CENTRO_GIRO": "Centro del giro",
        "AIUTO_CENTRO_GIRO": "Il punto attorno a cui girano le copie.",
        "AZIONE_CENTRO_CURSORE": "Cursore 3D",
        "AZIONE_CENTRO_SCENA": "Centro della scena",
        "ETICHETTA_VOLTA_COPIE": "Volta le copie verso l'esterno",
        "AIUTO_VOLTA_COPIE": "Ogni copia guarda fuori dal cerchio, come in un girotondo.",
        "MESSAGGIO_RIPETUTE_FILA": "Copie in fila: {numero} forme in tutto, ogni {distanza} {unita}.",
        "MESSAGGIO_RIPETUTE_CERCHIO": (
            "Copie in cerchio: {numero} forme in tutto, a {distanza} {unita} dal centro."
        ),
        "ERRORE_RIPETI": "Non è stato possibile ripetere la forma.",
        "ERRORE_RIPETI_CENTRO": (
            "Le copie finirebbero tutte sull'originale: dì una distanza dal centro maggiore di zero."
        ),
        "AZIONE_SPESSORE_PARETE": "Aggiungi spessore",
        "AIUTO_SPESSORE_PARETE": (
            "Dà spessore a una superficie sottile, senza cambiare la forma di partenza."
        ),
        "DIALOGO_SPESSORE": (
            "La superficie diventa una parete spessa: la forma di partenza resta dove è e la "
            "modifica si può togliere."
        ),
        "ETICHETTA_SPESSORE": "Spessore",
        "AIUTO_SPESSORE": "Quanto diventa spessa la parete, nell'unità della scena.",
        "ETICHETTA_VERSO_SPESSORE": "Verso dello spessore",
        "AIUTO_VERSO_SPESSORE": "Se lo spessore va verso l'interno o verso l'esterno della forma.",
        "AZIONE_SPESSORE_DENTRO": "Verso l'interno",
        "AZIONE_SPESSORE_FUORI": "Verso l'esterno",
        "MESSAGGIO_SPESSORE": "Spessore aggiunto: {nome}, {spessore} {unita}.",
        "MESSAGGIO_SPESSORE_RIDOTTO": (
            "Spessore aggiunto: {nome}, {spessore} {unita} (ridotto perché la forma è piccola)."
        ),
        "ERRORE_SPESSORE": "Non è stato possibile aggiungere lo spessore.",
        "AZIONE_UNISCI": "Unisci",
        "AIUTO_UNISCI": "Le due forme diventano una forma sola.",
        "AZIONE_TAGLIA": "Taglia",
        "AIUTO_TAGLIA": "La seconda forma viene tolta dalla prima, come un ritaglio.",
        "AZIONE_INCROCIA": "Incrocia",
        "AIUTO_INCROCIA": "Resta solo la parte in cui le due forme si sovrappongono.",
        "ETICHETTA_OPERAZIONE": "Cosa fare",
        "AIUTO_OPERAZIONE": "Scegli se unire, tagliare o incrociare le due forme scelte.",
        "ETICHETTA_OGGETTO_PRINCIPALE": "Forma principale: {nome}",
        "ETICHETTA_OGGETTO_ATTREZZO": "Che taglia o unisce: {nome}",
        "DIALOGO_UNISCI": (
            "Forma principale: {principale}. Che taglia o unisce: {attrezzo}. "
            "Il secondo resta nella scena, nascosto, e la modifica si può togliere."
        ),
        "MESSAGGIO_UNIONE": "Unite due forme: {principale} e {attrezzo}.",
        "MESSAGGIO_DIFFERENZA": "Tagliata una forma: {attrezzo} via da {principale}.",
        "MESSAGGIO_INTERSEZIONE": "Incrociate due forme: {principale} e {attrezzo}.",
        "ERRORE_UNISCI_POCHI": (
            "Per unire o tagliare servono due forme scelte: la principale e quella che taglia."
        ),
        "ERRORE_UNISCI_TROPPI": (
            "Hai scelto più di due oggetti: scegline due, quello attivo è la forma principale."
        ),
        "ERRORE_UNISCI_SERVE_FORMA": (
            "Si uniscono e si tagliano solo forme (mesh): {nome} non lo è."
        ),
        "ERRORE_UNISCI_ATTREZZO_APERTO": (
            "L'oggetto che taglia non è chiuso (per esempio è un piano): serve una forma chiusa."
        ),
        "ERRORE_UNISCI_STESSA_FORMA": "La forma principale e quella che taglia devono essere due oggetti diversi.",
        "ERRORE_UNISCI_VUOTO": "Il risultato è vuoto: le due forme non si toccano.",
        "ERRORE_UNISCI_TROPPE_FACCE": "Il risultato avrebbe troppe facce: prova con forme più semplici.",
        "ERRORE_UNISCI": "Non è stato possibile unire o tagliare le forme.",
        "AZIONE_CONVERTI_IN_FORMA": "Trasforma in forma",
        "AIUTO_CONVERTI_IN_FORMA": (
            "Trasforma una scritta o una curva in una forma (mesh), come fa Blender."
        ),
        "DIALOGO_CONVERTI_IN_FORMA": (
            "La scritta (o la curva) diventa una forma: da quel momento non si può più cambiare "
            "il testo, ma si può lavorare come su tutte le altre forme. Si annulla con Ctrl+Z."
        ),
        "MESSAGGIO_CONVERTITA": "Trasformata in forma: {nome}.",
        "ERRORE_CONVERTI": "Non è stato possibile trasformare l'oggetto in una forma.",
        "AZIONE_ALLINEA": "Allinea",
        "AIUTO_ALLINEA": "Sposta gli oggetti scelti fino a far combaciare i bordi o i centri.",
        "ETICHETTA_ASSE_ALLINEA": "Su quale asse",
        "AIUTO_ASSE_ALLINEA": "L'asse lungo cui gli oggetti vengono messi in riga.",
        "ETICHETTA_BORDO_ALLINEA": "Attacca a",
        "AIUTO_BORDO_ALLINEA": "Quale parte degli oggetti deve combaciare.",
        "AZIONE_ALLINEA_INIZIO": "Inizio",
        "AZIONE_ALLINEA_CENTRO": "Centro",
        "AZIONE_ALLINEA_FINE": "Fine",
        "ETICHETTA_RIFERIMENTO_ALLINEA": "Misura dal punto di riferimento",
        "AIUTO_RIFERIMENTO_ALLINEA": (
            "Allinea i punti di riferimento (le origini) invece dei bordi delle forme."
        ),
        "AZIONE_RIFERIMENTO_BORDO": "Bordo",
        "AZIONE_RIFERIMENTO_PUNTO": "Punto di riferimento",
        "MESSAGGIO_ALLINEATI": "Allineati {numero} oggetti sull'asse {asse}.",
        "MESSAGGIO_ALLINEATI_INVARIATI": "Gli oggetti scelti erano già allineati.",
        "AIUTO_GRUPPO_ALLINEA": (
            "Allinea: bordi o centri alla stessa posizione. Spazia: stessa distanza fra un oggetto e l'altro."
        ),
        "AZIONE_SPAZIA": "Spazia in modo uguale",
        "AIUTO_SPAZIA": "Mette gli oggetti scelti alla stessa distanza l'uno dall'altro.",
        "MESSAGGIO_SPAZIATI": "Spaziati {numero} oggetti sull'asse {asse}, a {spazio} {unita} l'uno dall'altro.",
        "MESSAGGIO_SPAZIATI_STRETTI": (
            "Spaziati {numero} oggetti sull'asse {asse}: si sovrappongono un po'."
        ),
        "ERRORE_ALLINEA": "Non è stato possibile allineare gli oggetti.",
        "ERRORE_ALLINEA_POCHI": "Per allineare servono almeno due oggetti scelti.",
        "ERRORE_ALLINEA_INVARIATI": "Gli oggetti scelti sono già a posto: non c'è nulla da spostare.",
        "ERRORE_SPAZIA_POCHI": "Per spaziare in modo uguale servono almeno tre oggetti scelti.",
        "AZIONE_RAGGRUPPA": "Raggruppa la scelta",
        "AIUTO_RAGGRUPPA": "Crea un gruppo con gli oggetti scelti: si scelgono e si nascondono insieme.",
        "DIALOGO_RAGGRUPPA": (
            "Gli oggetti scelti finiscono in un gruppo con questo nome: da qui in poi si scelgono "
            "e si nascondono tutti insieme. Nessun oggetto viene eliminato."
        ),
        "ETICHETTA_GRUPPO_NOME": "Nome del gruppo",
        "AIUTO_GRUPPO_NOME": "Il nome che vedrai nell'elenco dei gruppi.",
        "MESSAGGIO_GRUPPO": "Gruppo creato: {nome}, con {numero} oggetti.",
        "AIUTO_GRUPPI": (
            "Un gruppo raccoglie oggetti imparentati: si sceglie e si nasconde tutto insieme."
        ),
        "ETICHETTA_GRUPPO_RIGA": "{nome}: {numero} oggetti",
        "AZIONE_SCEGLI_GRUPPO": "Scegli il gruppo",
        "AIUTO_SCEGLI_GRUPPO": "Sceglie tutti gli oggetti del gruppo {nome}.",
        "MESSAGGIO_GRUPPO_SCELTO": "Scelti {numero} oggetti del gruppo {nome}.",
        "MESSAGGIO_GRUPPO_GRUPPO_VUOTO": "Il gruppo {nome} non ha oggetti da scegliere.",
        "AZIONE_ALTERNA_GRUPPO": "Mostra o nascondi il gruppo",
        "AIUTO_ALTERNA_GRUPPO": "Nasconde o fa ricomparire tutti gli oggetti del gruppo {nome}.",
        "MESSAGGIO_GRUPPO_MOSTRATO": "Gruppo {nome}: visibile.",
        "MESSAGGIO_GRUPPO_NASCOSTO": "Gruppo {nome}: nascosto.",
        "AZIONE_TOGLI_DAL_GRUPPO": "Togli dal gruppo",
        "AIUTO_TOGLI_DAL_GRUPPO": "Riporta gli oggetti scelti nella raccolta principale della scena.",
        "MESSAGGIO_TOGLI_GRUPPO": "Tolti dal gruppo {numero} oggetti.",
        "MESSAGGIO_TOGLI_GRUPPO_NESSUNO": "Gli oggetti scelti non sono in un gruppo.",
        "ERRORE_GRUPPO": "Non è stato possibile creare il gruppo.",
        "ERRORE_GRUPPO_SENZA_OGGETTI": "Prima scegli gli oggetti da raggruppare.",
        "ERRORE_GRUPPO_ASSENTE": "Questo gruppo non esiste più.",
        "ERRORE_TOGLI_GRUPPO": "Non è stato possibile togliere gli oggetti dal gruppo.",
        "AZIONE_TOGLI_MODIFICHE": "Togli le modifiche",
        "AIUTO_TOGLI_MODIFICHE": "Toglie le modifiche non applicate: la forma torna com'era.",
        "ETICHETTA_MODIFICHE": "Modifiche non applicate: {numero}",
        "AIUTO_MODIFICHE": (
            "Sono modifiche che si vedono ma non sono state applicate: la forma di partenza è "
            "sempre quella che hai creato."
        ),
        "AZIONE_TOGLI_MODIFICA": "Togli",
        "AIUTO_TOGLI_MODIFICA": "Toglie questa modifica e rimette la forma com'era.",
        "MESSAGGIO_MODIFICHE_TOLTE": "Tolte {numero} modifiche: la forma è tornata com'era.",
        "MESSAGGIO_MODIFICA_TOLTA": "Tolta la modifica: la forma è tornata com'era.",
        "MESSAGGIO_MODIFICHE_NESSUNA": "Questo oggetto non ha modifiche da togliere.",
        "AVVISO_SERIE_SENZA_CENTRO": "Manca il centro del giro: le copie sono tutte sovrapposte.",
        "AVVISO_TAGLIO_SENZA_OGGETTO": "Manca l'oggetto da tagliare: la modifica non fa nulla.",
        "MESSAGGIO_MODIFICATORE_TOLTO": "Modifica tolta: {nome}.",
        "PAROLA_MOD_BEVEL": "Arrotondamento degli spigoli",
        "PAROLA_MOD_SUBSURF": "Forma più arrotondata",
        "PAROLA_MOD_MIRROR": "Specchio",
        "PAROLA_MOD_ARRAY": "Ripetizione",
        "PAROLA_MOD_SOLIDIFY": "Spessore",
        "PAROLA_MOD_BOOLEAN": "Unione o taglio",
        "PAROLA_MOD_ALTRO": "Modifica",
        # Guida passo passo: la casetta.
        "GUIDA_CASETTA_TITOLO": "Una casetta in 13 passi",
        "GUIDA_CASETTA_DESCRIZIONE": (
            "Tre forme semplici, unite e raggruppate. Ogni passo spiega che cosa sta per "
            "succedere prima di farlo."
        ),
        "NOME_CASETTA_CORPO": "Corpo",
        "NOME_CASETTA_TETTO": "Tetto",
        "NOME_CASETTA_CAMINO": "Camino",
        "NOME_CASETTA_GRUPPO": "Casetta",
        "AZIONE_GUIDA_INIZIA": "Inizia la guida",
        "AIUTO_GUIDA_INIZIA": "Apre la guida passo passo: nessuna modifica viene fatta adesso.",
        "AZIONE_GUIDA_ESEGUI": "Fai questo passo",
        "AIUTO_GUIDA_ESEGUI": "Esegue il passo mostrato, con gli stessi comandi dei pulsanti.",
        "AZIONE_GUIDA_AVANTI": "Avanti",
        "AIUTO_GUIDA_AVANTI": "Passa al passo successivo, anche senza eseguirlo.",
        "AZIONE_GUIDA_INDIETRO": "Indietro",
        "AIUTO_GUIDA_INDIETRO": "Torna al passo precedente.",
        "AZIONE_GUIDA_CHIUDI": "Chiudi la guida",
        "AIUTO_GUIDA_CHIUDI": "Chiude la guida: la scena resta come è.",
        "ETICHETTA_GUIDA_PASSO": "Passo {numero} di {totale}",
        "ETICHETTA_GUIDA_FINITA": "Guida completata: la casetta è pronta.",
        "MESSAGGIO_GUIDA_INIZIO": "Guida avviata: una casetta. {totale} passi.",
        "MESSAGGIO_GUIDA_PASSO_FATTO": "Passo {numero} di {totale}: fatto.",
        "MESSAGGIO_GUIDA_FINE": "Guida completata: la casetta è pronta.",
        "MESSAGGIO_GUIDA_CHIUSA": "Guida chiusa.",
        "ERRORE_GUIDA_ASSENTE": "Questa guida non è disponibile.",
        "ERRORE_GUIDA_SELEZIONE": (
            "La guida non trova l'oggetto {nome}: forse è stato rinominato o eliminato."
        ),
        "AIUTO_GUIDA_OGGETTI": "La guida crea gli oggetti che le servono: nessun passaggio è obbligatorio.",
        "GUIDA_CASETTA_CORPO_TITOLO": "Il corpo della casa",
        "GUIDA_CASETTA_CORPO_SPIEGAZIONE": (
            "Aggiunge un cubo grande 2 m e lo chiama Corpo: sarà il corpo della casa."
        ),
        "GUIDA_CASETTA_CORPO_CENTRO_TITOLO": "Il corpo al centro",
        "GUIDA_CASETTA_CORPO_CENTRO_SPIEGAZIONE": (
            "Porta il corpo al centro della scena, così la casa cresce attorno al punto di riferimento."
        ),
        "GUIDA_CASETTA_CORPO_PIANO_TITOLO": "Il corpo appoggiato",
        "GUIDA_CASETTA_CORPO_PIANO_SPIEGAZIONE": (
            "Fa toccare il piano di lavoro al corpo: la casa non resta sospesa per aria."
        ),
        "GUIDA_CASETTA_TETTO_TITOLO": "Il tetto",
        "GUIDA_CASETTA_TETTO_SPIEGAZIONE": (
            "Aggiunge un cono grande 2 m e lo chiama Tetto: la punta sarà il tetto."
        ),
        "GUIDA_CASETTA_TETTO_CENTRO_TITOLO": "Il tetto al centro",
        "GUIDA_CASETTA_TETTO_CENTRO_SPIEGAZIONE": "Porta il tetto sopra il corpo della casa.",
        "GUIDA_CASETTA_TETTO_PIANO_TITOLO": "Il tetto appoggiato",
        "GUIDA_CASETTA_TETTO_PIANO_SPIEGAZIONE": (
            "Appoggia il tetto: da qui si alza di quanto serve, un passo alla volta."
        ),
        "GUIDA_CASETTA_TETTO_ALTO_TITOLO": "Il tetto in alto",
        "GUIDA_CASETTA_TETTO_ALTO_SPIEGAZIONE": (
            "Alza il tetto di 1,90 m: la sua base entra un po' dentro il corpo, così le due forme "
            "si toccano davvero."
        ),
        "GUIDA_CASETTA_CAMINO_TITOLO": "Il camino",
        "GUIDA_CASETTA_CAMINO_SPIEGAZIONE": (
            "Aggiunge un cilindro piccolo (0,50 m) e lo chiama Camino."
        ),
        "GUIDA_CASETTA_CAMINO_CENTRO_TITOLO": "Il camino al centro",
        "GUIDA_CASETTA_CAMINO_CENTRO_SPIEGAZIONE": "Porta il camino sopra la casa.",
        "GUIDA_CASETTA_CAMINO_ALTO_TITOLO": "Il camino in alto",
        "GUIDA_CASETTA_CAMINO_ALTO_SPIEGAZIONE": (
            "Alza il camino di 2,55 m: entra nel tetto e spunta dalla falda."
        ),
        "GUIDA_CASETTA_CAMINO_LATO_TITOLO": "Il camino di lato",
        "GUIDA_CASETTA_CAMINO_LATO_SPIEGAZIONE": (
            "Sposta il camino di 0,50 m verso destra, come un camino vero sul tetto."
        ),
        "GUIDA_CASETTA_UNIRE_TITOLO": "Unisci tetto e corpo",
        "GUIDA_CASETTA_UNIRE_SPIEGAZIONE": (
            "Il tetto diventa un tutt'uno con il corpo. Il cono resta nella scena, nascosto: "
            "la modifica si può togliere."
        ),
        "GUIDA_CASETTA_GRUPPO_TITOLO": "Raggruppa la casetta",
        "GUIDA_CASETTA_GRUPPO_SPIEGAZIONE": (
            "Raccoglie la casa e il camino in un gruppo: da qui in poi si scelgono e si "
            "nascondono insieme. La forma del tetto, usata per unire, resta nascosta."
        ),
        # Pannello "Dai forma": spiegazioni brevi, che stanno nella barra stretta.
        "ETICHETTA_MODELLA_SCELTA": "Dai forma alla forma attiva",
        "ETICHETTA_MODELLA_SCELTI": "Dai forma alla forma attiva",
        "NOTA_MODELLA_PIU_SCELTI": (
            "Hai scelto {numero} oggetti: gli strumenti qui sotto lavorano sulla forma "
            "attiva, cioè l'ultima scelta."
        ),
        "ETICHETTA_MODELLA_NIENTE": "Scegli prima una forma da rifinire.",
        "AIUTO_MODELLA_NIENTE": "Scegli la forma nell'elenco dei pannelli qui sopra: gli strumenti di questo pannello lavorano sulla scelta.",
        "NOTA_ASPETTO_SUPERFICIE": "Qui cambia solo l'aspetto: le facce restano le stesse.",
        "NOTA_ALLINEA": "Allinea mette in riga; Spazia mette alla stessa distanza.",
        "NOTA_GRUPPI": "Un gruppo si sceglie e si nasconde tutto insieme.",
        "NOTA_MODIFICHE": "La forma di partenza resta: si tolgono quando vuoi.",
        "NOTA_MODIFICHE_NIENTE": "Nessuna modifica da togliere su questa forma.",
        "NOTA_UNISCI_SCELTA": (
            "Scegli due forme: quella attiva è la principale, l'altra la taglia o si unisce."
        ),
        "NOTA_UNISCI_MODIFICATORE": "L'unione e il taglio sono modifiche non applicate: si tolgono dalle modifiche qui sotto.",
        "NOTA_GUIDA_CASETTA": "Tre forme diventano una casetta, un passo alla volta.",
        "ETICHETTA_GRUPPI_VUOTA": "Non ci sono ancora gruppi: scegli e usa Raggruppa.",
        "ETICHETTA_MANCANO_GRUPPI": "Altri {totali} gruppi non mostrati.",
        "ETICHETTA_OPZIONI_AVANZATE": "Opzioni avanzate",
        "ETICHETTA_SPIGOLI_TROVATI": "Spigoli da arrotondare: {numero}",
        "MESSAGGIO_SUPERFICIE_INVARIATA": "La superficie era già mostrata così: non c'è nulla da cambiare.",
        "AIUTO_ASSE_X": "La X va da sinistra a destra.",
        "AIUTO_ASSE_Y": "La Y va dalla parte vicina a quella lontana.",
        "AIUTO_ASSE_Z": "La Z va dal basso verso l'alto.",
        # Errori degli strumenti guidati che spiegano che cosa manca.
        "ERRORE_SERVE_FORMA_ALTRO": "Qui si danno forma alle forme: questo oggetto è di un altro tipo.",
        "ERRORE_CONVERTI_NIENTE": "Questo oggetto è già una forma: non serve trasformarlo.",
        "ERRORE_CONVERTI_VUOTA": "La trasformazione non ha prodotto una forma utilizzabile.",
        "ERRORE_UNISCI_NESSUN_CAMBIO": "Le due forme non si toccano: unisci o taglia forme che si sovrappongono.",
        "ERRORE_GUIDA_BLOCCATO": "L'oggetto {nome} è bloccato: sbloccalo per continuare la guida.",
        "ERRORE_GUIDA_PASSO": "Questo passo non è riuscito: la guida si ferma qui.",
        "ERRORE_GUIDA_FINITA": "La guida è già arrivata in fondo: chiudila per rifarla.",
        "LOG_ERRORE_GUIDA": "Un passo della guida non è riuscito.",
        "AVVISO_LIVELLI_RIDOTTI": "Ho usato meno livelli per non appesantire la forma.",
        "MESSAGGIO_FORMA_LISCIA_GIA": "La forma è già arrotondata a questo livello: non c'è altro da fare.",
        "AVVISO_SELEZIONE_PARZIALE": "{numero} oggetti erano nascosti o bloccati: sono rimasti fuori.",
        "AVVISO_SPESSORE_FORMA_CHIUSA": "La forma era già chiusa: lo spessore crea una parete interna.",
        # Comandi tecnici della modalità completa.
        "ETICHETTA_NOME": "Nome",
        "ETICHETTA_POSIZIONE": "Posizione",
        "ETICHETTA_ROTAZIONE": "Rotazione",
        "ETICHETTA_DIMENSIONE": "Dimensione",
        "ETICHETTA_MODO_ROTAZIONE": "Modo di rotazione",
        "ETICHETTA_ASPETTO": "Aspetto",
        "ETICHETTA_BLOCCO_SCELTA": "Blocca la scelta",
        "ETICHETTA_NASCONDI_RENDER": "Nascondi nell'immagine finale",
        "AZIONE_PULISCI_FILTRO": "Pulisci",
        "AIUTO_PULISCI_FILTRO": "Cancella il testo di ricerca.",
        "AZIONE_APRI_BARRA": "FormaFacile",
        "AIUTO_APRI_BARRA": "Apre la barra laterale con gli strumenti FormaFacile.",
        # Avvio e diagnostica.
        "DESCRIZIONE_AVVIO": "Avvia FormaFacile 3D con una versione compatibile di Blender.",
        "USO_LAUNCHER": "python3 scripts/avvia_formafacile.py [--blender PERCORSO] [-- OPZIONI_BLENDER]",
        "AIUTO_PERCORSO_BLENDER": "Percorso dell'eseguibile Blender da usare.",
        "AIUTO_ARGOMENTI_BLENDER": "Opzioni da inoltrare a Blender dopo il separatore --.",
        "BLENDER_NON_TROVATO": (
            "Non trovo Blender 4.5 LTS. Installa Blender 4.5.x dalla pagina ufficiale "
            "https://www.blender.org/download/lts/ oppure indica il suo percorso con "
            "--blender o con la variabile FORMAFACILE_BLENDER."
        ),
        "PERCORSO_BLENDER_NON_VALIDO": "Il percorso indicato non contiene un eseguibile Blender valido.",
        "VERSIONE_BLENDER_NON_LEGGIBILE": "Non riesco a verificare la versione di Blender. Controlla l'installazione.",
        "VERSIONE_BLENDER_NON_SUPPORTATA": (
            "La versione rilevata è {versione}. FormaFacile supporta Blender 4.5.x LTS. "
            "Installa una versione compatibile oppure indica il percorso corretto."
        ),
        "AVVIO_BLENDER": "Avvio Blender 4.5 LTS con FormaFacile 3D.",
        "ERRORE_AVVIO_BLENDER": "Blender non è riuscito ad avviarsi.",
        # Controllo e pacchetto.
        "CONTROLLO_FILE_RIUSCITO": "Controllo dei file richiesti superato.",
        "CONTROLLO_SINTASSI_RIUSCITO": "Controllo della sintassi Python superato.",
        "CONTROLLO_MANIFEST_RIUSCITO": "Metadati del componente aggiuntivo validi.",
        "TEST_UNITA_RIUSCITI": "Test automatici superati.",
        "AVVIO_TEST_BLENDER": "Esecuzione del test dell'operatore in Blender.",
    "AVVIO_TEST_BPY": "Esecuzione dei test di FormaFacile con il modulo bpy.",
        "TEST_BLENDER_RIUSCITO": "Test dell'operatore in Blender superato.",
    "TEST_BPY_RIUSCITO": "Test del componente aggiuntivo con il modulo bpy superato.",
    "TEST_BPY_SALTATO": "Test con il modulo bpy non eseguito: il modulo bpy non è installato qui.",
        "DESCRIZIONE_CONTROLLI": "Controlla file, sintassi, traduzioni e prove di FormaFacile 3D.",
        "ARGPARSE_ERRORE": "Errore: {messaggio}\n",
        "ARGPARSE_USO": "Uso: ",
        "ARGPARSE_POSIZIONALI": "argomenti posizionali",
        "ARGPARSE_OPZIONI": "opzioni",
        "ARGPARSE_AIUTO": "mostra questo messaggio di aiuto ed esce",
        "ARGPARSE_PARAMETRO_PREFISSO": "parametro ",
        "ARGPARSE_NON_RICONOSCIUTI_PREFISSO": "argomenti non riconosciuti: ",
        "ARGPARSE_OBBLIGATORI_PREFISSO": "mancano gli argomenti obbligatori: ",
        "ARGPARSE_SCELTA_PREFISSO": "valore non valido: ",
        "ARGPARSE_VALORI_AMMESSI_PREFISSO": " (valori ammessi: ",
        "ARGPARSE_UN_VALORE": "è richiesto un valore",
        "ARGPARSE_UNO_MINIMO": "è richiesto almeno un valore",
        "ARGPARSE_UNO_MASSIMO": "è ammesso un solo valore",
        "AIUTO_TEST_BLENDER": "Esegue anche la prova reale con Blender 4.5.x.",
    "AIUTO_TEST_BPY": "Esegue i test del componente aggiuntivo con il modulo bpy, senza interfaccia grafica.",
    "AIUTO_PERCORSO_BPY": "Interprete Python che ha il modulo bpy installato.",
        "AIUTO_PERCORSO_TEST_BLENDER": "Percorso dell'eseguibile Blender da usare per la prova reale.",
        "FILE_RICHIESTI_ASSENTI": "Controllo non superato: mancano i file richiesti.",
        "ERRORE_SINTASSI": "Controllo della sintassi non superato nel file {file}, riga {riga}.",
        "ERRORE_MANIFEST": "Metadati non validi: controlla il manifesto e il supporto Blender 4.5.x.",
        "ERRORE_TEST_BLENDER": "Test Blender non superato (versione {versione}).",
    "ERRORE_TEST_BPY": "Test con il modulo bpy non superato. Ecco la parte finale dell'uscita:",
        "PACCHETTO_CREATO": "Pacchetto creato: {percorso}",
        # Ambiente di prova senza finestre.
        "DESCRIZIONE_AMBIENTE_BPY": "Esegue i test di FormaFacile con il modulo bpy, anche senza Blender grafico.",
        "AIUTO_FILE_AMBIENTE_BPY": "File Python da eseguire con il modulo bpy.",
        "AIUTO_PERCORSO_PYTHON": "Interprete Python dell'ambiente virtuale che contiene bpy.",
        "AIUTO_PREPARA_LIBRERIE": "Prepara librerie grafiche fittizie per usare bpy senza schermo.",
        "BPY_NON_DISPONIBILE": "Il modulo bpy non è disponibile: installalo con pip.",
        "AMBIENTE_BPY_PRONTO": "Ambiente bpy pronto per i test senza finestre.",
        "AMBIENTE_BPY_AVVIO": "Esecuzione del test con il modulo bpy.",
        "AMBIENTE_BPY_NON_RIUSCITO": "Il test con il modulo bpy non è stato superato.",
        "AMBIENTE_BPY_FINITO": "Test con il modulo bpy completato.",
        "AMBIENTE_BPY_LIBRERIE_FINTE": "Librerie grafiche fittizie preparate in {percorso}.",
        "AMBIENTE_BPY_ERRORE_LIBRERIE": "Non è stato possibile preparare le librerie fittizie.",
    }
)


def testo(chiave: str, **valori: object) -> str:
    """Restituisce un testo italiano, applicando se necessario i valori indicati."""
    return TESTI[chiave].format(**valori) if valori else TESTI[chiave]
