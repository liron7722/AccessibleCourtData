from glob import glob
from shutil import move
from pathlib import Path
from platform import system
from os import sep, path, mkdir


# do - return current path if didn't got oldPath and remove N folders from the end
def getPath(oldPath=None, N=0, endSep=True):
    currPath = Path().parent.absolute() if oldPath is None else oldPath  # get curr path in not provided
    splitPath = str(currPath).split(sep)  # split path to folders
    N = -N if N > 0 else len(splitPath)  # fix N for proper slice
    newPath = f"{sep}".join(splitPath[:N])  # rejoin wanted folders into path
    return newPath + sep if endSep else newPath  # path + sep if true else path


# do - get all files of that type at this path
def getFiles(folderPath, fileType='json'):
    return [f for f in glob(folderPath + "*." + fileType)]


# input - if dirName is string create folder at current path else create all the path
def createDir(dirName, logger=None):
    try:
        if not path.exists(dirName):  # Create target Directory if don't exist
            mkdir(dirName)
            message = f"Creating dir with the name: {dirName}"
            logger.info(message) if logger is not None else print(message)
    except FileNotFoundError as _:
        n = 1 if system() == 'Windows' else 2  # in case system is not windows - splitPath will have sep at the end
        createDir(getPath(dirName, N=n))  # create parent target folder
        createDir(dirName)  # create target folder


# move file\folder from oldPath to newPath, fileName can be inside oldPath
def changeDir(oldPath, newPath, fileName=None):
    move(oldPath, newPath) if fileName is None else move(oldPath + sep + fileName, newPath)
