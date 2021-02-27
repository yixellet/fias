from datetime import date

def convertStringToDate(string):
    lastVerrsionDateArray = string.split('.')
    lastVerrsionDate = date(
        int(lastVerrsionDateArray[2]), 
        int(lastVerrsionDateArray[1]), 
        int(lastVerrsionDateArray[0]))
    return lastVerrsionDate

def convertDateToString(date):
    return date.strftime('%d.%m.%Y')