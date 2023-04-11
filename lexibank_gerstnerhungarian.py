"""
lexibank script to convert data to CLDF standard
"""

from collections import defaultdict
from functools import lru_cache
import json
import pathlib
import re

import attr
from clldutils.misc import slug
from epitran import Epitran
from lingpy.sequence.sound_classes import ipa2tokens
from loanpy.utils import IPA
from loanpy.scapplier import Adrc
from pylexibank import Dataset as BaseDataset, FormSpec, Lexeme
import pylexibank
from cldfbench import CLDFSpec
import spacy

REP = [(x, "") for x in "†×∆-¹²³⁴’"]
# install first with $ python -m spacy download de_core_news_lg
nlp = spacy.load('de_core_news_lg')
nr_of_meanings = 0
nr_of_suitable_meanings = 0
tokens2clusters = IPA().get_clusters
rc = Adrc("etc/H2EAHsc.json")
orth2ipa = Epitran("hun-Latn").transliterate

@attr.s
class CustomLexeme(Lexeme):
    Meaning = attr.ib(default=None)
    Sense_ID = attr.ib(default=None)
    Entry_ID = attr.ib(default=None)

def clean1(word):
    return re.sub("[†×∆\-¹²³⁴’ ]", "", word)

def clean(text):
    """
    apply this in filter_vectors to clean meanings
    """
    text = re.sub(r'[〈〉:;!,.?-]', '', text)  # Remove special characters and punctuation
    text = re.sub(r'\s+', ' ', text)         # Replace multiple whitespaces with a single space
    text = text.strip()
    return text

@lru_cache(maxsize=None)
def filter_vectors(meaning):
    """
    filter out stopwords, add only if vector available.
    """
    clean_mean = clean(meaning)
    return clean_mean if nlp(clean_mean).has_vector else None

class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "gerstnerhungarian"

    form_spec = FormSpec(separators=",", first_form_only=True,
                         replacements=REP)
    lexeme_class = CustomLexeme

    def cldf_specs(self):
        return {
            None: pylexibank.Dataset.cldf_specs(self),
            "dictionary": CLDFSpec(
                module="Dictionary",
                dir=self.cldf_dir,
            ),
        }

    def cmd_makecldf(self, args):
        senses = defaultdict(list)
        idxs = {}
        form2idx = {}
        # assemble senses
        for idx, row in enumerate(self.raw_dir.read_csv(
            "Gerstner-2016-10176.tsv", delimiter="\t", dicts=True)):
            if row["sense"].strip():
                fidx = str(idx+1)+"-"+slug(row["form"])
                idxs[fidx] = row
                for sense in re.split("[,;]", row["sense"]):
                    if row["form"].strip() and sense.strip():
                        senses[slug(sense, lowercase=False)] += [(fidx, sense)]
                        form2idx[row["form"], sense.strip()] = fidx

        with self.cldf_writer(args) as writer:
            writer.add_sources()
            ## add concept
            concepts = {}
            for concept in self.conceptlists[0].concepts.values():
                idx = "{0}-{1}".format(concept.number, slug(concept.gloss))
                writer.add_concept(
                        ID=idx,
                        Name=concept.gloss,
                        Concepticon_ID=concept.concepticon_id,
                        Concepticon_Gloss=concept.concepticon_gloss,
                        )
                concepts[concept.concepticon_id] = idx
            args.log.info("added concepts")

            ## add languages
            for language in self.languages:
                writer.add_language(
                        ID="Hungarian",
                        Name="Hungarian",
                        Glottocode="hung1274"
                        )
            args.log.info("added languages")

            language_table = writer.cldf["LanguageTable"]

            ## add forms
#            try:
                #with open("form2idx.txt", "w") as f:
                #    f.write(str(form2idx))
            for row in self.raw_dir.read_csv(
                "wordlist.tsv", delimiter="\t", dicts=True):
                try:
                    writer.add_forms_from_value(
                        Local_ID=row["ID"],
                        Language_ID="Hungarian",
                        Parameter_ID=concepts[row["CONCEPTICON_ID"]],
                        Value=row["FORM"],
                        Meaning=row["MEANING"],
                        Entry_ID=form2idx[row["FORM"], row["SENSE"].strip()],
                        Sense_ID=row["SENSE_ID"],
                        Source="uesz"
                        )
                except KeyError:
                    pass
#            except FileNotFoundError:
#                args.log.info("wordlist.tsv missing, create with $ cldfbench gerstnerhungarian.map")
#                pass

        with self.cldf_writer(args, cldf_spec="dictionary", clean=False) as writer:

            # we use the same language table for the data
            writer.cldf.add_component(language_table)

            writer.cldf.add_columns(
                "EntryTable",
                {"name": "Segments", "datatype": "string"},
                {"name": "Year", "datatype": "integer"},
                {"name": "Etymology", "datatype": "string"},
                {"name": "Loan", "datatype": "string"},
                {"name": "rc100", "datatype": "string"}
            )

            writer.cldf.add_columns(
                "SenseTable",
                {"name": "Spacy", "datatype": "string"}
            )

            senses_items = senses.items()
            for j, (sense, values) in enumerate(senses_items):
                for i, (fidx, sense_desc) in enumerate(values):
                    vector = filter_vectors(sense_desc)
                    writer.objects["SenseTable"].append({
                        "ID": sense + "-" + str(i + 1),
                        "Entry_ID": fidx,
                        "Description": sense_desc.strip(),
                        "Spacy": vector
                        })
                    print(f"{j+1}/{len(senses_items)} meanings checked for word vectors", end="\r")

            for i, (fidx, row) in enumerate(idxs.items()):
                seg_ipa = tokens2clusters(ipa2tokens(orth2ipa(clean1(row["form"]))))
                writer.objects["EntryTable"].append({
                    "ID": fidx,
                    "Language_ID": "Hungarian",
                    "Headword": row["form"],
                    "Segments": seg_ipa,
                    "Year": row["year"],
                    "Etymology": row["origin"],
                    "Loan": row["Loan"],
                    "rc100": rc.reconstruct(seg_ipa, 100)
                    })
