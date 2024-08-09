import csv
import os
import sys

from tglstemmer.helpers.affixes import PREFIXES, INFIXES, SUFFIXES


script_dir = os.path.dirname(os.path.realpath(__file__))


def generate(lang):
    """Generates word frequency files of chosen language."""
    with open(os.path.join(script_dir, f"original/{lang}_freqlist.csv")) as in_file:
        freqlist = {str(row[0]): int(row[1]) for row in csv.reader(in_file)}

    included = load_included(lang)
    excluded = load_excluded()

    included_freqlist = include(freqlist, included)
    excluded_freqlist = exclude(included_freqlist, excluded)
    freqlist = dict(sorted(excluded_freqlist.items(), key=lambda x: x[1], reverse=True))

    with open(os.path.join(script_dir, f"{lang}_freqlist.csv"), "w") as outfile:
        writer = csv.writer(outfile)
        for word in freqlist:
            writer.writerow([word, freqlist[word]])


def include(freqlist, included):
    """Include certain words to word list."""
    included_freqlist = {}

    for word in freqlist:
        if word in included:
            included_freqlist[word] = freqlist[word] + 1
        else:
            included_freqlist[word] = freqlist[word]

    for word in included:
        if word not in freqlist:
            included_freqlist[word] = 1

    return included_freqlist


def exclude(freqlist, excluded):
    """Excluded certain words from word list."""
    excluded_freqlist = {}
    for word in freqlist:
        if word not in excluded:
            excluded_freqlist[word] = freqlist[word]
    return excluded_freqlist


def load_included(lang):
    """Load included words from txt files."""
    included = []
    for filename in os.listdir(f"{script_dir}/included"):
        if filename.endswith(".txt") and filename.startswith(lang):
            with open(os.path.join(script_dir, f"included/{filename}")) as in_file:
                included.extend([word.strip().lower() for word in in_file.readlines()])

    included.extend(PREFIXES + INFIXES + SUFFIXES)

    return included


def load_excluded():
    """Load excluded words from txt files."""
    excluded = []
    for filename in os.listdir(f"{script_dir}/excluded"):
        if filename.endswith(".txt"):
            with open(os.path.join(script_dir, f"excluded/{filename}")) as in_file:
                excluded.extend([word.strip().lower() for word in in_file.readlines()])

    return excluded


if __name__ == "__main__":
    LANGUAGES = ["eng", "tgl"]

    if len(sys.argv) == 2 and sys.argv[1].lower() in LANGUAGES:
        LANG = sys.argv[1].lower()
        generate(LANG)

    else:
        for LANG in LANGUAGES:
            generate(LANG)
