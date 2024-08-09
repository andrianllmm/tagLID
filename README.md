# TagLID

**A Word level Language Identification (LID) tool for Tagalog-English (Taglish) text.**


## About

[taglid](src/taglid/) labels words in a Taglish (mix of Tagalog and English) text simply their language or detailed English and Tagalog frequency values and corresponding flag that indicates how it was identified. It is a rule-based and opinionated system of counting the frequency of languages in a code-switched text. It primarily depends on dictionary lookup to identify the language of a word. Additionally, it also considers cases such as exclusion for numerical numerals, named entities, universal interjections and inclusions such as unpacking abbreviations and contractions, slangs, stemming or lemmatizing inflected words, intrawords, and correction of misspellings.


## Installation

To install the latest development version from GitHub, use:

```bash
git clone https://github.com/andrianllmm/taglid.git
cd taglid
pip install .
```

## Usage

taglid can act as a standalone library that can be imported via `import taglid` or as a CLI application via `python -m taglid`.


### Library Mode


#### Textual data

To use taglid in textual data use the `lid` module.

To identify each word in a text use `lang_identify`. This takes any string and returns a list of words and their corresponding English and Tagalog values, flag, and correction.
```python
from taglid.lid import lang_identify

labeled_text = lang_identify("hello, mundo")
print(labeled_text)
```
```
Output:
[{'Word': 'hello', 'eng': 1.0, 'tgl': 0.0, 'Flag': 'DICT', 'Correction': None}, {'Word': 'mundo', 'eng': 0.0, 'tgl': 1.0, 'Flag': 'DICT', 'Correction': None}]
```

You can use [`tabulate`](https://pypi.org/project/tabulate/) to view output in tabular format.
```python
from tabulate import tabulate

print(tabulate(labeled_text, headers="keys"))
```
```
Output:
word      eng    tgl  flag    correction
------  -----  -----  ------  ------------
hello       1      0  DICT
mundo       0      1  DICT
```

You could also simplify this output to just showing the words and their language using `simplify`. This takes the return value of `lang_identify` and returns a list of tuples containing the word and its language.
```python
from taglid.lid import simplify

simplified_text = simplify(labeled_text)
print(simplified_text)
```
```
Output:
[('hello', 'eng'), ('mundo', 'tgl')]
```


#### Datasets

To use taglid in datasets use the `lid_dataset` module.

To label each word in each cell in a [`pandas`](https://pypi.org/project/pandas/) DataFrame use `lang_identify_df`. This takes a DataFrame of multiple rows and columns with each cell containing textual data and returns a labeled DataFrame where each token is a row labeled by its original row, original column, and token index.
```python
import pandas as pd
from taglid.lid_dataset import lang_identify_df

data = [['hello po', 'ano?'], ['mag-aask lang po', 'what?']]

df = pd.DataFrame(data)

labeled_df = lang_identify_df(df)
print(labeled_df)
```
```
Output:
     col  token_index      word  eng  tgl  flag correction
row
0      0            1     hello  1.0  0.0  DICT       None
0      0            2        po  0.0  1.0  DICT       None
0      1            1       ano  0.0  1.0  FREQ       None
1      0            1  mag-aask  0.5  0.5  INTW       None
1      0            2      lang  0.0  1.0  FREQ       None
1      0            3        po  0.0  1.0  DICT       None
1      1            1      what  1.0  0.0  DICT       None
```

### CLI Mode

Similarly, you can run `python -m taglid.lid` to directly input textual data and have taglid output the labeled text in tabular format.
```bash
python -m taglid.lid

text: hello, mundo

word      eng    tgl  flag    correction
------  -----  -----  ------  ------------
hello       1      0  DICT
mundo       0      1  DICT
```
The output can also be simplified by adding `--simplify`.
```bash
python -m taglid.lid --simplify --text hello, mundo

-----  ---
hello  eng
mundo  tgl
-----  ---
```

You can also use `lid_dataset` with Excel files by running `python -m taglid.lid_dataset in_path out_path` to directly label spreadsheets.
```bash
python -m taglid.lid_dataset sample.xlsx sample_labeled.xlsx
```

## Accuracy

The accuracy of taglid is yet to be tested.


## Issues

* No issues

If you encounter any issues or bugs, please report them on the [GitHub issues page](#).


## Contributing

This projects welcomes contributions and suggestions. Please follow these steps:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.


## License

This project is licensed under the [GPL-3.0 License](LICENSE).

---

For more information contact [maagmaandrian@gmail.com](mailto:maagmaandrian@gmail.com) with any additional questions or comments.