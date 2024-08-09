from taglid import lid


def test_preprocess():
    test_text = "   lower  UPPER Capital 1 $20 P579.00 don't  paulit-ulit... haha   "
    expected_tokens = [
        "lower", "UPPER", "Capital", "1", "$20", "P579.00", "don't", "paulit-ulit...", "haha"
    ]
    assert lid.preprocess(test_text) == expected_tokens


def test_identify_num():
    assert lid.identify_num("123") == {"eng": 0, "tgl": 0}
    assert lid.identify_num("$456") == {"eng": 0, "tgl": 0}
    assert lid.identify_num("Php78.90") == {"eng": 0, "tgl": 0}
    assert not lid.identify_num("abc")


def test_identify_untj():
    assert lid.identify_untj("haha") == {"eng": 0, "tgl": 0}
    assert not lid.identify_untj("hey")
    assert not lid.identify_untj("hoy")


def test_identify_ne():
    assert lid.identify_ne("Name") == {"eng": 0, "tgl": 0}
    assert lid.identify_ne("NAME") == {"eng": 0, "tgl": 0}
    assert not lid.identify_ne("name")


def test_identify_cont():
    assert lid.identify_cont("don't") == {"eng": 1.5, "tgl": 0}
    assert lid.identify_cont("doo't") == {"eng": 0, "tgl": 1.5}
    assert not lid.identify_cont("'tod")
    assert not lid.identify_cont("dot")

    assert lid.identify_cont("dunno") == {"eng": 1.5, "tgl": 0}
    assert not lid.identify_cont("idunno")

def test_identify_abbr():
    assert lid.identify_abbr("asap") == {"eng": 2.5, "tgl": 0}  # asap: as soon as possible
    assert lid.identify_abbr("aka") == {"eng": 2, "tgl": 0}  # aka: also known as
    assert lid.identify_abbr("fr") == {"eng": 1.5, "tgl": 0}  # fr: for real
    assert lid.identify_abbr("id") == {"eng": 1, "tgl": 0}  # id: identification
    assert lid.identify_abbr("skl") == {"eng": 0.67, "tgl": 1.33}  # skl: share ko lang
    assert not lid.identify_abbr("word")


def test_identify_dict():
    assert lid.identify_dict("english") == {"eng": 1, "tgl": 0}
    assert lid.identify_dict("ingles") == {"eng": 0, "tgl": 1}
    assert lid.identify_dict("at") == {"eng": 0, "tgl": 1}  # by frequency
    assert not lid.identify_dict("wordnotfound")


def test_identify_slng():
    assert lid.identify_slng("yeet") == {"eng": 1, "tgl": 0}
    assert lid.identify_slng("jowa") == {"eng": 0, "tgl": 1}
    assert not lid.identify_slng("word")


def test_identify_root():
    assert lid.identify_root("plurals") == {"eng": 1, "tgl": 0}
    assert lid.identify_root("pinakamagandang") == {"eng": 0, "tgl": 1}
    assert lid.identify_root("nagwowork") == {"eng": 0.5, "tgl": 0.5}
    assert lid.identify_root("shinashare") == {"eng": 0.5, "tgl": 0.5}
    assert not lid.identify_root("word")


def test_identify_corrected():
    assert lid.identify_corrected("mistke") == {"eng": 1, "tgl": 0, "correction": "mistake"}
    assert lid.identify_corrected("salaa") == {"eng": 0, "tgl": 1, "correction": "sala"}
    assert not lid.identify_corrected("wordnotfound")