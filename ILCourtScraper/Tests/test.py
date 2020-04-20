from docToDict import *


def printDict(tempDict):
    for key, value in tempDict.items():
        print('{}: {}'.format(key, value))

listOfFiles = getFilesFromFolder(folderName=readFolder)
if len(listOfFiles) > 0:
    for fileName in listOfFiles:
        doc = readJson('', fileName, side='')
        text = doc['Doc Details']
        txtDict, succeed = doc_into_dict(text)