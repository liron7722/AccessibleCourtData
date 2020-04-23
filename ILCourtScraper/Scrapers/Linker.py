from ILCourtScraper.Extra.time import *
from ILCourtScraper.Extra.path import *
from ILCourtScraper.Extra.json import saveData, readData

# Functions
# input - startDate as string, format as string
# do - create list of dict contain {'date' as string, 'first' as int, 'last' as int, 'is taken' as boolean}
def createDates(startDate=None, format="%d-%m-%Y"):
    dates = list()

    if startDate is None:  # no endDate input so we use today date
        sD = '31-12-1996'
    else:
        sD = startDate.replace('/', '-')

    eD = strftime(format, localtime())

    for date in generateDates(startDate=sD, endDate=eD, format=format):
        strDate = str(date).replace('-', '/')
        item = {'date': strDate, 'first': 0, 'last': -1, 'is taken': False, 'case List': []}
        dates.append(item)
    return dates


# do - make sure local file is up to date, if not not exist create one
def upToDateFile():
    if path.isfile(filePath + sep + DateListFileName):  # check file exist
        datesList = readData(DateListFileName, filePath)
        if len(datesList) > 0:
            item = datesList[-1]  # get the last day that scraped,
            new_dates = createDates(startDate=item['date'])
        else:
            new_dates = createDates()

        if len(new_dates) > 0:
            datesList.extend(new_dates)

    else:  # local file doesn't exist
        datesList = createDates()
    saveData(datesList, DateListFileName, filePath)  # create\update local file


def upToDateDB(db=None):
    datesList = list()
    if db is not None:
        collection = db.get_collection('dates')
        query = collection.find({})
        for item in query:
            item.pop('_id')
            datesList.append(item)

        new_dates = createDates(startDate=datesList[-1]['date'])
        datesList.extend(new_dates)

        for item in new_dates:
            collection = db.get_collection('dates')
            collection.insert_one(item)

        saveData(datesList, DateListFileName, filePath)


# output - return list of links as list({'date': string, first': int, 'last': int, 'is taken': boolean})
def getLinks(db=None):
    if db is not None:  # use db
        upToDateDB(db)
        collection = db.get_collection('dates')
        dateList = list(collection.find({'is taken': False}).skip(0))
        if len(dateList) > 0:
            item = dateList[-1]  # last item from non taken dates
            UpdateScrapeList(db, item['date'], item['first'], item['last'], True, item['case List'])
            return item
        else:
            resetDatesInDB(db)
            return getLinks(db)

    else:  # use file
        upToDateFile()
        datesList = readData(DateListFileName, filePath)
        while True:
            for item in datesList:
                if item['is taken'] == False:
                    return item


# input - db as database, date as string, first as int, last as int, status as boolean
# do - update all function relate to the list
def UpdateScrapeList(db, date, first, last, status, case_List):
    result = []
    for func in updateFunction:
        res = func(db, date, first, last, status, case_List)
        result.append(res)
    return result


# input - date as string, first as int, last as int, status as boolean
def updateDateInFile(db, date, first, last, status, case_List):
    datesList = readData(DateListFileName, filePath)
    for item in datesList:
        if item['date'] == date:
            item['first'] = first
            item['last'] = last
            item['is taken'] = status
            item['case List'] = case_List
    saveData(datesList, DateListFileName, filePath)
    return True


# input - db as database, date as string, first as int, last as int, status as boolean
def updateDateInDB(db, date, first, last, status, case_List):
    collection = db.get_collection('dates')
    collection.update_one({'date': date},
                          {"$set": {'first': first, 'last': last, 'is taken': status, 'case List': case_List}})
    return True


def resetDatesInDB(db):
    collection = db.get_collection('dates')
    collection.update_many({}, {'$set': {'is taken': False}})

dateURL_P1 = 'https://supreme.court.gov.il/Pages/SearchJudgments.aspx?&OpenYearDate=null&CaseNumber=null&DateType=2&SearchPeriod=null&COpenDate='
dateURL_P2 = '&CEndDate='
dateURL_P3 = '&freeText=null&Importance=null'

filePath = getPath(N=2) + f'products{sep}'
DateListFileName = 'dateList.json'

updateFunction = [updateDateInFile, updateDateInDB]

#from ILCourtScraper.Extra.db import DB
#db = DB().getDB('SupremeCourt')
#resetDatesInDB(db)