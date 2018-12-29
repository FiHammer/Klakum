import time


class ServerPortUsed(Exception):
    def __init__(self, port):
        print("The port: %s is already used, please use another one!" % port)


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


def TimeFor(Time):
    if (round(Time) % 60) == 0:
        TimeFor = "%s:%s%s" % (round(Time) // 60, 0, 0)
    elif (round(Time) % 60) < 10:
        TimeFor = "%s:%s%s" % (round(Time) // 60, 0, round(Time) % 60)
    else:
        TimeFor = "%s:%s" % (round(Time) // 60, round(Time) % 60)
    return TimeFor


class TimerC:
    def __init__(self):
        self.starttime = 0
        self.stoptime = 0
        self.startpausetime = 0
        self.stoppausetime = 0
        self.Time = 0
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
        self.Time = 0
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
            self.Time = self.stoptime - self.starttime - self.Pause
        else:
            self.Time = time.time() - self.starttime - self.Pause - self.curPause

    def getTime(self):
        self.reload()
        return self.Time

    def getTimeFor(self):
        self.reload()
        return TimeFor(self.Time)