"""
Write vector-coverage info to readme
"""
import json
import re

def run(args):
    with open("vector_coverage.json", "r") as f:
        stat = json.load(f)

    with open("README.md", 'r') as f:
        readme = f.read()

    # Find the Statistics section and modify it
    statistics_start = readme.find('\n\n- **Varieties:**')
    statistics_end = readme.find('## CLDF Datasets')
    statistics_section = readme[statistics_start:statistics_end]

    # Add a new badge to the end of the Statistics section
    new_badges = f'\n![Vector Coverage {stat[0]}](https://img.shields.io/badg\
e/Vector_Coverage-{stat[0]}25-brightgreen)\n![SpaCy v3.2.0](https://img.shie\
lds.io/badge/SpaCy-v3.2.0-blue)'
    updated_statistics_section = new_badges + "\n\n" + statistics_section.strip()

    # Add another bullet point below the existing bullet points
    new_bullet = f'\n- **Meanings:** {stat[1]:,}\n.'
    updated_statistics_section += new_bullet + '\n## CLDF Datasets'

    # Update the README with the modified Statistics section
    updated_readme = readme[:statistics_start] + updated_statistics_section + readme[statistics_end:]

    # Write the updated README to a new file
    with open('updated_README.md', 'w+') as f:
        f.write(updated_readme)
