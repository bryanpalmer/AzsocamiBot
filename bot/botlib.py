#  botlib

# Generic functions for the discord bot
import datetime
from pytz import timezone

# import time

TIMEZONE = "US/Central"  # Timezone for bot responses
TIMEFORMAT = "%Y-%m-%d %H:%M:%S %Z"


def str2embedarray(origString, maxlen=1024):
    if len(origString) < maxlen:
        return [origString]
    aLines = origString.splitlines(True)
    retArray = []
    tempStr = ""
    for line in aLines:
        if len(tempStr + line) < maxlen:
            tempStr += line
        else:
            retArray.append(tempStr)
            tempStr = line
    retArray.append(tempStr)
    return retArray


def localTimeStr(utcTime):
    return utcTime.astimezone(timezone(TIMEZONE)).strftime(TIMEFORMAT)


def localNow():
    return localTimeStr(datetime.datetime.now())
