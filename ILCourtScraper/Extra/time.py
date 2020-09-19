from time import time, sleep, strftime, localtime
from datetime import datetime, timedelta


def currTime(numSep='-', dateTimeSep='_'):
    return strftime(f"%d{numSep}%m{numSep}%Y{dateTimeSep}%H{numSep}%M{numSep}%S", localtime())


def callSleep(logger=None, days=0, hours=0, minutes=0, seconds=0):
    massage = f"Going to sleep for {days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
    if logger is not None:
        logger.info(massage)
    else:
        print(massage)
    sleep((days * 24 * 60 * 60) + (hours * 60 * 60) + (minutes * 60) + seconds)


# input - startDate as string, endDate as string, format as string
# do - generate the fallowing date every call
def generateDates(startDate='31-12-1996', endDate='01-01-2020', fmt='%d-%m-%Y', numSep='-',
                  startDay=None, startMonth=None, startYear=None, endDay=None, endMonth=None, endYear=None):

    if startDate and startMonth and startYear and endDay and endMonth and endYear:
        start = datetime.strptime(f"{startDay}{numSep}{startMonth}{numSep}{startYear}", '%d-%m-%Y')
        end = datetime.strptime(f"{endDay}{numSep}{endMonth}{numSep}{endYear}", '%d-%m-%Y')

    else:
        start = datetime.strptime(startDate, fmt)
        end = datetime.strptime(endDate, fmt)

    step = timedelta(days=1)
    while start < end:
        start += step
        yield start.date().strftime(fmt)
