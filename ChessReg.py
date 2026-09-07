# Chessreg, Data Concepimento 21/12/2018
# Gestionale per Risultati ottenuti giocando a scacchi sulle mie scacchiere
# 10/11/2020, cambio nome in Chessreg
# 28/06/2024 Spostato su Github
# 26/05/2026 Versione 5.0.0, migrazione a JSON, ottimizzazioni e accessibilità display Braille.
# 02/09/2026 Versione 5.0.1, Vecchiume rimossa da GBUtils V92 e riportata qui in locale.
# 07/09/2026 Versione 6.0.0, revisione 1 dell'analisi del codice: archivio protetto,
#            salvataggio atomico, statistiche corrette e messaggi accessibili.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalita' auto)

import json
import os
import statistics
import sys

from GBUtils import dgt, key, sonify


def Vecchiume(y=1974, m=9, g=13, h=22, i=10):
    """Restituisce quanto tempo e' passato dalla data indicata a ora.
    V1.1 del 2 settembre 2026, versione locale dopo la rimozione da GBUtils V92.
    Riceve anno, mese, giorno, ora e minuto e ne descrive a parole la distanza da adesso.
    """
    from datetime import datetime, timezone

    from dateutil import relativedelta
    adesso = datetime.now(timezone.utc).astimezone()
    quando = datetime(y, m, g, h, i, tzinfo=adesso.tzinfo)
    eta = relativedelta.relativedelta(adesso, quando)
    parti = []
    if eta.years > 0:
        parti.append(f"{eta.years} anno" if eta.years == 1 else f"{eta.years} anni")
    if eta.months > 0:
        parti.append(f"{eta.months} mese" if eta.months == 1 else f"{eta.months} mesi")
    if eta.days > 0:
        parti.append(f"{eta.days} giorno" if eta.days == 1 else f"{eta.days} giorni")
    if eta.hours > 0:
        parti.append(f"{eta.hours} ora" if eta.hours == 1 else f"{eta.hours} ore")
    if eta.minutes > 0:
        parti.append(f"{eta.minutes} minuto" if eta.minutes == 1 else f"{eta.minutes} minuti")
    if not parti:
        return "pochi istanti"
    if len(parti) == 1:
        return parti[0]
    return ", ".join(parti[:-1]) + " e " + parti[-1]


# Costanti
VERSIONE = "6.0.0"
RELEASE_DATE = "7 settembre 2026"
RELEASE_STAMP = (2026, 9, 7, 22, 30)
NASCITA_STAMP = (2018, 12, 21, 22, 10)

# Quanti valori servono come minimo per il grafico sonoro,
# per la stringa DEA e per le statistiche Elo.
MIN_GRAFICO = 3
MIN_DEA = 5
MIN_STATISTICHE = 6

PRI1, PRI2, PRI3, PRI4 = (
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
    '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
    '0123456789!"£$%&/()=[]{}<>ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
)

# Costanti indici scacchiera
IDX_DESC = 0
IDX_LUOGO = 1
IDX_AVVERSARIO = 2
IDX_MEZZO = 3
IDX_COLORE = 4  # True = Bianco, False = Nero
IDX_VIT_BIANCO = 5
IDX_PAT_BIANCO = 6
IDX_SCO_BIANCO = 7
IDX_VIT_NERO = 8
IDX_PAT_NERO = 9
IDX_SCO_NERO = 10

# Tabella unica dei comandi del menu principale:
# chiave digitata, descrizione parlata. E' l'unica fonte sia per il menu
# stampato sia per il filtro dei comandi accettati.
COMANDI = {
    "dea": "Da Elo ad ASCII",
    "edt": "Edita dati scacchiera",
    "elo": "Modifica Elo registrati",
    "gle": "Gestione liste Elo",
    "gse": "Grafico sonoro degli Elo registrati",
    "lst": "Vedi Elo",
    "sca": "Gestione scacchiere",
    "sgp": "Statistiche generali sulle partite",
    "slv": "Salva il database su disco",
    "ste": "Statistiche sui valori Elo registrati",
    "?": "Rilegge questo menu",
}

# Voci che non sono comandi a tre lettere e vanno spiegate a parte.
COMANDI_SPECIALI = {
    "INVIO": "Esce dal programma",
    "ESC": "Esce dal programma, come INVIO: ogni modifica e' gia' salvata",
    ".parola": "Cerca la parola nei dati delle scacchiere",
}

# Variabili
dizsch, dizelo = {}, {}
elo = []
contcom = 1
salva = False
acccom = [*COMANDI.keys(), "esc", ""]

# I percorsi sono ancorati alla cartella del programma, non a quella di lavoro,
# cosi' l'archivio e' sempre lo stesso da qualunque cartella si avvii ChessReg.
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DB_PATH = os.path.join(BASE_DIR, "ChessReg.json")
BAK_DB_PATH = os.path.join(BASE_DIR, "ChessReg.json.bak")
TMP_DB_PATH = os.path.join(BASE_DIR, "ChessReg.json.tmp")

# qf
def SalvaDB():
    """Salva il db sul disco in formato JSON.
    Scrive prima su un file temporaneo e poi lo mette al posto
    dell'archivio con os.replace, che e' atomico: se qualcosa va storto
    l'archivio precedente resta intatto. Della versione sostituita
    conserva una copia con estensione .bak.
    Restituisce True se il salvataggio e' riuscito.
    """
    data = {
        "dizsch": dizsch,
        "dizelo": dizelo
    }
    try:
        with open(TMP_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.flush()
            os.fsync(f.fileno())
        if os.path.exists(JSON_DB_PATH):
            os.replace(JSON_DB_PATH, BAK_DB_PATH)
        os.replace(TMP_DB_PATH, JSON_DB_PATH)
    except OSError as e:
        print(f"Errore durante il salvataggio del database: {e}")
        print("L'archivio precedente non e' stato toccato.")
        return False
    return True

def Salvasubito():
    """Registra sul disco la modifica appena fatta.
    Se il salvataggio non riesce, lascia il lavoro in sospeso
    cosi' che il comando SLV o l'uscita possano riprovarci.
    """
    global salva
    salva = True
    if SalvaDB():
        salva = False

def Elencosch():
    """Restituisce i nomi delle scacchiere vere, senza la chiave di stato"""
    return [k for k in dizsch if k != "active_sch"]

def Elencoliste():
    """Restituisce i nomi delle liste Elo vere, senza la chiave di stato"""
    return [k for k in dizelo if k != "active_elo"]

def Cercasch(chiave):
    """Riceve la chiave da cercare sia nelle chiavi che nei valori del dizionario scacchiere
    restituisce la lista dei risultati"""
    ris = []
    chiave_lower = chiave.lower()
    for k, v in dizsch.items():
        if k == "active_sch":
            continue
        if chiave_lower in k.lower():
            ris.append(k)
        elif isinstance(v, list):
            for j in v:
                if isinstance(j, str) and chiave_lower in j.lower() and k not in ris:
                    ris.append(k)
    return ris

def Vedising(k):
    """Mostra una scacchiera della quale riceve la chiave"""
    ln = str(k) + ", VS "
    ln += dizsch[k][IDX_AVVERSARIO] + " col "
    if dizsch[k][IDX_COLORE]:
        ln += "Bianco. "
    else:
        ln += "Nero. "
    prt = (
        dizsch[k][IDX_VIT_BIANCO] + dizsch[k][IDX_PAT_BIANCO] + dizsch[k][IDX_SCO_BIANCO] +
        dizsch[k][IDX_VIT_NERO] + dizsch[k][IDX_PAT_NERO] + dizsch[k][IDX_SCO_NERO]
    )
    ln += f"{prt} Partite."
    if dizsch['active_sch'] == k:
        ln += " Selezionata!"
    ln += "\nDescrizione/Nota: " + dizsch[k][IDX_DESC] + "\n"
    ln += "Si trova in: " + dizsch[k][IDX_LUOGO] + "\n"
    ln += "Si gioca via: " + dizsch[k][IDX_MEZZO] + "\n"
    print(ln)

def Vedisch():
    print(f"\nArchivio scacchiere registrate ({len(Elencosch())}).")
    for k in dizsch:
        if k != "active_sch":
            Vedising(k)

def Cancellasch():
    if len(Elencosch()) < 2:
        print("\nNon è possibile cancellare l'ultima scacchiera rimasta, l'archivio non può restare vuoto.")
        return
    print("Cancellazione di una delle scacchiere salvate.")
    chiave = dgt(
        prompt="\nDigita una o più parole chiave da cercare nei dati della scacchiera> ",
        kind='s', smin=1, smax=36, default='generica'
    )
    s1 = Cercasch(chiave)
    if len(s1) == 0:
        print(f"Nessuna delle {len(Elencosch())} scacchiere presenti nell'archivio, contiene la chiave cercata.")
        return
    elif len(s1) > 1:
        print(f"I risultati riportano {len(s1)} scacchiere. Prova ad usare chiavi diverse per ridurre il risultato ad una sola scacchiera")
        for j in s1:
            Vedising(j)
        return
    if s1[0] == dizsch["active_sch"]:
        print("\nNon è possibile eliminare la scacchiera attiva, selezionarne una diversa prima di procedere all'eliminazione.")
        return
    s = key(f"Sicuro di voler cancellare {s1}? (S o N)? >", 30)
    if s == "s":
        print(f"\nOk, cancello la scacchiera {s1}.")
        del dizsch[s1[0]]
        print(f"\nFatto, ora ci sono {len(Elencosch())} scacchiere in archivio.")
        Salvasubito()
        return
    else:
        print("\nNo problem! Non tocco nulla.")
        return

def Impostasch():
    print("Imposta la scacchiera attiva.")
    chiave = dgt(
        prompt="\nDigita una o più parole chiave da cercare nei dati della scacchiera> ",
        kind='s', smin=1, smax=36, default='generica'
    )
    s1 = Cercasch(chiave)
    if len(s1) > 1:
        print(f"I risultati riportano {len(s1)} scacchiere. Prova ad usare chiavi diverse per ridurre il risultato ad una sola scacchiera")
        for j in s1:
            Vedising(j)
        return
    elif len(s1) == 0:
        print(f"Nessuna delle {len(Elencosch())} scacchiere presenti nell'archivio, contiene la chiave cercata.")
        return
    elif s1[0] == dizsch["active_sch"]:
        print(f"\n{s1} è già la scacchiera attiva.")
        return
    print(f"Imposto {s1[0]} come scacchiera attiva.")
    dizsch["active_sch"] = str(s1[0])
    print(f"Scacchiera {dizsch['active_sch']} attivata.")
    Salvasubito()
    return

def Riscrivisch():
    print("Sovrascrivi alcuni dati di una delle tue scacchiere.")
    chiave = dgt(
        prompt="\nDigita una o più parole chiave da cercare nei dati della scacchiera> ",
        kind='s', smin=1, smax=36, default='generica'
    )
    s1 = Cercasch(chiave)
    if len(s1) > 1:
        print(f"I risultati riportano {len(s1)} scacchiere. Prova ad usare chiavi diverse per ridurre il risultato ad una sola scacchiera")
        for j in s1:
            Vedising(j)
        return
    if len(s1) == 0:
        print(f"Nessuna delle {len(Elencosch())} scacchiere presenti nell'archivio, contiene la chiave cercata.")
        return
    print(f"E' stata trovata la scacchiera {s1[0]}")
    id_sch, nome = s1[0].split(":", maxsplit=1)
    if id_sch.isdigit():
        idpre = int(id_sch)
    else:
        idpre = 1
    nid = dgt(prompt=f"Nuovo ID scacchiera: INVIO per accettare {idpre} >", kind="i", imin=1, imax=999, default=idpre)
    nnome = dgt(prompt=f"Nuovo nome: INVIO accetta {nome} >", smin=3, smax=128, default=nome)
    nnome = nnome.replace(":", " ").strip()
    if not nnome:
        nnome = nome
    chiave = f"{nid}:{nnome.capitalize()}"
    if s1[0] != chiave:
        if chiave in dizsch:
            print(f"Esiste gia' una scacchiera {chiave}.")
            print("Tengo il nome vecchio per non perderla.")
            chiave = s1[0]
        else:
            print(f"Ok, rinomino {s1[0]} in {chiave}.")
            dizsch[chiave] = dizsch.pop(s1[0])
            if dizsch["active_sch"] == s1[0]:
                dizsch["active_sch"] = chiave
    ndesc = dgt(
        f"\nNuova Descrizione/Nota? (INVIO) accetta {dizsch[chiave][IDX_DESC]}> ",
        smin=0, smax=4096, default=dizsch[chiave][IDX_DESC]
    )
    dizsch[chiave][IDX_DESC] = ndesc
    navv = dgt(
        f"\nNuovo Avversario? (INVIO) accetta {dizsch[chiave][IDX_AVVERSARIO]}> ",
        smin=0, smax=128, default=dizsch[chiave][IDX_AVVERSARIO]
    )
    dizsch[chiave][IDX_AVVERSARIO] = navv
    nluog = dgt(
        f"\nNuovo luogo? (INVIO) accetta {dizsch[chiave][IDX_LUOGO]}> ",
        smin=0, smax=256, default=dizsch[chiave][IDX_LUOGO]
    )
    dizsch[chiave][IDX_LUOGO] = nluog
    nmezz = dgt(
        f"\nNuovo mezzo? (INVIO) accetta {dizsch[chiave][IDX_MEZZO]}> ",
        smin=0, smax=128, default=dizsch[chiave][IDX_MEZZO]
    )
    dizsch[chiave][IDX_MEZZO] = nmezz
    print("Fatto!")
    dizsch["active_sch"] = chiave
    print(f"La scacchiera attiva è ora: {chiave}")
    Salvasubito()
    return

def Aggiungisch():
    print("Aggiungi una nuova scacchiera.")
    idsch = 1
    while any(k.startswith(f"{idsch}:") for k in dizsch):
        idsch += 1
    id_sch = dgt(prompt=f"ID Scacchiera, INVIO per accettare {idsch} >", kind="i", imin=1, imax=999, default=idsch)
    nb = dgt(prompt="Nome scacchiera: >", smin=3, smax=128, default="Generica")
    nb = nb.replace(":", " ").strip()
    if not nb:
        nb = "Generica"
    chiave = f"{id_sch}:{nb.capitalize()}"
    if chiave in dizsch:
        print("Questa scacchiera esiste già in archivio.")
        return
    desc = dgt(prompt="Descrizione, nota, situazione: >", smin=0, smax=4096, default="Nessuna descrizione")
    scacchiera = [desc]
    posi = dgt(prompt="Dove si trova: >", smin=0, smax=256, default="Ovunque")
    scacchiera.append(posi)
    avve = dgt(prompt="Avversario: >", smin=0, smax=128, default="Un cattivone!")
    scacchiera.append(avve)
    mezzo = dgt(prompt="Sito/mezzo: >", smin=0, smax=128, default="Piccione viaggiatore!")
    scacchiera.append(mezzo)
    scacchiera.append(True)
    print("Colore impostato su: BIANCO")
    vps = [0, 0, 0, 0, 0, 0]
    scacchiera.extend(vps)
    dizsch[chiave] = scacchiera
    print(f"Scacchiera creata! L'archivio ne contiene ora {len(Elencosch())}.")
    Salvasubito()
    return

def Gestsch(dizsch):
    """Gestione delle scacchiere
    riceve e restituisce il dizionario che le contiene"""
    print(f"Gestione delle scacchiere registrate.\nCi sono {len(Elencosch())} scacchiere salvate\n\t{dizsch['active_sch']} è la scacchiera attualmente selezionata.")
    print("Menù: A Aggiungi, V Vedi, I Imposta, R Riscrivi, C Cancella, E Esci.")
    while True:
        s = key("Fai la tua scelta: AVIRCE> ", 60).lower()
        if s in {"", "\x1b"}:
            break
        if s == "v":
            Vedisch()
        elif s == "i":
            Impostasch()
        elif s == "a":
            Aggiungisch()
        elif s == "r":
            Riscrivisch()
        elif s == "c":
            Cancellasch()
        elif s == "e":
            break
        else:
            print("\nScelta non valida:\nA Aggiungi una scacchiera nuova,\nV Vedi lista scacchiere;\nI Imposta la scacchiera attiva;\nR riscrivi i dati della scacchiera;\nC Cancella una scacchiera;\nE Esci e torna al menù principale.")
    print("\nTorno al menù principale.")
    return dizsch

def Riparaattivi(dizsch, dizelo):
    """Controlla che le due chiavi di stato indichino elementi esistenti.
    Se non lo fanno le corregge in memoria, avvisando: e' una riparazione
    silenziosa dello stato, mai una sostituzione dei dati.
    """
    schede = [k for k in dizsch if k != "active_sch"]
    if dizsch.get("active_sch") not in schede:
        if not schede:
            return False
        dizsch["active_sch"] = schede[0]
        print(f"Scacchiera attiva non valida, attivo {schede[0]}.")
    liste = [k for k in dizelo if k != "active_elo"]
    if dizelo.get("active_elo") not in liste:
        if not liste:
            return False
        dizelo["active_elo"] = liste[0]
        print(f"Lista Elo attiva non valida, attivo {liste[0]}.")
    return True

def Loaddisco():
    """Carica il registro dal disco, o ne crea uno nuovo se non esiste.
    Se l'archivio esiste ma non si riesce a leggerlo, la funzione si ferma
    e restituisce None senza scrivere niente: i dati sul disco restano
    intatti e la decisione su cosa fare passa a Gabriele.
    """
    print("Caricamento dati in corso...")
    if os.path.exists(JSON_DB_PATH):
        try:
            with open(JSON_DB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            dizsch = data["dizsch"]
            dizelo = data["dizelo"]
        except (OSError, ValueError, KeyError) as e:
            print("\nL'archivio esiste ma non si riesce a leggerlo.")
            print(f"Motivo: {e}")
            print(f"File: {JSON_DB_PATH}")
            print("Non ho scritto niente: i dati sul disco")
            print("sono rimasti come erano.")
            if os.path.exists(BAK_DB_PATH):
                print("C'e' una copia precedente in")
                print(f"{BAK_DB_PATH}")
                print("Per usarla, rinominala in ChessReg.json")
                print("dopo aver messo al sicuro quella rotta.")
            return None
        if not Riparaattivi(dizsch, dizelo):
            print("\nL'archivio e' stato letto ma non contiene")
            print("nessuna scacchiera o nessuna lista Elo.")
            print("Non ho scritto niente.")
            return None
        elo = dizelo[dizelo["active_elo"]]
        print("   dati caricati dall'archivio.")
        return dizsch, dizelo, elo

    # L'archivio non esiste: si parte da zero.
    print("Archivio non trovato, ne creo uno nuovo.")
    dizsch = {
        "1:Generica": [
            "Spero di vincere",
            "Ovunque",
            "Un cattivone",
            "Piccione",
            True,
            0, 0, 0, 0, 0, 0
        ],
        "active_sch": "1:Generica"
    }
    dizelo = {
        "active_elo": "Default",
        "Default": []
    }
    elo = dizelo[dizelo["active_elo"]]
    return dizsch, dizelo, elo

def Gestelo(elo, nelo):
    """routine di servizio di Modelo
    riceve la lista elo attiva e il valore da aggiungere
    restituisce la lista aggiornata
    """
    celo = elo.count(nelo)
    if celo == 0:
        print(f"\nL'Elo {nelo} non è mai stato registrato prima in questa lista.")
    else:
        print(f"\nL'elo inserito, {nelo}, compare altre {celo} volte, in questa lista.")
    lista_vuota = len(elo) == 0
    if not lista_vuota:
        omed = statistics.mean(elo)
        elorange = max(elo) - min(elo)
        if len(elo) > 2 and elorange > 0:
            print(f"Minimo: {min(elo)}.")
            print(f"Massimo: {max(elo)}.")
            print(f"Posizione del nuovo valore: {(nelo-min(elo)) * 100 / elorange:.1f}%.")
    else:
        omed = 0.0
    elo.append(nelo)
    print("Nuovo ELO aggiunto.")
    nmed = statistics.mean(elo)
    if lista_vuota:
        print(f"Primo valore della lista: {nelo}.")
        print("Non c'e' ancora una variazione da")
        print("confrontare.")
    else:
        print(f"Media prima: {omed:.3f}.")
        print(f"Media adesso: {nmed:.3f}.")
        print(f"Differenza: {nmed-omed:.3f}.")
    return elo

def Grafson(e):
    """Seleziona un quantitativo degli ultimi elo registrati e produce un grafico sonoro"""
    if len(e) < MIN_GRAFICO:
        print(f"La lista Elo contiene solo {len(e)} valori.")
        print(f"Ne servono almeno {MIN_GRAFICO} per il grafico.")
        return
    q = dgt(f"Quanti ELO prendo in considerazione? (fra {MIN_GRAFICO} e {len(e)}), (INVIO = Tutti) >", kind="i", imin=MIN_GRAFICO, imax=len(e), default=len(e))
    durgraf = dgt("Durata del grafico in secondi? ", kind="f", fmin=1.0, fmax=120.0, default=20.0)
    print(f"Grafico sonoro degli ultimi {q} punteggi Elo.")
    print(f"Durata: {durgraf:.1f} secondi.")
    sonify(e[len(e)-q:len(e)], durgraf, vol=0.3)
    return

def Perc(x, y=100):
    """restituisce la percentuale di x rispetto ad y"""
    if y == 0:
        return 0.0
    return (x * 100 / y)

def Cercalista():
    """Cerca una lista Elo per nome.
    Se le corrispondenze sono piu' di una lo dice e le elenca,
    restituendo stringa vuota: tocca a chi cerca precisare meglio.
    """
    print("Digita il nome, o parte del nome, della lista da selezionare.")
    s = dgt(prompt="> ", kind="s", smin=1, smax=20).lower()
    trovate = [k for k in Elencoliste() if s in k.lower()]
    if len(trovate) > 1:
        print(f"Trovate {len(trovate)} liste con questa chiave.")
        print("Precisa meglio. Ecco le liste trovate:")
        for k in trovate:
            print(f"- {k}, valori {len(dizelo[k])}.")
        return ""
    if len(trovate) == 1:
        return trovate[0]
    return ""

def Rinominalista():
    print("Rinomina una delle tue liste Elo.")
    s1 = Cercalista()
    if not s1:
        print("Nessuna lista scelta, non tocco nulla.")
        return
    nn = dgt(prompt="Nuovo nome: ", smin=3, smax=64)
    if nn == s1:
        print("Il nome e' lo stesso, non tocco nulla.")
        return
    if nn in dizelo:
        print(f"Esiste gia' una lista {nn}.")
        print("Scegli un nome diverso, non tocco nulla.")
        return
    print(f"Ok, rinomino {s1} in {nn}.")
    dizelo[nn] = dizelo[s1]
    del dizelo[s1]
    if dizelo["active_elo"] == s1:
        dizelo["active_elo"] = nn
        print(f"{nn} è la lista attiva.")
    print("Fatto!")
    Salvasubito()
    return

def Impostalista():
    """sub di ActiveEloList"""
    global elo
    print("Imposta la lista Elo attiva.")
    s1 = Cercalista()
    if not s1:
        print("Nessuna lista scelta, non tocco nulla.")
        return
    print(f"Imposto {s1} come lista attiva.")
    dizelo["active_elo"] = s1
    elo = dizelo[s1]
    print(f"Lista {s1} attivata, contiene {len(elo)} valori.")
    Salvasubito()
    return

def Vediliste():
    """sub di ActiveEloList"""
    print("\nListe Elo salvate.\nNome lista, numero valori registrati.")
    for k, v in dizelo.items():
        if k != "active_elo":
            ln = f"- {k}, {len(v)}."
            if dizelo['active_elo'] == k:
                ln += " (Lista attiva!)"
            print(ln)

def Cancellalista():
    if len(Elencoliste()) < 2:
        print("\nNon è possibile cancellare l'ultima lista, l'archivio non può restare vuoto.")
        return
    print("Cancellazione di una delle liste Elo salvate.")
    s1 = Cercalista()
    if not s1:
        print("Nessuna lista scelta, non tocco nulla.")
        return
    if s1 == dizelo["active_elo"]:
        print("\nNon è possibile eliminare la lista attiva, selezionarne una diversa, prima di procedere all'eliminazione.")
        return
    s = key(f"Sicuro di voler cancellare {s1}? (S o N)? ", 180).lower()
    if s == "s":
        print(f"Ok, cancello la lista {s1}.")
        del dizelo[s1]
        print(f"Fatto, ora ci sono {len(Elencoliste())} liste in archivio.")
        Salvasubito()
        return
    else:
        print("No problem! Non tocco nulla.")
        return

def Aggiungilista():
    print("Aggiungi una nuova lista Elo.")
    n = dgt(prompt="Nome: ", smin=3, smax=64)
    idelo = 1
    while any(k.startswith(f"{idelo}:") for k in dizelo):
        idelo += 1
    n = f"{idelo}:{n}"
    dizelo[n] = []
    print(f"Lista aggiunta. L'archivio ne contiene ora {len(Elencoliste())}.")
    Salvasubito()

def ActiveEloList():
    """Managing delle liste degli Elo    """
    print(f"Gestione liste Elo.\nCi sono {len(Elencoliste())} liste salvate\n\t{dizelo['active_elo']} è la lista attualmente selezionata.")
    print("Menù: A Aggiungi, V Vedi, I Imposta, R Rinomina, C Cancella, E Esci.")
    while True:
        s = key("Fai la tua scelta: AVIRCE> ", 60).lower()
        if s in {"", "\x1b"}:
            break
        if s == "v":
            Vediliste()
        elif s == "i":
            Impostalista()
        elif s == "a":
            Aggiungilista()
        elif s == "r":
            Rinominalista()
        elif s == "c":
            Cancellalista()
        elif s == "e":
            break
        else:
            print("\nScelta non valida:\nA Aggiungi una lista nuova,\nV Vedi liste Elo;\nI Imposta la lista attiva;\nR Dai un nuovo nome alla lista;\nC Cancella la lista;\nE Esci e torna al menù principale.")
    print("\nTorno al menù principale.")

def Statgen():
    print("Pagina di statistiche generali sulle partite registrate.")
    tvitb, tparb, tscob, tvitn, tparn, tscon = 0, 0, 0, 0, 0, 0
    for k, v in dizsch.items():
        if k != "active_sch":
            tvitb += v[IDX_VIT_BIANCO]
            tvitn += v[IDX_VIT_NERO]
            tparb += v[IDX_PAT_BIANCO]
            tparn += v[IDX_PAT_NERO]
            tscob += v[IDX_SCO_BIANCO]
            tscon += v[IDX_SCO_NERO]
    tpartite = tvitb + tvitn + tparb + tparn + tscob + tscon
    num_boards = len(dizsch) - 1
    if num_boards > 0:
        avg_part = tpartite / num_boards
    else:
        avg_part = 0.0
    print(f"Totale risultati registrati: {tpartite} partite, giocate su {num_boards} scacchiere\n\tin media {avg_part:.1f} partite su ciascuna scacchiera.")
    tvitp, tparp, tscop = Perc(tvitb + tvitn, tpartite), Perc(tparb + tparn, tpartite), Perc(tscob + tscon, tpartite)
    print(f"\nSul totale c'è il {tvitp:3.2f}%, ({tvitb+tvitn}) di partite vinte,\n\til {tparp:3.2f}%, ({tparb+tparn}) di partite patte ed il {tscop:3.2f}%, ({tscob+tscon}) di partite perse.")
    print("\t\tPer colore")
    tpartiteb = tvitb + tparb + tscob
    tpartiten = tvitn + tparn + tscon
    print(f"Ci sono il {Perc(tpartiteb,tpartite):.2f}% di partite col Bianco e il {Perc(tpartiten,tpartite):.2f}% col Nero.")
    print(f"Vittorie: col Bianco {Perc(tvitb,tvitb+tvitn):.2f}%, su {tvitb+tvitn} partite, contro il {Perc(tvitn,tvitb+tvitn):.2f}% col Nero.")
    print(f"Patte: col Bianco {Perc(tparb,tparb+tparn):.2f}%, su {tparb+tparn} partite, contro il {Perc(tparn,tparb+tparn):.2f}% col Nero.")
    print(f"Sconfitte: col Bianco {Perc(tscob,tscob+tscon):.2f}%, su {tscob+tscon} partite, contro il {Perc(tscon,tscob+tscon):.2f}% col Nero.")

def Statelo(e):
    """Statistiche sulla lista Elo ricevuta, calcolate su tutti i valori"""
    if len(e) < MIN_STATISTICHE:
        print("Ancora pochi valori Elo registrati per produrre statistiche.")
        print(f"Ne servono almeno {MIN_STATISTICHE}.")
        return
    print("Statistiche sui valori registrati.")
    print(f"Valori elaborati: {len(e)}.")
    print(f"Minimo: {min(e)}.")
    print(f"Media bassa: {statistics.median_low(e)}.")
    print(f"Valore medio: {statistics.mean(e):.2f}.")
    print(f"Mediana: {statistics.median(e):.2f}.")
    print(f"Mediana interpolata: {statistics.median_grouped(e, interval=1):.1f}.")
    print(f"Media alta: {statistics.median_high(e)}.")
    print(f"Massimo: {max(e)}.")
    print(f"Dispersione: {statistics.pvariance(e, mu=None):.3f}.")
    return

def Daeloascii(e):
    """Trasforma i valori ELO in una stringa per leggerne l'andamento"""
    if len(e) < MIN_DEA:
        print("Non ci sono abbastanza ELO salvati")
        print("per effettuare questo calcolo.")
        print(f"Riprova con almeno {MIN_DEA} valori.")
        return
    print("Da ELO ad ASCII.")
    print("Trasforma i valori della lista Elo")
    print("in una stringa di caratteri.")
    print("La stringa parte dal carattere piu' basso")
    print("e sale fino al piu' alto della tabella")
    print("di riferimento che sceglierai.")
    print("Ci sono 4 tabelle, in ordine di risoluzione")
    print("crescente.")
    print("1, solo maiuscole, risoluzione 26.")
    print("2, maiuscole e minuscole, risoluzione 52.")
    print("3, numeri, maiuscole e minuscole,")
    print("   risoluzione 62.")
    print("4, numeri, simboli, maiuscole e minuscole,")
    print("   risoluzione 78.")
    while True:
        q = key("Quale vuoi usare, 1 2 3 o 4? ", 30)
        if q in {"1", "2", "3", "4"}:
            break
        print("Risposta non valida. Inserisci un numero da 1 a 4.")
    if q == "1":
        pri, pridiv = PRI1, len(PRI1)
    elif q == "2":
        pri, pridiv = PRI2, len(PRI2)
    elif q == "3":
        pri, pridiv = PRI3, len(PRI3)
    elif q == "4":
        pri, pridiv = PRI4, len(PRI4)
    q = dgt("Quanti ELO prendo in considerazione? (invio uguale tutti)", kind="i", imin=MIN_DEA, imax=len(e), default=len(e))
    print(f"Elaboro gli ultimi {q} punteggi Elo.")
    e = e[len(e)-q:len(e)]
    emin, emax = min(e), max(e)
    emed = int(sum(e) / len(e))
    print(f"Valore piu' basso: {emin}.")
    print(f"Media approssimata: {emed}.")
    print(f"Valore piu' alto: {emax}.")
    eran = emax - emin
    print(f"Escursione coperta: {eran}.")
    print(f"Tabella scelta, risoluzione {len(pri)}:")
    print(pri)
    dea = ""
    for j in e:
        x = j - emin
        y = x * 100 / eran if eran > 0 else 0.0
        w = y / 100 * (pridiv - 1)
        dea += pri[round(w)]
    print("Stringa DEA elaborata:")
    print(dea)
    return

def Vedie(e):
    """Mostra la lista elo"""
    if len(e) == 0:
        print("Non ci sono ancora punteggi registrati.")
        return
    q = dgt("Visualizza gli ultimi elo salvati.\n\tQuanti ne vuoi vedere? (INVIO = ultimi 15)> ", kind="i", imax=len(e), imin=1, default=15)
    print(f"\nLista degli ultimi {q} punteggi Elo inseriti:")
    for j in range(len(e)-q, len(e)):
        if j >= 1:
            lelo = f"{j+1}: {e[j]}, variazione {e[j]-e[j-1]}."
        else:
            lelo = f"{j+1}: {e[j]}, primo valore."
        print(lelo)
    return

def Vedis(m):
    """Mostra situazione scacchiera"""
    print("Vedi scacchiera.")
    print(" - Titolo: " + m[IDX_DESC])
    if m[IDX_COLORE]:
        c = "il Bianco"
    else:
        c = "il Nero"
    print(" - Giochi con " + c)
    print(" - Hai: " + str(m[IDX_VIT_BIANCO]) + " vittorie, " + str(m[IDX_PAT_BIANCO]) + " patte e " + str(m[IDX_SCO_BIANCO]) + " sconfitte, col Bianco;")
    print(" - Hai: " + str(m[IDX_VIT_NERO]) + " vittorie, " + str(m[IDX_PAT_NERO]) + " patte e " + str(m[IDX_SCO_NERO]) + " sconfitte, col Nero.")

def Modelo(elo):
    """aggiunge o toglie elo dalla lista attiva"""
    prompt1 = f"Modifica lista ELO\n(1) Aggiunge, (2) applica una modifica all'ultimo valore, oppure (3) per rimuovere l'ultimo inserito.\n\tCi sono {len(elo)} valori attualmente registrati, cosa vuoi fare, 1, 2, 3? "
    while True:
        s = key(prompt1, 60)
        if s in {"1", "2", "3"}:
            break
        if s in {"", "\x1b"}:
            print("Nessuna scelta fatta, non tocco la lista.")
            return elo
        print("Rispondi 1 per aggiungere valori, 2 per aggiungere un valore all'ultimo registrato o 3 per rimuovere l'ultimo inserito.")
    if s == "2":
        if not elo:
            print("La lista e' vuota, non c'e' nessun")
            print("ultimo valore da modificare.")
            return elo
        uelo = elo[-1]
        nelo = uelo + dgt(kind="i", prompt=f"\nInserire la variazione da applicare a {uelo} > ", imin=-1000, imax=1000)
        elo = Gestelo(elo, nelo)
        Salvasubito()
        return elo
    elif s == "1":
        nelo = dgt(kind="i", prompt="\nNuovo valore Elo? ", imin=500, imax=5000)
        elo = Gestelo(elo, nelo)
        Salvasubito()
        return elo
    else:
        if not elo:
            print("La lista e' vuota, non c'e' niente")
            print("da rimuovere.")
            return elo
        rim = elo.pop()
        print(f"Rimosso il valore {rim}.")
        Salvasubito()
        return elo

def Fineparita(attiva):
    """Chiede se la partita e' finita e, se lo e', libera l'avversario.
    La descrizione, che e' una nota scritta a mano, non viene mai toccata.
    """
    r = key("Partita finita? Libero l'avversario? (S o N)> ", 30).lower()
    if r == "s":
        dizsch[attiva][IDX_AVVERSARIO] = "Nessuno"
        print("Avversario azzerato, scacchiera libera.")
        print("La descrizione e' rimasta com'era.")
    else:
        print("Avversario lasciato com'era.")

def Edit():
    """Modifica avversario, colore e contatori della scacchiera attiva"""
    attiva = dizsch["active_sch"]
    print("Modifica alcuni dati della scacchiera attiva.")
    while True:
        ln = str(attiva) + ", VS "
        ln += dizsch[attiva][IDX_AVVERSARIO] + " col "
        if dizsch[attiva][IDX_COLORE]:
            p = "Bianco"
            delta = 0
        else:
            p = "Nero"
            delta = 3
        ln += p
        prt = (
            dizsch[attiva][IDX_VIT_BIANCO] + dizsch[attiva][IDX_PAT_BIANCO] + dizsch[attiva][IDX_SCO_BIANCO] +
            dizsch[attiva][IDX_VIT_NERO] + dizsch[attiva][IDX_PAT_NERO] + dizsch[attiva][IDX_SCO_NERO]
        )
        ln += f" {prt} Partite."
        print(f"\n{ln}")
        print(f"Col {p}: {dizsch[attiva][5+delta]} vittorie,")
        print(f"{dizsch[attiva][6+delta]} patte,")
        print(f"{dizsch[attiva][7+delta]} sconfitte.")
        s = key("Quale dato vuoi cambiare:\nA per l'avversario, C per il colore, D per la Descrizione oppure\nV di Vittorie, P di Patte o S di Sconfitte?\n ESC per uscire.> ", 300).lower()
        if s in {"\x1b", ""}:
            break
        if s == "a":
            dizsch[attiva][IDX_AVVERSARIO] = dgt(prompt="\nAvversario: >", smin=0, smax=128, default="Un cattivone!")
            Salvasubito()
        elif s == "d":
            dizsch[attiva][IDX_DESC] = dgt(prompt="\nDesc./Nota? >", smin=0, smax=2048, default="Nessuna nota.")
            Salvasubito()
        elif s == "c":
            dizsch[attiva][IDX_COLORE] = not dizsch[attiva][IDX_COLORE]
            if dizsch[attiva][IDX_COLORE]:
                print("\nColore impostato a Bianco.")
            else:
                print("\nColore impostato a Nero.")
            Salvasubito()
        elif s == "v":
            v = dgt("\nModifica numero vittorie, digita il valore da aggiungere: (INVIO = +1)> ", kind="i", imin=-5, imax=5, default=1)
            dizsch[attiva][5+delta] += v
            Fineparita(attiva)
            Salvasubito()
        elif s == "p":
            v = dgt("\nModifica numero patte, digita il valore da aggiungere: (INVIO = +1)> ", kind="i", imin=-5, imax=5, default=1)
            dizsch[attiva][6+delta] += v
            Fineparita(attiva)
            Salvasubito()
        elif s == "s":
            v = dgt("\nModifica numero sconfitte, digita il valore da aggiungere: (INVIO = +1)> ", kind="i", imin=-5, imax=5, default=1)
            dizsch[attiva][7+delta] += v
            Fineparita(attiva)
            Salvasubito()
        else:
            print(f"\n{s} non è un comando valido. Digita A, C, D, V, P, S oppure ESC.")
    print("\n")

def Menu():
    """Visualizza il menu, ricavandolo dalla tabella unica dei comandi"""
    print("\nMenu dell'applicazione ChessReg")
    for k, v in COMANDI.items():
        print(f"{k.upper()}, {v}.")
    for k, v in COMANDI_SPECIALI.items():
        print(f"{k}, {v}.")

def main():
    global dizsch, dizelo, elo, contcom, salva
    print("\nBenvenuto in ChessReg di Gabriele Battaglia.")
    print(f"Versione {VERSIONE} del {RELEASE_DATE}.")
    print(f"Questa applicazione e' nata {Vecchiume(*NASCITA_STAMP)} fa.")
    print(f"Questa versione e' uscita {Vecchiume(*RELEASE_STAMP)} fa.")
    print("E' un registro dei risultati ottenuti sulle")
    print("scacchiere con cui gioco a scacchi online,")
    print("e tiene anche le liste dei punteggi Elo.")

    archivio_nuovo = not os.path.exists(JSON_DB_PATH)
    dati = Loaddisco()
    if dati is None:
        print("\nChessReg si ferma qui per non rischiare")
        print("di rovinare l'archivio. Ciao ciao.")
        return
    dizsch, dizelo, elo = dati
    if archivio_nuovo:
        Salvasubito()
        print("Nuovo archivio creato e salvato.")

    print("I comandi vanno confermati con INVIO.")
    print("Punto interrogativo per il menu,")
    print("INVIO a vuoto per uscire.")

    while True:
        s = dgt(f"[{contcom}] comandi signore: ", kind="s", smin=0, smax=16)
        s = s.lower()
        if s in acccom or (s and s[0] == "."):
            contcom += 1
            if s in {"", "esc"}:
                break
            elif s == "?":
                Menu()
            elif s == "edt":
                Edit()
            elif s == "elo":
                elo = Modelo(elo)
                dizelo[dizelo["active_elo"]] = elo
            elif s == "slv":
                if salva:
                    if SalvaDB():
                        print("\nDB salvato!")
                        salva = False
                else:
                    print("\nSalvataggio non necessario.")
                    contcom -= 1
            elif s == "gle":
                ActiveEloList()
                elo = dizelo[dizelo["active_elo"]]
            elif s == "gse":
                Grafson(elo)
            elif s == "ste":
                Statelo(elo)
            elif s == "sgp":
                Statgen()
            elif s == "sca":
                dizsch = Gestsch(dizsch)
            elif s == "dea":
                Daeloascii(elo)
            elif s and s[0] == "." and len(s) > 1:
                chiave = Cercasch(s[1:])
                if len(chiave) > 0:
                    print(f"\nTrovati {len(chiave)} risultati:")
                    for j in chiave:
                        Vedising(str(j))
                else:
                    print(f"{s[1:]} non è presente nei dati delle scacchiere registrate.")
                if len(chiave) == 1:
                    dizsch["active_sch"] = str(chiave[0])
                    print(f"{chiave[0]} è ora la scacchiera attiva.")
                    Salvasubito()
            elif s == "lst":
                Vedie(elo)
        else:
            print("Spiacente, comando non valido")

    # Chiusura
    if salva:
        if SalvaDB():
            print("Dati aggiornati salvati con successo.")
        else:
            print("Attenzione: modifiche non salvate.")
    else:
        print("Tutto gia' salvato sul disco.")
    print("Grazie per avermi usato!")
    print("Ciao ciao.")

if __name__ == "__main__":
    main()
