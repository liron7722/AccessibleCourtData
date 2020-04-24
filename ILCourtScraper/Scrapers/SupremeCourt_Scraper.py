# -*- coding: utf-8 -*-
import sys
sys.path.insert(1, '../..')
from ILCourtScraper.Scrapers.Scraper import *
from ILCourtScraper.Extra.json import saveData
from ILCourtScraper.Extra.time import callSleep, time
from ILCourtScraper.Crawler.Crawler import Crawler, WebDriverException
from ILCourtScraper.Scrapers.Linker import getLinks, UpdateScrapeList, dateURL_P1, dateURL_P2, dateURL_P3


class SupremeCourtScraper(Scraper):
    site = 'SupremeCourt'

    def __init__(self, numOfCrawlers=0):
        super().__init__(numOfCrawlers, self.site)

    # Functions
    def get_link(self):
        item = getLinks(self.db)
        if item is not None:
            self.logger.info(f'crawler took date {item["date"]}')
            url = dateURL_P1 + item['date'] + dateURL_P2 + item['date'] + dateURL_P3
            return item['date'], url, item['first'], item['last'], item['case List']
        self.logger.info('Did not get dates from db or file')
        return None, None, None, None, None

    def get_Frame(self, crawler, elem_type, string):
        frame = crawler.find_elem(elem_type, string)
        if frame is not None:
            return crawler.switch_frame(frame)
        else:
            massage = f'could not switch to frame: {string}'
            self.logger.info(massage)
            return False

    # input - driver as web driver
    # output - return number of case in the page as int
    def get_num_of_Cases(self, crawler):
        caseNumLoc = ['/html/body/div[2]/div/form/section/div/div']
        crawler.switch_to_default_content()
        self.get_Frame(crawler, 'id', 'serviceFram')
        for location in caseNumLoc:
            elem = crawler.find_elem('xpath', location, delay=8)
            if elem is not None:
                update = crawler.read_elem_text(elem)
                text = crawler.get_text_query(update)
                if text is not None and len(text) > 0:
                    N = [int(s) for s in text.split() if s.isdigit()][0]
                    massage = 'this page got {} cases'.format(N)
                    self.logger.info(massage)
                    return N
        massage = 'could not get this page amount of cases'
        self.logger.warning(massage)
        return 500

    # input - N as int, first as int, last as int
    # output - start as int, finish as int
    @staticmethod
    def case_picker(N, first, last):
        delta = N - last
        if delta > 0:  # got new cases
            if first < last:  # didn't finish scrape page - so start from scratch
                return 1, N, N
            return 1, delta - 1, N  # scrape only new cases
        elif first < last:  # keep going where left off
            return first, last, N

    @staticmethod
    def get_string_by_index(xpath, index):
        if xpath == 'case Name':
            return f'/html/body/div[2]/div/form/div/div/div[1]/div[3]/ul/li[{index}]/div[2]/a'
        elif xpath == 'column':
            return f'/html/body/div/div[1]/div/div/div[{index}]/a'
        elif xpath == 'inside column':
            return f'/html/body/div/div[2]/div[{index}]'
        elif xpath == 'no info column':
            return f'/html/body/div/div[2]/div[{index}]/table/tbody/tr[4]/td/h4'
        elif xpath == 'many rows':
            return f'/html/body/div/div[2]/div[{index}]/table/tbody/tr[1]/td[1]'
        elif xpath == 'html':
            return f'/html/body/div[2]/div/form/div/div/div[1]/div[3]/ul/li[{index}]/div[4]/div[2]/a[3]'

    def get_elem(self, crawler, xpath, index):
        string = self.get_string_by_index(xpath, index)
        return crawler.find_elem('xpath', string, raise_error=False)

    # input - driver as web driver, N is the index we want to reach as int
    # do - put in view the item we want to click
    def scrollIntoView(self, crawler, N):
        result = True
        if N > 90:
            for index in range(84, N - 5):
                elem = self.get_elem(crawler, 'case Name', index)
                result = crawler.scroll_to_elem(elem)
            if result:
                massage = 'Scrolled to elem'
            else:
                massage = 'could not scrolled to case'
            self.logger.debug(massage)

    # input - driver as web driver, index as int
    # output - return case name as element, otherwise print error massage and return none
    # do - return case name and click that case
    def getCase(self, crawler, index):
        elem = self.get_elem(crawler, 'case Name', index)
        if elem is not None:
            case_name = elem.text
            massage = 'Got case name'
            self.logger.info(massage)
            crawler.click_elem(elem)
            return case_name
        else:
            massage = 'did not found case name or could not click it'
            self.logger.warning(massage)
            return None

    # input - driver as web driver
    # do - call switchWindow, getFramebyID and getFramebyXpath functions
    def set_Up_Befor_Get_Case_Inside_Details(self, crawler):
        # position browser to see all info
        elem = crawler.find_elem('xpath', '/html/body/div[2]/div/div/section/div/a[1]')
        crawler.scroll_to_elem(elem)
        # get second frame
        self.get_Frame(crawler, 'xpath', '/html/body/div[2]/div/div/div[2]/div/div[1]/div/div/iframe')

    # input - index as int
    # output - array of titles as strings
    @staticmethod
    def getTitles(index):
        if index == 1:
            return [['מספר הליך', 'מדור', 'תאריך הגשה', 'סטטוס תיק'], ['מערער', 'משיב', 'אירוע אחרון']]
        elif index == 2:
            return ['סוג צד', '#', 'שם', 'באי כוח']
        elif index == 3:
            return ['שם בית המשפט', 'מספר תיק דלמטה', 'ת.החלטה', 'הרכב/שופט']
        elif index == 4:
            return ['תאריך', 'שעת דיון', 'אולם', 'גורם שיפוטי', 'סטטוס']
        elif index == 5:
            return ['#', 'ארוע ראשי', 'ארוע משני', 'תאריך', 'יוזם']
        elif index == 6:
            return ['#', 'נמען', 'תאריך חתימה']
        elif index == 7:
            return ['#', 'תיאור בקשה', 'תאריך', 'מגיש', 'נדחה מהמרשם']

    def getGeneralDetails(self, crawler, index):
        m_dict = dict()
        title = self.getTitles(index)
        for col in range(len(title)):
            for row in range(len(title[col])):
                string = '/html/body/div/div[2]/div[1]/div[' + str(col + 1) + ']/div[' + str(row + 1) + ']/span[2]'
                elem = crawler.find_elem('xpath', string)
                update = crawler.read_elem_text(elem)
                m_dict[title[col][row]] = crawler.get_text_query(update)
        return m_dict

    def getOtherCaseDetails(self, crawler, index):
        m_list = list()
        title = self.getTitles(index)
        row = 0
        keepGoing = True

        elem = self.get_elem(crawler, 'many rows', index)
        multiRow = crawler.read_elem_text(elem)

        while keepGoing is True:
            row += 1
            m_dict = dict()
            for col in range(len(title)):
                if multiRow:
                    xpath = '/html/body/div/div[2]/div[' + str(index) + ']/table/tbody/tr[' + str(
                        row) + ']/td[' + str(col + 1) + ']'
                else:
                    xpath = '/html/body/div/div[2]/div[' + str(index) + ']/table/tbody/tr/td[' + str(col) + ']'

                elem = crawler.find_elem('xpath', xpath, raise_error=False)
                update = crawler.read_elem_text(elem)
                text = crawler.get_text_query(update)

                if update:
                    m_dict[title[col]] = text
                else:  # No more info to scrape here
                    keepGoing = False
                    break

            if keepGoing is True:
                m_list.append(m_dict)
                if multiRow is False:
                    break
        return m_list

    # input - driver as web driver, index as int
    # output - return column inside text
    def getColumnText(self, crawler, index):
        string = self.get_string_by_index('no info column', index)
        elem = crawler.find_elem('xpath', string, raise_error=False)
        update = crawler.read_elem_text(elem)
        if update is True:  # No info here
            return None

        string = self.get_string_by_index('inside column', index)
        elem = crawler.find_elem('xpath', string)
        callSleep(seconds=1)

        if index == 1:
            func = self.getGeneralDetails
        else:
            func = self.getOtherCaseDetails

        if elem is not None:
            return func(crawler, index)
        else:
            return None

    # input - driver as web driver
    # output - return False if this is a private case, otherwise True
    def isBlockedCase(self, crawler):
        elem = crawler.find_elem('xpath', '/html/body/table/tbody/tr[1]/td/b', raise_error=False)
        if elem is not None:
            massage = 'This case in a private !!!'
            result = False
        else:
            massage = 'This case in not private - we can scrape more info'
            result = True
        self.logger.info(massage)
        return result

    # input - driver as web driver
    # output - return all of the case info as dict[column name] = text
    def getCaseInsideDetails(self, crawler):
        table = dict()
        if self.isBlockedCase(crawler):
            start, finish = 1, 8  # make more loops for more columns
            for index in range(start, finish):
                elem = self.get_elem(crawler, 'column', index)
                if elem is not None:
                    update = crawler.read_elem_text(elem)
                    headline = crawler.get_text_query(update)
                    crawler.click_elem(elem)
                    table[headline] = self.getColumnText(crawler, index)
                    massage = 'got info from column number: {}'.format(index)
                else:
                    massage = 'could not get text or press column number: {}'.format(index)
                self.logger.info(massage)
        return table

    @staticmethod
    def get_doc(crawler):
        text = None
        elem = crawler.find_elem('xpath', '/html/body/div[2]/div/div/div[2]/div/div[2]')
        if elem is not None:
            text = elem.text  # clean spaces
        return text

    # input - driver as web driver
    def getCaseDetails(self, crawler, index):
        caseDetailsDict = dict()

        crawler.switch_to_default_content()
        self.get_Frame(crawler, 'id', 'serviceFram')

        self.scrollIntoView(crawler, index)
        caseName = self.getCase(crawler, index)

        if caseName is not None:
            self.fixPageLocation(crawler)
            caseDetailsDict['Doc Details'] = self.get_doc(crawler)

            self.get_Frame(crawler, 'xpath', '/html/body/div[2]/div/div/div[2]/div/div[1]/div/div/iframe')
            caseDetailsDict['Case Details'] = self.getCaseInsideDetails(crawler)

            crawler.go_back()
        else:
            caseDetailsDict['Doc Details'] = None
            caseDetailsDict['Case Details'] = None

        return caseDetailsDict

    @staticmethod
    def checkForBackButton(crawler):
        elem = crawler.find_elem('xpath', '/html/body/div[2]/div/div/section/div/a[1]')
        return crawler.click_elem(elem)

    @staticmethod
    def fixPageLocation(crawler):
        elem = crawler.find_elem('xpath', '/html/body/div[2]/div/div/section/div/a[1]')
        crawler.scroll_to_elem(elem)

    def checkCaseNum(self, crawler, link):
        # pick cases
        N, tries = 500, 3
        pageLoaded = crawler.update_page(link)
        while N == 500 and tries > 0:
            N = self.get_num_of_Cases(crawler)
            tries -= 1
            self.checkForBackButton(crawler)  # in page got only the same case - happen in old dates
        return N, pageLoaded

    # input - driver as web driver
    # output (disabled) - return all the cases for the page he see as dict[caseName] = [caseFileDict, caseDetailsDict]
    #                                                    caseFileDict as dict['Case File'] = document text
    #                                                    caseDetailsDict as dict['Case Details'] = Case Details
    def get_Cases_Data(self, crawler, date, link, first, last, caseList):
        N, pageLoaded = self.checkCaseNum(crawler, link)
        caseList = [i + N - last for i in caseList]  # fix case number
        caseList.extend([i for i in range(1, N - last + 1)])  # add new cases
        caseList.sort()
        start, finish, N = self.case_picker(N, first, last)

        if pageLoaded is False or N == 500:
            self.logger.info('Page Not loaded')
            return None

        if finish == 0:
            UpdateScrapeList(self.db, date, start, finish, True, caseList)
        else:
            caseList = [i for i in range(1, N + 1)] if len(caseList) == 0 else caseList
            massage = f'page scrape cases {caseList}'
            self.logger.info(massage)
            for index in caseList:
                try:
                    t1 = time()
                    case_details_dict = self.getCaseDetails(crawler, index)
                    if case_details_dict['Doc Details'] is not None:
                        saveData(case_details_dict, self.randomName(index), self.product_path)
                    caseList.remove(index)
                    massage = f'Case: {index} took in seconds: {time() - t1}'
                    self.logger.info(massage)
                    UpdateScrapeList(self.db, date, index + 1, N, True, caseList)
                except WebDriverException as _:
                    raise WebDriverException
                except Exception as _:
                    massage = f'Case: {index} Failed'
                    self.logger.exception(massage)

    # input - index as int
    def start_crawler(self, index):
        crawler = None
        canIGO = self.getSettings('crawler Run')
        callSleep(seconds=index)  # make crawlers start in different times to ensure they don't take the same page

        while canIGO:
            crawler = Crawler(index=index, delay=2) if crawler is None else crawler
            try:
                date, link, first, last, caseList = self.get_link()
                if first <= last or last == -1:
                    massage = f'Starting to scrape date: {date}'
                    self.logger.info(massage)
                    t1 = time()
                    self.get_Cases_Data(crawler, date, link, first, last, caseList)
                    massage = f'Finished crawling page with the date: {date}, it took {(time() - t1) / 60} minutes'
                else:
                    massage = 'Nothing to crawl here'
                self.logger.info(massage)

            except WebDriverException as _:
                message = f'browser closed or crashed - restart value is {canIGO}'
                self.logger.exception(message)
            except Exception as _:
                message = 'unknown error'
                self.logger.exception(message)
            finally:
                canIGO = self.getSettings('crawler Run')

        if crawler is not None:
            crawler.close()
        callSleep(minutes=10)
        self.start_crawler(index=index)


# run scraper only if run directly from python and not from import
if __name__ == "__main__":
    scraper = SupremeCourtScraper(numOfCrawlers=1)
    with ThreadPoolExecutor() as executor:
        indexes = [index for index in range(1, scraper.getNumOfCrawlers() + 1)]
        executor.map(scraper.start_crawler, indexes)

