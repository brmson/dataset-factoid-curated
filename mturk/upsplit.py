#!/usr/bin/python3
# From a shared "full" file, update a split file.
# Usage: mturk/upsplit.py curated-full.tsv curated-train.tsv >curatedv2-train,.tsv

from __future__ import print_function

import sys


def get_questions(tsv):
    for line in tsv:
        line = line.rstrip()
        yield line.split('\t')


if __name__ == "__main__":
    tsvf, splitf = sys.argv[1:]

    qidx = dict()
    tsv = open(tsvf, 'r')
    for i, q in enumerate(get_questions(tsv)):
        qidx[q[0]] = q

    spl = open(splitf, 'r')
    for i, q in enumerate(get_questions(spl)):
        print('\t'.join(qidx.get(q[0], q)))
