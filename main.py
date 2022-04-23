from __future__ import with_statement
import json
from pathlib import Path
import os
import sys
import nwork
from lxml import etree

directory_registered = ("/home/nikolaj/Hentet/"
                        "DownloadedFilesForMapsTimelineWork/"
                        "files-for-timeline")
file_paths_timeline = []

directory_timeline = ("/home/nikolaj/Hentet/"
                      "DownloadedFilesForMapsTimelineWork/"
                      "SemanticLocationHistory")
file_paths_registered = []

workplace_name = "Burger King"

if not os.path.exists(directory_timeline):
    sys.exit()

print("Listing files holding registered data")

for folder in os.listdir(directory_timeline):
    folder_path = Path(directory_timeline, folder)
    for file in os.listdir(folder_path):
        if not file.endswith((".json")):
            continue
        file_path = Path(folder_path, file)
        file_paths_timeline.append(file_path)

visits_timeline = []

print("Try to get information from JSON files")
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

sum = 0

for visit in visits_timeline:
    sum += visit.duration()

print("Hours spent at work {0:.2f}".format(sum))

print()
print("Listing files holding registered data")

for file in os.listdir(directory_registered):
    file_path = Path(directory_registered, file)

    if not file.endswith((".html")):
        continue

    file_paths_registered.append(file_path)

for file_path in file_paths_registered:
    with open(file_path, 'r') as file:
        parser = etree.HTMLParser()
        tree = etree.parse(file, parser)

        trial_amount = len(tree.xpath(
            "/html/body/div/div/div/div/div[2]/div[2]/div/div[2]/div[2]/"
            "div/div/div"))

        for i in range(2, trial_amount):
            text = tree.xpath(
                "/html/body/div/div/div/div/div[2]/div[2]/div/div[2]/div[2]/"
                "div/div/div[{}]/div/div[1]".format(i))

            print(text[0].text)

print("Exiting")
