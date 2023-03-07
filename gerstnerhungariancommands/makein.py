"""
Create input file for loanpy
"""

from lexibank_gerstnerhungarian import Dataset as HNG
from ipatok import tokenise
import epitran
from re import sub
from clldutils.misc import slug

epi = epitran.Epitran("hun-Latn").transliterate

def segipa(w):
    w = sub("[†×∆\-¹²³⁴’ ]", "", w)
    return ' '.join(tokenise(epi(w)))

def cln(w):
    #TODO: clean so vector coverage is higher
    return w

def run(args):
    """
    Read values from forms.csv and IPA-transcribe the Spanish ones
    """
    hng = HNG()
    #ds = Dataset.from_metadata("./cldf/cldf-metadata.json")
    lines = "Segments\tMeaning\tEntry_ID"
    with open("raw/Gerstner-2016-10176.tsv", "r") as f:
        for i, row in enumerate(f.read().split("\n")[1:][:-1]):
            row = row.split("\t")
            lines += f"\n{segipa(row[0])}\t{cln(row[1])}\t{str(i+1)}-{slug(row[0])}"

    # write csv
    with open("loanpy/hun.tsv", "w+") as file:
        file.write(lines)
