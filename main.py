import json
from pathlib import Path
import os
import sys
import nwork
from lxml import etree
import datetime

DIRECTORY_REGISTERED = ("/home/nikolaj/Hentet/"
                        "DownloadedFilesForMapsTimelineWork/"
                        "files-for-timeline")
file_paths_timeline = []

DIRECTORY_TIMELINE = ("/home/nikolaj/Hentet/"
                      "DownloadedFilesForMapsTimelineWork/"
                      "SemanticLocationHistory")
file_paths_registered = []

DAY_NAMES = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag",
             "lørdag", "søndag"]

workplace_name = "Burger King"

if not os.path.exists(DIRECTORY_TIMELINE):
    sys.exit()

print("Listing files holding registered data")

for folder in os.listdir(DIRECTORY_TIMELINE):
    folder_path = Path(DIRECTORY_TIMELINE, folder)
    for file in os.listdir(folder_path):
        if not file.endswith((".json")):
            continue
        file_path = Path(folder_path, file)
        file_paths_timeline.append(file_path)

visits_timeline = []

print("Try to get information from JSON files.\n"
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
            visits_timeline.append(nvisit)

print("Succesfully got data from JSON.\n"
      "Showing a bit of information gathered...\n")

sum = 0

for visit in visits_timeline:
    sum += visit.duration()

print("Hours spent at work {0:.2f}".format(sum))

print()
print("Finding files holding registered data...\n")

for file in os.listdir(DIRECTORY_REGISTERED):
    file_path = Path(DIRECTORY_REGISTERED, file)

    if not file.endswith((".html")):
        continue

    file_paths_registered.append(file_path)

file_paths_registered.sort()

print("Getting registered work attests from Quinyx...\n")
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
                "/html/body/div/div/div/div/div[2]/div[2]/div/div[2]/div[2]/"
                "div/div/div[{}]/div/div[1]".format(i))
            text = text[0].text

            if text.lower() == "uge":
                continue

            text_list = text.split(", ")
            if text_list[0].lower() in DAY_NAMES:
                if visit is not None:
                    visits_registered.append(visit)
                day, month, year = map(int, text_list[1].split('.'))
                visit = nwork.registeredVisit()
                visit.date = datetime.datetime(year, month, day)
                continue

            if visit is not None:
                start_hour, start_minute = map(int,
                                               text.split(" - ")[0].split(':'))
                end_hour, end_minute = map(int,
                                           text.split(" - ")[1].split(':'))

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

sum = 0

for visit in visits_registered:
    sum += visit.sum

print("Hours registered at work {0:.2f}\n".format(sum))


print("Exiting...")
