"""
Create input file for loanpy
"""
import csv
import re

from clldutils.misc import slug
from epitran import Epitran
from ipatok import tokenise
from loanpy.utils import find_optimal_year_cutoff, IPA

ORIGINS = ("Proto-Finno-Ugric", "Turkic", "unknown", "uncertain", "Proto-Ugric")

def find_empty(senses_file):
    """
    Loop through cldf/senses.csv and add Entry_ID to list if Spacy empty.
    """
    empty_keys = set()
    with open(senses_file, 'r') as f:
        senses = list(csv.reader(f))
        h = {i: senses[0].index(i) for i in senses[0]}
        for row in senses:
            if not row[h["Spacy"]]:
                empty_keys.add(row[h["Entry_ID"]])

    return empty_keys

def register(parser):
    parser.add_argument("cutoff_year", nargs="?")

def run(args):
    """
    Read raw file
    find the optimal year
    filter raw
    write results to new raw file
    """

    # Read entries content
    with open("cldf/entries.csv", "r") as f:
        entries = list(csv.reader(f))
    h = {i: entries[0].index(i) for i in entries[0]}

    if not args.cutoff_year:
        args.cutoff_year = find_optimal_year_cutoff(entries, ORIGINS)
    # create entries
    entries_filtered = [["ID", "EntryID", "Year", "Etymology"]]
    empty_keys = find_empty("cldf/senses.csv")
    i = 0
    for row in entries[1:]:
        if row[h["ID"]] not in empty_keys and row[h["Year"]]:
            if int(row[h["Year"]]) < int(args.cutoff_year):
                entries_filtered.append(
                    [str(i) + "-" + row[h["ID"]], row[h["ID"]],
                     row[h["Year"]], row[h["Etymology"]]]
                    )
                i += 1

    with open(f"loanpy/hun{args.cutoff_year}.tsv", "w+", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(entries_filtered)
