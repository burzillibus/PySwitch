# PySwitch — MIDI Captain Mini6 per BOSS GX-100

Questo progetto contiene il firmware CircuitPython e la configurazione PySwitch
per usare una PaintAudio MIDI Captain Mini6 con una BOSS GX-100 tramite MIDI DIN.
Il profilo attivo e' `gx100`: all'avvio la pedaliera entra in modalita' **STOMP**.

## Collegamento e sincronizzazione

Collegare entrambe le direzioni MIDI DIN:

- MIDI OUT della MIDI Captain a MIDI IN della GX-100;
- MIDI OUT della GX-100 a MIDI IN della MIDI Captain.

La MIDI Captain trasmette sul canale MIDI 1. La GX-100 deve trasmettere un
Program Change ogni volta che si seleziona una memoria, anche dalla sua
interfaccia: questo mantiene la navigazione della Mini6 sincronizzata con la
patch effettivamente selezionata. Sul display il numero ricevuto appare come
`GX PC n` in rosso.

## Modalita' STOMP

STOMP e' la modalita' iniziale. Il testo `STOMP` e' rosso.

| Pulsante | Funzione |
| --- | --- |
| 1 | Entra in modalita' NAVI. |
| 2 | FX 1: Control Change 64, alterna 127/0. |
| 3 | FX 2: Control Change 65, alterna 127/0. |
| 4 | FX 3: Control Change 66, alterna 127/0. |
| 5 | FX 4: Control Change 67, alterna 127/0. |
| 6 | FX 5: Control Change 68, alterna 127/0. |

Per i pulsanti FX occorre configurare nella GX-100 gli ASSIGN corrispondenti
per ricevere e, per ottenere il feedback LED, ritrasmettere gli stessi Control
Change. I LED in STOMP mantengono il colore associato a ciascun FX.

## Modalita' NAVI

Premere 1 per entrare in NAVI. Il testo `NAVI` e' rosso. La navigazione usa il
Program Change ricevuto dalla GX-100 come punto di partenza e invia il Program
Change della memoria richiesta.

| Pulsante | Funzione | LED in NAVI |
| --- | --- | --- |
| 1 | Indicatore NAVI, nessun messaggio MIDI. | Bianco |
| 2 | Banco precedente, conserva la posizione della patch. | Rosso |
| 3 | Banco successivo, conserva la posizione della patch. | Verde |
| 4 | Torna in STOMP. | Bianco |
| 5 | Patch precedente; passa dalla prima alla quarta patch dello stesso banco. | Rosso |
| 6 | Patch successiva; passa dalla quarta alla prima patch dello stesso banco. | Verde |

Un banco e' composto da quattro patch. Ai limiti MIDI (Program Change 1 e 128)
la navigazione dei banchi resta sul limite. Finche' la Mini6 non ha ricevuto
almeno un Program Change dalla GX-100, i comandi di navigazione non inviano
messaggi: selezionare prima una patch dalla GX-100 per stabilire lo stato
sincronizzato.

## File principali

- `content/config.py`: seleziona il profilo `gx100`.
- `content/communication_gx100.py`: instrada il MIDI DIN in entrambe le direzioni.
- `content/inputs_gx100.py`: definisce pulsanti, modalita' e LED della Mini6.
- `content/lib/pyswitch/clients/boss/gx100/`: messaggi MIDI e azioni specifiche GX-100.

## Verifica e installazione

Per eseguire i test dal repository:

```bash
PYTHONPATH=content python3 -m unittest discover -t test -s test/pyswitch
```

Per installare il firmware, copiare il contenuto di `content/` nella radice
della MIDI Captain montata come disco CircuitPython. Espellere il disco in modo
sicuro al termine della copia.
