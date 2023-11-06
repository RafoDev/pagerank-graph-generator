import json
import random
import boto3
from botocore.exceptions import NoCredentialsError
from io import BytesIO

s3_client = boto3.client('s3')
corpus_filename = "data/corpus.json"
pagerank_filename =  "data/pagerank.txt"

corpus_object = s3_client.get_object('search-engine-bd', corpus_filename)
corpus_data = corpus_object['Body'].read().decode('utf-8')
corpus = json.loads(corpus_data)

# with open(corpus_filename, "r") as corpus_json:
#     corpus = json.load(corpus_json)

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

lines_bytes = lines.encode('utf-8')

lines_buffer = BytesIO(lines_bytes)

s3_client.upload_fileobj(lines_buffer, 'search-engine-bd', pagerank_filename)

lines_buffer.close()

# with open('s3://search-engine-bd/data/pagerank.txt', 'w') as f:
#     f.writelines(lines)

# f.close()
