# PySwitch — MIDI Captain Mini6 per BOSS GX-100

Questo progetto contiene il firmware CircuitPython e il profilo PySwitch per
usare una PaintAudio MIDI Captain Mini6 con una BOSS GX-100 tramite MIDI DIN.
Il profilo attivo e' `gx100` e all'avvio la pedaliera entra in **STOMP**.

## Collegamento e sincronizzazione

Collegare MIDI OUT della Mini6 a MIDI IN della GX-100 e MIDI OUT della GX-100
a MIDI IN della Mini6. La Mini6 trasmette sul canale MIDI 1. Per la
sincronizzazione, la GX-100 deve trasmettere un Program Change ogni volta che
viene selezionata una memoria; il display mostra il valore ricevuto come
`GX PC n` in rosso.

## Modalita' STOMP

Il testo `STOMP` e' rosso.

| Pulsante | Funzione |
| --- | --- |
| 1 | Entra in NAVI. |
| 2 | FX 1: CC 64, alterna 127/0. |
| 3 | FX 2: CC 65, alterna 127/0. |
| 4 | Resta in STOMP; LED bianco fisso. Non invia messaggi MIDI. |
| 5 | FX 4: CC 67, alterna 127/0. |
| 6 | FX 5: CC 68, alterna 127/0. |

Configurare nella GX-100 gli ASSIGN che ricevono questi CC e, se si desidera
il feedback LED, fare ritrasmettere alla GX-100 lo stesso CC quando cambia lo
stato dell'effetto.

## Modalita' NAVI

Premere 1 per entrare in NAVI. Il testo `NAVI` e' rosso. La navigazione parte
dall'ultimo Program Change ricevuto dalla GX-100 e invia il Program Change
della memoria richiesta.

| Pulsante | Funzione | LED |
| --- | --- | --- |
| 1 | Indicatore NAVI. | Bianco |
| 2 | Banco precedente, stessa posizione patch. | Rosso |
| 3 | Banco successivo, stessa posizione patch. | Verde |
| 4 | Torna in STOMP. | Bianco |
| 5 | Patch precedente, con ciclo interno al banco. | Rosso |
| 6 | Patch successiva, con ciclo interno al banco. | Verde |

Un banco contiene quattro patch. Ai limiti MIDI, Program Change 1 e 128, il
cambio banco resta sul limite. Prima di navigare la Mini6 deve ricevere almeno
un Program Change dalla GX-100: selezionare quindi una patch direttamente
sulla GX-100 dopo l'accensione.

## File e verifica

- `content/config.py`: attiva il profilo `gx100`.
- `content/communication_gx100.py`: routing MIDI DIN bidirezionale.
- `content/inputs_gx100.py`: pulsanti, modalita' e LED Mini6.

Per eseguire i test:

```bash
PYTHONPATH=content python3 -m unittest discover -t test -s test/pyswitch
```

Per installare, copiare `content/` nella radice della Mini6 montata come disco
CircuitPython ed espellere il disco in modo sicuro.
