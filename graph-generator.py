import json

from os import listdir
import random

corpus_filename = "data/corpus.json"

with open(corpus_filename, "r") as corpus_json:
    corpus = json.load(corpus_json)

lines = ""

def generate_graph(paper, pids):
    global lines
    if len(paper["references"]) == 0:
        for pid in pids:
            lines += pid + '\t' + paper["pid"] + '\n'

    for ref in paper["references"]:
        pids.append(paper["pid"])
        generate_graph(ref, pids)
        pids.pop()


generate_graph(corpus, [])

with open('data/pagerank.txt', 'w') as f:
    f.writelines(lines)

f.close()
