# Verifica della lingua italiana

## Controlli automatici

La risorsa `addon/formafacile_3d/localization.py` contiene le etichette, le descrizioni, gli errori e i messaggi del programma di avvio. Il test `tests/unit/test_localization.py` controlla che i testi non siano vuoti, che non contengano alcuni segnaposto inglesi comuni e che il codice dei pannelli non inserisca etichette visibili direttamente.

Esegui il controllo con:

```sh
python3 scripts/controlla.py
```

Il controllo automatico è un filtro, non una prova completa della qualità linguistica.

## Revisione manuale della base attuale

Quando Blender 4.5.x è disponibile, controllare:

- il pannello **FormaFacile 3D** nella Vista 3D;
- il pulsante **Aggiungi cubo**, la sua descrizione e i messaggi di conferma/errore;
- i messaggi del programma di avvio quando Blender manca, il percorso è errato o la versione non è supportata;
- l'interfaccia standard di Blender dopo l'attivazione della lingua italiana;
- leggibilità e taglio delle etichette a finestre piccole e con ingrandimento del sistema.

La revisione visiva non è ancora stata eseguita perché nell'ambiente corrente manca Blender grafico. Le traduzioni dell'interfaccia standard dipendono dai file lingua forniti dalla distribuzione ufficiale di Blender.
