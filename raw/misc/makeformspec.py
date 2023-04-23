"""
#. Read raw file
#. Create empty dictionary for formspec
#. Loop through rows
#. If a word ends on -ik: add it as dictionary key.
   Value is the word without -ik
#. Write the dictionary to json
"""

import csv
import json
import re

PLIST = ["dozik$", "kodik$", "kedik$", "kozik$", "ködik$",
         "odik$", "ődik$", "ozik$", "edik$", "ödik$", "ázik$", "ezik$",
         "edik$", "ödik$", "ődik$", "ozik$", "ik$"]

with open("../Gerstner-2016-10176.tsv", "r") as f:
    dfraw = list(csv.reader(f, delimiter="\t"))

formspec = {}

for row in dfraw:
    row0cln = re.sub("†×∆-¹²³⁴’ ", "", row[0])
    #print(row0cln)
    if bool(re.findall("|".join(PLIST), row0cln)):
        if row0cln not in ["antik", "bolsevik"]:
            formspec[row[0]] = re.sub("|".join(PLIST), "", row0cln)

with open("../../etc/formspec.json", "w+") as f:
    json.dump(formspec, f)
