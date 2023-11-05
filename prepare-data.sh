#!/bin/bash

# dirs creation for corpus and related data
mkdir corpus
mkdir corpus/pdf
mkdir corpus/txt
mkdir data

# script to get pids and download files 
python3 corpus-generator.py

# script to generate the pagerank graph
python3 graph-generator.py 
