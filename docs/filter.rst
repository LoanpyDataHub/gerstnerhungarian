
Part 2: Filtering
-----------------

Different analyses require different portions of the original data
``raw/Gerstner-2016-10176.tsv``. Most tasks in computational historical
linguistics require words that can be mapped to core concepts of a language's
vocabulary. For these type of tasks, one has to try to map the complex and
multifaceted meanings of a word to a single concept in a catalogue. Here,
this task is achieved with following command:

.. code-block:: sh

   cldfbench gerstnerhungarian.map

This command creates the file ``raw/wordlist.tsv`` from ``cldf/senses.csv``.
A file that contains less than half the amount of rows than the ca. 10,000
row long ``raw/Gerstner-2016-10176.tsv``.

.. automodule:: gerstnerhungariancommands.map
   :members:

To search for old loanwords with loanpy, we will also need to filter the
original input data, but according to different criteria. One filter criterion
is the year of first appearance in a written source. Words that start
appearing late are unlikely to be old. With this command:

.. code-block:: sh

   cldfbench gerstnerhungarian.filter

the rows of ``cldf/entries.csv`` are filtered according to their year of first
appearance, which is stored in the column ``Year``. The optimal cut-off year
is calculated automatically by looking at the oldest layers of Hungarian:
words of Proto-Uralic, Proto-Finno-Ugric, Proto-Ugric, Turkic, unknown, and
and uncertain origin. The optimal cut-off year in our case is 1416, which
is reflected in the output file name ``loanpy/hun1416.tsv``. For more details
on how the optimal cut-off year is calculated see the documentation of
`loanpy.utility's find_optimal_year_cutoff
<https://loanpy.readthedocs.io/en/latest/documentation.html#loanpy.utils.find_optimal_year_cutoff>`_
function. Filtering by year of first appearance is possible with the -y flag,
by etymological origin with the -o flag, and with the -a flag one can indicate
whether entries with missing data should be included. For example:

.. code-block:: sh

   cldfbench gerstnerhungarian.filter -y 1600 -o SlavicTurkic -a

will include words of Slavic or Turkic origin that appeared before 1600 in a
written text while words with no data about year or etymological origin
will still be included.

.. automodule:: gerstnerhungariancommands.filter
   :members:

