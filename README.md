### BreakoutQLearning
BrekoutQLearning è un progetto che mira a comparare le prestazioni di tre algoritmi di RL (Q-Learning, Double Q-Learning e S.A.R.S.A.) nella risoluzione di un livello del gioco arcade Breakout.
La repository è così strutturata:
- main.py: contiene il codice per il training, prende come parametro un file json che contiene reward e metaparametri.
- test.py: contiene il codice per il testing di un modello addestrato, nel file la variabile "test_id" rappresenta l'identificativo del n-esimo modello addestrato. Il test verrà fatto su 100 episodi.
- play.py: contiene il codice per provare il gioco (controlli: freccia sinistra, freccia destra)
- package "control": contiene il codice che definisce l'ambiente di gioco
- package "objects": contiene gli oggetti di gioco
- package "utils": oggetti di utilità
- package "tests": qui verranno create le cartelle contenti modello addestrato, grafici di prestazioni e punteggi serializzati
- requirements.txt: dipendenze python

Il progetto dispone di 3 branch principali e ogni branch implementa un modello:
- master(Q-Learning);
- DoubleQLearningVariant;
- SARSAVariant

Per avviare un addestramento:
- Scegliere un modello (una branch)
- Scrivere un file di parametri. Esempio "parameters.json":
```json
{
  "metaparameters": {
    "id": 45,
    "epsilon": 0.01,
    "min_epsilon": 0.01,
    "learning_rate": 0.2,
    "decay_rate": 0.00003,
    "discount_factor": 0.95,
    "episodes": 100000
  },
  "rewards": {
    "min_penalty": -10,
    "max_penalty": -100,
    "tick_penalty": -0.001,
    "ceiling_penalty": -1,
    "bounce_reward": 1,
    "brick_reward": 10,
    "time_exceeded_penalty": -10,
    "win_reward": 1000
  }
}
```
NOTA: il campo "id" non deve andare in conflitto con altri test
- Lanciare: python3 main.py parameters.json. Ogni 500 episodi si vedrà un output sul terminale, inoltre verranno creati dei grafici di andamento delle prestazioni in training.

Per bloccare l'addestramento:
- Ctrl+C (attendere la chiusura del programma)
- Verrà fatto un dump del modello addestrato fino a quel punto.

Per avviare un test di performance dell'agente:
- Modificare la varaibile "test_id" nel file test.py:
- Avviare test.py e attendere la terminazione dei 100 episodi.
