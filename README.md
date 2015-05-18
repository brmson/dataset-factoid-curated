Reference QA Benchmarking Dataset
=================================

This repository contains **factoid-curated**, a reference question dataset
for benchmarking Question Answering systems, as used e.g. by the YodaQA
system.

The complete dataset is a combination of two sub-datasets (irc/ and trec/)
and consists of three files:

  * ``curated-full.tsv`` is the complete set of questions that are part
    of this dataset.  If you modify this set, you should also tweak the
    appropriate sub-dataset.

  * ``curated-train.tsv`` is the standard *train* split of the dataset, for
    primary development, detailed performance analysis and training (and
    if possible also testing) machine learning algorithms.

  * ``curated-test.tsv`` is the standard *test* split of the dataset, for
    benchmarking and reporting system performance.  Everyone should attempt
    to treat this dataset as "blind" and do not analyze or optimize
    performance for individual questions in this dataset!

(Some small portion of questions may be left out of the splits; these are
left reserved for future use, e.g. as part of a validation dataset.)

Ideally, humans should be doing all stages of evaluation instead of just
using regex matches, as time by time an unconcieved legitimate answer
pops up and on the other hand, sometimes the regex is unintentionally
over-permissive.  For a similar reason (to allow e.g. leading the/a
and other variations), we declare the answer as correct when the regex
matches any substring.


Using This Dataset
------------------

As explained above, please use the test dataset only for performance
reporting, not for question-by-question error analysis.  Always report
the version of the dataset you used - this is v1; other branches may
contain better, work-in-progress datasets.

To make results comparable, it is not enough to use the same set of
questions, we should strive to use the same or similar knowledge bases
as well; we realize that especially as time goes, this might not be
practical, but some degree of effort would be appreciated.  We also
expect the primary public YodaQA endpoints to track the latest version
of this dataset, so these could be reused.  We use:

  * enwiki-20150112 (archived at http://v.or.cz/~pasky/brmson/)
  * Freebase RDF dump from Jan 11 2015 (but it's probably not very volatile)
  * DBpedia 2014
  * WordNet 3.1


Aims of This Dataset
--------------------

We want to build a dataset of questions, which are:

  * Factoid.  This means that there is only a single answer (not a list
    or a sequence [of steps]), the answer is typically a simple phrase
    (not a story or topic summary; definition query like "Who is Obama?"
    is borderline and does not occur much) and the question is not
    a boolean yes/no (which requires quite different techniques to answer).

  * Wikipedia focused.  Wikipedia is a vast, unstructured repository of
    knowledge, so the bias is not terribly high, but we would like to think
    that a human with Wikipedia in hand would be able to answer all of these
    questions.  Most of them should require just a straightforward
    information retrieval, some are more challenging and might need some
    inference.

We may want to relax either requirement, but at that point we should start
tagging the questions to still keep a set of "simpler" ones.  The motivation
is to give a chance even to simple, focused systems.
