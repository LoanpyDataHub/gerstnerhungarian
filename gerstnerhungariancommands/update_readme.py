"""
Write vector-coverage info to readme
"""
import csv
import json
import re

def run(args):
    with open("cldf/senses.csv", "r") as f:
        senses = list(csv.reader(f))
    h = {i: senses[0].index(i) for i in senses[0]}
    stat = [len([i for i in senses if i[h["Spacy"]]])/len(senses), len(senses)]

    with open("README.md", 'r') as f:
        readme = f.read()

    # Find the Statistics section and modify it
    statistics_start = readme.find('\n\n- **Varieties:**')
    statistics_end = readme.find('# Contributors')
    statistics_section = readme[statistics_start:statistics_end]

    # Add a new badge to the end of the Statistics section
    new_badges = f'\n![Vector Coverage {stat[0]:.0%}](https://img.shields.io/\
badge/Vector_Coverage-{stat[0]:.0%}25-brightgreen)\n[![SpaCy v3.5.1](https://\
img.shields.io/badge/SpaCy-v3.2.0-blue)](https://pypi.org/project/spacy/)'
    updated_statistics_section = new_badges + "\n\n" + statistics_section.strip()

    # Add another bullet point below the existing bullet points
    new_bullet = f'\n- **Senses:** {stat[1]:,}\n\n'
    updated_statistics_section += new_bullet

    # Update the README with the modified Statistics section
    updated_readme = readme[:statistics_start] + updated_statistics_section + readme[statistics_end:]

    # Write the updated README to a new file
    with open('README.md', 'w+') as f:
        f.write(updated_readme)
