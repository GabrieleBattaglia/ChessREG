# Changelog di ChessReg

Il formato segue il versionamento x.y.z: x per le grosse novita' o i
refactoring profondi, y per ogni nuova funzionalita', z per ogni
correzione o cambiamento minore.

## 6.0.0 del 7 settembre 2026

Revisione 1 dell'analisi del codice. Ventiquattro rilievi corretti su
venticinque, piu' due perdite di dati trovate strada facendo. La
persistenza e' stata riscritta, percio' cambia la prima cifra.

### Sicurezza dell'archivio
- L'archivio illeggibile non viene piu' sostituito. Se ChessReg.json
  esiste ma non si riesce a leggerlo, il programma lo dice e si ferma
  senza scrivere niente, indicando dove trovare la copia .bak.
- Il ripiego sul vecchio pickle ChessReg.dat e' stato tolto: la
  migrazione a JSON era conclusa dalla 5.0.0 e quel file poteva
  rimpiazzare l'archivio aggiornato.
- Il salvataggio e' atomico: scrive su un file temporaneo e lo mette al
  posto dell'archivio con os.replace, conservando la versione
  precedente come ChessReg.json.bak.
- Ogni modifica viene salvata subito, non piu' soltanto con SLV o
  all'uscita. Di conseguenza ESC non annulla piu' niente: esce e basta.
- I percorsi dell'archivio sono ancorati alla cartella del programma e
  non piu' a quella di lavoro.
- Se le chiavi active_sch o active_elo puntano a elementi inesistenti,
  vengono riportate su un elemento valido avvisando, invece di far
  cadere il caricamento.

### Perdite silenziose
- Nel comando ELO la scelta veniva accettata con l'operatore in su una
  stringa, che e' vero anche per la stringa vuota: lasciando scadere i
  sessanta secondi si cancellava l'ultimo Elo. Ora l'attesa scaduta non
  tocca nulla.
- La rimozione dell'ultimo Elo su una lista vuota sollevava IndexError.
  Ora avvisa e basta. Stesso controllo sulla modifica dell'ultimo
  valore.
- Dentro EDT il tasto Escape veniva riconosciuto con ord, che su una
  freccia o alla scadenza dell'attesa sollevava TypeError e chiudeva il
  programma. Ora il confronto e' diretto.
- La chiave della scacchiera viene divisa sulla prima occorrenza dei due
  punti, e i due punti dentro il nome non sono piu' accettati.

### Verita' delle statistiche
- Statelo e Grafson scartavano il primo valore di ogni lista Elo, cioe'
  il piu' antico. Ora lavorano su tutti i valori: nella lista Lichess
  Corrispondenza il minimo torna a essere 1719 invece di 1726.
- Le soglie minime di grafico sonoro, stringa DEA e statistiche sono
  tre costanti coerenti: una lista di cinque valori si puo' ascoltare.
- In Daeloascii minimo e massimo si calcolano con min e max invece che
  a partire da valori inventati.
- Il primo Elo di una lista nuova non viene piu' annunciato come una
  variazione di millecinquecento punti.

### Uso quotidiano
- Registrare una vittoria, una patta o una sconfitta non cancella piu'
  la descrizione della scacchiera. Viene chiesto se la partita e'
  finita e, solo rispondendo di si', l'avversario torna a Nessuno.
- L'identificativo della scacchiera viene letto come numero, quindi i
  limiti fra 1 e 999 valgono davvero.
- Le conferme di cancellazione e i comandi di EDT accettano anche le
  maiuscole.
- Le conferme mostrano il nome della scacchiera e non la lista Python
  che lo contiene.
- La ricerca di una lista Elo dichiara l'ambiguita' ed elenca le liste
  trovate, come gia' faceva quella delle scacchiere.

### Accessibilita'
- Versione e data di rilascio sono due costanti separate, e le due
  frasi di apertura sono in italiano corretto.
- Le statistiche Elo dicono prima l'etichetta e poi il valore, una
  frase per riga, senza trattini di separazione e dentro i quaranta
  caratteri utili al display braille.
- Le spiegazioni lunghe e le tabelle di riferimento della funzione da
  Elo ad ASCII sono state spezzate.

### Pulizia
- L'elenco dei comandi del menu principale e' una tabella sola, da cui
  discendono sia il menu stampato sia i comandi accettati.
- Il .gitignore adesso esclude davvero __pycache__ e i file compilati.
  Dal repository sono spariti tre .pyc, un file vuoto chiamato git e il
  vecchio archivio ChessReg.dat.
- Il sorgente passa ruff senza rilievi.

### Trovate durante il lavoro
- Rinominare una scacchiera dandole un identificativo e un nome gia'
  usati da un'altra cancellava quell'altra. Ora il programma avvisa e
  tiene il nome vecchio. Se la scacchiera rinominata era quella attiva,
  la chiave di stato la segue.
- Stessa perdita rinominando una lista Elo su un nome esistente. Ora il
  nome duplicato viene rifiutato.

### Non fatto
- Il rilievo 21, cioe' separare le chiavi di stato active_sch e
  active_elo dai dati e trasformare la scacchiera da lista a
  dizionario, resta aperto: e' un cambiamento di formato che richiede
  una migrazione dell'archivio.

## 5.0.1 del 2 settembre 2026
- Vecchiume rimossa da GBUtils V92 e riportata qui in locale.

## 5.0.0 del 26 maggio 2026
- Migrazione dell'archivio da pickle a JSON, ottimizzazioni e
  accessibilita' per display braille.
