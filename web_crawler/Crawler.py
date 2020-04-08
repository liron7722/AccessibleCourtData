from extra import *
from pathlib import Path
import platform
import logging
import logging.handlers
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, \
    ElementNotVisibleException, ElementNotSelectableException, ElementNotInteractableException, NoAlertPresentException, \
    JavascriptException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


class Crawler:
    _driver = None  # Web Driver
    _delay = None  # Timer for finding web element as int
    _url = None  # starting page as string
    _log = list()  # Inside log as list
    _text_query = None  # latest text scrape as string
    _index = None  # number of crawler running as int
    _log_name = None  # log name as string
    _log_path = None  # log path as string

    def __init__(self, index=1, browser=webdriver.Chrome, delay=1, url=None):
        self._log_name = f'crawler_{index}.log'  # name log file
        self._log_path = self.fixPath() + f'{os.sep}logs{os.sep}'
        self._logger = self.startLogger()
        self._driver = browser() if platform.system() == 'Windows' \
            else browser(executable_path=get_path() + os.sep + 'chromedriver')  # True if windows, false linux
        self._driver.maximize_window()  # fullscreen_window()  # Maximize browser window
        self.update_delay(delay)  # update delay
        self.update_page(url)  # open url
        self.update_log('Finished Initialize')

    # Functions
    @staticmethod
    def fixPath(path=None, N=1):
        path = Path().parent.absolute() if path is None else path
        splitPath = str(path).split(os.sep)
        return f"{os.sep}".join(splitPath[:-N])

    def startLogger(self, logger=None):
        newLogger = logging.getLogger(__name__) if logger is None else logger
        newLogger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s: %(message)s', datefmt='%d-%m-%Y %H-%M-%S')

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        file_handler = logging.handlers.RotatingFileHandler(self._log_path + self._log_name, maxBytes=52428800, backupCount=10)
        file_handler.setFormatter(formatter)

        newLogger.addHandler(file_handler)
        newLogger.addHandler(stream_handler)

        newLogger.info('Initialize')
        return newLogger

    def get_text_query(self, update=True):
        if update:
            return self._text_query
        else:
            return None

    # input - massage as string
    def update_log(self, massage, logType='debug'):
        if logType == 'info':
            self._logger.info(massage)
        elif logType == 'debug':
            self._logger.debug(massage)
        elif logType == 'warning':
            self._logger.warning(massage)
        elif logType == 'error':
            self._logger.error(massage)
        elif logType == 'critical':
            self._logger.critical(massage)

    def update_delay(self, delay=1):
        if type(delay) is int:
            self._delay = delay
            massage = f'Delay change to: {delay}'
        else:
            massage = 'Delay input was not int'

        self.update_log(massage)

    def update_page(self, url=None):
        result = False
        if url is not None:
            if type(url) is str:
                self._driver.get(url)
                callSleep(minutes=0, seconds=5)
                if True:  # TODO check if page loaded aka code 200
                    self._url = url
                    massage = f'URL change to: {url}'
                    result = True
                else:
                    self._driver.back()
                    massage = f'Could not load: {url}'
            else:
                massage = 'URL input was not string'
        else:
            massage = 'Did not get new URL to load'

        self.update_log(massage)
        return result

    # output - return True if successful
    def close(self):
        self._driver.quit()  # close the browser
        massage = 'Closing browser'
        self.update_log(massage, logType='info')
        return True

    def go_back(self):
        self._driver.back()
        massage = 'went to previous page'
        self.update_log(massage)
        return True

    def refresh(self):
        self._driver.refresh()
        massage = 'Refresh page'
        self.update_log(massage)
        return True

    # input - frame as web element
    def switch_frame(self, frame):
        self._driver.switch_to.frame(frame)
        massage = 'switch to frame'
        self.update_log(massage)
        return True

    # do - switch windows handle after case was clicked
    def switch_window_handle(self, index=0):
        window = self._driver.window_handles[index]
        self._driver.switch_to.window(window)
        massage = 'switch window handle'
        self.update_log(massage)
        return True

    # do - switch to default content
    def switch_to_default_content(self):
        self._driver.switch_to.default_content()
        massage = 'switch to default content'
        self.update_log(massage)
        return True

    def get_page_source(self):
        page_source = self._driver.page_source
        massage = 'Got page Source'
        self.update_log(massage, logType='info')
        return page_source

    # input - elem_type as string, string as string
    # output - return element if found in <delay> seconds, None otherwise
    def find_elem(self, elem_type, string, driver=None, delay=2, raise_error=True):
        if driver is None:
            driver = self._driver
        try:
            elem = None
            message = f'found elem: {string}, type: {elem_type}'
            if elem_type == 'xpath':
                WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, string)))
                elem = driver.find_element_by_xpath(string)
            elif elem_type == 'id':
                WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, string)))
                elem = driver.find_element_by_id(string)
            else:
                message = f'find_elem function do not have: {elem_type}'
            self.update_log(message)
            return elem

        except TimeoutException as exception:  # did not found elem in time
            if raise_error:
                message = f'Did not find elem: {string}, type: {elem_type}, delay: {delay}'
                self._logger.exception(msg=message)
            return None

        except ElementNotVisibleException as exception:  # did not found elem
            if raise_error:
                message = f'Elem is not visible: {string}, type: {elem_type}'
                self._logger.exception(msg=message)
            return None

        except NoSuchElementException as exception:  # did not found elem
            if raise_error:
                message = f'Did not find elem: {string}, type: {elem_type}'
                self._logger.exception(msg=message)
            return None

    # input - driver as web driver, elem as web element
    # output - return True if successful, otherwise False
    # do - hover the elem
    def hover_elem(self, driver, elem):
        try:
            hover = ActionChains(driver).move_to_element(elem)
            hover.perform()
            message = 'elem got hovered'
            self.update_log(message)
            return True

        except:
            message = 'Could not hover that'
            self._logger.exception(msg=message)
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
            self.update_log(message)
            return True

        except ElementNotSelectableException as exception:
            if message is None:
                message = 'Could not select that'
            self._logger.exception(msg=message)
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
            self.update_log(message)
            return True

        except ElementClickInterceptedException as exception:
            message = 'Could not click that'
            self._logger.exception(msg=message)
            return False

        except ElementNotInteractableException as exception:
            message = 'Could not click that'
            self._logger.exception(msg=message)
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
            self.update_log(message)
            return True

        except:
            message = 'Could not send elem this data'
            self._logger.exception(msg=message)
            return False

    # input - elem as web element
    # output - return True if successful, otherwise False
    # do - get the elem text
    def read_elem_text(self, elem):
        if elem is not None:
            try:
                text = elem.text  # get elem text
                self._text_query = text
                message = f'Got text from elem: {text}'
                self.update_log(message)
                return True

            except:
                self._text_query = None
                message = 'Could not get elem text'
                self._logger.exception(msg=message)
                return False
        else:
            message = 'cant read NoneType'
            self.update_log(message)
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
            self.update_log(message)
            return True

        except JavascriptException as exception:
            message = 'Could not execute script'
            self._logger.exception(msg=message)
            return False

    # input - result as string
    # output - return True if successful
    # do - return massage if result none, accept alert if result accept so accept, if result dismiss so dismiss
    def alert_handle(self, driver=None, result=None):
        if driver is None:
            driver = self._driver
        try:
            obj = driver.switch_to.alert  # driver focus on alert window
            text = f'alert message says: {obj.text}'  # take alert window message

            if result is not None:
                if result == 'accept':
                    obj.accept()  # accept alert window
                elif result == 'dismiss':
                    obj.dismiss()  # dismiss alert window

            driver.switch_to.default_content()  # return to main window

            self._text_query = text
            message = f'Alert say: {text}'
            self.update_log(message)
            return True

        except NoAlertPresentException as exception:
            message = 'Did not find any alert'
            self._logger.exception(msg=message)
            return False
