from dateutil.parser import parse


class nVisit:
    def __init__(self, start, end):
        self.start = parse(start)
        self.end = parse(end)

    def duration(self):
        time_between = self.end - self.start
        hours = time_between.total_seconds() / 60 / 60
        return(hours)
