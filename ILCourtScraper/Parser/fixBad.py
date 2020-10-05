from ILCourtScraper.Extra.json import readData, saveData
from ILCourtScraper.Extra.path import getPath, sep, getFiles, remove

readFolder = getPath(N=0) + f'products{sep}handled_json_products{sep}'
writeFolder = getPath(N=0) + f'products{sep}unhandled_json_products{sep}'


def fixSchema(doc):
    for key in doc['Doc Info']:
        doc['Doc Details'][key] = doc['Doc Info'][key] if key != 'עמודים' \
            else [int(s) for s in doc['Doc Info'][key].split() if s.isdigit()][0]
    doc.pop('Doc Info', None)
    return doc


def moveFile(data, fileName, sourceFolder, destFolder):
    remove(fileName)  # delete old copy
    fileName = fileName.replace(sourceFolder, '')  # extract file name
    saveData(data, fileName, destFolder)  # save new copy


def run():
    listOfFiles = getFiles(folderPath=readFolder)
    for fileName in listOfFiles:
        doc = readData('', fileName)  # fileName include path and os.sep not needed
        doc = fixSchema(doc)
        moveFile(doc, fileName, readFolder, writeFolder)


run()