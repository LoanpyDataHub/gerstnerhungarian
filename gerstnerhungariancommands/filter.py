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

def register(parser):
    parser.add_argument("cutoff_year", nargs="?")

def run(args):
    """
    Read raw file
    find the optimal year
    filter raw
    write results to new raw file
    """
    # Read table content
    with open("cldf/entries.csv", "r") as f:
        table = list(csv.reader(f))
    h = {i: table[0].index(i) for i in table[0]}

    if not args.cutoff_year:
        args.cutoff_year = find_optimal_year_cutoff(table, ORIGINS)
        print("Optmal cutoff year is ", args.cutoff_year)
    # create table
    newtable = [["ID", "EntryID", "Segments", "Meaning"]]
    i = 0
    for row in table[1:]:
        if row[h["Spacy"]] and row[h["Year"]]:
            if int(row[h["Year"]]) < int(args.cutoff_year):
                newtable.append(
                    [i, row[h["ID"]], row[h["Segments"]], row[h["Spacy"]]]
                    )
                i += 1

    with open("loanpy/hun0.tsv", "w+", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(newtable)
