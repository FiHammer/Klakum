import time
import os
import sys
import threading
import random

def cls():
    if sys.platform == "win32":
        os.system("cls")

class ddbug(threading.Thread):
    def __init__(self):
        super().__init__()
        self.work = True

    def run(self):
        while self.work:
            time.sleep(1)

def turnStr(word: str):
    wordfin = ""
    for x in range(len(word)):
        wordfin += word[len(word) - 1 - x]
    return wordfin


def lsame(fullword: str, partword: str, exact=True):
    matches = 0
    if not exact:
        fullword = fullword.lower()
        partword = partword.lower()
    for x, y in zip(fullword, partword):
        if x == y:
            matches += 1
    if matches == len(partword):
        return True
    else:
        return False


def rsame(fullword: str, partword: str, exact=True):
    matches = 0
    if not exact:
        fullword = fullword.lower()
        partword = partword.lower()
    fullwordX = turnStr(fullword)
    partwordX = turnStr(partword)
    for x, y in zip(fullwordX, partwordX):
        if x == y:
            matches += 1
    if matches == len(partword):
        return True
    else:
        return False




class TimerC:
    def __init__(self):
        self.starttime = 0
        self.stoptime = 0
        self.startpausetime = 0
        self.stoppausetime = 0
        self._time = 0
        self.Pause = 0
        self.curPause = 0
        self.startcurPause = 0
        self.startpausetimetmp = 0

        self.Running = False
        self.Paused = False
        self.End = False

    def start(self):
        self.reset()
        self.Running = True
        self.starttime = time.time()

    def stop(self):
        if self.Running:
            if self.Paused:
                self.unpause()
            self.stoptime = time.time()
            self.reload()
            self.End = True

    def pause(self):
        if not self.End:
            if not self.Paused:
                self.Paused = True
                self.startcurPause = time.time()
                self.startpausetimetmp = time.time()

    def unpause(self):
        if not self.End:
            if self.Paused:
                self.Paused = False
                self.startpausetime += self.startpausetimetmp
                self.stoppausetime += time.time()
                self.reload()
                self.curPause = 0
                self.startcurPause = 0

    def reset(self):
        self.starttime = 0
        self.stoptime = 0
        self.startpausetime = 0
        self.stoppausetime = 0
        self._time = 0
        self.Pause = 0
        self.curPause = 0
        self.startcurPause = 0
        self.startpausetimetmp = 0

        self.Running = False
        self.Paused = False
        self.End = False

    def switch(self):
        if not self.Paused:
            self.pause()
        else:
            self.unpause()

    def reload(self):

        if self.Paused:
            self.curPause = time.time() - self.startcurPause
        else:
            self.curPause = 0
            self.startcurPause = 0

        self.Pause = self.stoppausetime - self.startpausetime

        if self.End:
            self._time = self.stoptime - self.starttime - self.Pause
        else:
            self._time = time.time() - self.starttime - self.Pause - self.curPause

    def getTime(self):
        self.reload()
        return self._time

    time = property(getTime)

    def getTimeFor(self):
        self.reload()
        return TimeFor(self._time)

def TimeFor(Time):
    if (round(Time) % 60) == 0:
        output = "%s:%s%s" % (round(Time) // 60, 0, 0)
    elif (round(Time) % 60) < 10:
        output = "%s:%s%s" % (round(Time) // 60, 0, round(Time) % 60)
    else:
        output = "%s:%s" % (round(Time) // 60, round(Time) % 60)
    return output

def timeFormat_minsec(milsec, enMilsec=True, enSec=True, enMin=True, enHr=False, enDay=False, auto=True, units=True):
    """
    formats the time, given in milliseconds, parsed in str
    the parameters beginning with 'en' enables the output
    seconds, minutes, hours, days
    :param auto: this will automaticly decide, which ouput types will be activated

    :type milsec: int
    :type enMilsec: bool
    :type enSec: bool
    :type enMin: bool
    :type enHr: bool
    :type enDay: bool
    :type auto: bool
    :type units: bool

    :rtype: str
    :return: formatted time day:hr:min:sec:milsec
    """

    _milsec = milsec
    _sec = _milsec // 1000
    _mi = _sec // 60
    _hr = _mi // 60
    _day = _hr // 60

    milsec = _milsec % 1000
    sec = _sec % 60
    mi = _mi % 60
    hr = _hr % 24
    day = _day

    parse = ""

    if auto:
        if day:
            if units:
                parse += str(int(day)) + "d:"
            else:
                parse += str(int(day)) + ":"
        else:
            hr += day * 60
        if hr:
            if units:
                parse += str(int(hr)) + "h:"
            else:
                parse += str(int(hr)) + ":"
        else:
            mi += hr * 60
        if mi:
            if units:
                parse += str(int(mi)) + "m:"
            else:
                parse += str(int(mi)) + ":"
        else:
            sec += mi * 60
        if sec:
            if units:
                parse += str(sec) + "s:"
            else:
                parse += str(sec) + ":"
        else:
            milsec += sec * 60
        if milsec:
            if units:
                parse += str(int(milsec)) + "ms"
            else:
                parse += str(int(milsec))
    else:
        if enDay:
            if units:
                parse += str(int(day)) + "d:"
            else:
                parse += str(int(day)) + ":"
        else:
            hr += day * 60
        if enHr:
            if units:
                parse += str(int(hr)) + "h:"
            else:
                parse += str(int(hr)) + ":"
        else:
            mi += hr * 60
        if enMin:
            if units:
                parse += str(int(mi)) + "m:"
            else:
                parse += str(int(mi)) + ":"
        else:
            sec += mi * 60
        if enSec:
            if units:
                parse += str(int(sec)) + "s:"
            else:
                parse += str(int(sec)) + ":"
        else:
            milsec += sec * 60
        if enMilsec:
            if units:
                parse += str(int(milsec)) + "ms"
            else:
                parse += str(int(milsec))

    return parse


def timeFormat_sec(sec, enMilsec=True, enSec=True, enMin=True, enHr=False, enDay=False, auto=True, units=True):
    """
    formats the time, given in milliseconds, parsed in str
    the parameters beginning with 'en' enables the output
    seconds, minutes, hours, days
    :param auto: this will automaticly decide, which ouput types will be activated

    :type sec: float
    :type enMilsec: bool
    :type enSec: bool
    :type enMin: bool
    :type enHr: bool
    :type enDay: bool
    :type auto: bool
    :type units: bool

    :rtype: str
    :return: formatted time
    """

    _milsec = sec * 1000
    _sec = _milsec // 1000
    _mi = _sec // 60
    _hr = _mi // 60
    _day = _hr // 60

    milsec = _milsec % 1000
    sec = _sec % 60
    mi = _mi % 60
    hr = _hr % 24
    day = _day

    parse = ""

    if auto:
        if day:
            if units:
                parse += str(int(day)) + "d:"
            else:
                parse += str(int(day)) + ":"
        else:
            hr += day * 60
        if hr:
            if units:
                parse += str(int(hr)) + "h:"
            else:
                parse += str(int(hr)) + ":"
        else:
            mi += hr * 60
        if mi:
            if units:
                parse += str(int(mi)) + "m:"
            else:
                parse += str(int(mi)) + ":"
        else:
            sec += mi * 60
        if sec:
            if units:
                parse += str(int(sec)) + "s:"
            else:
                parse += str(int(sec)) + ":"
        else:
            milsec += sec * 60
        if milsec:
            if units:
                parse += str(int(milsec)) + "ms"
            else:
                parse += str(int(milsec))
    else:
        if enDay:
            if units:
                parse += str(int(day)) + "d:"
            else:
                parse += str(int(day)) + ":"
        else:
            hr += day * 60
        if enHr:
            if units:
                parse += str(int(hr)) + "h:"
            else:
                parse += str(int(hr)) + ":"
        else:
            mi += hr * 60
        if enMin:
            if units:
                parse += str(int(mi)) + "m:"
            else:
                parse += str(int(mi)) + ":"
        else:
            sec += mi * 60
        if enSec:
            if units:
                parse += str(int(sec)) + "s:"
            else:
                parse += str(int(sec)) + ":"
        else:
            milsec += sec * 60
        if enMilsec:
            if units:
                parse += str(int(milsec)) + "ms"
            else:
                parse += str(int(milsec))

    return parse


def timeFormat_min(mi, enMilsec=True, enSec=True, enMin=True, enHr=False, enDay=False, auto=True, units=True):
    """
    formats the time, given in milliseconds, parsed in str
    the parameters beginning with 'en' enables the output
    seconds, minutes, hours, days
    :param auto: this will automaticly decide, which ouput types will be activated

    :type mi: float
    :type enMilsec: bool
    :type enSec: bool
    :type enMin: bool
    :type enHr: bool
    :type enDay: bool
    :type auto: bool
    :type units: bool

    :rtype: str
    :return: formatted time
    """

    _milsec = mi * 60 * 1000
    _sec = _milsec // 1000
    _mi = _sec // 60
    _hr = _mi // 60
    _day = _hr // 60

    milsec = _milsec % 1000
    sec = _sec % 60
    mi = _mi % 60
    hr = _hr % 24
    day = _day

    parse = ""

    if auto:
        if day:
            if units:
                parse += str(int(day)) + "d:"
            else:
                parse += str(int(day)) + ":"
        else:
            hr += day * 60
        if hr:
            if units:
                parse += str(int(hr)) + "h:"
            else:
                parse += str(int(hr)) + ":"
        else:
            mi += hr * 60
        if mi:
            if units:
                parse += str(int(mi)) + "m:"
            else:
                parse += str(int(mi)) + ":"
        else:
            sec += mi * 60
        if sec:
            if units:
                parse += str(sec) + "s:"
            else:
                parse += str(sec) + ":"
        else:
            milsec += sec * 60
        if milsec:
            if units:
                parse += str(int(milsec)) + "ms"
            else:
                parse += str(int(milsec))
    else:
        if enDay:
            if units:
                parse += str(int(day)) + "d:"
            else:
                parse += str(int(day)) + ":"
        else:
            hr += day * 60
        if enHr:
            if units:
                parse += str(int(hr)) + "h:"
            else:
                parse += str(int(hr)) + ":"
        else:
            mi += hr * 60
        if enMin:
            if units:
                parse += str(int(mi)) + "m:"
            else:
                parse += str(int(mi)) + ":"
        else:
            sec += mi * 60
        if enSec:
            if units:
                parse += str(int(sec)) + "s:"
            else:
                parse += str(int(sec)) + ":"
        else:
            milsec += sec * 60
        if enMilsec:
            if units:
                parse += str(int(milsec)) + "ms"
            else:
                parse += str(int(milsec))

    return parse


def timeFormat_hr(hr, enMilsec=True, enSec=True, enMin=True, enHr=False, enDay=False, auto=True, units=True):
    """
    formats the time, given in milliseconds, parsed in str
    the parameters beginning with 'en' enables the output
    seconds, minutes, hours, days
    :param auto: this will automaticly decide, which ouput types will be activated

    :type hr: float
    :type enMilsec: bool
    :type enSec: bool
    :type enMin: bool
    :type enHr: bool
    :type enDay: bool
    :type auto: bool
    :type units: bool

    :rtype: str
    :return: formatted time
    """

    _milsec = hr * 60 * 60 * 1000
    _sec = _milsec // 1000
    _mi = _sec // 60
    _hr = _mi // 60
    _day = _hr // 60

    milsec = _milsec % 1000
    sec = _sec % 60
    mi = _mi % 60
    hr = _hr % 24
    day = _day

    parse = ""

    if auto:
        if day:
            if units:
                parse += str(int(day)) + "d:"
            else:
                parse += str(int(day)) + ":"
        else:
            hr += day * 60
        if hr:
            if units:
                parse += str(int(hr)) + "h:"
            else:
                parse += str(int(hr)) + ":"
        else:
            mi += hr * 60
        if mi:
            if units:
                parse += str(int(mi)) + "m:"
            else:
                parse += str(int(mi)) + ":"
        else:
            sec += mi * 60
        if sec:
            if units:
                parse += str(int(sec)) + "s:"
            else:
                parse += str(int(sec)) + ":"
        else:
            milsec += sec * 60
        if milsec:
            if units:
                parse += str(int(milsec)) + "ms"
            else:
                parse += str(int(milsec))
    else:
        if enDay:
            if units:
                parse += str(int(day)) + "d:"
            else:
                parse += str(int(day)) + ":"
        else:
            hr += day * 60
        if enHr:
            if units:
                parse += str(int(hr)) + "h:"
            else:
                parse += str(int(hr)) + ":"
        else:
            mi += hr * 60
        if enMin:
            if units:
                parse += str(int(mi)) + "m:"
            else:
                parse += str(int(mi)) + ":"
        else:
            sec += mi * 60
        if enSec:
            if units:
                parse += str(int(sec)) + "s:"
            else:
                parse += str(int(sec)) + ":"
        else:
            milsec += sec * 60
        if enMilsec:
            if units:
                parse += str(int(milsec)) + "ms"
            else:
                parse += str(int(milsec))

    return parse


def timeFormat_day(day, enMilsec=True, enSec=True, enMin=True, enHr=False, enDay=False, auto=True, units=True):
    """
    formats the time, given in milliseconds, parsed in str
    the parameters beginning with 'en' enables the output
    seconds, minutes, hours, days
    :param auto: this will automaticly decide, which ouput types will be activated

    :type day: float
    :type enMilsec: bool
    :type enSec: bool
    :type enMin: bool
    :type enHr: bool
    :type enDay: bool
    :type auto: bool
    :type units: bool

    :rtype: str
    :return: formatted time
    """

    _milsec = day * 24 * 60 * 60 * 1000
    _sec = _milsec // 1000
    _mi = _sec // 60
    _hr = _mi // 60
    _day = _hr // 60

    milsec = _milsec % 1000
    sec = _sec % 60
    mi = _mi % 60
    hr = _hr % 24
    day = _day

    parse = ""

    if auto:
        if day:
            if units:
                parse += str(int(day)) + "d:"
            else:
                parse += str(int(day)) + ":"
        else:
            hr += day * 60
        if hr:
            if units:
                parse += str(int(hr)) + "h:"
            else:
                parse += str(int(hr)) + ":"
        else:
            mi += hr * 60
        if mi:
            if units:
                parse += str(int(mi)) + "m:"
            else:
                parse += str(int(mi)) + ":"
        else:
            sec += mi * 60
        if sec:
            if units:
                parse += str(int(sec)) + "s:"
            else:
                parse += str(int(sec)) + ":"
        else:
            milsec += sec * 60
        if milsec:
            if units:
                parse += str(int(milsec)) + "ms"
            else:
                parse += str(int(milsec))
    else:
        if enDay:
            if units:
                parse += str(int(day)) + "d:"
            else:
                parse += str(int(day)) + ":"
        else:
            hr += day * 60
        if enHr:
            if units:
                parse += str(int(hr)) + "h:"
            else:
                parse += str(int(hr)) + ":"
        else:
            mi += hr * 60
        if enMin:
            if units:
                parse += str(int(mi)) + "m:"
            else:
                parse += str(int(mi)) + ":"
        else:
            sec += mi * 60
        if enSec:
            if units:
                parse += str(int(sec)) + "s:"
            else:
                parse += str(int(sec)) + ":"
        else:
            milsec += sec * 60
        if enMilsec:
            if units:
                parse += str(int(milsec)) + "ms"
            else:
                parse += str(int(milsec))

    return parse


def MusicType(mType, exact=False):
    if rsame(mType, "mp3"):
        if exact:
            return "mp3"
        else:
            return True
    elif rsame(mType, "mp4"):
        if exact:
            return "mp4"
        else:
            return True
    else:
        return False


def Search(searchkeyU, searchlistU, exact=False, lower=True, onlyOnce=True):

    if len(searchkeyU) == 0:
        return []

    if lower:
        searchkey = searchkeyU.lower()
        searchlist = []
        for x in searchlistU:
            searchlist.append(x.lower())
    else:
        searchkey = searchkeyU
        searchlist = []
        for x in searchlistU:
            searchlist.append(x)

    OutputNum = []

    for sListNum in range(len(searchlist)): # wort aus der liste
        if exact:
            if searchlist[sListNum] == searchkey:
                OutputNum.append(sListNum)
            else:
                continue
        if len(searchkey) > len(searchlist[sListNum]):
            continue  # suchwort größer als anderes wort (jetzt in der Liste)

        for letterNum in range(len(searchlist[sListNum])): # buchstabe aus wort aus der gesamt liste
            if searchlist[sListNum][letterNum] == searchkey[0]: # ist ein Buchstabe (aus der for-Schleife) auch in dem Suchwort[0] vorhanden?
                test = True

                for keyNum in range(len(searchkey)):
                    if test:
                        test = False
                        if keyNum == len(searchkey) - 1: # Fall: Wenn das Suchwort nur ein Buchstabe groß ist!
                            OutputNum.append(sListNum)
                            break
                        continue

                    # was macht das ?: wenn es der letzte buchstabe vom String ist ende
                    if len(searchlist[sListNum]) - 1 < keyNum + letterNum:
                        break
                    #if len(searchlist[sListNum]) - 1 < keyNum + letterNum:
                    #    print(OutputNum, sListNum, searchlist[sListNum], letterNum, searchlist[sListNum][letterNum], keyNum)

                    if searchlist[sListNum][keyNum + letterNum] == searchkey[keyNum]:
                        if keyNum == len(searchkey) - 1:

                            # if the keyword is two times in the fullword: this is a protect of duplication
                            doit = True
                            for NumOldList in OutputNum:
                                if NumOldList == sListNum:
                                    doit = False
                                    break

                            if doit:
                                OutputNum.append(sListNum)
                            break
                    else:
                        break

    if onlyOnce:
        OutputNum = DelDouble(OutputNum)


    return OutputNum


def DelDouble(workList: list):
    """
    deletes everything in the list which is multiple in the list

    :param workList: the list
    :return: new list
    """

    newList = []

    for x in workList:
        found=False
        for y in newList:
            if x == y:
                found=True
        if not found:
            newList.append(x)


    return newList


def SearchStr(searchkeyU: str, searchStrU: str, exact=False):

    if len(searchkeyU) == 0:
        return None

    if not exact:
        searchkey = searchkeyU.lower()
        searchlist = searchStrU.lower()
    else:
        searchkey = searchkeyU
        searchlist = searchStrU

    OutputNum = []


    for letterNum in range(len(searchlist)):
        if searchlist[letterNum] == searchkey[0]:
            test = False

            for keyNum in range(len(searchkey)):
                if test:
                    test = False
                    if keyNum == len(searchkey) - 1:
                        OutputNum.append(keyNum)
                        break
                    continue
                if len(searchlist) - 1 < keyNum + letterNum:
                    break

                if searchlist[keyNum + letterNum] == searchkey[keyNum]:
                    if keyNum == len(searchkey) - 1:
                        OutputNum.append(letterNum)
                        break
                else:
                    break

    return OutputNum

def unge(zahl):
    if type(zahl) != int:
        pass
    elif zahl/2 == int(zahl/2):
        return 0
    else:
        return 1

def getPartStr(word: str, begin: int, end: int):
    part = ""
    if len(word) < end or len(word) <= begin or begin >= end:
        return False

    for x in range(end):
        if x < begin:
            continue
        part += word[x]
    return part

def getPartStrToStr(word: str, endkey: str, beginkey="", exact=False):
    if exact:
        word = word.lower()
        endkey = endkey.lower()
    part = ""
    x = 0
    end = False
    beginskip = False
    beginover = False
    while True:
        if beginkey != "" and not beginover:
            z = 0
            for y in range(len(beginkey)):
                if word[x + y] == beginkey[y]:
                    z += 1
                else:
                    beginskip = True
                if z == len(beginkey):
                    beginover = True
                    x += z
            if beginskip:
                beginskip = False
                x += 1
                continue
        z = 0
        for y in range(len(endkey)):
            if word[x + y] == endkey[y]:
                z += 1
            else:
                break
            if z == len(endkey):
                end = True
                break
        if end:
            break
        part += word[x]
        x += 1

    return part

def randompw(returnpw=False, length=150, printpw=True, exclude=None):
    if exclude is None:
        exclude = []
    listx = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
             "V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p",
             "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "!",
             "§", "$", "%", "&", "/", "(", ")", "=", "?", "ß", "#", "'", "+", "*", "~", "ü", "ö", "ä", "-", "_", ".",
             ":", ",", ";", "{", "[", "]", "}", ">", "<", "|"]

    for x in exclude:
        for y in range(len(listx) - 1):
            if x == listx[y]:
                del listx[y]

    pw = ""

    for rx in range(length):
        pw += listx[random.randint(0, len(listx) - 1)]

    if returnpw:
        return pw

    if printpw:
        cls()
        print("Password: (length: %s) \n\n%s" % (length, pw))

        input()

