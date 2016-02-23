#!/usr/bin/python3
# From TSV input and Mechanical Turk Batch Results CSV, produce a revised TSV
# based on MT replies.
# Usage: mturk/mt2tsv.py curated-full.tsv Batch_results.csv >curated-full-v2.tsv
#
# TODO: Negative analysis - check which answers *would* be matched by the new
# gold standard but weren't marked so by Turkers.

from __future__ import print_function

import csv
from collections import namedtuple
import re
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

    def reconcile_gsans(self):
        """ this routine contains the main logic of updating gsans based on
        MT responses """
        mtans = []
        for ans in self.mtans:
            if ans.stock:
                mtans += ans.stock.split('|')
            if ans.custom:
                mtans += ans.custom.split('|')

        n_matches = 0
        mtans_novel = []
        for mta in mtans:
            if re.search(self.gsans, mta, re.IGNORECASE):
                n_matches += 1
            elif mta != '':
                mtans_novel.append(re.escape(mta).replace('\\ ', ' '))

        if len(mtans) - n_matches <= 1:
            return  # good enough, no modifications required

        # sort by length and prune redundant (matchable by shorter)
        mtans_novel.sort(key=lambda x: len(x))
        mtans_dupes = set()
        mtans_pruned = []
        for i, mta in enumerate(mtans_novel):
            if mta in mtans_dupes:
                continue
            n_amatches = 0
            for mtb in mtans_novel[i+1:]:
                if re.search(mta, mtb.replace('\\', ''), re.IGNORECASE):
                    mtans_dupes.add(mtb)
                    n_amatches += 1
            if n_amatches > 0 or n_matches < 1:  # skip completely unique answers, except when we are short on good ones
                mtans_pruned.append(mta)

        if mtans_pruned:
            self.gsans += '|'.join([''] + mtans_pruned)


def get_questions(tsv):
    for line in tsv:
        line = line.rstrip()
        yield line.split('\t')


def questions_by_text(tsv):
    qdict = dict()
    qidx = dict()
    qlist = list()
    for q in get_questions(tsv):
        q = Question(q)
        qdict[q.text] = q
        qidx[q.qid] = q
        qlist.append(q.qid)
    return qdict, qidx, qlist


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


def print_question(q):
    print('\t'.join([str(q.qid), q.qtype, q.text, q.gsans]))


def gen_questions(qlist, qidx, debug=False):
    for qid in qlist:
        q = qidx[qid]
        if debug:
            print(':: %05d  %-60s  ### %s ###  %s' % (q.qid, q.text, q.gsans, ' :: '.join([ans_to_str(a) for a in q.mtans])))
            print_question(q)
        q.reconcile_gsans()
        print_question(q)


if __name__ == "__main__":
    tsvf = sys.argv[1]
    mtfs = sys.argv[2:]

    tsv = open(tsvf, 'r')
    qdict, qidx, qlist = questions_by_text(tsv)

    qcovered = set()
    for mtf in mtfs:
        mt = open(mtf, 'r')
        mtc = csv.DictReader(mt)
        qcovered |= process_mt(mtc, qdict)

    gen_questions(qlist, qidx)
