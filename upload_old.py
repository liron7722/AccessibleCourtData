from ILCourtScraper.Extra.path import getPath, sep, getFiles, createDir
from ILCourtScraper.Extra.db import DB
from ILCourtScraper.Extra.json import readData, saveData

readFolder = getPath(N=0) + f'products{sep}json_products{sep}'
handledFolder = getPath(N=0) + sep + f'products{sep}handled_json_products{sep}'
unhandledFolder = getPath(N=0) + sep + f'products{sep}unhandled_json_products{sep}'
backupFolder = getPath(N=0) + sep + f'products{sep}backup_json_products{sep}'
unBackupFolder = getPath(N=0) + sep + f'products{sep}unBackup_json_products{sep}'
createDir(unBackupFolder)


def run():
    total = 0
    counter = 0
    db = DB().getDB('SupremeCourt')
    connection = db.get_collection('files')
    cursor = list(connection.find({}))
    fileList = [file['name'] for file in cursor]

    for folder in [backupFolder, unhandledFolder, handledFolder]:
        listOfFiles = getFiles(folderPath=folder)
        total += len(listOfFiles)
        print(f"Got {len(listOfFiles)} files to upload in folder {folder}...")
        if len(listOfFiles) > 0:
            index = 0

            for fileName in listOfFiles:
                index += 1
                print(f"Starting to upload file {index} of {len(listOfFiles)}... ", end='')
                data = readData(fileName, '')
                temp = fileName
                fileName = fileName.replace(folder, '')  # extract file name
                if fileName not in fileList:
                    try:
                        connection.insert_one({"name": fileName, "data": data})
                        counter += 1
                        print("Succeed")
                    except:
                        saveData(data, fileName, unBackupFolder)
                        print("Failed")
                else:
                    print("Failed")

    print(f"{counter} files Succeed, {total - counter} Failed, Total {total} files")


run()
