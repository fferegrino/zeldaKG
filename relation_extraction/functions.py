import numpy as np
from slugify import slugify
import re


from urllib.parse import urlparse
from urllib.parse import unquote


def levenshtein(seq1, seq2):  
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros ((size_x, size_y))
    for x in range(size_x):
        matrix [x, 0] = x
    for y in range(size_y):
        matrix [0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x-1] == seq2[y-1]:
                matrix [x,y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1],
                    matrix[x, y-1] + 1
                )
            else:
                matrix [x,y] = min(
                    matrix[x-1,y] + 1,
                    matrix[x-1,y-1] + 1,
                    matrix[x,y-1] + 1
                )
    return (matrix[size_x - 1, size_y - 1])

# Infoboxes

def infobox_clean_url(url):
    """
    Clean the url to met the structure adopted for the dataset
    """
    parsed = urlparse(url)
    path = unquote(parsed.path)
    if path.startswith("../"):
        path = path[3:]
    path = path.replace("/", "%2F")
    query = None if parsed.query == '' else parsed.query
    fragment = None if parsed.fragment == '' else parsed.fragment
    return (path, query, fragment)


parentheses = re.compile("\(.+\)")

def infobox_get_canonical_relation(label):
    """
    Canonicalize the relationship
    """
    lbl = re.sub(parentheses, '', label)
    l =  slugify(lbl.strip(), separator='_')
    return l.upper()
