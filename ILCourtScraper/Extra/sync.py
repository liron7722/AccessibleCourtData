from ILCourtScraper.Extra.db import DB
from ILCourtScraper.Extra.logger import Logger
from ILCourtScraper.Extra.time import callSleep
from ILCourtScraper.Extra.json import readData, saveData
from ILCourtScraper.Extra.path import getPath, sep, getFiles, createDir, changeDir


handledFolder = getPath(N=0) + f'products{sep}handled_json_products{sep}'
unhandledFolder = getPath(N=0) + f'products{sep}unhandled_json_products{sep}'
backupFolder = getPath(N=0) + f'products{sep}backup_json_products{sep}'
unBackupFolder = getPath(N=0) + f'products{sep}unBackup_json_products{sep}'

# key = source, value = destination
uploadFolders = {handledFolder: handledFolder,
                 unhandledFolder: unhandledFolder,
                 backupFolder: backupFolder,
                 unBackupFolder: backupFolder}
downloadFolders = [handledFolder, backupFolder]


for folder in [handledFolder, unhandledFolder, backupFolder, unBackupFolder]:
    createDir(folder)


def fixData(name, data):
    if "ת.החלטה" in str(data):
        for item in data["Case Details"]["תיק דלמטה"]:
            item["תאריך החלטה"] = item.pop("ת.החלטה")
        saveData(data, name, "")


def uploadSync(loop=True, delay=600):
    _logger = Logger('uploadSync.log', getPath(N=0) + f'logs{sep}').getLogger()
    while True:
        total = 0
        uCounter = 0
        sCounter = 0
        db = DB().getDB('SupremeCourt')

        for folder in uploadFolders.keys():
            connection = db.get_collection(uploadFolders)
            cursor = list(connection.find({}))
            backupFileList = [file['name'] for file in cursor]
            listOfFiles = getFiles(folderPath=folder)
            total += len(listOfFiles)
            _logger.info(f"Got {len(listOfFiles)} files to upload in folder {folder}...")
            if len(listOfFiles) > 0:
                index = 0
                for fileName in listOfFiles:
                    index += 1
                    _logger.info(f"Starting to upload file {index} of {len(listOfFiles)}... ", end='')
                    data = readData(fileName, '')
                    fixData(fileName, data)
                    temp = fileName
                    fileName = fileName.replace(folder, '')  # extract file name
                    if fileName not in backupFileList:
                        try:
                            connection.insert_one({"name": fileName, "data": data})
                            uCounter += 1
                            _logger.info("Succeed")
                            changeDir(temp, uploadFolders[folder])
                        except Exception as e:  # TODO better Exception
                            _logger.info(f"Failed to upload file{temp}")
                            _logger.info(e)
                    else:
                        _logger.info("Skipped")
                        sCounter += 1

        _logger.info(f"{uCounter} files Uploaded...\n{sCounter} files Skipped...\n{total - uCounter - sCounter} Failed...\nTotal {total} files")
        if loop is False:
            break
        callSleep(logger=_logger, seconds=delay)


def downloadSync(loop=True, delay=360):
    _logger = Logger('downloadSync.log', getPath(N=0) + f'logs{sep}').getLogger()
    while True:
        total = 0
        db = DB().getDB('SupremeCourt')
        for folder in downloadFolders:
            counter = 0
            connection = db.get_collection(downloadFolders)
            cursor = list(connection.find({}))
            fileList = [file.replace(folder, '') for file in getFiles(folderPath=folder)]  # extract file name
            for file in cursor:
                if file['name'] not in fileList:
                    saveData(file['data'], file['name'], folder)
                    counter += 1
            total += counter
            _logger.info(f"Total {counter} files ware downloaded into {folder}")
        _logger.info(f"Total {total} files ware downloaded")
        if loop is False:
            break
        callSleep(logger=_logger, seconds=delay)
