"""
Open terminal in folder containing GitHub projects
or in a newly created folder and run the commands below to...

...create the contents of the cldf-folder (downloadsize: 1.5GB+):

.. code-block:: sh

   python3 -m venv venv && source venv/bin/activate

   git clone https://github.com/martino-vic/gerstnerhungarian.git
   mkdir concepticon
   cd concepticon
   git clone https://github.com/concepticon/concepticon-data.git
   cd ..
   git clone https://github.com/glottolog/glottolog.git
   git clone https://github.com/cldf-clts/clts.git

   pip install -e gerstnerhungarian
   pip install loanpy
   pip install pytest-cldf

   python3 -m spacy download de_core_news_lg

   cd gerstnerhungarian
   cldfbench lexibank.makecldf lexibank_gerstnerhungarian.py  --concepticon-version=v2.5.0 --glottolog-version=v4.5 --clts-version=v2.2.0 --concepticon=../concepticon/concepticon-data --glottolog=../glottolog --clts=../clts

   cldfbench gerstnerhungarian.update_readme

...to filter word lists according to different criteria:

.. code-block:: sh

   cldfbench gerstnerhungarian.map

   cldfbench gerstnerhungarian.filter -y 1600 -o SlavicTurkic -a

...to test whether the converted data conforms to the CLDF standard:

.. code-block:: sh

   pytest --cldf-metadata=cldf/cldf-metadata.json test.py

"""
