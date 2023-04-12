"""
Filter ``cldf/entries.csv`` according to year or first appearance and
etymological origin. Run ``cldfbench gerstnerhungarian.filter --help``
for help.
"""
import csv
import re

from clldutils.misc import slug
from loanpy.utils import find_optimal_year_cutoff, IPA

ORIGINS = ("Proto-Uralic", "Proto-Finno-Ugric", "Proto-Ugric",
           "Turkic", "unknown", "uncertain")

def find_empty(senses_file):
    """
    Loop through ``cldf/senses.csv`` and add ``Entry_ID`` to list if ``Spacy``
    empty.
    """
    empty_keys = set()
    with open(senses_file, 'r') as f:
        senses = list(csv.reader(f))
        h = {i: senses[0].index(i) for i in senses[0]}
        for row in senses:
            if not row[h["Spacy"]]:
                empty_keys.add(row[h["Entry_ID"]])

    return empty_keys

def add_all_etymologies(entries, h):
    """
    Loop through column ``Etymology`` in ``entries.csv`` and return a set
    of all possible etymologies.
    """
    etym = set()
    for row in entries:
        if row[h["Etymology"]]:
            etym.add(row[h["Etymology"]])
    return etym

def register(parser):
    """
    Register arguments for the run-function. Three optional flags: -y -o -a.
    An integer after -y indicates the year above which words are filtered out.
    The string after -o indicates the etymological origins the words in the
    output should belong to. If -a is toggled on, words with missing data
    will be included in the output.
    """
    parser.add_argument("-y", "--cutoff-year", dest="cutoff_year", nargs="?",
        default=None, help="Higher years will be filtered out")
    parser.add_argument("-o", "--etymology", dest="etymology", nargs="?",
        default=None, help="Etymological origins to keep")
    parser.add_argument("-a", "--add-empty", dest="add_empty",
        action="store_true", help="Adds word with missing information about \
year of first appearance or etymological origin if toggled on")


def run(args):
    """
    #. Read ``cldf/entries.csv``
    #. Filter according to year of first appearance, etymological origin,
       and missing data.
    #. write results to ``loanpy/hun{year}{etymology}.tsv``
    """

    # Read entries content
    with open("cldf/entries.csv", "r") as f:
        entries = list(csv.reader(f))
    h = {i: entries[0].index(i) for i in entries[0]}

    filename = args.etymology
    if not args.cutoff_year:
        args.cutoff_year = find_optimal_year_cutoff(entries, ORIGINS)
    if not args.etymology:
        args.etymology = add_all_etymologies(entries, h)
        filename = "all"

    # create entries
    entries_filtered = [["ID", "EntryID", "Year", "Etymology"]]
    empty_keys = find_empty("cldf/senses.csv")
    i = 0
    for row in entries[1:]:
        if row[h["ID"]] not in empty_keys:
            if row[h["Year"]] and row[h["Etymology"]]:
                if int(row[h["Year"]]) < int(args.cutoff_year):
                    if row[h["Etymology"]] in args.etymology:
                        entries_filtered.append(
                            [str(i) + "-" + row[h["ID"]], row[h["ID"]],
                             row[h["Year"]], row[h["Etymology"]]]
                            )
            elif args.add_empty:
                entries_filtered.append(
                        [str(i) + "-" + row[h["ID"]], row[h["ID"]],
                        row[h["Year"]], row[h["Etymology"]]]
                        )

            i += 1


    with open(f"loanpy/hun{args.cutoff_year}{filename}.tsv", "w+",
            newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(entries_filtered)
