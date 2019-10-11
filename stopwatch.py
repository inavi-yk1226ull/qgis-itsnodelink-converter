from datetime import datetime, timedelta


class Stopwatch:
    def __init__(self):
        self.start = datetime.now()
        self.checkPointStart = datetime.now()
        self.minusTime = timedelta()

    def PrintText(self, elapsed):
        sec = elapsed.seconds
        msec = elapsed.microseconds

        ret = ''
        if sec > 60:
            ret += '{}m '.format(int(sec / 60))
        ret += '{}s {}'.format(sec % 60, str(int(msec/1000)).zfill(3))
        return ret

    def GetTotal(self):
        elapsed = datetime.now() - self.start - self.minusTime
        return self.PrintText(elapsed)

    def CheckPoint(self):
        current = datetime.now()
        elapsed = current - self.checkPointStart
        self.checkPointStart = current
        return self.PrintText(elapsed)

    def SaveExTime(self):
        current = datetime.now()
        elapsed = current - self.checkPointStart
        self.checkPointStart = current
        self.minusTime = self.minusTime + elapsed
