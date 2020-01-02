import os
import re
import json
#from datetime import date


# output - return Today Day, Month and Year as int
def getTodayDate():
    from datetime import date
    today = date.today()
    day = today.strftime("%d")
    month = today.strftime("%m")
    year = today.strftime("%Y")
    return int(day), int(month), int(year)


# output - return  day, month, year as int
# do - send the most early date that should be scraped
def getStartDate():
    day = 2
    month = 12
    year = 2019
    return day, month, year


# output - return Search link in 3 parts - between should be the date as string
def getLinkParts():
    dateURL_P1 = 'https://supreme.court.gov.il/Pages/SearchJudgments.aspx?&OpenYearDate=null&CaseNumber=null&DateType=2&SearchPeriod=null&COpenDate='
    dateURL_P2 = '&CEndDate='
    dateURL_P3 = '&freeText=null&Importance=null'
    return dateURL_P1, dateURL_P2, dateURL_P3


# input - year as int
# output - return list contain amount of days in each month for each year
def isThisLeapYear(year):
    if (year % 4) != 0:
        return [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    else:
        return [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


# input - date (day, month, year) as int
# output - return next day (day, month, year) as int
def getTheNextDay(day, month, year):
    maxDay = isThisLeapYear(year)
    if day < maxDay[month - 1]:
        day += 1
    else:
        day = 1
        if month < 12:
            month += 1
        else:
            month = 1
            year += 1
    return day, month, year


# input - start Day, Month, Year and End Day, Month, Year as int
# output - return start and end dates as list
def getListofsplitDates(startD, startM, startY, endD, EndM, EndY):
    startDateList = list()
    EndDateList = list()
    while startY <= EndY:
        if startY + 2 < EndY:
            EndDateList.append([startD, startM, (startY + 2)])
        else:
            EndDateList.append([endD, EndM, EndY])
        startDateList.append([startD, startM, startY])
        startD, startM, startY = getTheNextDay(startD, startM, startY + 2)

    return startDateList, EndDateList


# input - day, month and year as int
# output - return dict[date] = Search url of that date
def get_Dict_of_links(startDay, startMonth, startYear, endDay, endMonth, endYear):
    # Initialize
    index = 0
    dict_of_links = dict()
    dateURL_P1, dateURL_P2, dateURL_P3 = getLinkParts()

    # Create list of links
    for year in range(startYear, endYear + 1):

        # In case of a leap year we decide how many days in each month
        maxDay = isThisLeapYear(year)

        # setting month limits
        if (startMonth > 1 and year > startYear):
            start_M = 1
        else:
            start_M = startMonth
        if (endMonth < 12 and year == endYear):
            end_M = endMonth
        else:
            end_M = 12

        for month in range(start_M, end_M + 1):
            # setting Days limits
            if (startDay > 1 and year > startYear):
                start_D = 1
            else:
                start_D = startDay
            if (month == end_M and year == endYear):
                end_D = endDay
            else:
                end_D = maxDay[month - 1]

            for day in range(start_D, end_D + 1):
                # set day string
                if (day < 10):
                    str_day = '0' + str(day)
                else:
                    str_day = str(day)

                # set month string
                if (month < 10):
                    str_month = '0' + str(month)
                else:
                    str_month = str(month)

                date = str_day + '/' + str_month + '/' + str(year)  # Create date in string
                dict_of_links[date] = dateURL_P1 + date + dateURL_P2 + date + dateURL_P3  # save link

    return dict_of_links


# output - folder path as string
def getFilesPath():
    return './'


# output - date list file name as string
def getDateListFileName():
    return 'ListOfDatesToScrape.json'


# output - last date file name as string
def getLastDateFileName():
    return 'DatesOfScrape.json'


# output - return list(dict{date:link},dict{date:link},...) output
# do - check if there is new dates to scrape since last run
def isThereNew():
    d, m, y = 0, 1, 2
    filePath = getFilesPath()
    fileName = getLastDateFileName()
    todayD, todayM, todayY = getTodayDate()
    if os.path.isfile(filePath + fileName):
        lastDate = readFromJson(fileName)
        if lastDate[d] == todayD and lastDate[m] == todayM and lastDate[y] == todayY:
            return None
    lastD, lastM, lastY = getTheNextDay(lastDate[d], lastDate[m], lastDate[y])
    return createListToScrape(fileName, lastD, lastM, lastY, todayD, todayM, todayY)


# input - fileName as string, startDay, startMonth, startYear, endDay, endMonth, endYear as int
# output - list of links to scrape as list(dict{date:link},dict{date:link},...)
# do - get start and end dates, split them into 2 years split then save them
def createListToScrape(fileName, startDay, startMonth, startYear, endDay, endMonth, endYear):
    mylist = list()
    d, m, y = 0, 1, 2  # day = 0, month = 1, year = 2
    startDateList, endDateList = getListofsplitDates(startDay, startMonth, startYear, endDay, endMonth, endYear)

    for index in range(len(startDateList)):
        mylist.append(get_Dict_of_links(
            startDateList[index][d], startDateList[index][m], startDateList[index][y]
            , endDateList[index][d], endDateList[index][m], endDateList[index][y]))
    writeToJson(fileName, mylist)
    writeToJson(getLastDateFileName(), (endDay, endMonth, endYear))
    return mylist


# output - return list of links as list(dict{date:link},dict{date:link},...)
def getListofLinks():
    mylist = list()
    fileName = getDateListFileName()
    filePath = getFilesPath()
    if os.path.isfile(filePath + getDateListFileName()):
        mylist = readFromJson(fileName)
        newDate = isThereNew()
        if newDate != None:
            mylist.append(newDate)
    else:
        startDay, startMonth, startYear = getStartDate()
        endDay, endMonth, endYear = getTodayDate()
        mylist = createListToScrape(fileName, startDay, startMonth, startYear, endDay, endMonth, endYear)

    return mylist


# input - date as string
# do - if date in list remove it from the file
def dropDateFromScrapeList(date):
    fileName = getDateListFileName()
    mylist = readFromJson(fileName)
    for index in range(len(mylist)):
        if date in mylist[index]:
            mylist[index].pop(date)
    writeToJson(fileName, mylist)


# input - date as string, index as int
# output - return case file name by date and page index as string
def fileNameforJsonCase(date, index):
    fixedDate = re.sub(r'/', '_', date)
    return fixedDate + '_' + str(index) + '.json'


# input - fileName as string, item as list\dict\tuple
def writeToJson(fileName, item):
    # open output file for writing
    with open(fileName, 'w') as filehandle:
        json.dump(item, filehandle)


# input - fileName as string
# output - list\dict\tuple
def readFromJson(fileName):
    # open output file for reading
    with open(fileName, 'r') as filehandle:
        item = json.load(filehandle)
    return item