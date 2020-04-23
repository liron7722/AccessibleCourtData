from platform import system
from ILCourtScraper.Extra.logger import Logger
from ILCourtScraper.Extra.path import getPath, sep
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, \
    ElementNotVisibleException, ElementNotSelectableException, ElementNotInteractableException, NoAlertPresentException, \
    JavascriptException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


class Crawler:
    _driver = None  # Web Driver
    _delay = None  # Timer for finding web element as int
    _url = None  # starting page as string
    _text_query = None  # latest text scrape as string
    _logger = None  # logging log class

    def __init__(self, index=1, browser='chrome', delay=1, url=None):
        self._logger = Logger(f'{__name__}crawler_{index}.log', getPath(N=2) + f'logs{sep}').getLogger()
        self._driver = self.getBrowser(browser)
        self._driver.maximize_window()  # fullscreen_window()  # Maximize browser window
        self.update_delay(delay)  # update delay
        self.update_page(url)  # open url
        self._logger.info('Finished crawler Initialize')

    # Functions
    @staticmethod
    def getBrowser(browser='chrome'):
        if browser == 'chrome':
            if system() == 'Windows':
                return webdriver.Chrome(executable_path=getPath(N=1) + f'WebDrivers{sep}chromedriver.exe')
            return webdriver.Chrome(executable_path=getPath(N=1) + f'WebDrivers{sep}chromedriver')
        elif browser == 'firefox':
            if system() == 'Windows':
                return webdriver.Firefox(executable_path=getPath(N=1) + f'WebDrivers{sep}geckodriver.exe')
            return webdriver.Firefox(executable_path=getPath(N=1) + f'WebDrivers{sep}geckodriver')  # TODO add path
        elif browser == 'edge':
            if system() == 'Windows':
                return webdriver.Edge(executable_path=getPath(N=1) + f'WebDrivers{sep}msedgedriver.exe')

    # input - update as boolean
    # output - return string if true, else None
    # do - return the last text that got scraped
    def get_text_query(self, update=True):
        if update:
            return self._text_query
        else:
            return None

    # input - delay as int
    # do - change the main delay for the crawler
    def update_delay(self, delay=1):
        if type(delay) is int:
            self._delay = delay
            message = f'Delay change to: {delay}'
        else:
            message = 'Delay input was not int'
        self._logger.info(message)

    # input - url as string
    # output - return true if succeed else false
    # do - load the url for the crawler
    def update_page(self, url=None):
        result = False
        if url is not None:
            if type(url) is str:
                self._driver.get(url)
                if True:  # TODO check if page loaded aka code 200
                    self._url = url
                    message = f'URL change to: {url}'
                    result = True
                # else:
                    # self._driver.back()
                    # massage = f'Could not load: {url}'
            else:
                message = 'URL input was not string'
        else:
            message = 'Did not get new URL to load'

        self._logger.info(message)
        return result

    # output - return True if successful
    # do - close web driver
    def close(self):
        self._driver.quit()  # close the browser
        message = 'Closing browser'
        self._logger.info(message)
        return True

    # output - return True if successful
    # do - return to previous page
    def go_back(self):
        self._driver.back()
        message = 'went to previous page'
        self._logger.info(message)
        return True

    # output - return True if successful
    # do - refresh page loaded on crawler
    def refresh(self):
        self._driver.refresh()
        message = 'Refresh page'
        self._logger.info(message)
        return True

    # input - frame as web element
    # do
    def switch_frame(self, frame):
        self._driver.switch_to.frame(frame)
        message = 'switch to frame'
        self._logger.info(message)
        return True

    # do - switch windows handle after case was clicked
    def switch_window_handle(self, index=0):
        window = self._driver.window_handles[index]
        self._driver.switch_to.window(window)
        message = 'switch window handle'
        self._logger.info(message)
        return True

    # do - switch to default content
    def switch_to_default_content(self):
        self._driver.switch_to.default_content()
        message = 'switch to default content'
        self._logger.info(message)
        return True

    def get_page_source(self):
        page_source = self._driver.page_source
        message = 'Got page Source'
        self._logger.info(message)
        return page_source

    # input - elem_type as string, string as string
    # output - return element if found in <delay> seconds, None otherwise
    def find_elem(self, elem_type, string, singleElement=True, driver=None, delay=2, raise_error=True):
        driver = self._driver if driver is None else driver
        message = ''
        try:
            elem = None
            message = f'found elem: {string}, type: {elem_type}'
            if singleElement:
                if elem_type == 'xpath':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, string)))
                    elem = driver.find_element_by_xpath(string)
                elif elem_type == 'id':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, string)))
                    elem = driver.find_element_by_id(string)
                elif elem_type == 'tag':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.TAG_NAME, string)))
                    elem = driver.find_element_by_tag_name(string)
                elif elem_type == 'name':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.NAME, string)))
                    elem = driver.find_element_by_name(string)
                elif elem_type == 'link_text':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.LINK_TEXT, string)))
                    elem = driver.find_element_by_link_text(string)
                elif elem_type == 'partial_link_text':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, string)))
                    elem = driver.find_element_by_partial_link_text(string)
                elif elem_type == 'css':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, string)))
                    elem = driver.find_element_by_css_selector(string)
                elif elem_type == 'class_name':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, string)))
                    elem = driver.find_element_by_class_name(string)
                else:
                    message = f'find_element function do not have: {elem_type}'
            else:
                if elem_type == 'xpath':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, string)))
                    elem = driver.find_elements_by_xpath(string)
                elif elem_type == 'id':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, string)))
                    elem = driver.find_elements_by_id(string)
                elif elem_type == 'tag':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.TAG_NAME, string)))
                    elem = driver.find_elements_by_tag_name(string)
                elif elem_type == 'name':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.NAME, string)))
                    elem = driver.find_elements_by_name(string)
                elif elem_type == 'link_text':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.LINK_TEXT, string)))
                    elem = driver.find_elements_by_link_text(string)
                elif elem_type == 'partial_link_text':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, string)))
                    elem = driver.find_elements_by_partial_link_text(string)
                elif elem_type == 'css':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, string)))
                    elem = driver.find_elements_by_css_selector(string)
                elif elem_type == 'class_name':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, string)))
                    elem = driver.find_elements_by_class_name(string)
                else:
                    message = f'find_element function do not have: {elem_type}'
            self._logger.info(message)
            return elem

        except TimeoutException as _:  # did not found elem in time
            if raise_error:
                message = f'Did not find elem: {string}, type: {elem_type}, delay: {delay} in time'
                self._logger.exception(message)
            return None

        except ElementNotVisibleException as _:  # did not found elem
            if raise_error:
                message = f'Elem is not visible: {string}, type: {elem_type}'
                self._logger.exception(message)
            return None

        except NoSuchElementException as _:  # did not found elem
            if raise_error:
                message = f'No Such elem: {string}, type: {elem_type}'
                self._logger.exception(message)
            return None
        finally:
            if raise_error is False:
                self._logger.error(message)

    # input - driver as web driver, elem as web element
    # output - return True if successful, otherwise False
    # do - hover the elem
    def hover_elem(self, driver, elem):
        try:
            hover = ActionChains(driver).move_to_element(elem)
            hover.perform()
            message = 'elem got hovered'
            self._logger.info(message)
            return True

        except Exception as _:
            message = 'Could not hover that'
            self._logger.exception(message)
            return False

    # input - elem as web element, value as string, msg as string
    # output - return True if successful, otherwise False
    # do - select the option in elem
    def select_elem(self, elem, option):
        message = None
        if type(option) is not str:  # if value is not string
            message = f'option should be string and not {type(option)}'
        try:
            select = Select(elem)  # select the elem
            select.select_by_visible_text(option)  # select by text
            message = 'elem got selected'
            self._logger.info(message)
            return True

        except ElementNotSelectableException as _:
            if message is None:
                message = 'Could not select that'
            self._logger.error(message)
            return False

    # input - elem as web element, msg as string
    # output - return True if successful, otherwise False
    def click_elem(self, elem):
        try:
            if elem is not None:
                elem.click()  # click the elem
                message = 'element got clicked'
            else:
                message = 'didnt got element to click - got None instead'
            self._logger.info(message)
            return True

        except ElementClickInterceptedException as _:
            message = 'Element Click Intercepted'
            self._logger.exception(message)
            return False

        except ElementNotInteractableException as _:
            message = 'Element Not Interactable'
            self._logger.exception(message)
            return False

    # input - elem as web element, data as string
    # output - return True if successful, otherwise False
    # do - send the text box elem string
    def send_data_to_elem(self, elem, data, toClear=True):
        try:
            message = ''
            if toClear:
                elem.clear()  # clear text box
                message = 'text box got cleared'
            elem.send_keys(data)  # type sting into text box
            message += ', element got the data'
            self._logger.info(message)
            return True

        except Exception as _:
            message = 'Could not send elem this data'
            self._logger.exception(message)
            return False

    # input - elem as web element
    # output - return True if successful, otherwise False
    # do - get the elem text
    def read_elem_text(self, elem):
        try:
            text = elem.text  # get elem text
            self._text_query = text
            message = f'Got text from elem: {text}'
            self._logger.info(message)
            return True

        except Exception as _:
            self._text_query = None
            message = 'Could not get elem text'
            self._logger.exception(message)
            return False

    # input - driver as web driver, N is the index we want to reach as int
    # do - put in view the item we want
    @staticmethod
    def scroll_to_elem(elem):
        if elem is not None:
            elem.location_once_scrolled_into_view  # don't put ()
            return True
        else:
            return False

    # input - driver as web driver, elem as web element, string as string
    # output - return True if successful, False as stop flag, massage as string
    # do - execute script on element
    def exec_script(self, driver, elem, string):
        try:
            driver.execute_script(string, elem)
            message = 'Script executed'
            self._logger.info(message)
            return True

        except JavascriptException as _:
            message = 'Could not execute script'
            self._logger.exception(message)
            return False

    # input - result as string
    # output - return True if successful
    # do - return massage if result none, accept alert if result accept so accept, if result dismiss so dismiss
    def alert_handle(self, driver=None, result=None):
        driver = self._driver if driver is None else driver
        try:
            obj = driver.switch_to.alert  # driver focus on alert window
            text = f'alert massage says: {obj.text}'  # take alert window massage

            if result is not None:
                if result == 'accept':
                    obj.accept()  # accept alert window
                elif result == 'dismiss':
                    obj.dismiss()  # dismiss alert window

            driver.switch_to.default_content()  # return to main window

            self._text_query = text
            message = f'Alert say: {text}'
            self._logger.info(message)
            return True

        except NoAlertPresentException as _:
            message = 'Did not find any alert'
            self._logger.error(message)
            return False
