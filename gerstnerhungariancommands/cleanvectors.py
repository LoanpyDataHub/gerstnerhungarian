"""
Add reconstructions to hun.tsv
"""
import csv
import re

import nltk
import spacy


nltk.download("stopwords")
from nltk.corpus import stopwords

german_stop_words = stopwords.words("german")

def read_tsv(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    header = lines[0].strip().split('\t')
    data = [line.strip().split('\t') for line in lines[1:]]
    return header, data

def save_to_file(file_path, terms):
    with open(file_path, 'w') as file:
        for term in terms:
            file.write(f"{term}\n")

def run(args):
    input_file = 'loanpy/rchun.tsv'
    output_file = 'loanpy/rchun.tsv'
    header, data = read_tsv(input_file)

    nlp = spacy.load('de_core_news_lg')

    meaning_index = header.index("Meaning")
    for i, row in enumerate(data):
        print(f"{i+1}/{len(data)} iterations completed", end="\r")
        meanings = re.split(r',\s+|\s', row[meaning_index])
        vectors = []
        for meaning in meanings:
            if meaning not in german_stop_words:
                token = nlp(meaning.strip())
                if token.has_vector:
                    vectors.append(meaning)

        # Overwrite the 'Meaning' column with the words that have existing vectors
        row[meaning_index] = ', '.join(vectors)

    # Save the modified data to a new file
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(header)
        writer.writerows(data)

    print(f"\nFinished processing. The output file is '{output_file}'.")
