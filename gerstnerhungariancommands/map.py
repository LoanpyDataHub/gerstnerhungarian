"""
Map concepts to concepticon and make a wordlist.
"""
from lexibank_gerstnerhungarian import Dataset as SG
from cldfbench.cli_util import add_catalog_spec
from pycldf import Dataset
from collections import defaultdict
from pysem.glosses import to_concepticon
from tabulate import tabulate
from clldutils.clilib import Table, add_format


def register(parser):
    """
    Register optional arguments
    """
    add_catalog_spec(parser, 'concepticon')
    add_format(parser, default="simple")
    parser.add_argument("--conceptlist", default="Dellert-2018-1016")
    parser.add_argument("--language", default="de")

def run(args):
    """
    Filter raw data according to whether it occurs in the concept list called
    "Dellert-2018-1016", which was specified in ``metadata.json`` after
    creating the repository with the ``cldfbench new`` command. The concept
    list is fetched through concepticon's API. Note that this script only
    functions after a conversion to CLDF was already successful. This is
    because the input is ``cldf/senses.csv``, which was created during the
    cldf-conversion. The senses in that table are automatically mapped to
    concepticon with the `pyesm <https://pypi.org/project/pysem/>`_ package.
    The output file is written to ``raw/wordlist.tsv``.
    """
    clist = {c.concepticon_id: c for c in
            args.concepticon.api.conceptlists[args.conceptlist].concepts.values()
            if c.concepticon_gloss}
    sg = SG()
    ds = Dataset.from_metadata(
            sg.cldf_dir.joinpath("Dictionary-metadata.json"))
    mapped = defaultdict(list)
    entries = defaultdict(list)

    for sense in ds.objects("SenseTable"):
        try:
            entry = sense.entries[0]
        except KeyError:  # https://github.com/cldf/cldfbench/issues/86
            continue
        entries[entry.cldf.headword] += [sense.cldf.description]
        pos = entry.cldf.partOfSpeech.split(",")[0] if entry.cldf.partOfSpeech else ""
        maps = to_concepticon([{"gloss": sense.cldf.description, "pos_ref":
            pos}], language=args.language)
        if maps[sense.cldf.description]:
            cid, cgl, _, score = maps[sense.cldf.description][0]
            if cid in clist:
                mapped[cid, cgl] += [[
                    sense.id,
                    sense.cldf.description,
                    entry.cldf.headword]]
    table = []
    visited = set()
    for k, values in mapped.items():
        for sense_id, sense, form in values:
            table += [[k[0], k[1], form, "; ".join(entries.get(form, [""])), sense, sense_id]]
        visited.add(k[0])
    for idx, concept in clist.items():
        if idx not in visited:
            table += [[idx, concept.concepticon_gloss, "", "", "", ""]]
    with Table(args, "ID", "CONCEPTICON_ID", "CONCEPTICON_GLOSS",
            "FORM", "MEANING", "SENSE", "SENSE_ID") as tbl:
        for i, row in enumerate(sorted(table, key=lambda x: x[1])):
            tbl.append([i+1]+row)
    with open(sg.raw_dir / "wordlist.tsv", "w") as f:
        f.write("\t".join(["ID", "CONCEPTICON_ID", "CONCEPTICON_GLOSS",
            "FORM", "MEANING", "SENSE", "SENSE_ID"])+"\n")
        for i, row in enumerate(sorted(table, key=lambda x: x[1])):
            f.write(str(i+1)+"\t"+"\t".join(row)+"\n")
