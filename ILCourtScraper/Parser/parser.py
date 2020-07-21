from ILCourtScraper.Extra.logger import Logger
from ILCourtScraper.Extra.time import callSleep
from ILCourtScraper.Extra.json import readData, saveData
from ILCourtScraper.Extra.path import getPath, sep, createDir, getFiles, remove

readFolder = getPath(N=0) + f'products{sep}json_products{sep}'
handledFolder = getPath(N=0) + f'products{sep}handled_json_products{sep}'
unhandledFolder = getPath(N=0) + f'products{sep}unhandled_json_products{sep}'

for f in [readFolder, handledFolder, unhandledFolder]:
    createDir(f)


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


def makeSureNoNumber(line, minimum=1, maximum=200):
    for number in range(minimum, maximum):
        if str(number) in line:
            line = line.replace(str(number), '')
    return clean_spaces(line)


def drop_extra_info(text, minimum=1, maximum=5):
    product = list()
    EOFSign = '__'
    startWord = 'לפני'
    keyInLineSign = ':'
    bannedWords = ['נגד', 'נ ג ד', 'ש ו פ ט ת', 'ש ו פ ט', 'ר ש ם', 'ר ש מ ת', 'ה נ ש י א ה', 'ה נ ש י א']
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
                      'בשם העורר', 'בשם העוררת', 'בשם העוררים', 'בשם העוררות',
                      'בשם המאשים', 'בשם המאשימה', 'בשם המאשימים', 'בשם המאשימות',
                      'בשם התובע', 'בשם התובעת', 'בשם התובעים', 'בשם התובעות'],

        'בשם המשיב': ['בשם המשיבים', 'בשם המשיב', 'בשם המשיבות', 'בשם המשיבה',
                      'בשם הנאשמים', 'בשם הנאשם', 'בשם הנאשמות', 'בשם הנאשמת',
                      'בשם הנתבעים', 'בשם הנתבע', 'בשם הנתבעות', 'בשם הנתבעת'],

        'העותר': ['המערערים', 'המערער', 'המערערת', 'המערערות',
                  'העותר', 'העותרת', 'העותרים', 'העותרות',
                  'המבקש', 'המבקשת', 'המבקשים', 'המבקשות',
                  'המאשים', 'המאשימים', 'המאשימה', 'המאשימות',
                  'העורר', 'העוררת', 'העוררים', 'העוררות',
                  'התובע', 'התובעת', 'התובעים', 'התובעות'],

        'המשיב': ['המשיבים', 'המשיב', 'המשיבות', 'המשיבה',
                  'הנאשם', 'הנאשמת', 'הנאשמים', 'הנאשמות',
                  'הנתבעים', 'הנתבעת', 'הנתבעות', 'הנתבע'],
    }

    for key, item in temp_dict.items():
        if tempKey in item:
            return key
    for key, item in temp_dict.items():
        for possibleKey in item:
            if possibleKey in tempKey:
                return key

    return None  # if it get here we missing some keys or No key in given tempKey


def gotVerdict(line):
    verdictKeyList = ['החלטה', 'פסק-דין', 'פסק דין', 'צו-על-תנאי']
    for key in verdictKeyList:
        if key in line:
            return True, key
    return False, None


def gotExtraInformation(line):
    ExtraInformationKeys = ['בקשה', 'ערעור', 'העברת מקום דיון', 'הגשת עיקרי טיעון', 'צו על תנאי']
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


def parser(caseText):
    doc_dict = dict()
    addToken, moreInfoToken, tempKey, valuesList, numOfValues, linesToSkip = False, False, None, None, 1, []
    caseText = drop_extra_info(caseText)
    verdictLines = caseText.splitlines()
    doc_dict['מספר הליך'] = verdictLines[0]
    N = len(verdictLines)
    for index in range(1, N):
        if index in linesToSkip:
            continue
        elif ':' in verdictLines[index] or get_Key(verdictLines[index]) is not None:  # we got a key
            if addToken:  # finished getting values for previous key
                key = get_Key(tempKey)
                if key not in doc_dict.keys():
                    doc_dict[key] = valuesList
                else:
                    doc_dict[key].extend(valuesList)
                numOfValues = 1
            valuesList = list()  # start gather values for found key
            temp_list = verdictLines[index].split(':')
            tempKey = temp_list[0]
            addToken = True
            if len(temp_list) > 1:
                if len(temp_list[1]) > 0:
                    valuesList.append(temp_list[1])
        elif gotVerdict(verdictLines[index])[0]:  # what remain is verdict text
            key = get_Key(tempKey)
            doc_dict[key] = valuesList
            doc_dict['סוג מסמך'] = gotVerdict(verdictLines[index])[1]
            doc_dict['סיכום'] = "\n".join(verdictLines[index + 1:])
            break
        else:  # get another values for key or get extra text pre verdict
            strValue = f"{numOfValues}. "  # string to replace in ordered values
            if strValue in verdictLines[index]:  # if we got another value to add
                numOfValues += 1  # increment value for next in order
                valuesList.append(verdictLines[index].replace(strValue, ''))  # remove the number + dot + space from the new value
            elif gotExtraInformation(verdictLines[index]):  # if we got extra info
                extraInfoValues = verdictLines[index]
                while index + 1 < N:  # start gather all extra info in coming rows
                    if ":" in verdictLines[index + 1]: # if we finished with extra info
                        if "תאריך הישיבה:" not in verdictLines[index + 1]:  # private case of extra info
                            if get_Key(verdictLines[index + 1].split(':')[0]) is not None:
                                break
                    elif gotVerdict(verdictLines[index+1])[0]:
                        break

                    index += 1
                    linesToSkip.append(index)  # make list of lines we added
                    extraInfoValues += f";{verdictLines[index]}"  # concatenate value to string
                doc_dict['מידע נוסף'] = isThereMore(extraInfoValues)  # get list from the string we built
            else:  # add new value\s to the list
                valuesList = isThereMore(verdictLines[index], valuesList)

    if iGotItAll(doc_dict, getKeyList()):
        for key in getKeyList(mustHave=False):
            if key not in doc_dict.keys():
                doc_dict[key] = list()
            if None in doc_dict.keys():
                return caseText, False
        return doc_dict, True
    return caseText, False


def moveFile(data, fileName, sourceFolder, destFolder):
    remove(fileName)  # delete old copy
    fileName = fileName.replace(sourceFolder, '')  # extract file name
    saveData(data, fileName, destFolder)  # save new copy


def run(folder, logger=None, minDelay=10):
    listOfFiles = getFiles(folderPath=folder)
    message = f"Got {len(listOfFiles)} files to parse."
    logger.info(message) if logger is not None else print(message)
    if len(listOfFiles) > 0:
        index = 0
        counter = 0
        skipCounter = 0
        for fileName in listOfFiles:
            index += 1
            message = f"Starting to parse file {index} of {len(listOfFiles)}... "
            logger.info(message) if logger is not None else print(message, end='')
            doc = readData('', fileName)  # fileName include path and os.sep not needed
            if len(doc) < 1:  # private case - we got empty file
                logger.info("Skipped") if logger is not None else print(message)
                skipCounter += 1
                moveFile(doc, fileName, folder, unhandledFolder)
                continue
            elif 'לפני:' not in str(doc['Doc Details']):  # old type of case
                logger.info("Skipped") if logger is not None else print(message)
                skipCounter += 1
                moveFile(doc, fileName, folder, unhandledFolder)
                continue
            doc['Doc Details'], succeed = parser(doc['Doc Details'])  # if succeed Dict, else text
            writeFolder = handledFolder if succeed else unhandledFolder
            moveFile(doc, fileName, folder, writeFolder)
            if succeed:
                counter += 1
                logger.info(f"File {index} succeed") if logger is not None else print('Succeed')
            else:
                # from pprint import pprint  # for testing
                # pprint(doc['Doc Details'])  # for testing
                logger.info(f"File {index} failed") if logger is not None else print('Failed')
        message = f"{counter} files Succeed, {skipCounter} files Skipped, {len(listOfFiles) - counter - skipCounter} files Failed, Total {len(listOfFiles)} files"
        logger.info(message) if logger is not None else print(message)

    else:
        logger.info('Parser finished his job.') if logger is not None else print('Parser finished his job.')
        callSleep(logger=logger, minutes=minDelay)  # after finished with all the files wait a bit - hours * minutes * seconds


def main():
    _logger = Logger('parser.log', getPath(N=0) + f'logs{sep}').getLogger()
    _logger.info("Parser is Starting")
    run(unhandledFolder, _logger, minDelay=0)
    while True:
        _logger.info("Parser is Starting")
        run(readFolder, _logger)


if __name__ == '__main__':
    main()
