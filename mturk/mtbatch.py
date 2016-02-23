#!/usr/bin/python3
# From TSV input and qdata/ fetched data, produce CSV file for Mechanical Turk.
# Usage: mturk/mtbatch.py curated-full.tsv qdata/ batch.csv

from __future__ import print_function

import csv
from itertools import islice
import json
import sys

BATCH_SIZE = 10


def get_questions(tsv):
    for line in tsv:
        line = line.rstrip()
        yield line.split('\t')


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def colnames():
    cols = []
    for i in range(BATCH_SIZE):
        n = i + 1
        cols += ["q%d_question"%(n,), "q%d_gsans"%(n,),
                 "q%d_ans0"%(n,), "q%d_ev0"%(n,), "q%d_ans1"%(n,), "q%d_ev1"%(n,),
                 "q%d_ans2"%(n,), "q%d_ev2"%(n,), "q%d_ans3"%(n,), "q%d_ev3"%(n,),
                 "q%d_ans4"%(n,), "q%d_ev4"%(n,)]
    return cols


def get_answers(qres, N=5):
    for ans in qres['answers'][:N]:
        atext = ans['text']

        snippet = qres['snippets'][str(ans['snippetIDs'][0])]
        source = qres['sources'][str(snippet['sourceID'])]
        aev = '['+source['title']+'] '
        if 'propertyLabel' in snippet:
            aev += '<<%s>> knowledge base property' % (snippet['propertyLabel'],)
        elif 'passageText' in snippet:
            aev += snippet['passageText']

        yield (atext, aev)


def process_qbatch(qbatch, qdata):
    fields = dict()
    for i, q in enumerate(qbatch):
        n = i + 1
        qid, qtype, text, gsans = q
        print('[%s] %s' % (qid, text))
        fields["q%d_question"%(n,)] = text
        fields["q%d_gsans"%(n,)] = gsans
        with open("%s/%d.json" % (qdata, int(qid))) as qfile:
            qres = json.load(qfile)
        for j, a in enumerate(get_answers(qres)):
            fields["q%d_ans%d"%(n, j)] = a[0]
            fields["q%d_ev%d"%(n, j)] = a[1]
    return dict([(k, v.replace('<', '&lt;')) for k, v in fields.items()])


if __name__ == "__main__":
    tsvf, qdata, outf = sys.argv[1:]

    tsv = open(tsvf, 'r')
    out = open(outf, 'w')
    outc = csv.DictWriter(out, colnames())
    outc.writeheader()
    for qbatch in chunk(get_questions(tsv), BATCH_SIZE):
        outc.writerow(process_qbatch(qbatch, qdata))
