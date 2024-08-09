import argparse
import os
import pandas as pd
import sys
from typing import Optional

from .lid import lang_identify


def lang_identify_df(df: pd.DataFrame) -> pd.DataFrame:
    """Labels each token in each cell in a pandas DataFrame its English and Tagalog value and flag.

    Args:
        df (DataFrame): The original DataFrame to be labeled.

    Returns:
        DataFrame: The labeled DataFrame.
    """
    rows = list(df.index)
    cols = list(df.columns)

    labeled_data = []
    for row in rows:
        for col in cols:
            print(row, col, end="")

            labeled_text = lang_identify(df.loc[row, col])

            token_index = 1
            for word_info in labeled_text:
                print(".", end="")

                data = {
                    "row": row,
                    "col": col,
                    "token_index": token_index,
                } | word_info

                token_index += 1

                labeled_data.append(data)

            print()

    labeled_df = pd.DataFrame(labeled_data)
    labeled_df.set_index(["row", "col", "token_index"], inplace=True)
    labeled_df.sort_index(inplace=True)
    labeled_df.reset_index(inplace=True)
    labeled_df.set_index("row", inplace=True)

    return labeled_df


def lang_identify_file(
    in_path: str,
    out_path: str,
    in_sheet: Optional[str] = None,
    out_sheet: Optional[str] = None,
    index: Optional[str] = None,
) -> bool:
    """Labels each token in each cell in an Excel file its English and Tagalog value and flag.

    Args:
        in_path (str): The path to the input Excel file.
        out_path (str): The path to the output Excel file.
        in_sheet (str, optional): The sheet name of the input file. Defaults to None.
        out_sheet (str, optional): The sheet name of the output file. Defaults to None.
        index (str, optional): Specific index to set. Defaults to None.

    Returns:
        bool: True if successful, False otherwise.
    """
    if check_in_file(in_path) and check_out_file(out_path):
        df = read_file(in_path, in_sheet, index)

        labeled_df = lang_identify_df(df)

        write_file(labeled_df, out_path, out_sheet)

        return True

    return False


def read_file(
    filename: str, sheet_name: Optional[str] = None, index: Optional[str] = None
) -> pd.DataFrame:
    """Reads an Excel file to a pandas DataFrame."""
    if sheet_name:
        df = pd.read_excel(filename, sheet_name)
    else:
        df = pd.read_excel(filename)

    if index:
        df.set_index(index, inplace=True)

    return df


def write_file(
    df: pd.DataFrame, filename: str, sheet_name: Optional[str] = None
) -> bool:
    """Writes a pandas DataFrame to an Excel file."""
    if sheet_name:
        df.to_excel(filename, sheet_name)
    else:
        df.to_excel(filename)

    print("Exported successfully.")

    return True


def check_in_file(in_path: str) -> bool:
    """Checks if the input file name exists."""
    if os.path.isfile(in_path):
        return True
    else:
        sys.exit(f"{in_path} does not exist.")


def check_out_file(out_path: str) -> bool:
    """Checks if the output file name exists."""
    if os.path.isfile(out_path):
        print(f"{out_path} already exists.")
        permit = input("Do you want to overwrite it? (Y/n) ").lower()
        if permit == "y":
            return True
        else:
            sys.exit("Terminated.")
    else:
        return True


if __name__ == "__main__":
    description = "Labels each token in each cell in an Excel file its English and Tagalog value and flag."

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("in_path", type=str, help="The path to the input Excel file.")
    parser.add_argument("out_path", type=str, help="The path to the output Excel file.")
    parser.add_argument(
        "--in_sheet",
        type=str,
        default=None,
        help="The sheet name the input Excel file.",
    )
    parser.add_argument(
        "--out_sheet",
        type=str,
        default=None,
        help="The sheet name the output Excel file.",
    )
    parser.add_argument(
        "--index", type=str, default=None, help="The index name the input Excel file."
    )

    args = parser.parse_args()

    lang_identify_file(
        args.in_path,
        args.out_path,
        in_sheet=args.in_sheet,
        out_sheet=args.out_sheet,
        index=args.index,
    )
