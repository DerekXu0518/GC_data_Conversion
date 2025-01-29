import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def extract_and_validate_peak_table(file_path, peak_table='Ch1'):
    """
    Extracts and validates the peak table from a file.

    :param file_path: Path to the TXT file.
    :param peak_table: The identifier for the peak table section (default: 'Ch1').
    :return: DataFrame with extracted peak table data.
    """
    try:
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            lines = file.readlines()
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return pd.DataFrame(columns=['R.Time', 'Area', 'Height'])

    # Locate the peak table section
    section_header = f"[Peak Table ({peak_table})]"
    start_index = next((i for i, line in enumerate(lines) if section_header in line), None)

    if start_index is None:
        logging.warning(f"Section {section_header} not found in {file_path}.")
        return pd.DataFrame(columns=['R.Time', 'Area', 'Height'])

    # Parse header and extract data
    header_line = lines[start_index + 2].strip().split("\t")
    relevant_columns = ['R.Time', 'Area', 'Height']
    column_indices = {col: header_line.index(col) for col in relevant_columns if col in header_line}

    if set(relevant_columns) - set(column_indices):
        logging.warning(f"Missing columns in file {file_path}: {set(relevant_columns) - set(column_indices)}")
        return pd.DataFrame(columns=relevant_columns)

    # Extract relevant data
    extracted_data = []
    for line in lines[start_index + 3:]:
        if not line.strip():
            break
        row = line.strip().split("\t")
        extracted_data.append({col: row[idx] for col, idx in column_indices.items()})

    return pd.DataFrame(extracted_data)