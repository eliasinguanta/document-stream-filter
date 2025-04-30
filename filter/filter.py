# file_handler.py
import re
from datetime import datetime

import random
import string
import time

import logging
import Levenshtein
from utils import Query, Document, Match

app_name = "document-stream-filter"
logger = logging.getLogger(app_name)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
logger.addHandler(console_handler)



def hamming_distance(s1, s2):
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))

def filter_documents(queries: list[Query], documents: list[Document]) -> list[dict]:
    results: list[Match] = []
    for query in queries:
        query_word = query.word.lower()
        metric = query.metric.lower()
        matching_docs: list[Document] = []

        for doc in documents:
            for word in doc.words:
                word = word.lower()

                if metric == "exact":
                    if word == query_word:
                        matching_docs.append(doc)
                        break

                elif metric == "edit":
                    if Levenshtein.distance(word, query_word) <= query.distance:
                        matching_docs.append(doc)
                        break

                elif metric == "hamming":
                    if len(word) == len(query_word) and hamming_distance(word, query_word) <= query.distance:
                        matching_docs.append(doc)
                        break

                else:
                    raise ValueError(f"Invalid metric: {query.metric}")


        results.append(Match(query=query, results=matching_docs))
    return [res.model_dump() for res in results]

