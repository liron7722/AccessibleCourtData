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
def create_list_of_links(startDay, startMonth, startYear, endDay, endMonth, endYear):
    # Initialize
    list_of_links = list()

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
                list_of_links.append({'date': date, 'url': url, 'first': 0, 'last': -1})

    return list_of_links


# output - return list of links as list(dict{date/link/first,last},dict{date/link/first,last},...)
def getListOfLinks():
    if os.path.isfile(filePath + DateListFileName):  # check file exist
        mylist = readJson(filePath, DateListFileName)
        startDay, startMonth, startYear = mylist[-1]['date']
        endDay, endMonth, endYear = getTodayDate()
        new_dates = create_list_of_links(startDay, startMonth, startYear, endDay, endMonth, endYear)
        if new_dates is not None:
            mylist.append(new_dates)
    else:
        startDay, startMonth, startYear = getStartDate()
        endDay, endMonth, endYear = getTodayDate()
        mylist = create_list_of_links(startDay, startMonth, startYear, endDay, endMonth, endYear)

    writeJson(filePath, DateListFileName, mylist)
    return mylist


# input - date as string
# do - if date in list remove it from the file
def UpdateScrapeList(date, first, last):
    mylist = readJson(filePath, DateListFileName)
    for item in mylist:
        if date == item['date']:
            item['first'] = first
            item['last'] = last
            break
    writeJson(filePath, DateListFileName, mylist)
    return True
