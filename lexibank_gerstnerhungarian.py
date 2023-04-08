from collections import defaultdict
import functools
import json
import pathlib
import re

import attr
from clldutils.misc import slug
from epitran import Epitran
from ipatok import tokenise
from loanpy.utils import IPA
from pylexibank import Dataset as BaseDataset, FormSpec, Lexeme
import pylexibank
from cldfbench import CLDFSpec
import spacy

REP = [(x, "") for x in "†×∆-¹²³⁴’"]
with open("etc/stopwords.json", "r") as f:  # from nltk.corpus import stopwords
    STOPWORDS = json.load(f)  # stopwords.words("german")
# install first with $ python -m spacy download de_core_news_lg
nlp = spacy.load('de_core_news_lg')
nr_of_meanings = 0
nr_of_suitable_meanings = 0
epi = Epitran("hun-Latn").transliterate
get_clusters = IPA().get_clusters

@attr.s
class CustomLexeme(Lexeme):
    Meaning = attr.ib(default=None)
    Sense_ID = attr.ib(default=None)
    Entry_ID = attr.ib(default=None)

def segipa(word):
    word = re.sub("[†×∆\-¹²³⁴’ ]", "", word)
    return get_clusters(tokenise(epi(word)))

def clean(text):
    """
    apply this in filter_vectors to clean meanings
    """
    text = re.sub(r'[〈〉:;!,.?]', '', text)  # Remove special characters and punctuation
    text = re.sub(r'\s+', ' ', text)         # Replace multiple whitespaces with a single space
    text = text.strip()
    return text

def filter_vectors(meanings):
    """
    split meanings, filter out stopwords, add only if vector available.
    """
    meanings = clean(meanings)
    meanings = re.split(r',\s+|\s', meanings)
    vectors = []
    @functools.lru_cache
    def is_suitable(meaning):
        if meaning not in STOPWORDS:
            token = nlp(meaning.strip())
            if token.has_vector:
                return True
        return False

    for meaning in meanings:
        global nr_of_meanings
        nr_of_meanings += 1
        if is_suitable(meaning):
            global nr_of_suitable_meanings
            nr_of_suitable_meanings += 1
            vectors.append(meaning)

    # Add the row to the new_data list only if vectors is not empty
    return ', '.join(vectors)

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
            try:
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
            except FileNotFoundError:
                args.log.info("wordlist.tsv missing, create with $ cldfbench gerstnerhungarian.map")
                pass

        with self.cldf_writer(args, cldf_spec="dictionary", clean=False) as writer:

            # we use the same language table for the data
            writer.cldf.add_component(language_table)

            writer.cldf.add_columns(
                "EntryTable",
                {"name": "Segments", "datatype": "string"},
                {"name": "Year", "datatype": "integer"},
                {"name": "Etymology", "datatype": "string"},
                {"name": "Loan", "datatype": "string"},
                {"name": "Spacy", "datatype": "string"}
            )

            for sense, values in senses.items():
                for i, (fidx, sense_desc) in enumerate(values):
                    writer.objects["SenseTable"].append({
                        "ID": sense+"-"+str(i+1),
                        "Description": sense_desc,
                        "Entry_ID": fidx
                        })

            for i, (fidx, row) in enumerate(idxs.items()):
                print(f"{i+1}/{len(idxs)} meanings checked for word vectors", end="\r")
                writer.objects["EntryTable"].append({
                    "ID": fidx,
                    "Language_ID": "Hungarian",
                    "Headword": row["form"],
                    "Segments": segipa(row["form"]),
                    "Year": row["year"],
                    "Etymology": row["origin"],
                    "Loan": row["Loan"],
                    "Spacy": filter_vectors(row["sense"])
                    })

        with open("vector_coverage.json", "w+") as f:
            json.dump(
                [f'{nr_of_suitable_meanings/nr_of_meanings:.0%}',
                 nr_of_meanings], f
                )
            #for idx, row in enumerate(self.raw_dir.read_csv(
            #    "Streitberg-1910-3645.tsv", delimiter="\t", dicts=True)):
            #    entry_id = "{0}-{1}".format(idx+1, slug(row["form"]))
            #    sense_id = "{0}-{1}".format(idx+1, slug(row["SENSE"]))
            #    writer.objects["EntryTable"].append({
            #        "ID": entry_id,
            #        "Language_ID": "Gothic",
            #        "Headword": row["form"],
            #        "Part_Of_Speech": row["pos"]
            #        })
            #    writer.objects["SenseTable"].append({
            #        "ID": sense_id,
            #        "Description": row["SENSE"],
            #        "Entry_ID": entry_id
            #        })
