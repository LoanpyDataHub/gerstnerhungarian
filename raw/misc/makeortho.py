"""cd to folder `misc` and run `python makeortho.py` from terminal"""

from pathlib import Path
import re

import epitran
import pandas as pd
from ipatok import tokenise

epi = epitran.Epitran("hun-Latn").transliterate


def segment(word): return ' '.join(tokenise(epi(word)))


def main():
    """creates othography.tsv with Graphemes 2 IPA mappings"""

    # create orthography.tsv
    in_path = Path.cwd().parent.parent / "cldf" / "forms.csv"
    out_path = Path.cwd().parent.parent / "etc" / "orthography.tsv"
    df = pd.read_csv(in_path, usecols=["Form"])\
      .assign(IPA=lambda x: list(map(segment, x.Form)))\
      .rename(columns={"Form": "Grapheme"})\
      .drop_duplicates()

     # bugfix
    df["Grapheme"] = ["^" + i + "$" for i in df["Grapheme"]]

    df.to_csv(out_path, index=False, encoding="utf-8", sep="\t")



if __name__ == "__main__":
    main()
