from glob import glob
from shutil import move
from pathlib import Path
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
def createDir(dirName):
    try:
        if not path.exists(dirName):  # Create target Directory if don't exist
            mkdir(dirName)
    except FileNotFoundError as _:
        createDir(getPath(dirName, N=1))  # create parent target folder
        createDir(dirName)  # create target folder


# move file\folder from oldPath to newPath, fileName can be inside oldPath
def changeDir(oldPath, newPath, fileName=None):
    move(oldPath, newPath) if fileName is None else move(oldPath + sep + fileName, newPath)
