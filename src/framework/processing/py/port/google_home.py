"""
DDP extract Google Home
"""
from pathlib import Path
import logging
import zipfile
import re
import io

import zipfile
import json
from io import TextIOWrapper

import pandas as pd

import port.unzipddp as unzipddp
import port.helpers as helpers

from port.validate import (
    DDPCategory,
    Language,
    DDPFiletype,
    ValidateInput,
    StatusCode,
)

logger = logging.getLogger(__name__)


DDP_CATEGORIES = [
    DDPCategory(
        id="json_en",
        ddp_filetype=DDPFiletype.JSON,
        language=Language.EN,
        known_files=[
            "archive_browser.html",
            "watch-history.json",
            "my-comments.html",
            "my-live-chat-messages.html",
            "subscriptions.csv",
        ],
    ),
]


STATUS_CODES = [
    StatusCode(id=0, description="Valid DDP", message=""),
    StatusCode(id=1, description="Valid DDP unhandled format", message=""),
    StatusCode(id=2, description="Not a valid DDP", message=""),
    StatusCode(id=3, description="Bad zipfile", message=""),
]


def validate(zfile: Path) -> ValidateInput:
    """
    Validates the input of an Youtube zipfile

    This function sets a validation object generated with ValidateInput
    This validation object can be read later on to infer possible problems with the zipfile
    I dont like this design myself, but I also havent found any alternatives that are better
    """

    validation = ValidateInput(STATUS_CODES, DDP_CATEGORIES)

    try:
        paths = []
        with zipfile.ZipFile(zfile, "r") as zf:
            for f in zf.namelist():
                p = Path(f)
                if p.suffix in (".json", ".csv", ".html"):
                    logger.debug("Found: %s in zip", p.name)
                    paths.append(p.name)

        validation.infer_ddp_category(paths)
        if validation.ddp_category.ddp_filetype == DDPFiletype.HTML:
            validation.set_status_code(0)
        elif validation.ddp_category.id is None:
            validation.set_status_code(2)
        else:
            validation.set_status_code(1)

    except zipfile.BadZipFile:
        validation.set_status_code(3)

    return validation



def json_data_to_dataframe(json_data):
    try:
        # Check if the loaded data is a list
        if isinstance(json_data, list):
            # Create a DataFrame from the list of objects
            df = pd.DataFrame(json_data, dtype=str)

            return df

        else:
            print("The JSON data is not a list.")
            return None

    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def clean_extracted_data(df):
    # Convert to DataFrame
    df_raw = pd.DataFrame(df)

    # Extract relevant columns
    selected_columns = ['title', 'time', 'subtitles']
    df_cleaned = df.loc[:, selected_columns]

    # Create 'command' and 'response' columns
    df_cleaned['command'] = df_cleaned['title'].astype(str)
    df_cleaned['response'] = df_cleaned['subtitles'].astype(str)

    # Remove additional columns
    columns_to_remove2 = ['title', 'subtitles']
    df_to_donate = df_cleaned.drop(columns=columns_to_remove2, axis=1)

    # Convert 'time' to datetime
    df_to_donate['time_datetime'] = pd.to_datetime(df_to_donate['time'], format='mixed')

    # Extract date and timestamp
    df_to_donate['date'] = df_to_donate['time_datetime'].dt.date
    df_to_donate['timestamp'] = df_to_donate['time_datetime'].dt.time

    # Select and reorder columns
    df_selected_to_donate = df_to_donate[['time_datetime', 'date', 'timestamp', 'command', 'response']]
    
    return df_selected_to_donate


def extract_googlehome_data_to_df(zip_file):
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_file:
            # Iterate through all files in the zip archive
            for file_info in zip_file.infolist():
                # Check if the file has a .json extension
                if file_info.filename.lower().endswith('.json'):
                    # Extract the JSON file
                    with zip_file.open(file_info.filename) as json_file:
                        # Load the JSON content
                        json_data = json.load(TextIOWrapper(json_file, 'utf-8'))

                    # Transform JSON data into a DataFrame
                    df = json_data_to_dataframe(json_data)

                    # Clean the data using a nested function
                    cleaned_df = clean_extracted_data(df)

                    return cleaned_df

            print("No JSON file found in the zip archive.")
            return None

    except FileNotFoundError:
        print(f"File not found: {zip_file}")
        return None
    except zipfile.BadZipFile:
        print(f"Invalid zip file: {zip_file}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
