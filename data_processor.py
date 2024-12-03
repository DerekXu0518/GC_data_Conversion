import os
import pandas as pd
import logging
from file_extractor import extract_and_validate_peak_table

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def process_and_separate_files_naturally_sorted(folder_path, peak_table):
    try:
        file_list = sorted([f for f in os.listdir(folder_path) if f.endswith(".TXT")])
        logging.info(f"Found {len(file_list)} files to process.")

        combined_data = pd.concat(
            [
                extract_and_validate_peak_table(os.path.join(folder_path, file), peak_table).assign(**{"Source File": file})
                for file in file_list
            ],
            ignore_index=True
        )
        if not combined_data.empty:
            logging.info("Combined data created successfully.")
        return combined_data

    except Exception as e:
        logging.error(f"Error during file processing: {e}")
        return pd.DataFrame()


def process_and_filter_file(input_data, target_r_times, tolerance):
    """
    Filters rows based on R.Time values and selects the largest peak.

    :param input_data: Combined DataFrame.
    :param target_r_times: List of target R.Time values.
    :param tolerance: Tolerance range for filtering.
    :return: Filtered DataFrame.
    """
    try:
        input_data['R.Time'] = pd.to_numeric(input_data['R.Time'], errors='coerce')
        input_data['Area'] = pd.to_numeric(input_data['Area'], errors='coerce')

        # Add Target R.Time column
        input_data['Target R.Time'] = input_data['R.Time'].apply(
            lambda x: next((target for target in target_r_times if abs(x - target) <= tolerance), None)
        )
        filtered_data = input_data[input_data['Target R.Time'].notnull()]

        # Select largest peak
        filtered_data = (
            filtered_data.loc[filtered_data.groupby(['Source File', 'Target R.Time'])['Area'].idxmax()]
            .reset_index(drop=True)
        )
        return filtered_data

    except Exception as e:
        logging.error(f"Error filtering data: {e}")
        raise