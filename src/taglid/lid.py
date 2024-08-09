import argparse
import re
from tabulate import tabulate
from typing import Optional


# Import helpers
from .helpers import load


# Import and initialize tokenizers
from nltk.tokenize import sent_tokenize
from nltk.tokenize import WhitespaceTokenizer

tokenizer = WhitespaceTokenizer()


# Import and initialize stemmers/lemmatizers
from lemminflect import Lemmatizer
import tglstemmer.stemmer as tgl_stemmer

eng_lemmatizer = Lemmatizer()


# Load resources
ENG_FREQLIST = load.load_freqlist("eng")
TGL_FREQLIST = load.load_freqlist("tgl")
ENG_SLNG = load.load_slng("eng")
TGL_SLNG = load.load_slng("tgl")
ABBR = load.load_abbr()
UNTJ = load.load_untj()


# Load spell checkers
EDITS = 1
eng_spell = load.load_spellchecker("eng", edits=EDITS)
tgl_spell = load.load_spellchecker("tgl", edits=EDITS)


def lang_identify(text: str, edits: Optional[int] = 1) -> list[dict]:
    """Labels each token in a text its English and Tagalog values and flag.

    Args:
        text (str): Any text.
        edits (int, optional): The edit distance of the spell checker. Defaults to 1.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary contains:
            - 'word' (str): The original word.
            - 'eng' (float): English value.
            - 'tgl' (float): Tagalog value.
            - 'flag' (str): Indicates how the language was identified. Values can be:
                - 'NUM': Contains numerals (e.g. 13, 3.14).
                - 'NE': Universal named entity (e.g. John Doe, Philippines).
                - 'UNTJ': Universal interjection (e.g. haha).
                - 'ABBR': Abbreviation of initialism and acronyms (e.g. LOL).
                - 'CONT': Contraction of multiple words (e.g. ya'll).
                - 'DICT': Word found in dictionary.
                - 'SLNG': Word not found in the dictionary but is found in a list of slang words.
                - 'ROOT': Word not found in the dictionary but its root word is.
                - 'INTW': Intraword or word that mixes English and Tagalog.
                - 'NA': Unidentified.
            - 'correction' (str, optional): The corrected spelling of the original word, if applicable.
    """
    tokens = preprocess(text)

    labeled = []
    for org_token in tokens:
        token = org_token.replace(".", "")

        lang_val = {"eng": 0, "tgl": 0}
        flag = "NA"

        if result := identify_num(org_token):
            lang_val = result
            flag = "NUM"
            token = token.strip(".")

        elif result := identify_ne(token):
            lang_val = result
            flag = "NE"

        elif result := identify_untj(token):
            lang_val = result
            flag = "UNTJ"

        elif result := identify_freq(token):
            lang_val = result
            flag = "FREQ"

        elif result := identify_dict(token):
            lang_val = result
            flag = "DICT"

        elif result := identify_cont(token):
            lang_val = result
            flag = "CONT"

        elif result := identify_abbr(token):
            lang_val = result
            flag = "ABBR"

        elif result := identify_slng(token):
            lang_val = result
            flag = "SLNG"

        elif result := identify_root(token):
            lang_val = result
            if lang_val == {"eng": 0.5, "tgl": 0.5}:
                flag = "INTW"
            else:
                flag = "ROOT"

        elif result := identify_corrected(token, edits=edits):
            lang_val = result
            flag = "DICT"

        labeled.append(
            {
                "word": token,
                "eng": float(lang_val["eng"]),
                "tgl": float(lang_val["tgl"]),
                "flag": flag,
                "correction": lang_val.get("correction"),
            }
        )

    return labeled


def simplify(labeled_text: list[dict]) -> list[tuple]:
    """Simplifies the labeled text returned by `lang_identify`.

    Args:
        labeled_text (list[dict]): The labeled text returned by `lang_identify`.

    Returns:
        list[tuple]: A list of tuples, where each tuple contains the word and its corresponding language. Values can be:
            - 'na': Unidentified.
            - 'eng': Mostly English.
            - 'tgl': Mostly Tagalog.
            - 'eng-tgl': Mix of English and Tagalog.
    """
    simplified_text = []

    for word_info in labeled_text:
        if not word_info["eng"] and not word_info["tgl"]:
            simplified_text.append((word_info["word"], "na"))

        elif word_info["eng"] > word_info["tgl"]:
            simplified_text.append((word_info["word"], "eng"))

        elif word_info["tgl"] > word_info["eng"]:
            simplified_text.append((word_info["word"], "tgl"))

        else:
            simplified_text.append((word_info["word"], "eng-tgl"))

    return simplified_text


def preprocess(text: str) -> list[str]:
    """Preprocess text by tokenizing and cleaning.

    Args:
        text (str): Any text.

    Returns:
        list[str]: A list of words from the text.
    """
    sents = sent_tokenize(str(text))

    preprocessed_tokens = []
    for sent in sents:
        for token in tokenizer.tokenize(sent.strip()):
            clean_token = re.sub(r"[^a-zA-Z\$0-9-'.]", "", token)
            if clean_token != "":
                preprocessed_tokens.append(clean_token)

    return preprocessed_tokens


def identify_num(token: str) -> Optional[dict]:
    """Identifies if a word contains a numeral.

    Args:
        token (str): The word to be identified.

    Returns:
        dict, optional: A dictionary containing English and Tagalog values of zero, if identified, None otherwise.
    """
    if match := re.match(r"(\$|Php)(.+)", token):
        token = match.group(2)

    try:
        float(token)
        return {"eng": 0, "tgl": 0}
    except ValueError:
        return None


def identify_ne(token: str) -> Optional[dict]:
    """Identifies if a word is a universal named entity.

    Args:
        token (str): The word to be identified.

    Returns:
        dict, optional: A dictionary containing English and Tagalog values of zero, if identified, None otherwise.
    """
    return {"eng": 0, "tgl": 0} if token[0].isupper() else None


def identify_untj(token: str) -> Optional[dict]:
    """Identifies if a word is a universal interjection.

    Args:
        token (str): The word to be identified.

    Returns:
        dict, optional: A dictionary containing English and Tagalog values of zero, if identified, None otherwise.
    """
    token = token.lower()

    return {"eng": 0, "tgl": 0} if token in UNTJ else None


def identify_freq(token: str) -> Optional[dict]:
    """Identifies the language of a word based on word frequencies.

    Args:
        token (str): The word to be identified.

    Returns:
        dict, optional: A dictionary containing the English and Tagalog values, if identified, None otherwise.
    """
    token = token.lower()

    if token in ENG_FREQLIST and token in TGL_FREQLIST:
        eng_val = 0.0
        tgl_val = 0.0

        if ENG_FREQLIST[token] > TGL_FREQLIST[token]:
            eng_val = 1
        elif TGL_FREQLIST[token] > ENG_FREQLIST[token]:
            tgl_val = 1

        if eng_val or tgl_val:
            return {"eng": eng_val, "tgl": tgl_val}

    return None


def identify_dict(token: str) -> Optional[dict]:
    """Identifies the language of a word based on dictionary presence and word frequencies.

    Args:
        token (str): The word to be identified.

    Returns:
        dict, optional: A dictionary containing the English and Tagalog values, if identified, None otherwise.
    """
    token = token.lower()

    eng_val = 0.0
    tgl_val = 0.0

    if token in ENG_FREQLIST and token in TGL_FREQLIST:
        if ENG_FREQLIST[token] > TGL_FREQLIST[token]:
            eng_val = 1
        elif TGL_FREQLIST[token] > ENG_FREQLIST[token]:
            tgl_val = 1
    elif token in ENG_FREQLIST:
        eng_val = 1
    elif token in TGL_FREQLIST:
        tgl_val = 1

    if eng_val or tgl_val:
        return {"eng": eng_val, "tgl": tgl_val}

    return None


def identify_cont(token: str) -> Optional[dict]:
    """Identifies the language of a word based on common contraction characteristics.

    Args:
        token (str): The word to be identified.

    Returns:
        dict, optional: A dictionary containing the English and Tagalog values, if identified, None otherwise.
    """
    token = token.lower()

    eng_val = 0.0
    tgl_val = 0.0

    eng_cont = re.compile(
        r"(^[a-z]+('s|'m|'d|'re|'ve|'ll|n't|'a|'me|'em|'cha)$)|(^(dunno)$)"
    )

    tgl_cont = re.compile(
        r"(^[a-z]+('t|'y|'ko|'yo|'kin|'tin)$)|(^(di'ba|t'saka|ayoko|anyare|nubayan)$)"
    )

    if eng_cont.search(token):
        eng_val = 1.5
    elif tgl_cont.search(token):
        tgl_val = 1.5

    if eng_val or tgl_val:
        return {"eng": eng_val, "tgl": tgl_val}

    return None


def identify_abbr(token: str) -> Optional[dict]:
    """Identifies the language of an abbreviation (initialism/acronym).

    Args:
        token (str): The word to be identified.

    Returns:
        dict, optional: A dictionary containing the English and Tagalog values, if identified, None otherwise.
    """
    token = token.lower()

    if token in ABBR:
        eng_val = 0.0
        tgl_val = 0.0

        for word in ABBR[token].split():
            if lang_vals := identify_dict(word):
                eng_val += lang_vals["eng"]
                tgl_val += lang_vals["tgl"]
            elif lang_vals := identify_cont(word):
                eng_val += lang_vals["eng"]
                tgl_val += lang_vals["tgl"]

        if eng_val or tgl_val:
            total = eng_val + tgl_val
            average = (total + 1) / 2

            eng_val = round(eng_val * (average / total), 2)
            tgl_val = round(tgl_val * (average / total), 2)

            return {"eng": eng_val, "tgl": tgl_val}

    return None


def identify_slng(token: str) -> Optional[dict]:
    """Identifies the language of a slang.

    Args:
        token (str): The word to be identified.

    Returns:
        dict, optional: A dictionary containing the English and Tagalog values, if identified, None otherwise.
    """
    token = token.lower()

    eng_val = 0.0
    tgl_val = 0.0

    if token in ENG_SLNG:
        eng_val = 1
    elif token in TGL_SLNG:
        tgl_val = 1

    if eng_val or tgl_val:
        return {"eng": eng_val, "tgl": tgl_val}

    return None


def identify_root(token: str) -> Optional[dict]:
    """Identifies the language of a word after attempting lemmatization or stemming.

    Args:
        token (str): The word to be identified.

    Returns:
        dict, optional: A dictionary containing the English and Tagalog values, if identified, None otherwise.
    """
    token = token.lower()

    eng_val = 0.0
    tgl_val = 0.0

    if lemmas := list(eng_lemmatizer.getAllLemmas(token).values()):
        lemma = lemmas[0][0]

        if lemma != token:
            if lemma_lang := identify_dict(lemma):
                if lemma_lang["tgl"] and not lemma_lang["eng"]:
                    eng_val = 0.5
                    tgl_val = 0.5
                else:
                    eng_val = 1
            else:
                eng_val = 0.5

    elif stem := tgl_stemmer.get_stem(
        token, valid_words=list(TGL_FREQLIST.keys()) + list(ENG_FREQLIST.keys())
    ):
        if stem != token:
            if stem_lang := identify_dict(stem):
                if stem_lang["eng"] and not stem_lang["tgl"]:
                    eng_val = 0.5
                    tgl_val = 0.5
                else:
                    tgl_val = 1
            else:
                tgl_val = 0.5

    if eng_val or tgl_val:
        return {"eng": eng_val, "tgl": tgl_val}

    return None


def identify_corrected(token: str, edits: Optional[int] = 1) -> Optional[dict]:
    """Identifies the language of a word after attempting spelling correction.

    Args:
        token (str): The word to be corrected and detected.
        edits (int, optional): The edit distance of the spell checker. Defaults to 1.

    Returns:
        dict, optional: A dictionary containing the English and Tagalog values and the corrected word, if identified, None otherwise.
    """
    token = token.lower()

    eng_val = 0.0
    tgl_val = 0.0
    correction = None

    if eng_suggestions := eng_spell.lookup(
        token, verbosity="closest", max_edit_distance=edits
    ):
        eng_correct = eng_suggestions[0]

    if tgl_suggestions := tgl_spell.lookup(
        token, verbosity="closest", max_edit_distance=edits
    ):
        tgl_correct = tgl_suggestions[0]

    if eng_suggestions and tgl_suggestions:
        if eng_correct.distance < tgl_correct.distance:
            eng_val = 1
        elif tgl_correct.distance < eng_correct.distance:
            tgl_val = 1
        else:
            if eng_correct.count > tgl_correct.count:
                eng_val = 1
            elif tgl_correct.count > eng_correct.count:
                tgl_val = 1

    elif eng_suggestions:
        eng_val = 1
    elif tgl_suggestions:
        tgl_val = 1

    if eng_val > tgl_val:
        correction = eng_correct.term
    elif tgl_val > eng_val:
        correction = tgl_correct.term

    if eng_val or tgl_val:
        return {"eng": eng_val, "tgl": tgl_val, "correction": correction}

    return None


if __name__ == "__main__":
    description = "Labels each token in a text its language or English and Tagalog values and flag."

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-t",
        "--text",
        type=str,
        nargs="+",
        default=None,
        help="Text to process. If not provided, input will be requested interactively.",
    )
    parser.add_argument(
        "-s", "--simplify", action="store_true", help="Simplifies output"
    )

    args = parser.parse_args()

    if args.text is None:
        text = input("\ntext: ")
    else:
        text = " ".join(args.text)
    print()

    labeled_text = lang_identify(text, edits=EDITS)

    if args.simplify:
        simplified_text = simplify(labeled_text)
        print(tabulate(simplified_text))
    else:
        print(tabulate(labeled_text, headers="keys"))
    print()
