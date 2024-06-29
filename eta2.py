# Eta' utility che calcola la differenza fra una data e l'ADESSO.
# Di Gabriele Battaglia, concepito in data 15/03/2018, versione 1.0
def Vecchiume(y=1974, m=9, g=13, h=22, i=10):
    '''Riceve anno, mese, giorno, ora e minuto e calcola la differenza con l'ADESSO. Quindi la ritorna'''
    from datetime import datetime
    from dateutil import relativedelta
    APP=datetime(y,m,g,h,i)
    NOW = datetime.today()
    ETA=relativedelta.relativedelta(NOW,APP)
    if ETA.years > 0:
        if ETA.years == 1: f = str(ETA.years)+" anno, "
        else: f = str(ETA.years)+" anni, "
    else: f = ""
    if ETA.months > 0:
        if ETA.months == 1: f += str(ETA.months)+" mese, "
        else: f += str(ETA.months)+" mesi, "
    if ETA.days > 0:
        if ETA.days == 1: f += str(ETA.days)+" giorno, "
        else: f += str(ETA.days)+" giorni, "
    if ETA.hours > 0:
        if ETA.hours == 1: f += str(ETA.hours)+" ora e "
        else: f += str(ETA.hours)+" ore e "
    if ETA.minutes > 0:
        if ETA.minutes == 1: f += str(ETA.minutes)+" minuto."
        else: f += str(ETA.minutes)+" minuti"
    return(f)