#  botlib

# Generic functions for the discord bot


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
