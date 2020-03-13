import os
import json
import glob
from time import sleep


def callSleep(days=1, hours=1, minutes=1, seconds=60):
    sleep(days * hours * minutes * seconds)


def get_path():
    return os.path.abspath(os.getcwd())


def readJson(path, fileName, side=os.sep):
    with open(path + side + fileName) as json_file:
        data = json.load(json_file)
    return data


def writeJson(path, filename, data, side=os.sep):
    with open(path + side + filename, 'w') as outfile:
        json.dump(data, outfile, indent=4, ensure_ascii=False)


def getFilesFromFolder(folderName=get_path(), fileType='json'):
    return [f for f in glob.glob(folderName + os.sep + "*." + fileType)]