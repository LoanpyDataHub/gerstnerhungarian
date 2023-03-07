"""
IPA-transcribe Hungarian words
"""

from lexibank_gerstnerhungarian import Dataset as HNG
from ipatok import tokenise
import epitran
from re import sub

epi = epitran.Epitran("hun-Latn").transliterate

def segipa(w):
    return ' '.join(tokenise(epi(w)))

def run(args):
    """
    Read values from forms.csv and IPA-transcribe the Spanish ones
    """
    hng = HNG()
    #ds = Dataset.from_metadata("./cldf/cldf-metadata.json")
    lines = "Grapheme\tIPA"
    wrdlst = []
    for row in hng.cldf_dir.read_csv("forms.csv")[1:]:
        row[4] = sub("[†×∆\-¹²³⁴’ ]", "", row[4])
        if row[4] not in wrdlst:
            lines += f"\n^{row[4]}$\t{segipa(row[4])}"
            wrdlst.append(row[4])

    # write csv
    with open(hng.etc_dir / "orthography.tsv", "w+") as file:
        file.write(lines)
