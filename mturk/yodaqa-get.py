#!/usr/bin/python3
# yodaqa-get.py: Get candidate answers + evidence for questions of the dataset.
# Usage: mturk/yodaqa-get.py curated-full.tsv qdata/
# c.f. yodaqa/data/eval/rest-eval.py

from __future__ import print_function

import json
import requests
import sys
import time

URL = 'http://qa.ailao.eu:4567/q'


def get_questions(tsv):
    for line in tsv:
        yield line.split('\t')


def process_question(i, qdir, qid, qtype, text, ansgs):
    print('[%d] %s' % (i, text))
    yoda_qid = requests.post(URL, data={'text': text}).json()['id']
    while True:
        time.sleep(0.5)
        data = requests.get(URL + '/' + yoda_qid).json()
        if data["finished"]:
            break
    with open('%s/%s.json' % (qdir, qid), 'w') as f:
        print(json.dumps(data, indent=1, sort_keys=True), file=f)
    print('    %s | %s' % (data['answers'][0]['text'], ansgs))


if __name__ == "__main__":
    tsvf, qdata = sys.argv[1:3]
    if len(sys.argv) > 3:
        skip_n = int(sys.argv[3])
    else:
        skip_n = 0

    tsv = open(tsvf, 'r')
    for i, q in enumerate(get_questions(tsv)):
        if i < skip_n:
            continue
        process_question(i, qdata, *q)
