from ILCourtScraper.Extra.time import *

dateURL_P1 = 'https://supreme.court.gov.il/Pages/SearchJudgments.aspx?&OpenYearDate=null&CaseNumber=null&DateType=2&SearchPeriod=null&COpenDate='
dateURL_P2 = '&CEndDate='
dateURL_P3 = '&freeText=null&Importance=null'


# Functions
# input - startDate as string, format as string
# do - create list of dict contain {'date' as string, 'first' as int, 'last' as int, 'is taken' as boolean}
def createDates(startDate=None, fmt="%d-%m-%Y"):
    dates = list()

    if startDate is None:  # no endDate input so we use today date
        sD = '31-12-1996'
    else:
        sD = startDate.replace('/', '-')

    eD = strftime(fmt, localtime())

    for date in generateDates(startDate=sD, endDate=eD, fmt=fmt):
        strDate = str(date).replace('-', '/')
        item = {'date': strDate, 'first': 0, 'last': -1, 'is taken': False, 'case List': []}
        dates.append(item)
    return dates


def upToDateDB(db=None):
    datesList = list()
    if db is not None:
        collection = db.get_collection('dates')
        query = collection.find({})
        for item in query:
            item.pop('_id')
            datesList.append(item)
        new_dates = createDates(startDate=datesList[-1]['date']) if len(datesList) > 0 else createDates()

        for item in new_dates:
            collection = db.get_collection('dates')
            collection.insert_one(item)


# input - db as database, date as string, first as int, last as int, status as boolean
def updateDateInDB(db, date, first, last, status, case_List):
    collection = db.get_collection('dates')
    collection.update_one({'date': date},
                          {"$set": {'first': first, 'last': last, 'is taken': status, 'case List': case_List}})


def resetDatesInDB(db):
    collection = db.get_collection('dates')
    collection.update_many({}, {'$set': {'is taken': False}})


# output - return list of links as list contain:
#                           ({'date': string, first': int, 'last': int, 'is taken': boolean, 'case List': list})
def getLinks(db):
    if db is not None:  # use db
        upToDateDB(db)
        collection = db.get_collection('dates')
        dateList = list(collection.find({'is taken': False}).skip(0))
        if len(dateList) > 0:
            item = dateList[-1]  # last item from non taken dates
            updateDateInDB(db, item['date'], item['first'], item['last'], True, item['case List'])
            return item
        else:
            resetDatesInDB(db)
            return getLinks(db)
    else:
        print("Got None as db value")


def countStatus(db):
    count, N = 0, 0
    collection = db.get_collection('dates')
    cursor = collection.find({})
    for item in cursor:
        N += item['last']
        count += item['last'] - len(item['case List'])
    print(f'{count} of {N} files ware downloaded')
    print('This is {:.2f}% of all cases'.format(count / N * 100))


# For manual reset or count
# from ILCourtScraper.Extra.db import DB
# db = DB().getDB('SupremeCourt')
# resetDatesInDB(db)
# countStatus(db)
