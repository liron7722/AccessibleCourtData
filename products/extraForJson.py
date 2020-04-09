import os
import json
import glob
from time import sleep


def get_path():
    return os.path.abspath(os.getcwd())


def readJson(path, fileName, side=os.sep):
    with open(path + side + fileName, encoding='utf8') as json_file:
        data = json.load(json_file)
    return data


def writeJson(path, filename, data, side=os.sep):
    with open(path + side + filename, 'w') as outfile:
        json.dump(data, outfile, indent=4, ensure_ascii=True)


def getFilesFromFolder(folderName=get_path(), fileType='json'):
    return [f for f in glob.glob(folderName + os.sep + "*." + fileType)]


def change_path(old, new):
    count = 1
    while old[-count] is not os.sep:
        count += 1
    return new + old[len(old) - count:]


def callSleep(logFunc=None, days=0, hours=0, minutes=1, seconds=0):
    massage = f"Going to sleep for {days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
    if logFunc is not None:
        logFunc(massage)
    sleep((days * 24 * 60 * 60) + (hours * 60 * 60) + (minutes * 60) + seconds)