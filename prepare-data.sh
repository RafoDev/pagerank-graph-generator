#!/bin/bash

# compatibility with aws 2
pip install "urllib3<2.0"

# dirs creation for corpus and related data
python clean.py
python prepare-dirs.py

# script to get pids and download files 
python3 corpus-generator.py

# script to generate the pagerank graph
python3 graph-generator.py 
