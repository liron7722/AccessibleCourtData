import os
import json
import pandas as pd


def my_local_time():
    from time import strftime, localtime
    return strftime("%d-%m-%Y %H-%M-%S", localtime())


class Logger:
    _fileName = None  # String
    _filePath = None  # String
    _writeLevel = None  # int
    _printLevel = None  # int
    _log = list()  # list of dict [time: {}, user: {}, msg: {}, level: {} ]
    _printCsv = False

    def __init__(self, name=__name__ + ' log ' + my_local_time() + '.json', path=os.path.abspath(os.getcwd()),
                 writeLvl=3, PrintLvl=5, printCsv=False):
        self._fileName = name
        self._filePath = path
        self._writeLevel = writeLvl
        self._printLevel = PrintLvl
        self._printCsv = printCsv

    @staticmethod
    def dataToDict(data, user, writeLVL):
        return {'time': my_local_time(), 'user': user, 'msg': data, 'level': writeLVL}

    @staticmethod
    def dataDictToString(data):
        return '{} {}: {}'.format(data['time'], data['user'], data['msg'])

    def updateLog(self, data, user='', writeLVL=3, printLvl=10, filename=None, path=None, side=os.sep):
        dataDict = self.dataToDict(data, user, writeLVL)
        self._log.append(dataDict)
        massage = self.dataDictToString(dataDict)

        if writeLVL <= self._writeLevel:
            self.writeLog(massage, self._fileName, self._filePath, side)
            if self._printCsv:
                df = pd.DataFrame(data=self._log, index=[0])
                filename = filename.repalce('.json', '.csv')
                df.to_excel(path + side + filename)

        if printLvl <= self._printLevel:
            print(massage)

    @staticmethod
    def writeLog(data, filename, path, side=os.sep):
        with open(path + side + filename, 'a') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
            file.write("\n")

    def readLog(self, level=10):
        tempLog = list()
        for intent in self._log:
            if intent['level'] <= level:
                tempLog.append(self.dataDictToString(intent))
        return tempLog
