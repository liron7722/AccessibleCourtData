from extra import *
from Logger import Logger
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

    def __init__(self, index=1, browser=webdriver.Chrome, delay=1, url=None, log_level=4):
        self._log_name = 'crawler ' + str(index) + ' log ' + my_local_time() + '.json'  # name log file
        self._log_path = change_path(get_path(), 'logs')
        self.logger = Logger(self._log_name, self._log_path, writeLvl=log_level)
        self.update_log('Initialize')
        self._driver = browser()  # open Browser
        self._driver.fullscreen_window()  # Maximize browser window
        self.update_delay(delay)  # update delay
        self.update_page(url)  # open url
        self.update_log('Finished Initialize')

    # Functions
    def get_text_query(self, update=True):
        if update:
            return self._text_query
        else:
            return None

    # input - massage as string
    def update_log(self, massage, user='Crawler', level=3):
        self.logger.updateLog(massage, user, level)

    def update_delay(self, delay=1, user='Crawler'):
        if type(delay) is int:
            self._delay = delay
            massage = 'Delay change to: {}'.format(delay)
        else:
            massage = 'Delay input was not int'

        self.update_log(massage, user=user)

    def update_page(self, url=None, user='Crawler'):
        result = False
        if url is not None:
            if type(url) is str:
                self._driver.get(url)
                callSleep(seconds=5)
                if True:  # TODO check if page loaded aka code 200
                    self._url = url
                    massage = 'URL change to: ' + str(url)
                    result = True
                else:
                    self._driver.back()
                    massage = 'Could not load: {}'.format(url)
            else:
                massage = 'URL input was not string'
        else:
            massage = 'Did not get new URL to load'

        self.update_log(massage, user=user, level=2)
        return result

    # output - return True if successful
    def close(self, user='Crawler'):
        self._driver.quit()  # close the browser
        massage = 'Closing browser'
        self.update_log(massage, user=user)
        return True

    def go_back(self, user='Crawler'):
        self._driver.back()
        massage = 'went to previous page'
        self.update_log(massage, user=user)
        return True

    def refresh(self, user='Crawler'):
        self._driver.refresh()
        massage = 'Refresh page'
        self.update_log(massage, user=user)
        return True

    # input - frame as web element
    def switch_frame(self, frame, user='Crawler'):
        self._driver.switch_to.frame(frame)
        massage = 'switch to frame'
        self.update_log(massage, user=user, level=4)
        return True

    # do - switch windows handle after case was clicked
    def switch_window_handle(self, index=0, user='Crawler'):
        window = self._driver.window_handles[index]
        self._driver.switch_to.window(window)
        massage = 'switch window handle'
        self.update_log(massage, user=user, level=4)
        return True

    # do - switch to default content
    def switch_to_default_content(self, user='Crawler'):
        self._driver.switch_to.default_content()
        massage = 'switch to default content'
        self.update_log(massage, user=user, level=4)
        return True

    def get_page_source(self, user='Crawler'):
        page_source = self._driver.page_source
        massage = 'Got page Source'
        self.update_log(massage, user=user, level=3)
        return page_source

    # input - massage as string, exception as string
    def got_error(self, massage, exception=None, doPrint=True, user='Crawler'):
        if doPrint:
            self.update_log(massage, user=user)
            if exception is not None:
                self.update_log('Error: ' + exception.msg, user=user, level=0)
                # self.update_log('stacktrace: ' + exception.stacktrace)
            else:
                self.update_log('Error: No exception massage and no Trace', user=user)

    # input - elem_type as string, string as string
    # output - return element if found in <delay> seconds, None otherwise
    def find_elem(self, elem_type, string, driver=None, delay=2, raise_error=True, doPrint=True, user='Crawler'):
        if driver is None:
            driver = self._driver
        try:
            elem = None
            massage = 'found elem: {}, type: {}'.format(string, elem_type)
            if elem_type == 'xpath':
                WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, string)))
                elem = driver.find_element_by_xpath(string)
            elif elem_type == 'id':
                WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, string)))
                elem = driver.find_element_by_id(string)
            else:
                massage = 'find_elem function do not have: {}'.format(elem_type)
            self.update_log(massage, user=user, level=4)
            return elem

        except TimeoutException as exception:  # did not found elem in time
            if raise_error:
                massage = 'Did not find elem: {}, type: {}, delay: {}'.format(string, elem_type, delay)
                self.got_error(massage, exception, doPrint)
            return None

        except ElementNotVisibleException as exception:  # did not found elem
            if raise_error:
                massage = 'Elem is not visible: {}, type: {}'.format(string, elem_type)
                self.got_error(massage, exception, doPrint)
            return None

        except NoSuchElementException as exception:  # did not found elem
            if raise_error:
                massage = 'Did not find elem: {}, type: {}'.format(string, elem_type)
                self.got_error(massage, exception, doPrint)
            return None

    # input - driver as web driver, elem as web element
    # output - return True if successful, otherwise False
    # do - hover the elem
    def hover_elem(self, driver, elem, user='Crawler'):
        try:
            hover = ActionChains(driver).move_to_element(elem)
            hover.perform()
            massage = 'elem got hovered'
            self.update_log(massage, user=user, level=3)
            return True

        except:
            massage = 'Could not hover that'
            self.got_error(massage)
            return False

    # input - elem as web element, value as string, msg as string
    # output - return True if successful, otherwise False
    # do - select the option in elem
    def select_elem(self, elem, option, user='Crawler'):
        massage = None
        if type(option) is not str:  # if value is not string
            massage = 'option should be string and not {}'.format(type(option))
        try:
            select = Select(elem)  # select the elem
            select.select_by_visible_text(option)  # select by text
            massage = 'elem got selected'
            self.update_log(massage, user=user, level=4)
            return True

        except ElementNotSelectableException as exception:
            if massage is None:
                massage = 'Could not select that'
            self.got_error(massage, exception)
            return False

    # input - elem as web element, msg as string
    # output - return True if successful, otherwise False
    def click_elem(self, elem, user='Crawler'):
        try:
            elem.click()  # click the elem
            massage = 'element got clicked'
            self.update_log(massage, user=user, level=3)
            return True

        except ElementClickInterceptedException as exception:
            massage = 'Could not click that'
            self.got_error(massage, exception)
            return False

        except ElementNotInteractableException as exception:
            massage = 'Could not click that'
            self.got_error(massage, exception)
            return False

    # input - elem as web element, data as string
    # output - return True if successful, otherwise False
    # do - send the text box elem string
    def send_data_to_elem(self, elem, data, toClear=True, user='Crawler'):
        try:
            massage = ''
            if toClear:
                elem.clear()  # clear text box
                massage = 'text box got cleared'
            elem.send_keys(data)  # type sting into text box
            massage += ', element got the data'
            self.update_log(massage, user=user, level=4)
            return True

        except:
            massage = 'Could not send elem this data'
            self.got_error(massage)
            return False

    # input - elem as web element
    # output - return True if successful, otherwise False
    # do - get the elem text
    def read_elem_text(self, elem, user='Crawler'):
        try:
            text = elem.text  # get elem text
            self._text_query = text
            massage = 'Got text from elem: {}'.format(text)
            self.update_log(massage, user=user, level=4)
            return True

        except:
            self._text_query = None
            massage = 'Could not get elem text'
            self.got_error(massage)
            return False

    # input - driver as web driver, N is the index we want to reach as int
    # do - put in view the item we want to click
    @staticmethod
    def scroll_to_elem(elem):
        if elem is not None:
            elem.location_once_scrolled_into_view()  # remove () ?
            return True
        else:
            return False

    # input - driver as web driver, elem as web element, string as string
    # output - return True if successful, False as stop flag, massage as string
    # do - execute script on element
    def exec_script(self, driver, elem, string, user='Crawler'):
        try:
            driver.execute_script(string, elem)
            massage = 'Script executed'
            self.update_log(massage, user=user, level=3)
            return True

        except JavascriptException as exception:
            massage = 'Could not execute script'
            self.got_error(massage, exception)
            return False

    # input - result as string
    # output - return True if successful
    # do - return massage if result none, accept alert if result accept so accept, if result dismiss so dismiss
    def alert_handle(self, driver=None, result=None, user='Crawler'):
        if driver is None:
            driver = self._driver
        try:
            obj = driver.switch_to.alert  # driver focus on alert window
            text = 'alert massage says: {}'.format(obj.text)  # take alert window massage

            if result is not None:
                if result == 'accept':
                    obj.accept()  # accept alert window
                elif result == 'dismiss':
                    obj.dismiss()  # dismiss alert window

            driver.switch_to.default_content()  # return to main window

            self._text_query = text
            massage = 'Alert say: {}'.format(text)
            self.update_log(massage, user=user, level=2)
            return True

        except NoAlertPresentException as exception:
            massage = 'Did not find any alert'
            self.got_error(massage, exception)
            return False
