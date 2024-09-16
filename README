# Smarters

## Descrizione

Smarters è un simulatore avanzato per la gestione di robot in ambienti rappresentati come griglie di tasselli. Utilizza il framework Mesa per una visualizzazione dettagliata delle interazioni tra agenti e ambiente. Il simulatore permette di testare e valutare la performance di robot in scenari complessi con aree bloccate, aree isolate e diverse modalità di rimbalzo e taglio.

## Rappresentazione dell'Ambiente

### Griglia di Tasselli

L'ambiente di simulazione è rappresentato come una griglia di tasselli, gestita tramite il framework Mesa con un oggetto di tipo `MultiGrid`. Ogni tassello può contenere più agenti e risorse.

### Agenti e Risorse

- **Agenti:** Entità mobili e interattive implementate come istanze della classe `Agent` di Mesa. Interagiscono con l'ambiente e tra di loro.
- **Risorse:** Elementi statici distribuiti sui tasselli, come erba, linee guida, aree isolate e aperture.

### Struttura dei Tasselli

I tasselli sono quadrati e possono contenere diversi elementi grazie alla natura multi-agente della `MultiGrid`. Le risorse includono:
- Tasselli d'erba
- Linee guida
- Aree isolate
- Aperture

### Aree Bloccate

Le aree bloccate sono zone inaccessibili ai robot, rappresentate da `SquaredBlockedArea` e `CircledBlockedArea`. Possono includere edifici, piscine, o altre strutture impeditive. Possono essere impostate manualmente o distribuite casualmente.

### Aree Isolate

Le aree isolate sono zone in cui i robot possono entrare solo attraverso aperture designate. Modellate con `IsolatedArea` e `Opening`, le loro dimensioni e posizioni possono essere definite manualmente o generate casualmente.

## Personalizzazione

### Modello di Rimbalzo

Il modello di rimbalzo gestisce le collisioni del robot con ostacoli:
- **Ping Pong:** Il robot riflette il proprio movimento in direzione opposta dopo aver incontrato un ostacolo.
- **Random:** Il robot cerca sempre di avanzare verso il tassello in alto a sinistra. Se bloccato, tenta altre direzioni.

### Modello di Taglio

Il robot simula il taglio muovendosi sui tasselli e incrementando un contatore. Nella modalità random, il robot seleziona una direzione casuale e si sposta in modo rettilineo, influenzando i tasselli adiacenti.

## Ciclo e Output

### Ciclo di Simulazione

La simulazione si articola in:
1. Generazione di mappe e posizioni della stazione base.
2. Esplorazione di posizioni basate su aree bloccate.
3. Durata della simulazione specificata nel file JSON di configurazione.

### Ciclo di Autonomia

Il robot opera con un'autonomia limitata, eseguendo movimenti fino all'esaurimento. L'autonomia viene resettata dopo ogni ciclo, e la simulazione continua fino al numero di cicli impostato.

### Output

Dopo ogni ciclo di simulazione e di autonomia, vengono prodotti:
- **Heatmap**
- **File CSV:** Contenenti la matrice della mappa, informazioni sui tasselli e dettagli su erba, aree bloccate, e linee guida.

