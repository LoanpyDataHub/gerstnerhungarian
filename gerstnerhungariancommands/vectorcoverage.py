"""
Read the input file for loanpy.find
Loop through the column Meanings
Check how many of the words have a vector-representation in SpaCy
"""

import spacy
import re

def read_tsv(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    header = lines[0].strip().split('\t')
    data = [line.strip().split('\t') for line in lines[1:]]
    return header, data

def register(parser):
    parser.add_argument("input_file")

def run(args):
    header, data = read_tsv(args.input_file)

    nlp = spacy.load('de_core_news_lg')

    total_words = 0
    words_with_vectors = 0
    meaning_index = header.index("Meaning")
    for row in data:
        meanings = re.split(r',\s+|\s', row[meaning_index])
        for meaning in meanings:
            token = nlp(meaning.strip())
            total_words += 1
            if token.has_vector:
                words_with_vectors += 1

    percentage = (words_with_vectors / total_words) * 100

    # Update README.md with the badges
    with open('loanpy/README.md', 'r') as readme_file:
        readme_content = readme_file.read()

    # Remove existing badges
    readme_content = re.sub(r'!\[.*\]\(https://img.shields.io/badge/.*\)', '', readme_content)
    # Add new badges
    vector_coverage_badge = f"![Vector Coverage {percentage:.2f}%](https://img.shields.io/badge/Vector_Coverage-{percentage:.2f}%25-brightgreen)"
    spacy_badge = "![SpaCy v3.2.0](https://img.shields.io/badge/SpaCy-v3.2.0-blue)"

    updated_readme_content = vector_coverage_badge + "\n" + spacy_badge + "\n" + readme_content

    with open('loanpy/README.md', 'w+') as readme_file:
        readme_file.write(updated_readme_content)

    return percentage
