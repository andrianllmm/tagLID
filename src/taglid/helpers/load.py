import csv
import json
import os

from symspellpy import SymSpell


script_dir = os.path.dirname(os.path.realpath(__file__))


def load_freqlist(lang):
    """Loads either English or Tagalog dictionaries as a dictionary.

    Args:
        lang (str): The language of the dictionary; values can only be:
            - 'eng': English
            - 'tgl': Tagalog

    Returns:
        dict: A dictionary of words and its frequency.

    Notes:
        Dictionary characteristics:
            both includes:
                - lemmas
                - most inflected forms
                - some compound words
                - some abbreviations
                - affixes
            both excludes:
                - common names
                - commons locations
    """
    with open(
        os.path.join(script_dir, f"../resources/freqlist/{lang}_freqlist.csv")
    ) as in_file:
        return {row[0]: int(row[1]) for row in csv.reader(in_file)}


def load_slng(lang):
    """Loads English or Taglaog slangs as a list."""
    with open(
        os.path.join(script_dir, f"../resources/slang/{lang}_slang.txt")
    ) as in_file:
        return [slang.strip() for slang in in_file.readlines()]


def load_abbr():
    """Loads English and Tagalog abbreviatons as a dictionary."""
    with open(os.path.join(script_dir, f"../resources/abbr.json")) as abbr_file:
        return json.load(abbr_file)


def load_untj():
    """Loads universal interjections as a list."""
    with open(os.path.join(script_dir, f"../resources/untj.txt")) as untj_file:
        return [intj.strip() for intj in untj_file.readlines()]


def load_spellchecker(lang, edits=1):
    """Loads either English or Tagalog dictionaries as spellcheckers."""
    dir = os.path.join(script_dir, f"../resources/freqlist/{lang}_freqlist.csv")
    spell = SymSpell(max_dictionary_edit_distance=edits)
    spell.load_dictionary(dir, 0, 1, separator=",")
    return spell
