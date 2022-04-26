from dateutil.parser import parse


class nVisit:
    def __init__(self, start, end):
        self.start = parse(start)
        self.end = parse(end)
        self.date = self.start.date()

    def total_duration(self):
        time_between = self.end - self.start
        hours = time_between.total_seconds() / 60 / 60
        return(hours)

    def to_string(self):
        return "{} {}->{}".format(self.date.strftime("%d-%m-%Y"),
                                  self.start.astimezone().strftime("%H:%M"),
                                  self.end.astimezone().strftime("%H:%M"))
        # timezone is default UTC because it is from epoch timestamp,
        # calling .astimezone() without a parameter returns a datetime
        # with local timezone as described in
        # https://www.geeksforgeeks.org/python-datetime-astimezone-method/.


class registeredVisit:
    def __init__(self):
        self.sum = 0
        self.date = None
        self.part_shifts = []
        self.pause = 0

    def total_sum(self):
        return (self.part_shifts[-1][1] -
                self.part_shifts[0][0]).total_seconds() / 60 / 60

    def to_string(self):
        return "{} {}->{}".format(self.date.strftime("%d-%m-%Y"),
                                  self.part_shifts[0][0].strftime("%H:%M"),
                                  self.part_shifts[-1][1].strftime("%H:%M"))
        # .astimezone() is not needed here because the data from Quinyx is
        # shown in my local timezone. Todo: Add timezone data to the datetime
        # object, so you can change the timezone if needed later.
