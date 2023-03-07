from setuptools import setup
import json


with open('metadata.json', encoding='utf-8') as fp:
    metadata = json.load(fp)

setup(
    name='lexibank_gerstnerhungarian',
    description=metadata["title"],
    license=metadata.get("license", ""),
    url=metadata.get("url", ""),
    py_modules=['lexibank_gerstnerhungarian'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'lexibank.dataset': ['gerstnerhungarian=lexibank_gerstnerhungarian:Dataset'],
        'cldfbench.commands': [
            'gerstnerhungarian=gerstnerhungariancommands'
                    ]
    },
    install_requires=[["pylexibank>=3.0", "pysem", "epitran>=1.24",
        "pandas>=1.5.3", "ipatok>=0.4.1"]
    ],
    extras_require={
        'test': [
            'pytest-cldf',
        ],
    },
)
