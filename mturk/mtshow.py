#!/usr/bin/python3
# From TSV input and Mechanical Turk Batch Results CSV, produce a text output
# for analysis.
# Usage: mturk/mtshow.py curated-full.tsv Batch_2277985_batch_results.csv

from __future__ import print_function

import csv
from collections import namedtuple
import sys

BATCH_SIZE = 10


Answer = namedtuple('Answer', ['stock', 'custom', 'is_unk', 'is_bad', 'worker'])

def ans_to_str(ans):
    f = []
    if ans.stock:
        f.append(ans.stock)
    if ans.custom:
        f.append('C='+ans.custom)
    if ans.is_unk:
        f.append('UNK')
    if ans.is_bad:
        f.append('BAD')
    return ':'.join(f)


class Question:
    def __init__(self, q):
        self.qid, self.qtype, self.text, self.gsans = q
        self.qid = int(self.qid)
        self.text = self.text.strip()
        self.mtans = []


def get_questions(tsv):
    for line in tsv:
        line = line.rstrip()
        yield line.split('\t')


def questions_by_text(tsv):
    qdict = dict()
    qidx = dict()
    for q in get_questions(tsv):
        q = Question(q)
        qdict[q.text] = q
        qidx[q.qid] = q
    return qdict, qidx


def process_mt(mtc, qdict):
    qcovered = set()
    for row in mtc:
        for qn in range(1, BATCH_SIZE+1):
            qtext = row['Input.q%d_question'%(qn,)].strip()
            if not qtext:
                continue
            ans = Answer(row.get('Answer.q%d_answer'%(qn,), ''),
                         row.get('Answer.q%d_answer_cust'%(qn,), '').replace('{}', ''),
                         bool(row.get('Answer.q%d_answer_unk'%(qn,), '')),
                         bool(row.get('Answer.q%d_answer_bad'%(qn,), '')),
                         row['WorkerId'])
            q = qdict[qtext]
            q.mtans.append(ans)
            qcovered.add(q.qid)
    return qcovered


def show_questions(qcovered, qidx):
    for qid in sorted(qcovered):
        q = qidx[qid]
        print('%05d  %-60s  ### %s ###  %s' % (q.qid, q.text, q.gsans, ' :: '.join([ans_to_str(a) for a in q.mtans])))
        # print('                                                                                                     ' + ' :: '.join([a.worker for a in q.mtans]))


if __name__ == "__main__":
    tsvf, mtf = sys.argv[1:]

    tsv = open(tsvf, 'r')
    qdict, qidx = questions_by_text(tsv)

    mt = open(mtf, 'r')
    mtc = csv.DictReader(mt)
    qcovered = process_mt(mtc, qdict)

    show_questions(qcovered, qidx)
