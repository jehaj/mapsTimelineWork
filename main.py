import json
import locale
from pathlib import Path
import os
import sys
import nwork
from lxml import etree
import datetime


def get_visits_html():
    visits_registered = []
    for file_path in file_paths_registered:
        with open(file_path, 'r') as file:
            parser = etree.HTMLParser()
            tree = etree.parse(file, parser)

            trial_amount = len(tree.xpath(
                "/html/body/div/div/div/div/div[2]/div[2]/div/div[2]/div[2]/"
                "div/div/div"))

            visit = None

            for i in range(2, trial_amount+1):
                text = tree.xpath(
                    "/html/body/div/div/div/div/div[2]/div[2]/div/div[2]"
                    "/div[2]/div/div/div[{}]/div/div[1]".format(i))
                text = text[0].text

                if text.lower() == "uge":
                    continue

                text_list = text.split(", ")
                if text_list[0].lower() in DAY_NAMES:
                    if visit is not None:
                        visits_registered.append(visit)
                    day, month, year = map(int, text_list[1].split('.'))
                    visit = nwork.registeredVisit()
                    visit.date = datetime.date(year, month, day)
                    continue

                if visit is not None:
                    start_hour, start_minute = map(int,
                                                   text.split(" - ")[0]
                                                       .split(':'))
                    end_hour, end_minute = map(int,
                                               text.split(" - ")[1]
                                                   .split(':'))

                    start_time = datetime.time(start_hour, start_minute)
                    end_time = datetime.time(end_hour, end_minute)

                    start_datetime = datetime.datetime.combine(visit.date,
                                                               start_time)
                    end_datetime = datetime.datetime.combine(visit.date,
                                                             end_time)

                    visit.part_shifts.append([start_datetime, end_datetime])
                    duration = end_datetime - start_datetime
                    visit.sum += duration.total_seconds() / 60 / 60

            if visit is not None:
                visits_registered.append(visit)

    return visits_registered


def get_visits_json():
    visits_registered = []
    for file_path in file_paths_registered:
        with open(file_path, 'r') as file:
            file_json = json.load(file)
            punches = file_json["punches"]
            prev_date = None
            visit = None
            for i in range(len(punches)):
                punch = punches[i]
                punch_start = datetime.datetime.strptime(punch["punchStart"],
                                                         "%Y-%m-%d %H:%M:%S")
                punch_end = datetime.datetime.strptime(punch["punchEnd"],
                                                       "%Y-%m-%d %H:%M:%S")

                if prev_date != punch_start.date():
                    prev_date = punch_start.date()

                    visit = nwork.registeredVisit()
                    visit.date = punch_start.date()
                    visit.part_shifts.append([punch_start, punch_end])

                    visits_registered.append(visit)
                else:
                    visit.part_shifts.append([punch_start, punch_end])
                duration = punch_end - punch_start
                visit.sum += duration.total_seconds() / 60 / 60

    return visits_registered


DIRECTORY_REGISTERED = ("/home/nikolaj/Downloads/"
                        "DownloadedFilesForMapsTimelineWork/"
                        "QuinyxFærdigJSON")
file_paths_timeline = []

DIRECTORY_TIMELINE = ("/home/nikolaj/Downloads/"
                      "DownloadedFilesForMapsTimelineWork/"
                      "FærdigMapsTimeline")
file_paths_registered = []

OVERRIDE_FILE_PATH = "override_dates.json"

LOCALE = "da"

DAY_NAMES_DA = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag",
                "lørdag", "søndag"]
DAY_NAMES_EN = ["monday", "tuesday", "wednesday", "thursday", "friday",
                "saturday", "sunday"]
DAY_NAMES = DAY_NAMES_DA

MONTH_NAMES_DA = ["januar", "februar", "marts", "april", "maj", "juni", "juli",
                  "august", "september", "oktober", "november", "december"]
MONTH_NAMES_EN = ["january", "february", "march", "april", "may", "june",
                  "july", "august", "september", "oktober", "november",
                  "december"]
MONTH_NAMES = MONTH_NAMES_DA

workplace_name = "Burger King"

# is_pause_paid = False

# Minimum length of a visit to be counted
minimum_hours = 1

if (not os.path.exists(DIRECTORY_TIMELINE) or
        not os.path.exists(DIRECTORY_REGISTERED)):
    print("Cannot find folders at:")
    print("\t{}".format(DIRECTORY_TIMELINE))
    print("\t{}".format(DIRECTORY_REGISTERED))
    sys.exit()

days = {}
if (os.path.exists("override_dates.json")):
    with open("override_dates.json", 'r') as file:
        days = json.load(file)

print("Listing files holding registered data")

for folder in os.listdir(DIRECTORY_TIMELINE):
    folder_path = Path(DIRECTORY_TIMELINE, folder)
    for file in os.listdir(folder_path):
        if not file.endswith((".json")):
            continue
        file_path = Path(folder_path, file)
        file_paths_timeline.append(file_path)

# locale.setlocale(locale.LC_ALL, 'en_GB.utf8')
print("Sorting using {} locale.".format(locale.getlocale()))
file_paths_timeline.sort(
    key=lambda x: datetime.datetime.strptime(
        x.parts[-1].split('.')[0], "%Y_%B"
    )
)

visits_timeline = []

print("Try to get information from (Google Maps Timeline) JSON files.\n"
      "...")
for file_path in file_paths_timeline:
    with open(file_path, 'r') as file:
        file_json = json.load(file)
        root = file_json["timelineObjects"]
        for i in range(len(root)):
            if "placeVisit" not in root[i]:
                continue
            if not root[i]["placeVisit"]["location"]["name"] == workplace_name:
                continue
            timestamps = root[i]["placeVisit"]["duration"]
            start = timestamps["startTimestamp"]
            end = timestamps["endTimestamp"]
            nvisit = nwork.nVisit(start, end)
            if nvisit.total_duration() < minimum_hours:
                continue
            visits_timeline.append(nvisit)

print("Succesfully got data from JSON.\n"
      "Showing a bit of information gathered...\n")

total_hours_registered = 0

for visit in visits_timeline:
    total_hours_registered += visit.total_duration()

# Statistic analysis on shift length / average time spent at work
visits_duration = [x.total_duration() for x in visits_timeline]
visits_duration.sort()

print("Average shift is {:.2f} hours.".format(
    sum(visits_duration)/len(visits_duration)))
print()

# print visits_timeline to text file
with open("vagter.txt", "w") as file:
    for visit in visits_timeline:
        write_string = visit.to_string()
        file.write("{}\n".format(write_string))

print("Hours spent at work {0:.2f}.".format(total_hours_registered))
print("Note that this includes pauses.")

print()
print("Finding files holding registered data...\n")

for file in os.listdir(DIRECTORY_REGISTERED):
    file_path = Path(DIRECTORY_REGISTERED, file)

    if file.endswith((".json")):
        file_paths_registered.append(file_path)

file_paths_registered.sort()

# [print(str(x)) for x in file_paths_registered]
# print()

print("Getting registered work attests from Quinyx...\n")
# visits_registered = get_visits_html()
visits_registered = get_visits_json()

total_hours_registered = 0

for visit in visits_registered:
    total_hours_registered += visit.sum

print("Hours registered at work {0:.2f}\n".format(total_hours_registered))
print("Note this does not include pauses. Only hours clocked in.")

# Calculate pause time for a given day
total_pause = 0
for visit in visits_registered:
    if len(visit.part_shifts) > 1:
        pause = 0
        for i in range(1, len(visit.part_shifts)):
            pause += (visit.part_shifts[i][0] -
                      visit.part_shifts[i-1][1]).total_seconds() / 60 / 60
        total_pause += pause
        visit.pause = pause

print("You have had {:.2f} hours of pause.".format(total_pause))
print("Shifts including unpaid pauses total to {:.2f} hours."
      .format(total_hours_registered+total_pause))

print()
print("Amount of visits to {}: {:>13}".format(
    workplace_name,
    len(visits_timeline)))
print("Amount of registered shifts at {}: {}".format(
    workplace_name,
    len(visits_registered)))

print()
print("Finding dates that does not match:")

for i in range(0, len(visits_registered)):
    quinyxVisit = visits_registered[i]
    quinyxDate = quinyxVisit.date
    myList = []
    for n in range(0, len(visits_registered)):
        visit = visits_registered[n]
        date = visit.date
        if quinyxDate == date:
            myList.append([date, i, n])
    if len(myList) > 1:
        print("help")
        print(myList)

total_difference = 0
for visit in visits_timeline:
    # find same date in registered shift
    registered_shift = [x for x in visits_registered if x.date == visit.date]
    if not registered_shift or not registered_shift[0]:
        continue
    if len(registered_shift) > 1:
        print("Error: too many shifts in one day {}"
              .format(str(registered_shift)))
    registered_shift = registered_shift[0]
    difference = abs(visit.total_duration() - registered_shift.total_sum())
    if difference > 0.5:
        total_difference += difference
        print("Day {} does not add up. Difference is {:.2f} hours"
              .format(str(visit.date), difference))
        print("Timeline says {:>24}".format(visit.to_string()))
        print("Quinyx says {:>26}".format(registered_shift.to_string()))
        print()

print("Total difference is {:.2f} hours".format(total_difference))

print("Trying to calculate if hours reported by Quinyx "
      "match those on the pay check")

month_hours = {}
current_month_name = ""
for visit in visits_registered:
    date = visit.date.day
    month_index = visit.date.month-1
    month_name = MONTH_NAMES[month_index]

    if date <= 15 and current_month_name == "":
        current_month_name = MONTH_NAMES[month_index]
    elif date > 15 and current_month_name == "":
        current_month_name = MONTH_NAMES[(month_index+1) % 12]

    if date > 15 and (month_name != current_month_name or
                      month_name != MONTH_NAMES[month_index-1]):
        current_month_name = MONTH_NAMES[(month_index+1) % 12]

    if month_hours.get(current_month_name) is None:
        month_hours[current_month_name] = 0
    month_hours[current_month_name] += visit.sum

for key, value in month_hours.items():
    print("Month, {:<8}, reports {:>6.2f} hours.".format(key, value))

print()

print("Same as above, but hours are from timeline:")
month_hours = {}
current_month_name = ""
for visit in visits_timeline:
    date = visit.date.day
    month_index = visit.date.month-1
    month_name = MONTH_NAMES[month_index]

    if date <= 15 and current_month_name == "":
        current_month_name = MONTH_NAMES[month_index]
    elif date > 15 and current_month_name == "":
        current_month_name = MONTH_NAMES[(month_index+1) % 12]

    if date > 15 and (month_name != current_month_name or
                      month_name != MONTH_NAMES[month_index-1]):
        current_month_name = MONTH_NAMES[(month_index+1) % 12]

    if month_hours.get(current_month_name) is None:
        month_hours[current_month_name] = 0
    month_hours[current_month_name] += visit.total_duration() - \
        visit.pause_length()

for key, value in month_hours.items():
    print("Month, {:<8}, reports {:>6.2f} hours.".format(key, value))
print()

print("Following days pauses are exceeding normal length "
      "(30 minutes ~ 5 minutes leeway):")

for x in [x for x in visits_registered if x.pause > 0.5833]:
    pause_text = ""
    for i in range(1, len(x.part_shifts)):
        prev_part_shift = x.part_shifts[i-1]
        part_shift = x.part_shifts[i]

        pause_text += "{} to {}".format(prev_part_shift[1], part_shift[0])
        if i < len(x.part_shifts)-1:
            pause_text += " and "

    print("Quinyx reports {}".format(pause_text))

print()

print("Exiting...")
