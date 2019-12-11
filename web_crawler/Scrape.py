from datetime import date
from time import time, sleep
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def getTodayDate():
    today = date.today()
    day = today.strftime("%d")
    month = today.strftime("%m")
    year = today.strftime("%Y")
    return int(day), int(month), int(year)


def getLinkParts():
    dateURL_P1 = 'https://supreme.court.gov.il/Pages/SearchJudgments.aspx?&OpenYearDate=null&CaseNumber=null&DateType=2&SearchPeriod=null&COpenDate='
    dateURL_P2 = '&CEndDate='
    dateURL_P3 = '&freeText=null&Importance=null'

    return dateURL_P1, dateURL_P2, dateURL_P3


def myBadInputMassage():
    print('Bad  Input Mate!')
    return None


def isThisLeapYear(year):
    if ((year % 4) != 0):
        return [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    else:
        return [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def cheakDateInput(startDay, startMonth, startYear):  # TODO Fix

    endDay, endMonth, endYear = getTodayDate()

    if (startDay < 1 or startMonth < 1 or startYear < 2000):
        return False

    # if (startDay > endDay or startMonth > endMonth or startYear > endYear): #TODO Fix
    #    return False

    if (startYear > endYear):
        return False
    elif (startYear == endYear):
        if (startMonth > endMonth):
            return False
        elif (startMonth == endMonth):
            if (startDay > endDay):
                return False

    return True  # All good Mate


def get_startDate_to_Today_Dict_of_links(startDay, startMonth, startYear):
    # Initialize
    index = 0
    dict_of_links = dict()
    endDay, endMonth, endYear = getTodayDate()
    dateURL_P1, dateURL_P2, dateURL_P3 = getLinkParts()

    # No bad input in my watch
    # if not (assert(cheakDateInput(startDay,startMonth,startYear),myBadInputMassage())) # TODO Fix error?
    # return None

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
                # print(dateURL_P1 + date + dateURL_P2 + date + dateURL_P3) # Print Link for cheaking we can delets this
                dict_of_links[date] = dateURL_P1 + date + dateURL_P2 + date + dateURL_P3  # save link

    # saveLastDate(EndDay, EndMonth, EndYear) - TODO Save date of tommarow
    return dict_of_links


def getListofLinks():
    # We can make this an automated script
    # start date should take from saved file
    startDay = 2
    startMonth = 12
    startYear = 2019

    myDict = get_startDate_to_Today_Dict_of_links(startDay, startMonth, startYear)
    return myDict


def findElemByXpath(driver, Xpath):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, Xpath)))
        return True
    except:
        print('Could not find: ', str(Xpath))
        return False


def findElemByID(driver, ID):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, ID)))
        return True
    except:
        print('Could not find: ', str(ID))
        return False

def getElemByXpath(driver, Xpath):
    try:
        return driver.find_element_by_xpath(Xpath)
    except:
        print('Could not find: ',str(Xpath))
        return None

def getElemByID(driver, ID):
    try:
        return driver.find_element_by_id(ID)
    except:
        print('Could not find: ',str(ID))
        return None


def getCaseNameXpath(index):
    return '/html/body/div[2]/div/form/div/div/div[1]/div[3]/ul/li[' + str(index) + ']/div[2]/a'


def canIclick(driver, Xpath):
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, Xpath)))
        return True
    except:
        print('Cant click this: ', str(Xpath))
        return False


def getCaseName(driver, index):
    Xpath = getCaseNameXpath(index)
    if findElemByXpath(driver, Xpath):
        caseName = getElemByXpath(driver, Xpath).text
        return caseName, True
    else:
        print('getCaseName Broke at index: ', index)
        currentUrlErrorReport(driver)
        return None, False


def clickCaseName(driver, index):
    Xpath = getCaseNameXpath(index)
    if canIclick(driver, Xpath):
        getElemByXpath(driver, Xpath).click()
        # sleep(1)
        return True
    else:
        print('clickCaseName Broke at index: ', index)
        currentUrlErrorReport(driver)
        return False


def goToLink(driver, URL):
    driver.get(URL)


def getHtmlDocXpath(index):
    return '/html/body/div[2]/div/form/div/div/div[1]/div[3]/ul/li[' + str(index) + ']/div[4]/div[2]/a[3]'


def getElemLink(driver, index):
    Xpath = getHtmlDocXpath(index)
    # if index > 100:
    # driver.
    if findElemByXpath(driver, Xpath):
        elem = getElemByXpath(driver, Xpath)
        return elem.get_attribute('href')
    else:
        print('getElemLink Broke at index: ', index)
        currentUrlErrorReport(driver)


def getSourceText(driver):
    page_source = driver.page_source
    text = BeautifulSoup(page_source, 'html.parser').getText

    return text


def currentUrlErrorReport(driver):
    print(driver.current_url)
    print('Please review this !!!')


def switchWindow(driver):
    window = driver.window_handles[0]
    driver.switch_to_window(window)


def getFramebyXpath(driver):
    Xpath = get_Ng_src_Xpath()
    if findElemByXpath(driver, Xpath):
        frame = getElemByXpath(driver, Xpath)
        driver.switch_to.frame(frame)
    else:
        print('Could not find ng-src Frame in this page:')
        currentUrlErrorReport(driver)(driver)


def get_Ng_src_Xpath():
    return '/html/body/div[2]/div/div/div[2]/div/div[1]/div/div/iframe'


def getserviceFramID():
    return 'serviceFram'


def getFramebyID(driver):
    ID = getserviceFramID()
    if findElemByID(driver, ID):
        frame = getElemByID(driver, ID)
        driver.switch_to.frame(frame)
    else:
        print('Could not find serviceFram Frame in this page:')
        currentUrlErrorReport(driver)


def getBackToFrame(driver):
    driver.back()
    getFramebyID(driver)


def setUpBeforGetCaseInsideDetails(driver):
    switchWindow(driver)
    getFramebyID(driver)
    getFramebyXpath(driver)


def getColumnXpath(index):
    return '/html/body/div/div[1]/div/div/div[' + str(index) + ']/a'


def getColumnText(driver, index):
    Xpath = '/html/body/div/div[2]/div[' + str(index) + ']'
    if findElemByXpath(driver, Xpath):
        return driver.find_element_by_xpath(Xpath).text
    else:
        return None


def getCaseInsideDetails(driver):
    mydict = dict()

    # make more loops for more columns
    for index in range(1, 8):

        myColumnXpath = getColumnXpath(index)
        if canIclick(driver, myColumnXpath):
            getElemByXpath(driver, myColumnXpath).click()
        else:
            break

        headline = driver.find_element_by_xpath(myColumnXpath).text
        text = getColumnText(driver, index)

        mydict[headline] = text

    return mydict


def getCasesData(driver):
    dictofCases = dict()
    caseFileDict = dict()
    caseDetailsDict = dict()

    getFramebyID(driver)

    for index in range(1, 501):
        try:
            t1 = time()

            elem = getElemLink(driver, index)
            goToLink(driver, elem)
            caseFileDict['Case File'] = getSourceText(driver)
            getBackToFrame(driver)

            caseName, canIclick = getCaseName(driver, index)

            if canIclick:
                if clickCaseName(driver, index):
                    setUpBeforGetCaseInsideDetails(driver)
                    caseDetailsDict['Case Details'] = getCaseInsideDetails(driver)
                    getBackToFrame(driver)
                else:
                    caseDetailsDict['Case Details'] = None
            else:
                caseDetailsDict['Case Details'] = None

            dictofCases[caseName] = [caseFileDict, caseDetailsDict]
            print('page:', index, ' took in seconds: ', time() - t1)

        except:
            print('CaseData Broke at index: ', index)
            currentUrlErrorReport(driver)

    return dictofCases


def start():
    linksForEachDayofCourt = getListofLinks()
    print(len(linksForEachDayofCourt))
    # print(linksForEachDayofCourt)

    dictOfData = dict()
    driver = webdriver.Chrome()

    for date in linksForEachDayofCourt:
        t1 = time()
        driver.get(linksForEachDayofCourt[date])
        dictOfData[date] = getCasesData(driver)
        print('Date: ', date, ' took in minutes: ', (time() - t1) / 60)