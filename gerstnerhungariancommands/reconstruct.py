"""
Add reconstructions to hun.tsv
"""

from loanpy.apply import Adrc

BANNED = ("wrong clusters", "wrong phonotactics", "not old",
"wrong vowel harmony")

def run(args):
    """
    Read raw file
    find the optimal year
    filter raw
    write results to new raw file
    """
    # Read in data on correspondences and inventories
    rc = Adrc(
    "../ronataswestoldturkic/loanpy/H2EAHsc.json",
    "../ronataswestoldturkic/loanpy/invsEAH.json"
    )
    # Read TSV file content into a string
    with open("loanpy/hun.tsv", "r") as f:
        huntsv = f.read().strip().split("\n")
    lines = huntsv.pop(0) + "\t" + "reconstructed"

    # Add reconstructions to new column
    for row in huntsv:
        reconstructed = rc.reconstruct(row.split("\t")[2], 100)
        if any(i in reconstructed for i in BANNED):
            continue
        lines += "\n" + row + "\t" + reconstructed

    # write csv
    with open("loanpy/rchun.tsv", "w+") as file:
        file.write(lines)
