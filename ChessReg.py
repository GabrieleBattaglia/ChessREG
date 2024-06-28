# Chessreg, Data Concepimento 21/12/2018
# Gestionale per Risultati ottenuti giocando a scacchi sulle mie scacchiere
# 10/11/2020, cambio nome in Chessreg
# 28/06/2024 Spostato su Github

import pickle, eta2, statistics
from GBUtils import sonify, dgt, key

# Costanti
VERSIONE = "4.8.4 di ottobre 2023."
VETA=eta2.Vecchiume(2023,10,6,0,19)
ETA=eta2.Vecchiume(2018,12,21,22,10)
PRI1, PRI2, PRI3, PRI4 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',\
												 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',\
												 '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',\
												 '0123456789!"£$%&/()=[]{}<>ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
#Variabili
dizsch, dizelo = {}, {}
elo = []
contcom = 1
salva = False
acccom = ['slv','dea','edt','elo','gle','gse','lst','?','sgp','sca','ste','.','','esc']

#qf
def SalvaDB():
	'''Salva il db sul disco'''
	f = open("ChessReg.dat", "wb")
	pickle.dump(dizsch, f, pickle.HIGHEST_PROTOCOL)
	pickle.dump(dizelo, f, pickle.HIGHEST_PROTOCOL)
	f.close()
	return

def Cercasch(chiave):
	'''Riceve la chiave da cercare sia nelle chiavi che nei valori del dizionario scacchiere
	restituisce la lista dei risultati'''
	ris=[]
	for k,v in dizsch.items():
		if chiave in k.lower(): ris.append(k)
		elif isinstance(v, list):
			for j in v:
				if isinstance(j, str) and chiave in j.lower() and k.lower() not in ris: ris.append(k)
	if "active_sch" in ris: ris.remove("active_sch")
	return ris

def Vedising(k):
	'''Mostra una scacchiera della quale riceve la chiave'''
	ln=str(k)+", VS "
	ln+=dizsch[k][2]+" col "
	if dizsch[k][4]: ln+="Bianco. "
	else: ln+="Nero. "
	prt=dizsch[k][5]+dizsch[k][6]+dizsch[k][7]+dizsch[k][8]+dizsch[k][9]+dizsch[k][10]
	ln+=f"{prt} Partite."
	if dizsch['active_sch'] == k: ln += " Selezionata!"
	ln+="\nDescrizione/Nota: "+dizsch[k][0]+"\n"
	ln+="Si trova in: "+dizsch[k][1]+"\n"
	ln+="Si gioca via: "+dizsch[k][3]+"\n"
	print(ln)
	return

def Vedisch():
	print(f"\nArchivio scacchiere registrate ({len(dizsch)-1}).")
	for k in dizsch.keys():
		if k != "active_sch":
			Vedising(k)
	return

def Cancellasch():
	global salva
	if len(dizsch) == 2:
		print("\nNon è possibile cancellare l'ultima scacchiera rimasta, l'archivio non può restare vuoto.")
		return
	print("Cancellazione di una delle scacchiere salvate.")
	chiave=dgt(prompt="\nDigita una o più parole chiave da cercare nei dati della scacchiera> ",kind='s',smin=1,smax=36,default='generica')
	s1 = Cercasch(chiave)
	if len(s1) == 0:
		print(f"Nessuna delle {len(dizsch)-1} scacchiere presenti nell'archivio, contiene la chiave cercata.")
		return
	elif len(s1)>1:
		print(f"I risultati riportano {len(s1)} scacchiere. Prova ad usare chiavi diverse per ridurre il risultato ad una sola scacchiera")
		for j in s1:
			Vedising(j)
		return
	if s1[0] == dizsch["active_sch"]:
		print("\nNon è possibile eliminare la scacchiera attiva, selezionarne una diversa prima di procedere all'eliminazione.")
		return
	s = key(f"Sicuro di voler cancellare {s1}? (S o N)? >",30)
	if s == "s":
		print(f"\nOk, cancello la scacchiera {s1}.")
		del dizsch[s1[0]]
		print(f"\nFatto, ora ci sono {len(dizsch)-1} scacchiere in archivio.")
		salva=True
		return
	else:
		print("\nNo problem! Non tocco nulla.")
		return

def Impostasch():
	global salva
	print("Imposta la scacchiera attiva.")
	chiave=dgt(prompt="\nDigita una o più parole chiave da cercare nei dati della scacchiera> ",kind='s',smin=1,smax=36,default='generica')
	s1 = Cercasch(chiave)
	if len(s1)>1:
		print(f"I risultati riportano {len(s1)} scacchiere. Prova ad usare chiavi diverse per ridurre il risultato ad una sola scacchiera")
		for j in s1:
			Vedising(j)
		return
	elif len(s1) == 0:
		print(f"Nessuna delle {len(dizsch)-1} scacchiere presenti nell'archivio, contiene la chiave cercata.")
		return
	elif s1[0] == dizsch["active_sch"]:
		print(f"\n{s1} è già la scacchiera attiva.")
		return
	print(f"Imposto {s1[0]} come scacchiera attiva.")
	dizsch["active_sch"] = str(s1[0])
	print(f"Scacchiera {dizsch['active_sch']} attivata.")
	salva=True
	return

def Riscrivisch():
	global salva
	print("Sovrascrivi alcuni dati di una delle tue scacchiere.")
	chiave=dgt(prompt="\nDigita una o più parole chiave da cercare nei dati della scacchiera> ",kind='s',smin=1,smax=36,default='generica')
	s1 = Cercasch(chiave)
	if len(s1)>1:
		print(f"I risultati riportano {len(s1)} scacchiere. Prova ad usare chiavi diverse per ridurre il risultato ad una sola scacchiera")
		for j in s1:
			Vedising(j)
		return
	if len(s1) == 0:
		print(f"Nessuna delle {len(dizsch)-1} scacchiere presenti nell'archivio, contiene la chiave cercata.")
		return
	print(f"E' stata trovata la scacchiera {s1[0]}")
	id,nome=s1[0].split(":")
	nid=dgt(prompt=f"Nuovo ID scacchiera: INVIO per accettare {id} >", imin=1, imax=999,default=id)
	nnome=dgt(prompt=f"Nuovo nome: INVIO accetta {nome} >", smin=3, smax=128,default=nome)
	chiave=f"{nid}:{nnome.capitalize()}"
	if s1[0] != chiave:
		print(f"Ok, rinomino {s1[0]} in {chiave}.")
		dizsch[chiave] = dizsch.pop(s1[0])
	ndesc=dgt(f"\nNuova Descrizione/Nota? (INVIO) accetta {dizsch[chiave][0]}> ",smin=0,smax=4096,default=dizsch[chiave][0])
	dizsch[chiave][0]=ndesc
	navv=dgt(f"\nNuovo Avversario? (INVIO) accetta {dizsch[chiave][2]}> ",smin=0,smax=128,default=dizsch[chiave][2])
	dizsch[chiave][2]=navv
	nluog=dgt(f"\nNuovo luogo? (INVIO) accetta {dizsch[chiave][1]}> ",smin=0,smax=256,default=dizsch[chiave][1])
	dizsch[chiave][1]=nluog
	nmezz=dgt(f"\nNuovo mezzo? (INVIO) accetta {dizsch[chiave][3]}> ",smin=0,smax=128,default=dizsch[chiave][3])
	dizsch[chiave][3]=nmezz
	print("Fatto!")
	dizsch["active_sch"] = chiave
	print(f"La scacchiera attiva è ora: {chiave}")
	salva=True
	return

def Aggiungisch():
	global salva
	print("Aggiungi una nuova scacchiera.")
	idsch=0; pres=True
	while pres:
		idsch+=1
		for j in dizsch.keys():
			if str(idsch)+":" not in j: pres=False
			else: pres=True; break
	id=dgt(prompt=f"ID Scacchiera, INVIO per accettare {idsch} >",imin=1,imax=999,default=idsch)
	nb=dgt(prompt="Nome scacchiera: >",smin=3,smax=128,default="Generica")
	chiave=f"{id}:{nb.capitalize()}"
	if chiave in dizsch.keys():
		print("Questa scacchiera esiste già in archivio.")
		return
	desc=dgt(prompt="Descrizione, nota, situazione: >",smin=0,smax=4096,default="Nessuna descrizione")
	scacchiera=[desc]
	posi=dgt(prompt="Dove si trova: >",smin=0,smax=256,default="Ovunque")
	scacchiera.append(posi)
	avve=dgt(prompt="Avversario: >",smin=0,smax=128,default="Un cattivone!")
	scacchiera.append(avve)
	mezzo=dgt(prompt="Sito/mezzo: >",smin=0,smax=128,default="Piccione viaggiatore!")
	scacchiera.append(mezzo)
	scacchiera.append(True)
	print("Colore impostato su: BIANCO")
	vps=[0,0,0,0,0,0]
	scacchiera.extend(vps)
	dizsch[chiave] = scacchiera
	print(f"Scacchiera creata! L'archivio ne contiene ora {len(dizsch)-1}.")
	salva=True
	return

def Gestsch(dizsch):
	'''Gestione delle scacchiere
	riceve e restituisce il dizionario che le contiene'''
	print(f"Gestione delle scacchiere registrate.\nCi sono {len(dizsch)-1} scacchiere salvate\n\t{dizsch['active_sch']} è la scacchiera attualmente selezionata.")
	print("Menù: A Aggiungi, V Vedi, I Imposta, R Riscrivi, C Cancella, E Esci.")
	while True:
		s = key("Fai la tua scelta: AVIRCE> ", 60).lower()
		if s == "v": Vedisch()
		elif s == "i": Impostasch()
		elif s == "a": Aggiungisch()
		elif s == "r": Riscrivisch()
		elif s == "c": Cancellasch()
		elif s == "e": break
		else:
			print("\nScelta non valida:\nA Aggiungi una scacchiera nuova,\nV Vedi lista scacchiere;\nI Imposta la scacchiera attiva;\nR riscrivi i dati della scacchiera;\nC Cancella una scacchiera;\nE Esci e torna al menù principale.")
	print("\nTorno al menù principale.")
	return dizsch

def Loaddisco():
	'''Carica o crea il registro sul disco'''
	try:
		# Struttura scacchiera dizsch:
		# chiave "#:nome": valore = lista
		# struttura lista:
		# 0 str descrizione
		# 1 str posizione luogo
		# 2 str nome avversario
		# 3 str servizio social sistema mezzo
		# 4 booleano True = bianco
		# 5 int vittorie bianco
		# 6 int patte bianco
		# 7 int sconfitte bianco
		# 8 int vittorie nero
		# 9 int patte nero
		# 10 sconfitte nero
		# Struttura libreria elo: prima coppia chiave "active_elo": nome della lista in uso. Poi, chiave nomelista e valore lista elo.
		print("Caricamento dati in corso...")
		f = open ("ChessReg.dat", 'rb')
		dizsch = pickle.load(f)
		dizelo = pickle.load(f)
		f.close()
		elo = dizelo[dizelo["active_elo"]]
		print("   dati caricati.")
		return dizsch, dizelo, elo
	except IOError:
		print("...File ChessReg.dat, non trovato\n\t...creazione file in corso")
		dizsch = {"1:Generica":\
												["Spero di vincere",\
													"Ovunque",\
													"Un cattivone",\
													"Piccione",\
													True,\
													0,\
													0,\
													0,\
													0,\
													0,\
													0],\
														"active_sch":"1:Generica"}
		dizelo = {"active_elo":"Default", "Default":[]}
		elo = dizelo[dizelo["active_elo"]]
		SalvaDB()
		print("\nFile ChessReg.dat, creato con successo.")
		return dizsch, dizelo, elo

def Gestelo(elo, nelo):
	'''routine di servizio di Modelo
	riceve la lista elo attiva e il valore da aggiungere
	restituisce la lista aggiornata
	'''
	celo=elo.count(nelo)
	if celo==0: print(f"\nL'Elo {nelo} non è mai stato registrato prima in questa lista.")
	else: print(f"\nL'elo inserito, {nelo}, compare altre {celo} volte, in questa lista.")
	if len(elo) > 0:
		omed = statistics.mean(elo)
		elorange = max(elo)-min(elo)
		if len(elo)>2:
			print(f"Minimo / Valore inserito (posizionamento) / Massimo:\n\t{min(elo)} / {nelo}=({(nelo-min(elo)) * 100 / elorange:.3f}%) / {max(elo)}.")
	else: omed=0
	elo.append(nelo)
	print("Nuovo ELO aggiunto.")
	nmed = statistics.mean(elo)
	print(f"Variazione della media, prima / dopo / differenza:\n\t{omed:.3f} / {nmed:.3f} / {nmed-omed:.3f}")
	return elo

def Grafson(e):
	'''Seleziona un quantitativo degli ultimi elo registrati e produce un grafico sonoro'''
	if len(e)>5:
		e=e.copy()[1:]
	else:
		print(f"La lista Elo contiene solo {len(e)} valori.\nTroppo pochi per produrre un grafico audio.")
		return
	q=dgt(f"Quanti ELO prendo in considerazione? (fra 3 e {len(e)}), (INVIO = Tutti) >", kind="i", imin=3, imax=len(e), default=len(e))
	durgraf = dgt("Durata del grafico in secondi? ", kind="f", fmin=1.0, fmax=120.0, default=20.0)
	print(f"Grafico sonoro degli ultimi {q} punteggi Elo.\n\tDurata del grafico sonoro: {durgraf:.1f} secondi.")
	sonify(e[len(e)-q:len(e)], durgraf)
	return

def Perc(x, y=100):
	'''restituisce la percentuale di x rispetto ad y'''
	return (x*100/y)

def Cercalista():
	print("Digita il nome, o parte del nome, della lista da selezionare.")
	s = dgt(prompt="> ", kind="s", smin=1, smax=20)
	s1 = ""
	for k,v in dizelo.items():
		if s.lower() in k.lower(): s1=k
	return s1

def Rinominalista():
	global salva
	print("Rinomina una delle tue liste Elo.")
	s1 = Cercalista()
	if s1 == "" or s1 == "active_elo":
		print(f"Nessuno dei {len(dizelo)-1} nomi di liste presenti nell'archivio salvato, contiene la chiave cercata.")
		return
	nn=dgt(prompt="Nuovo nome: ", smin=3, smax=64)
	print(f"Ok, rinomino {s1} in {nn}.")
	dizelo[nn] = dizelo[s1]
	del dizelo[s1]
	if dizelo["active_elo"] == s1:
		dizelo["active_elo"] = nn
		print(f"{nn} è la lista attiva.")
	print("Fatto!")
	salva=True
	return

def Impostalista():
	'''sub di ActiveEloList'''
	global elo, salva
	print("Imposta la lista Elo attiva.")
	s1 = Cercalista()
	if s1 == "" or s1 == "active_elo":
		print(f"Nessuno dei {len(dizelo)-1} nomi di liste presenti nell'archivio salvato, contiene la chiave cercata.")
		return
	print(f"Imposto {s1} come lista attiva.")
	dizelo["active_elo"] = s1
	elo = dizelo[s1]
	print(f"Lista {s1} attivata, contiene {len(elo)} valori.")
	salva=True
	return

def Vediliste():
	'''sub di ActiveEloList'''
	print("\nListe Elo salvate.\nNome lista, numero valori registrati.")
	for k,v in dizelo.items():
		ln=f"- {k}, {len(v)}."
		if dizelo['active_elo'] == k: ln += " (Lista attiva!)"
		if k != "active_elo": print(ln)
	return

def Cancellalista():
	global salva
	if len(dizelo) == 2:
		print("\nNon è possibile cancellare l'ultima lista, l'archivio non può restare vuoto.")
		return
	print("Cancellazione di una delle liste Elo salvate.")
	s1=Cercalista()
	if s1 == "" or s1 == "active_elo":
		print(f"Nessuno dei {len(dizelo)-1} nomi di liste presenti nell'archivio salvato, contiene la chiave cercata.")
		return
	if s1 == dizelo["active_elo"]:
		print("\nNon è possibile eliminare la lista attiva, selezionarne una diversa, prima di procedere all'eliminazione.")
		return
	s = key(f"Sicuro di voler cancellare {s1}? (S o N)? ",180)
	if s == "s":
		print(f"Ok, cancello la lista {s1}.")
		del dizelo[s1]
		print(f"Fatto, ora ci sono {len(dizelo)-1} liste in archivio.")
		salva=True
		return
	else:
		print("No problem! Non tocco nulla.")
		return

def Aggiungilista():
	global salva
	print("Aggiungi una nuova lista Elo.")
	n=dgt(prompt="Nome: ",smin=3,smax=64)
	idelo=0; pres=True
	while pres:
		idelo+=1
		for j in dizelo.keys():
			if str(idelo)+":" not in j: pres=False
			else: pres=True; break
	n=f"{idelo}:{n}"
	dizelo[n] = []
	print(f"Lista aggiunta. L'archivio ne contiene ora {len(dizelo)-1}.")
	salva=True
	return

def ActiveEloList():
	'''Managing delle liste degli Elo	'''
	print(f"Gestione liste Elo.\nCi sono {len(dizelo)-1} liste salvate\n\t{dizelo['active_elo']} è la lista attualmente selezionata.")
	print("Menù: A Aggiungi, V Vedi, I Imposta, R Rinomina, C Cancella, E Esci.")
	while True:
		s = key("Fai la tua scelta: AVIRCE> ", 60).lower()
		if s == "v": Vediliste()
		elif s == "i": Impostalista()
		elif s == "a": Aggiungilista()
		elif s == "r": Rinominalista()
		elif s == "c": Cancellalista()
		elif s == "e": break
		else:
			print("\nScelta non valida:\nA Aggiungi una lista nuova,\nV Vedi liste Elo;\nI Imposta la lista attiva;\nR Dai un nuovo nome alla lista;\nC Cancella la lista;\nE Esci e torna al menù principale.")
	print("\nTorno al menù principale.")
	return

def Statgen():
	print("Pagina di statistiche generali sulle partite registrate.")
	tvitb, tparb, tscob, tvitn, tparn, tscon = 0,0,0,0,0,0
	for k,v in dizsch.items():
		if k != "active_sch":
			tvitb+=v[5]; tvitn+=v[8]
			tparb+=v[6]; tparn+=v[9]
			tscob+=v[7]; tscon+=v[10]
	tpartite=tvitb+tvitn+tparb+tparn+tscob+tscon
	print(f"Totale risultati registrati: {tpartite} partite, giocate su {len(dizsch)-1} scacchiere\n\tin media {tpartite/len(dizsch)-1:.1f} partite su ciascuna scacchiera.")
	tvitp, tparp, tscop = Perc(tvitb+tvitn, tpartite), Perc(tparb+tparn, tpartite), Perc(tscob+tscon, tpartite)
	print(f"\nSul totale c'è il {tvitp:3.2f}%, ({tvitb+tvitn})  di partite vinte,\n\til {tparp:3.2f}%, ({tparb+tparn}) di partite patte ed il {tscop:3.2f}%, ({tscob+tscon}) di partite perse.")
	print("\t\tPer colore")
	tpartiteb=tvitb+tparb+tscob
	tpartiten=tvitn+tparn+tscon
	print(f"Ci sono il {Perc(tpartiteb,tpartite):.2f}% di partite col Bianco e il {Perc(tpartiten,tpartite):.2f}% col Nero.")
	print(f"Vittorie: col Bianco {Perc(tvitb,tvitb+tvitn):.2f}%, su {tvitb+tvitn} partite, contro il {Perc(tvitn,tvitb+tvitn):.2f}% col Nero.")
	print(f"Patte: col Bianco {Perc(tparb,tparb+tparn):.2f}%, su {tparb+tparn} partite, contro il {Perc(tparn,tparb+tparn):.2f}% col Nero.")
	print(f"Sconfitte: col Bianco {Perc(tscob,tscob+tscon):.2f}%, su {tscob+tscon} partite, contro il {Perc(tscon,tscob+tscon):.2f}% col Nero.")
	return

def Statelo(e):
	e=e.copy()[1:]
	if len(e)<6:
		print("Ancora pochi valori Elo registrati per produrre statistiche.")
		return
	print("Pagina di statistiche sui valori registrati.")
	print("Elaborazione effettuata su",len(e),"ELO salvati.")
	print(min(e),"- - Valore minimo;")
	print(statistics.median_low(e),"- - Valore media bassa;")
	print("%4.2f - - Valore medio;" % statistics.mean(e))
	print("%4.2f - - Valore mediana;" % statistics.median(e))
	print("%4.1f - - Mediana a interpolazione;" % statistics.median_grouped(e, interval=1))
	print(statistics.median_high(e),"- - Valore media alta;")
	print(max(e),"- - Valore massimo;")
	print("%8.3f - - Dispersione dal punto mediano;" % statistics.pvariance(e, mu=None))
	return

def Daeloascii(e):
	'''Trasforma i valori ELO in una stringa per leggerne l'andamento'''
	if len(e) < 5:
		print("Non ci sono abbastanza ELO salvati per poter effettuare questo calcolo,\n\tRiprovare dopo aver aggiunto almeno 5 valori.")
		return
	print("Da ELO ad ASCII.\nQuesta funzione trasforma tutti i valori salvati nella lista ELO, in una stringa di caratteri.\nQuesta stringa parte da 0, il carattere con valore più basso, e sale fino al\n proprio valore più alto, Z o z, a seconda della stringa di riferimento scelta.")
	print("Ci sono 4 diversi modelli di stringhe, su cui effettuare la proiezione,\n\teccole in ordine ascendente di risoluzione:")
	print("1, - Solo gruppo maiuscole, risoluzione 26 valori:\n\t- "+PRI1+" -")
	print("2, - Gruppi maiuscole più minuscole, risoluzione 52 valori:\n\t- "+PRI2+" -")
	print("3, - Gruppi numeri, maiuscole e minuscole, risoluzione 62 valori:\n\t- "+PRI3+" -")
	print("4, - Gruppi numeri più simboli, maiuscole e minuscole, risoluzione 78 valori:\n\t- "+PRI4+" -")
	while True:
		q=key("Quale vuoi usare, 1 2 3 o 4? ", 30)
		if q in ['1','2','3','4']: break
		else: print("Risposta non valida. Inserisci un numero da 1 a 4.")
	if q == "1": pri, pridiv = PRI1, len(PRI1)
	elif q == "2": pri, pridiv = PRI2, len(PRI2)
	elif q == "3": pri, pridiv = PRI3, len(PRI3)
	elif q == "4": pri, pridiv = PRI4, len(PRI4)
	emin = 4000; emax = -1; econt = 0
	q=dgt("Quanti ELO prendo in considerazione? (invio uguale tutti)", kind="i", imin=5, imax=len(e), default=len(e))
	if q < 5: q = 5
	print("Elaboro gli ultimi",q,"punteggi ELO inseriti:")
	e = e[len(e)-q:len(e)]
	for j in e:
		if j < emin: emin = j
		if j > emax: emax = j
		econt += j
	emed = int(econt / len(e))
	print("L'ELO", emin, "è il più basso")
	print("Il valore approssimativo", emed, "rappresenta la media")
	print("L'ELO", emax, "è il più alto")
	eran = emax - emin
	print("Il valore", eran, "rappresenta la varianza coperta dagli ELO elaborati.")
	print("Stringa ASCII di riferimento, risoluzione",len(pri),":\n- "+pri+" -")
	dea = ""
	for j in e:
		x = j-emin
		y = x*100/eran
		w = y/100*(pridiv-1)
		dea += pri[round(w)]
	print("Stringa DEA elaborata:\n- "+dea+" -")
	return

def Vedie(e):
	'''Mostra la lista elo'''
	if len(e) == 0:
		print("Non ci sono ancora punteggi registrati.")
		return
	q=dgt("Visualizza gli ultimi elo salvati.\n\tQuanti ne vuoi vedere? (INVIO = ultimi 15)> ", kind="i", imax=len(e), imin=1,default=15)
	if q>len(e): q=len(e)
	print(f"\nLista degli ultimi {q} punteggi Elo inseriti:")
	for j in range(len(e)-q, len(e)):
		if j>=1:
			lelo=f" - {j+1}: {e[j]} --- ({e[j]-e[j-1]});"
		else:
			lelo=f" - {j+1}: {e[j]} --- (N/D);"
		print(lelo)
	return

def Vedis(m):
	'''Mostra situazione scacchiera'''
	print("Vedi scacchiera.")
	print(" - Titolo: "+ m[0])
	if m[1]: c="il Bianco"
	else: c="il Nero"
	print(" - Giochi con " + c)
	print(" - Hai: " + str(m[2]) + " vittorie, " + str(m[3]) + " patte e " + str(m[4]) + " sconfitte, col Bianco;")
	print(" - Hai: " + str(m[5]) + " vittorie, " + str(m[6]) + " patte e " + str(m[7]) + " sconfitte, col Nero.")
	return

def Modelo(elo):
	'''aggiunge o toglie elo dalla lista attivaa'''
	global salva
	prompt1=f"Modifica lista ELO\n(1) Aggiunge, (2) applica una modifica all'ultimo valore, oppure (3) per rimuovere l'ultimo inserito.\n\tCi sono {len(elo)} valori attualmente registrati, cosa vuoi fare, 1, 2, 3? "
	while True:
		s = key(prompt1, 60)
		if s in "123": break
		else: print("Rispondi 1 per aggiungere valori, 2 per aggiungere un valore all'ultimo registrato o 3 per rimuovere l'ultimo inserito.")
	if s == "2":
		uelo=elo[-1]
		nelo = uelo+dgt(kind="i", prompt=f"\nInserire la variazione da applicare a {uelo} > ", imin=-1000, imax=1000)
		elo = Gestelo(elo, nelo)
		salva = True
		return (elo)
	elif s == "1":
		nelo = dgt(kind="i", prompt="\nNuovo valore Elo? ", imin=500, imax=5000)
		elo = Gestelo(elo, nelo)
		salva = True
		return (elo)
	else:
		rim = elo.pop()
		print("Rimosso: ", rim)
		salva = True
		return (elo)

def Edit():
	'''Modifica avversario, colore e contatori della scacchiera attiva'''
	global salva  
	attiva=dizsch["active_sch"]
	print("Modifica alcuni dati della scacchiera attiva.")
	while True:
		ln=str(attiva)+", VS "
		ln+=dizsch[attiva][2]+" col "
		if dizsch[attiva][4]: p="Bianco";ln+=p; delta=0
		else: p="Nero";ln+=p; delta=3
		prt=dizsch[attiva][5]+dizsch[attiva][6]+dizsch[attiva][7]+dizsch[attiva][8]+dizsch[attiva][9]+dizsch[attiva][10]
		ln+=f" {prt} Partite."
		print(f"\n{ln}\nCol {p} ci sono {dizsch[attiva][5+delta]} vittorie, {dizsch[attiva][6+delta]} patte e {dizsch[attiva][7+delta]} sconfitte.\n")
		s = key("Quale dato vuoi cambiare:\nA per l'avversario, C per il colore, D per la Descrizione oppure\nV di Vittorie, P di Patte o S di Sconfitte?\n ESC per uscire.> ", 300)
		if s == "a":
			dizsch[attiva][2]=dgt(prompt="\nAvversario: >",smin=0,smax=128,default="Un cattivone!")
			salva=True
		elif s == "d":
			dizsch[attiva][0]=dgt(prompt="\nDesc./Nota? >",smin=0,smax=2048,default="Nessuna nota.")
			salva=True
		elif s == "c":
			if dizsch[attiva][4]:
				dizsch[attiva][4]=False
				print("\nColore impostato a Nero.")
				delta=3
				salva=True
			else:
				dizsch[attiva][4]=True
				print("\nColore impostato a Bianco.")
				delta=0
				salva=True
		elif s == "v":
			v=dgt("\nModifica numero vittorie, digita il valore da aggiungere: (INVIO = +1)> ", kind="i", imin=-5, imax=5, default=1)
			dizsch[attiva][5+delta]+=v
			dizsch[attiva][0]="Libera"; dizsch[attiva][2]="Nessuno"
			salva = True
		elif s == "p":
			v=dgt("\nModifica numero patte, digita il valore da aggiungere: (INVIO = +1> ", kind="i", imin=-5, imax=5,default=1)
			dizsch[attiva][6+delta]+=v
			dizsch[attiva][0]="Libera"; dizsch[attiva][2]="Nessuno"
			salva = True
		elif s == "s":
			v=dgt("\nModifica numero sconfitte, digita il valore da aggiungere: (INVIO = +1> ", kind="i", imin=-5, imax=5,default=1)
			dizsch[attiva][7+delta]+=v
			dizsch[attiva][0]="Libera"; dizsch[attiva][2]="Nessuno"
			salva = True
		elif ord(s)==27: break
		else:
			print(f"\n{s} non è un comando valido. Digita A, C, V, P, S oppure ESC.")
	print("\n")
	return

def Menu():
	'''Visualizza il menù'''
	print("\nMenù dell'applicazione ChessReg\n")
	print(" - - ( DEA ) - - Da Elo ad ASCII;")
	print(" - - ( EDT ) - - Edita dati scacchiera;")
	print(" - - ( ELO ) - - Modifica Elo registrati;")
	print(" - - ( GLE ) - - Gestione Liste Elo;")
	print(" - - ( GSE ) - - Grafico Sonoro degli Elo registrati;")
	print(" - - ( LST ) - - Vedi Elo;")
	print(" - - (  ?  ) - - visualizza il Menù;")
	print(" - - ( SCA ) - - Gestione scacchiere;")
	print(" - - ( SGP ) - - Statistiche Generali sulle partite;")
	print(" - - ( SLV ) - - Salva il database su disco;")
	print(" - - ( STE ) - - Statistiche sui valori Elo registrati;")
	print(" - - (INVIO) - - Uscita dal programma;")
	print(" - - ( ESC ) - - Uscita dal programma senza salvare;")
	print(" - - ( .***) - - Cerca nei dati delle scacchiere;")
	return

print("\n- - - - - Benvenuto in ChessReg "+VERSIONE+"\n")
print("Questa applicazione ha "+ETA)
print("L'ultima versione è di "+VETA+" fa.")
print("Questa applicazione è un registro utile a tenere traccia dei risultati\n  ottenuti sulle mie scacchiere con cui gioco a scacchi online.\n\tSalva anche un numero illimitato di liste Elo.")

dizsch, dizelo, elo = Loaddisco()

print("I comandi del menù vanno confermati con invio.\n\t(punto interrogativo) per visualizzare il Menù, un (INVIO) a vuoto per uscire.")
#qm
while True:
	s = dgt(f"[{contcom}] comandi signore: ", kind="s", smin=0, smax=16)
	s = s.lower()
	if s in acccom or s[0] == ".":
		contcom += 1
		if s == "": break
		elif s == "esc": salva=False; break
		elif s == "?": Menu()
		elif s == "edt": Edit()
		elif s == "elo": Modelo(elo)
		elif s == "slv":
			if salva: SalvaDB(); print("\nDB salvato!"); salva=False
			else: print("\nSalvataggio non necessario."); contcom-=1
		elif s == "gle": ActiveEloList()
		elif s == "gse": Grafson(elo)
		elif s == "ste": Statelo(elo)
		elif s == "sgp": Statgen()
		elif s == "sca": dizsch = Gestsch(dizsch)
		elif s == "dea": Daeloascii(elo)
		elif s[0] == "." and len(s)>1:
			chiave=Cercasch(s[1:])
			if len(chiave)>0:
				print(f"\nTrovati {len(chiave)} risultati:")
				for j in chiave:
					Vedising(str(j))
			else: print(f"{s[1:]} non è presente nei dati delle scacchiere registrate.")
			if len(chiave)==1:
				dizsch["active_sch"]=str(chiave[0])
				print(f"{str(chiave[0])} è ora la scacchiera attiva.")
				salva=True
		elif s == "lst": Vedie(elo)
	else: print("Spiacente, comando non valido")

# Chiusura
if salva:
	SalvaDB()
	print("Dati aggiornati salvati con successo.")
else:
	print("Nessuna modifica apportata. Salvataggio non necessario.")
print("Grazie per avermi usato!\nCiao ciao.")