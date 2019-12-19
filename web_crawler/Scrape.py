import os
import re
import json
from datetime import date
from threading import Thread
from time import time, sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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


# output - return Case number xpath as string
def getCaseNumberXpath():
    return '/html/body/div[2]/div/form/section/div/p'


# input - driver as web driver, xpath as string
# output - return element if found in 5 seconds, None otherwise
def findElemByXpath(driver, Xpath):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, Xpath)))
        return driver.find_element_by_xpath(Xpath)
    except:
        # print('Could not find: ', Xpath)
        return None


# input - driver as web driver, id as string
# output - return element if found in 5 seconds, None otherwise
def findElemByID(driver, ID):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, ID)))
        return driver.find_element_by_id(ID)
    except:
        # print('Could not find: ',ID)
        return None


# input - driver as web driver
# output - return number of case in the page as int
def getAmountofCases(driver):
    getFramebyID(driver)
    sleep(5)
    Xpath = getCaseNumberXpath()
    elem = findElemByXpath(driver, Xpath)
    if elem is not None:
        text = elem.text
        if len(text) > 0:
            return [int(s) for s in text.split() if s.isdigit()][0]
    return 500


# output return serviceFram frame id as string
def getserviceFramID():
    return 'serviceFram'


# input - driver as web driver
# do - if frame found by id webdriver will switch frame, otherwise return false
def getFramebyID(driver):
    ID = getserviceFramID()
    frame = findElemByID(driver, ID)
    if frame is not None:
        driver.switch_to.frame(frame)
        return True
    else:
        # print('Could not find serviceFram Frame in this page:')
        return False


# input - driver as web driver, N is the index we want to reach as int
# do - put in view the item we want to click
def scrollIntoView(driver, N):
    for index in range(1, N + 1):
        Xpath = getCaseNameXpath(index)
        elem = findElemByXpath(driver, Xpath)
        if elem is not None:
            elem.location_once_scrolled_into_view
        else:
            print('Could not scroll to index: ', index)


# input - index as int
# output - document url xpath as string
def getHtmlXpath(index):
    return '/html/body/div[2]/div/form/div/div/div[1]/div[3]/ul/li[' + str(index) + ']/div[4]/div[2]/a[3]'


# input - driver as web driver
# output - page source as text (string)
def getSourceText(driver):
    page_source = driver.page_source
    return BeautifulSoup(page_source, 'html.parser').getText


# input - driver as web driver
def badMassageforPageSource(driver, index):
    print('Couldnt get link at index: ', index)


# input - driver as web driver
def cheakUrl(driver, url):
    if driver.current_url != url:
        driver.get(url)


# input - index as int
# output - return case Name xpath as string
def getCaseNameXpath(index):
    return '/html/body/div[2]/div/form/div/div/div[1]/div[3]/ul/li[' + str(index) + ']/div[2]/a'


# input - driver as web driver, index as int
# output - return case name as element, otherwise print error massage and return none
# do - return case name and click that case
def getCase(driver, index):
    Xpath = getCaseNameXpath(index)
    case = findElemByXpath(driver, Xpath)
    if case is not None:
        caseName = case.text
        case.click()
        return caseName
    else:
        print('getCase Broke at index: ', index)
        return None


# input - driver as web driver
# do - switch windows handle after case was clicked
def switchWindow(driver):
    window = driver.window_handles[0]
    driver.switch_to.window(window)


# output return Ng-src frame xpath as string
def get_Ng_src_Xpath():
    return '/html/body/div[2]/div/div/div[2]/div/div[1]/div/div/iframe'


# input - driver as web driver
# do - if frame found by xpath webdriver will switch frame, otherwise print error massage
def getFramebyXpath(driver):
    Xpath = get_Ng_src_Xpath()
    frame = findElemByXpath(driver, Xpath)
    if frame is not None:
        driver.switch_to.frame(frame)
    else:
        print('Could not find ng-src Frame in this page:')


def getBackButtonXpath():
    return '/html/body/div[2]/div/div/section/div/a[1]'


def getThisPageUp(driver):
    Xpath = getBackButtonXpath()
    elem = findElemByXpath(driver, Xpath)
    if elem is not None:
        elem.location_once_scrolled_into_view
    else:
        print('Could not scroll to back button')


# input - driver as web driver
# do - call switchWindow, getFramebyID and getFramebyXpath functions
def setUpBeforGetCaseInsideDetails(driver):
    # add here window go up
    switchWindow(driver)
    getFramebyID(driver)
    getThisPageUp(driver)
    getFramebyXpath(driver)


# input - index as int
# output - return Column xpath
def getColumnXpath(index):
    return '/html/body/div/div[1]/div/div/div[' + str(index) + ']/a'


# input - driver as web driver, index as int
# output - return column inside text
def getColumnText(driver, index):
    Xpath = '/html/body/div/div[2]/div[' + str(index) + ']'
    elem = findElemByXpath(driver, Xpath)
    sleep(1)
    if elem is not None:
        return elem.text
    else:
        return None


# output - return blocked case xpath
def blockedCaseXpath():
    return '/html/body/table/tbody/tr[1]/td/b'


# input - driver as web driver
# output - return False if this is a private case, otherwise True
def isBlockedCase(driver):
    elem = findElemByXpath(driver, blockedCaseXpath())
    if elem is not None:
        print('This one in a private case !!!')
        return False
    else:
        return True


# input - driver as web driver
# output - return all of the case info as dict[column name] = text
def getCaseInsideDetails(driver):
    mydict = dict()

    if isBlockedCase(driver):
        # make more loops for more columns
        for index in range(1, 8):
            elem = findElemByXpath(driver, getColumnXpath(index))
            if elem is not None:
                headline = elem.text
                elem.click()
                text = getColumnText(driver, index)
                mydict[headline] = text
            else:
                print('Could not press Case column index: ', index)
                continue
    return mydict


# input - driver as web driver
def getPageSource(driver, index):
    caseFileDict = dict()
    getFramebyID(driver)

    if index > 90:
        scrollIntoView(driver, index)

    Xpath = getHtmlXpath(index)
    elem = findElemByXpath(driver, Xpath)
    if elem is not None:
        driver.get(elem.get_attribute('href'))
        pageSource = getSourceText(driver)
    else:
        badMassageforPageSource(driver, index)
        pageSource = 'Could not get this one'

    caseFileDict['Case File'] = pageSource
    driver.back()

    return caseFileDict


# input - driver as web driver
def getCaseDetails(driver, index):
    caseDetailsDict = dict()
    getFramebyID(driver)

    if index > 90:
        scrollIntoView(driver, index)

    caseName = getCase(driver, index)
    if caseName is not None:
        setUpBeforGetCaseInsideDetails(driver)
        caseDetailsDict['Case Details'] = getCaseInsideDetails(driver)
        driver.back()
    else:
        caseDetailsDict['Case Details'] = None

    return caseDetailsDict, caseName


# input - driver as web driver
def failedAtCase(driver, index, current_url):
    print('CaseData Broke at index: ', index)
    # driver.get(current_url)  # lets start over


# input - driver as web driver
# output (disabled) - return all the cases for the page he see as dict[caseName] = [caseFileDict, caseDetailsDict]
#                                                    caseFileDict as dict['Case File'] = document text
#                                                    caseDetailsDict as dict['Case Details'] = Case Details
def getCasesData(driver, date):
    N = getAmountofCases(driver) + 1
    current_url = driver.current_url
    errorCount = 0
    noErrors = True
    for index in range(1, N):
        t1 = time()
        while True:
            try:
                caseFileDict = getPageSource(driver, index)
                cheakUrl(driver, current_url)
                caseDetailsDict, caseName = getCaseDetails(driver, index)
                currentCase = [str(caseFileDict), caseDetailsDict]
                writeToJson(fileNameforJsonCase(date, index), currentCase)

                print('Case:', index, ' took in seconds: ', time() - t1)
                errorCount = 0
                break
            except:
                failedAtCase(driver, index, current_url)
                if errorCount < 1:
                    errorCount += 1
                    continue
                noErrors = False
                errorCount = 0
                break
    if noErrors:
        dropDateFromScrapeList(date)
    # else:
    # TODO add here make the list of dates and index that didnt scrape
    return dictofCases


def crawl(urlSet):
    driver = webdriver.Chrome()
    driver.maximize_window()

    for date in urlSet.keys():
        t1 = time()
        driver.get(urlSet[date])
        getCasesData(driver, date)
        print('Date: ', date, ' took in minutes: ', (time() - t1) / 60)
    # close web driver
    driver.quit()


# do - go to each day that not scraped and take all the case files from them
def start():
    # get set of links
    linksToScrape = getListofLinks()
    # create a list of threads
    threads = []
    # In this case 'urls' is a list of urls to be crawled.
    for set in range(len(linksToScrape)):
        # We start one thread per url present.
        process = Thread(target=crawl, args=[linksToScrape[set]])
        process.start()
        threads.append(process)
    # We now pause execution on the main thread by 'joining' all of our started threads.
    # This ensures that each has finished processing the urls.
    for process in threads:
        process.join()
    # At this point, results for each URL are now neatly stored in order in 'results'


start()

