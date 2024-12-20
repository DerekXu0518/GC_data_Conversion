import os
import pandas as pd
import logging
from file_extractor import extract_and_validate_peak_table

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

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
    Filters rows from the input DataFrame based on R.Time values, selects the largest Area,
    and restructures the output to display Area data for each compound in separate columns.

    :param input_data: DataFrame containing combined data.
    :param target_r_times: List of target R.Time values to filter.
    :param tolerance: Tolerance range for filtering.
    :return: Filtered DataFrame with Area data for each compound in separate columns.
    """
    try:
        if 'R.Time' not in input_data.columns:
            raise ValueError("Missing 'R.Time' column in the input data.")

        # Ensure numeric conversion
        input_data = input_data.copy()
        input_data['R.Time'] = pd.to_numeric(input_data['R.Time'], errors='coerce')
        input_data['Area'] = pd.to_numeric(input_data['Area'], errors='coerce')

        # Assign Target R.Time
        input_data['Target R.Time'] = input_data['R.Time'].apply(
            lambda x: next((target for target in target_r_times if abs(x - target) <= tolerance), None)
        )
        input_data = input_data.dropna(subset=['Target R.Time'])

        # Group and select the largest Area
        grouped = input_data.groupby(['Source File', 'Target R.Time'])
        largest_area_idx = grouped['Area'].idxmax()
        filtered_data = input_data.loc[largest_area_idx]

        # Pivot to restructure output
        compound_mapping = {1.6: 'PO', 2.3: 'Amino Alcohol', 3.6: 'Diglyme'}
        filtered_data['Compound'] = filtered_data['Target R.Time'].map(compound_mapping)
        pivoted_data = filtered_data.pivot(index='Source File', columns='Compound', values='Area').reset_index()

        # Rename columns for clarity
        pivoted_data.columns.name = None
        pivoted_data = pivoted_data.rename(columns={
            'PO': 'PO Area',
            'Amino Alcohol': 'Amino Alcohol Area',
            'Diglyme': 'Diglyme Area'
        })

        return pivoted_data

    except Exception as e:
        logging.error(f"Error filtering and restructuring data: {e}")
        return pd.DataFrame()