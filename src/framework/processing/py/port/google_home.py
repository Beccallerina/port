"""
DDP extract Google Home
"""
from pathlib import Path
import logging
import zipfile

import zipfile
import json
from io import TextIOWrapper

import pandas as pd

from port.validate import (
    DDPCategory,
    Language,
    DDPFiletype,
    ValidateInput,
    StatusCode,
)
import port.helpers as helpers

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
    Validates the input of an GoogleHome zipfile

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



def json_data_to_dataframe(json_data) -> pd.DataFrame:
    out = pd.DataFrame()
    try:
        # Check if the loaded data is a list
        if isinstance(json_data, list):
            # Create a DataFrame from the list of objects
            out = pd.DataFrame(json_data)

        else:
            print("The JSON data is not a list.")

    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        return out
 

def is_nan(value):
    if isinstance(value, float):
        return value != value  # NaN is the only value that is not equal to itself
    return False


def clean_response(response_list: list) -> str:
    """
    Get the list from a response
    Extract all values from the name key

    """
    responses = []
    try:
        if isinstance(response_list, list):
            for d in response_list:
                responses.append(d.get("name", ""))

            out = " ".join(responses)
           
        if is_nan(response_list):
            out = "no response"

        return out

    except Exception as e:
        return str(response_list)
        
        
def clean_extracted_data(df: pd.DataFrame) -> pd.DataFrame:
    out = df

    try:
        # Extract relevant columns
        selected_columns = ['title', 'time', 'subtitles']
        df_cleaned = df.loc[:, selected_columns]

        # Create 'command' and 'response' columns
        df_cleaned['Uw commando'] = df_cleaned['title'].astype(str)
        df_cleaned['Reactie van de assistent'] = df_cleaned['subtitles'].apply(clean_response)

        # Remove additional columns
        columns_to_remove2 = ['title', 'subtitles']
        df_to_donate = df_cleaned.drop(columns=columns_to_remove2, axis=1)

        # Remove last word in entries of the Commando column (ger: gesagt, en: said, nl: gezegd)
        df_to_donate['Uw commando'] = df_to_donate['Uw commando'].str.rsplit(' ', 1).str[0]
        # For NL this means also removing 'Je hebt' in combination with 'gezegd'
        df_to_donate['Uw commando'] = df_to_donate['Uw commando'].str.replace('Je hebt', '')


        # Dropping miliseconds and adjusting format of day and time
        df_to_donate['Dag en tijd'] = df_to_donate['time'].str.replace(r"\.\d+", "")
        # Replace 'T' with ',' and remove 'Z'
        df_to_donate['Dag en tijd'] = df_to_donate['Dag en tijd'].str.replace('T', ', ').str.replace('Z', '')


        # Convert time column >> THIS IS WHERE PART OF THE PROBLEMATIC CODE IS
        # Option 1
        #df_to_donate['Datum'] = pd.to_datetime(df_to_donate['time'], unit='s') --> this does not work
        
        # Option 2
        #df_to_donate['time_datetime'] = pd.to_datetime(df_to_donate['time'], errors='ignore')

        # Extract date and timestamp
        #df_to_donate['Datum'] = pd.to_datetime(df_to_donate['time_datetime'], unit='s').dt.date 
        #df_to_donate['timestamp'] = pd.to_datetime(df_to_donate['time_datetime'], unit='s').dt.time
       

        # Select and reorder columns
        out = df_to_donate[['Dag en tijd', 'Uw commando', 'Reactie van de assistent']]
    except Exception as e:
        print(e)
    finally:
        return out
    


def extract_googlehome_data_to_df(zip_file) -> pd.DataFrame:
    """
    Will return a cleaned dataframe. 
    If there is not data or it fails for whatever reason return an empty dataframe
    """

    out = pd.DataFrame()

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
                    out = clean_extracted_data(df)
                    print(out)
                    return out

            print("No JSON file found in the zip archive.")
 
    except FileNotFoundError:
        print(f"File not found: {zip_file}")
    except zipfile.BadZipFile:
        print(f"Invalid zip file: {zip_file}")
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        return out
