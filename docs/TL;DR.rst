`TL;DR <https://en.wikipedia.org/wiki/TL;DR>`_
==============================================

make cldf (downloadsize: 1.5GB+):

.. code-block:: sh

   python3 -m venv venv && source venv/bin/activate

   git clone https://github.com/martino-vic/koeblergothic.git
   mkdir concepticon
   cd concepticon
   git clone https://github.com/concepticon/concepticon-data.git
   cd ..
   git clone https://github.com/glottolog/glottolog.git
   git clone https://github.com/cldf-clts/clts.git
   git clone https://github.com/martino-vic/loanpy.git

   pip install -e koeblergothic
   pip install -e loanpy
   pip install pytest-cldf

   python3 -m spacy download de_core_news_lg

   cd koeblergothic
   cldfbench lexibank.makecldf lexibank_koeblergothic.py  --concepticon-version=v2.5.0 --glottolog-version=v4.5 --clts-version=v2.2.0 --concepticon=../concepticon/concepticon-data --glottolog=../glottolog --clts=../clts

   cldfbench koeblergothic.update_readme

   pytest --cldf-metadata=cldf/cldf-metadata.json test.py
