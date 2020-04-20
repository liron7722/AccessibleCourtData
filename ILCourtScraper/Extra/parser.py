from ILCourtScraper.Extra.time import callSleep
from ILCourtScraper.Extra.json import readData, saveData
from ILCourtScraper.Extra.path import getPath, sep, createDir, changeDir, getFiles

readFolder = getPath(N=2) + f'products{sep}json_products'
handledFolder = getPath(N=2) + sep + f'products{sep}handled_json_products'
unhandledFolder = getPath(N=2) + sep + f'products{sep}unhandled_json_products'
backupFolder = getPath(N=2) + sep + f'products{sep}backup_json_products'


def clean_spaces(text):
    if type(text) is str:  # if text is a string
        if '\n' in text:  # if there is more than one line
            return clean_spaces(text.splitlines())  # resend it as list
    else:  # if text is a list
        for index in range(len(text)):  # for each line in the list
            text[index] = clean_spaces(text[index])  # resend one line
        return text

    temp_list = list()  # the return list of characters
    space = ' '
    for index in range(len(text)):
        if text[index] == space:  # if this a space
            if index != 0:  # if we not on the first index
                if text[index - 1] == space:  # if we saw a space don't add this one
                    continue
                else:  # in this case we do want to add
                    pass
            else:
                continue
        temp_list.append(text[index])

    if len(temp_list) > 0:  # make sure we don't got empty list
        while temp_list[0] == space:  # clean spaces at the start
            temp_list.pop(0)
        while temp_list[-1] == space:  # clean spaces at the end
            temp_list.pop(-1)

    return "".join(temp_list)  # rejoin the set of characters


def makeSureNoNumber(line, minimum=1, maximum=20):
    for number in range(minimum, maximum):
        if str(number) in line:
            line = line.replace(str(number), '')
    return clean_spaces(line)


def drop_extra_info(text, minimum=1, maximum=5):
    product = list()
    EOFSign = '__'
    startWord = 'לפני'
    keyInLineSign = ':'
    bannedWords = ['נגד', 'נ ג ד']
    temp = clean_spaces(text)
    for index in range(len(temp)):
        if EOFSign in temp[index]:  # we got all we want lets pack it and go back
            return "\n".join(product)
        elif keyInLineSign in temp[index] or startWord in temp[index]:  # In case we have more rows between row 0 to judges names
            maximum = index

        if index not in range(minimum, maximum):  # Include all but unnecessary information
            doBreak = False
            for word in bannedWords:
                if word in temp[index]:
                    doBreak = True
                    break
            if doBreak:
                continue
            product.append(temp[index])
    return '\n'.join(product)  # rejoin all the line of the text


def removeWords(values):
    removeWord = ['כבוד']
    for word in removeWord:
        if type(values) is list:
            for index in range(len(values)):
                values[index] = values[index].replace(word, '')
                values[index] = clean_spaces(values[index])
        else:
            values = clean_spaces(values.replace(word, ''))
    return values


def isThereMore(line, oldValues=None, key=';'):
    oldValues = list() if oldValues is None else oldValues
    if key in line:
        values = line.split(key)
        for index in range(len(values)):
            values[index] = clean_spaces(values[index])
        oldValues.extend(removeWords(values))
    else:
        oldValues.append(removeWords(line))
    return oldValues


def get_Key(tempKey):
    tempKey = makeSureNoNumber(tempKey)
    temp_dict = {
        'לפני': ['לפני'],
        'בשם העותר': ['בשם המערערים', 'בשם המערער', 'בשם המערערת', 'בשם המערערות',
                      'בשם העותר', 'בשם העותרת', 'בשם העותרים', 'בשם העותרות',
                      'בשם המבקש', 'בשם המבקשת', 'בשם המבקשים', 'בשם המבקשות',
                      'בשם העורר', 'בשם העוררת', 'בשם העוררים', 'בשם העוררות'],
        'בשם המשיב': ['בשם המשיבים', 'בשם המשיב', 'בשם המשיבות', 'בשם המשיבה'],
        'העותר': ['המערערים', 'המערער', 'המערערת', 'המערערות',
                  'העותר', 'העותרת', 'העותרים', 'העותרות',
                  'המבקש', 'המבקשת', 'המבקשים', 'המבקשות',
                  'העורר', 'העוררת', 'העוררים', 'העוררות'],
        'המשיב': ['המשיבים', 'המשיב', 'המשיבות', 'המשיבה'],
    }

    for key, item in temp_dict.items():
        if tempKey in item:
            return key
    return None  # if it get here we missing some keys


def gotVerdict(line):
    verdictKeyList = ['החלטה', 'פסק-דין']
    for key in verdictKeyList:
        if key in line:
            return True, key
    return False, None


def gotExtraInformation(line):
    ExtraInformationKeys = ['בקשה']
    for key in ExtraInformationKeys:
        if key in line:
            return True
    return False


def getKeyList(mustHave=True):
    if mustHave:
        return ['לפני', 'העותר', 'המשיב', 'מספר הליך', 'סוג מסמך', 'סיכום']
    return ['מידע נוסף', 'בשם העותר', 'בשם המשיב']


def iGotItAll(tempDict, keyList):
    for key in keyList:
        if key in tempDict.keys():
            if tempDict[key] is None:
                return False
        else:
            return False
    return True


def parser(text):
    doc_dict = dict()
    shouldIAdd, moreInfo, someKey, value_list, numOfValues = False, False, None, None, 1
    text = drop_extra_info(text)
    temp = text.splitlines()
    doc_dict['מספר הליך'] = temp[0]
    for index in range(1, len(temp)):
        if ':' in temp[index]:
            if shouldIAdd:  # finished getting values for previous key
                key = get_Key(someKey)
                doc_dict[key] = value_list
                numOfValues = 1
            value_list = list()
            temp_list = temp[index].split(':')
            someKey = temp_list[0]
            shouldIAdd = True
            if len(temp_list[1]) > 0:
                value_list.append(temp_list[1])
        elif gotVerdict(temp[index])[0]:  # what remain is verdict text
            key = get_Key(someKey)
            doc_dict[key] = value_list
            doc_dict['סוג מסמך'] = gotVerdict(temp[index])[1]
            doc_dict['סיכום'] = "\n".join(temp[index + 1:])
            break
        else:  # get another values for key or get extra text pre verdict
            strValue = str(numOfValues) + '. '  # string to replace
            if strValue in temp[index]:  # if we got another value to add
                numOfValues += 1  # increment value
                value = temp[index].replace(strValue, '')  # remove the number + dot + space from the new value
                value_list.append(value)
            elif gotExtraInformation(temp[index]):  # if we got extra info
                doc_dict['מידע נוסף'] = isThereMore(temp[index]) if moreInfo is False \
                    else isThereMore(temp[index], doc_dict['מידע נוסף'])
                moreInfo = True
            else:  # add new value\s to the list
                value_list = isThereMore(temp[index], value_list)

    if iGotItAll(doc_dict, getKeyList()):
        for key in getKeyList(mustHave=False):
            if key not in doc_dict.keys():
                doc_dict[key] = list()
        return doc_dict, True
    return text, False


def run():
    listOfFiles = getFiles(folderPath=readFolder)
    if len(listOfFiles) > 0:
        for fileName in listOfFiles:
            doc = readData('', fileName)  # fileName include path and os.sep not needed
            doc['Doc Details'], succeed = parser(doc['Doc Details'])  # if succeed Dict, else text
            writeFolder = handledFolder if succeed else unhandledFolder
            changeDir(fileName, backupFolder)  # backup files
            fileName = fileName.replace(readFolder, '')  # extract file name
            saveData(writeFolder, fileName, doc)  # '' = fileName contain the path so no need in path or os.sep
    else:
        callSleep(minutes=10)  # after finished with all the files wait a bit - hours * minutes * seconds


if __name__ == '__main__':
    for folder in [readFolder, handledFolder, unhandledFolder, backupFolder]:
        createDir(folder)
    while True:
        run()
