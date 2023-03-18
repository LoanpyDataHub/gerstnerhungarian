"""
Create input file for loanpy
"""

from lexibank_gerstnerhungarian import Dataset as HNG
import epitran
from re import sub
from clldutils.misc import slug
import csv
from loanpy.help import find_optimal_year_cutoff
from io import StringIO
from lingpy.sequence.sound_classes import token2class
from ipatok import tokenise

epi = epitran.Epitran("hun-Latn").transliterate
ORIGINS =  ("Proto-Finno-Ugric", "Turkic", "unknown", "uncertain", "Proto-Ugric")

def get_clusters(segments):
    """
    Takes a list of phonemes and segments them into consonant and vowel
    clusters, like so: "abcdeaofgh" -> ["a", "bcd", "eao", "fgh"]
    """
    out = [segments[0]]
    for i in range(1, len(segments)):
        # can be optimized
        prev, this = token2class(segments[i-1], "cv"), token2class(
                segments[i], "cv")
        if prev == this:
            out[-1] += "."+segments[i]
        else:
            out += [segments[i]]
    return " ".join(out)

def segipa(w):
    w = sub("[†×∆\-¹²³⁴’ ]", "", w)
    return get_clusters(tokenise(epi(w)))

def clean(text):
    text = sub(r'[〈〉:;!,.?]', '', text)  # Remove special characters and punctuation
    text = sub(r'\s+', ' ', text)         # Replace multiple whitespaces with a single space
    text = text.strip()
    return text

def run(args):
    """
    Read raw file
    find the optimal year
    filter raw
    write results to new raw file
    """
    # Read TSV file content into a string
    with open("raw/Gerstner-2016-10176.tsv", "r") as f:
        tsv_string = f.read()

    optyear = find_optimal_year_cutoff(tsv_string, ORIGINS)
    lines = [["ID", "Entry_ID", "Segments", "Meaning"]]

    tsv_file = StringIO(tsv_string)
    reader = csv.reader(tsv_file, delimiter="\t")
    next(reader)  # Skip header row
    count = 0
    for i, row in enumerate(reader):
        if row[2] and int(row[2]) > optyear:  # filter years
            continue
        lines.append([count, f"{i + 1}-{slug(row[0])}", segipa(row[0]), clean(row[1])])
        count += 1
    # write csv
    with open("loanpy/hun.tsv", "w+", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerows(lines)
