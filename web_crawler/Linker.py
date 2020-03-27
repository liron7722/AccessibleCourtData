from extra import *


dateURL_P1 = 'https://supreme.court.gov.il/Pages/SearchJudgments.aspx?&OpenYearDate=null&CaseNumber=null&DateType=2&SearchPeriod=null&COpenDate='
dateURL_P2 = '&CEndDate='
dateURL_P3 = '&freeText=null&Importance=null'

filePath = get_path()
DateListFileName = 'ListOfDatesToScrape.json'


# Functions

# output - return  day, month, year as int
def getStartDate():
    day, month, year = 1, 1, 1997
    return day, month, year


# input - day, month and year as int
# output - return dict[date] = Search url of that date
def createLinksDict(startDay, startMonth, startYear, endDay, endMonth, endYear):
    # Initialize
    linkDict = dict()

    # Create list of links
    for year in range(startYear, endYear + 1):

        # In case of a leap year we decide how many days in each month
        maxDay = isThisLeapYear(year)

        # setting month limits
        if startMonth > 1 and year > startYear:
            start_M = 1
        else:
            start_M = startMonth
        if endMonth < 12 and year == endYear:
            end_M = endMonth
        else:
            end_M = 12

        for month in range(start_M, end_M + 1):
            # setting Days limits
            if startDay > 1 and year > startYear:
                start_D = 1
            else:
                start_D = startDay
            if month == end_M and year == endYear:
                end_D = endDay
            else:
                end_D = maxDay[month - 1]

            for day in range(start_D, end_D + 1):
                # set day string
                if day < 10:
                    str_day = '0' + str(day)
                else:
                    str_day = str(day)

                # set month string
                if month < 10:
                    str_month = '0' + str(month)
                else:
                    str_month = str(month)

                date = str_day + '/' + str_month + '/' + str(year)  # Create date in string
                url = dateURL_P1 + date + dateURL_P2 + date + dateURL_P3  # save link
                linkDict[date] = {'url': url, 'first': 0, 'last': -1}
    return linkDict


# output - return list of links as list(dict{date/link/first,last},dict{date/link/first,last},...)
def getLinks():
    if os.path.isfile(filePath + os.sep + DateListFileName):  # check file exist
        linkDict = readJson(filePath, DateListFileName)
        lastOne = len(linkDict)
        date = list(linkDict.get(lastOne).keys())[0]
        startDay, startMonth, startYear = separateDate(date)  # separate the Date
        endDay, endMonth, endYear = getTodayDate()
        new_dates = createLinksDict(int(startDay), int(startMonth), int(startYear), endDay, endMonth, endYear)
        if len(new_dates) > 0:
            for date in new_dates.keys():
                if date in linkDict.keys():
                    new_dates.pop(date)
            linkDict.update(new_dates)

    else:
        startDay, startMonth, startYear = getStartDate()
        endDay, endMonth, endYear = getTodayDate()
        linkDict = createLinksDict(startDay, startMonth, startYear, endDay, endMonth, endYear)

    writeJson(filePath, DateListFileName, linkDict)
    return linkDict


# input - date as string
# do - if date in list remove it from the file
def UpdateScrapeList(date, first, last):
    linksDict = readJson(filePath, DateListFileName)
    if date in linksDict.keys():
        linksDict[date]['first'] = first
        linksDict[date]['last'] = last
    writeJson(filePath, DateListFileName, linksDict)
    return True
