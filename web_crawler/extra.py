import os
import json
from time import sleep


def get_path():
    return os.path.abspath(os.getcwd())


def callSleep(days=1, hours=1, minutes=1, seconds=60):
    sleep(days * hours * minutes * seconds)


def readJson(path, filename, side=os.sep):
    with open(path + side + filename, encoding='utf8') as json_file:
        data = json.load(json_file)
    return data


def writeJson(path, filename, data, side=os.sep):
    with open(path + side + filename, 'w') as outfile:
        json.dump(data, outfile, indent=4, ensure_ascii=True)


def separateDate(date):
    return date.split('/')


def change_path(old, new):
    count = 1
    while old[-count] is not os.sep:
        count += 1
    return old[:len(old) - count + 1] + new


def getTodayDate():
    from datetime import date
    today = date.today()
    day = today.strftime("%d")
    month = today.strftime("%m")
    year = today.strftime("%Y")
    return int(day), int(month), int(year)


def my_local_time():
    from time import strftime, localtime
    return strftime("%d-%m-%Y %H-%M-%S", localtime())


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
    max_days = isThisLeapYear(year)
    if day < max_days[month - 1]:
        day += 1
    else:
        day = 1
        if month < 12:
            month += 1
        else:
            month = 1
            year += 1
    return day, month, year


def clean_spaces(text):
    temp_list = list()
    for index in range(len(text)):
        if text[index] == ' ':
            if index != 0:
                if text[index - 1] == ' ':
                    continue
            else:
                continue
        temp_list.append(text[index])
    while temp_list[-1] == ' ':  # clean last spaces in the end
        temp_list.pop(-1)
    return "".join(temp_list)


def makeSureNoNumber(line, minimum=1, maximum=20):
    for number in range(minimum, maximum):
        if str(number) in line:
            line = line.replace(str(number), '')
    return clean_spaces(line)
