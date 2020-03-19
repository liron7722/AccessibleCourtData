# -*- coding: utf-8 -*-
from extra import *
from Crawler import Crawler
from threading import Thread
from time import time, sleep
from Linker import getListOfLinks, UpdateScrapeList


class Scraper:
    num_of_crawlers = None  # number of threads as well
    links_To_Scrape = None  # list of dict of urls as [[date] = [url], [date] = [url], ...]
    product_path = None

    def __init__(self, num_of_crawlers=1):
        self.num_of_crawlers = num_of_crawlers
        self.links_To_Scrape = getListOfLinks()
        self.product_path = change_path(get_path(), 'products' + os.sep + 'json_products')

    # Functions
    def get_link(self):
        if len(self.links_To_Scrape) > 0:
            link = self.links_To_Scrape[0]
            self.links_To_Scrape.remove(link)
        else:
            self.links_To_Scrape = getListOfLinks()
            return self.get_link()
        return link['date'], link['url'], link['first'], link['last']

    # input - date as string, index as int
    # output - return case file name by date and page index as string
    @staticmethod
    def file_Name_for_Json_Case():
        return my_local_time() + '.json'

    @staticmethod
    def get_Frame(crawler, elem_type, string):
        frame = crawler.find_elem(elem_type, string)
        if frame is not None:
            return crawler.switch_frame(frame)
        else:
            massage = 'could not switch to frame: {}'.format(string)
            crawler.update_log(massage, level=4, user='Scraper')
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
                    crawler.update_log(massage, user='Scraper')
                    return N
        massage = 'could not get this page amount of cases'
        crawler.update_log(massage, level=3, user='Scraper')
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
            return '/html/body/div[2]/div/form/div/div/div[1]/div[3]/ul/li[' + str(index) + ']/div[2]/a'
        elif xpath == 'column':
            return '/html/body/div/div[1]/div/div/div[' + str(index) + ']/a'
        elif xpath == 'inside column':
            return '/html/body/div/div[2]/div[' + str(index) + ']'
        elif xpath == 'no info column':
            return '/html/body/div/div[2]/div[' + str(index) + ']/table/tbody/tr[4]/td/h4'
        elif xpath == 'many rows':
            return '/html/body/div/div[2]/div[' + str(index) + ']/table/tbody/tr[1]/td[1]'
        elif xpath == 'html':
            return '/html/body/div[2]/div/form/div/div/div[1]/div[3]/ul/li[' + str(index) + ']/div[4]/div[2]/a[3]'

    def get_elem(self, crawler, xpath, index):
        string = self.get_string_by_index(xpath, index)
        return crawler.find_elem('xpath', string, raise_error=False)

    # input - driver as web driver, N is the index we want to reach as int
    # do - put in view the item we want to click
    def scrollIntoView(self, crawler, N):
        result = True
        if N > 90:
            for index in range(1, N + 1):
                elem = self.get_elem(crawler, 'case Name', index)
                result = crawler.scroll_to_elem(elem)
            if result:
                massage = 'Scrolled to elem'
            else:
                massage = 'could not scrolled to case'
            crawler.update_log(massage, level=5, user='Scraper')

    # input - driver as web driver, index as int
    # output - return case name as element, otherwise print error massage and return none
    # do - return case name and click that case
    def getCase(self, crawler, index):
        elem = self.get_elem(crawler, 'case Name', index)
        if elem is not None:
            case_name = elem.text
            massage = 'Got case name'
            crawler.update_log(massage, user='Scraper')
            crawler.click_elem(elem)
            return case_name
        else:
            massage = 'did not found case name or could not click it'
            crawler.update_log(massage, user='Scraper')
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

    def getGenralDetails(self, crawler, index):
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
                    xpath = '/html/body/div/div[2]/div['+str(index)+']/table/tbody/tr['+str(row)+']/td['+str(col+1)+']'
                else:
                    xpath = '/html/body/div/div[2]/div[' + str(index) + ']/table/tbody/tr/td[' + str(col) + ']'

                elem = crawler.find_elem('xpath', xpath, raise_error=False, doPrint=False)
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
        elem = crawler.find_elem('xpath', string, raise_error=False, doPrint=False)
        update = crawler.read_elem_text(elem)
        if update is True:  # No info here
            return None

        string = self.get_string_by_index('inside column', index)
        elem = crawler.find_elem('xpath', string)
        sleep(1)

        if index == 1:
            func = self.getGenralDetails
        else:
            func = self.getOtherCaseDetails

        if elem is not None:
            return func(crawler, index)
        else:
            return None

    # input - driver as web driver
    # output - return False if this is a private case, otherwise True
    @staticmethod
    def isBlockedCase(crawler):
        elem = crawler.find_elem('xpath', '/html/body/table/tbody/tr[1]/td/b', raise_error=False, doPrint=False)
        if elem is not None:
            massage = 'This case in a private !!!'
            result = False
        else:
            massage = 'This case in not private - we can scrape more info'
            result = True
        crawler.update_log(massage, level=3, user='Scraper')
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
                crawler.update_log(massage, level=3, user='Scraper')
        return table

    @staticmethod
    def get_doc(crawler):
        text = None
        elem = crawler.find_elem('xpath', '/html/body/div[2]/div/div/div[2]/div/div[2]')
        if elem is not None:
            text = clean_spaces(elem.text)  # clean spaces
        return text

    # input - driver as web driver
    def getCaseDetails(self, crawler, index):
        caseDetailsDict = dict()

        crawler.switch_to_default_content()
        self.get_Frame(crawler, 'id', 'serviceFram')

        self.scrollIntoView(crawler, index)
        caseName = self.getCase(crawler, index)

        if caseName is not None:
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
        return crawler.click_elem(elem, user='Scraper')

    # input - driver as web driver
    # output (disabled) - return all the cases for the page he see as dict[caseName] = [caseFileDict, caseDetailsDict]
    #                                                    caseFileDict as dict['Case File'] = document text
    #                                                    caseDetailsDict as dict['Case Details'] = Case Details
    def get_Cases_Data(self, crawler, date, link, first, last):
        pageLoaded, noMoreUpdates = True, False
        # pick cases
        N, tries = 500, 3
        pageLoaded = crawler.update_page(link, user='Scraper')
        while N == 500 and tries > 0:
            N = self.get_num_of_Cases(crawler)
            tries -= 1
            self.checkForBackButton(crawler)  # in page got only the same case - happen in old dates
        if pageLoaded is False or N == 500:
            return None
        start, finish, N = self.case_picker(N, first, last)
        massage = 'page scrape start at case {} and end in case {}'.format(start, finish)
        crawler.update_log(massage, level=1, user='Scraper')
        if finish == 0:
            UpdateScrapeList(str(date), start, finish)
        for index in range(start, finish + 1):
            t1 = time()
            #while True:
                #try:
            case_details_dict = self.getCaseDetails(crawler, index)
            if case_details_dict['Doc Details'] is not None:
                writeJson(self.product_path, self.file_Name_for_Json_Case(), case_details_dict)

            massage = 'Case: {} took in seconds: {}'.format(index, time() - t1)
            crawler.update_log(massage, level=1)
            UpdateScrapeList(str(date), index + 1, N)


                #except:
                #massage = 'second error at scraping case number: {} at: {} - Moving to next case'.format(index, date)
                #crawler.update_log(massage, level=1, user='Scraper')

                #break

    # input - index as int
    def start_crawler(self, index):
        crawler = Crawler(index=index, delay=2)
        while True:
            date, link, first, last = self.get_link()
            if date is None:
                continue
            massage = 'Starting to scrape date: {}'.format(date)
            crawler.update_log(massage, user='Scraper', level=1)
            if first < last or last == -1:
                t1 = time()
                self.get_Cases_Data(crawler, date, link, first, last)
                massage = 'Finished crawling page with the date: {}, it took {} minutes'.format(date, (time() - t1) / 60)
                crawler.update_log(massage, user='Scraper', level=1)
            else:
                massage = 'Nothing to crawl here'
                crawler.update_log(massage, user='Scraper', level=1)

        # close web driver
        crawler.close()

    # do - go to each day that not scraped and take all the case files from them
    def start(self):
        # create a list of threads
        threads = []
        # In this case 'urls' is a list of urls to be crawled.
        for index in range(self.num_of_crawlers):  # make N crawlers
            # We start one thread per url present.
            process = Thread(target=self.start_crawler, args=[index + 1])
            process.start()
            threads.append(process)
        # We now pause execution on the main thread by 'joining' all of our started threads.
        # This ensures that each has finished processing the urls.
        for process in threads:
            process.join()
        # At this point, results for each URL are now neatly stored in order in 'results'


# run scraper only if run directly from python and not from import
if __name__ == "__main__":
    Scraper().start()
