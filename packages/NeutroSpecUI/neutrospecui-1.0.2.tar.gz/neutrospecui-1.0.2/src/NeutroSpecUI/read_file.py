from typing import Callable
import re

import pandas as pd


def load_file(file_name: str) -> pd.DataFrame:
    """
    Reads the data from a .txt, .csv, or .mft file and creates a pandas DataFrame.

    Parameters:
    file_name (str): The path to the file to be read.

    Returns:
    pd.DataFrame: A pandas DataFrame containing the data from the file.
    """
    if not isinstance(file_name, str):
        raise TypeError("The file name must be a string.")

    file_type = re.search(r"(\.[^.]+)$", file_name)

    if file_type is None or file_type.group() not in READ_FUNCTIONS:
        raise ValueError(
            f"This file type is not supported. Please provide a {', '.join(READ_FUNCTIONS.keys())} file."
        )

    df = READ_FUNCTIONS[file_type.group()](file_name)
    return df


def load_mft(file_name: str) -> pd.DataFrame:
    with open(file_name, "r") as file:
        # Read the .mft file, skipping the metadata lines
        info = {}
        while line := file.readline():
            if line == "\n":
                break

            if ":" not in line:
                continue

            key, value = line.split(":", 1)
            info[key.strip()] = value.strip()
        print(
            f"Information for {file_name}", info
        )  # TODO: Add proper handling of metadata

        # Read the data section into a DataFrame
        df = pd.read_csv(file, sep=r"\s{2,}", engine="python")
        # make all column floats
        df = df.apply(pd.to_numeric, errors="coerce")
    return df


# dictionary of file types and their corresponding read functions
READ_FUNCTIONS: dict[str, Callable[[str], pd.DataFrame]] = {
    ".csv": pd.read_csv,
    ".txt": lambda file_name: pd.read_csv(file_name, sep=r"\t+", engine="python"),
    ".mft": load_mft,
}
