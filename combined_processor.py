import os
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def extract_and_validate_peak_table(file_path, peak_table='Ch1'):
    """
    Extracts and validates peak table data from a file.

    :param file_path: Path to the file.
    :param peak_table: Peak table identifier.
    :return: DataFrame with 'R.Time', 'Area', 'Height' columns.
    """
    try:
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            lines = file.readlines()
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return pd.DataFrame(columns=['R.Time', 'Area', 'Height'])

    section_header = f"[Peak Table ({peak_table})]"
    start_index = next((i for i, line in enumerate(lines) if section_header in line), None)

    if start_index is None:
        logging.warning(f"Section {section_header} not found in {file_path}.")
        return pd.DataFrame(columns=['R.Time', 'Area', 'Height'])

    header_line = lines[start_index + 2].strip().split("\t")
    relevant_columns = ['R.Time', 'Area', 'Height']
    column_indices = {col: header_line.index(col) for col in relevant_columns if col in header_line}

    missing_columns = set(relevant_columns) - set(column_indices.keys())
    if missing_columns:
        logging.warning(f"Missing columns {missing_columns} in file {file_path}.")
        return pd.DataFrame(columns=relevant_columns)

    extracted_data = []
    for line in lines[start_index + 3:]:
        if not line.strip():
            break
        row = line.strip().split("\t")
        extracted_data.append({col: row[idx] for col, idx in column_indices.items()})

    return pd.DataFrame(extracted_data)


def process_and_separate_files_naturally_sorted(folder_path, peak_table):
    """
    Processes files with natural sorting and returns a combined DataFrame.

    :param folder_path: Path to the folder containing the files.
    :param peak_table: Peak table identifier.
    :return: Combined DataFrame.
    """
    try:
        combined_data = pd.DataFrame()
        file_list = sorted([f for f in os.listdir(folder_path) if f.endswith(".TXT")])
        logging.info(f"Found {len(file_list)} files to process.")

        for file_name in file_list:
            file_path = os.path.join(folder_path, file_name)
            logging.info(f"Processing file: {file_name}")
            try:
                data = extract_and_validate_peak_table(file_path, peak_table)
                if data.empty:
                    logging.warning(f"No valid data extracted from {file_name}.")
                    continue

                # Add a 'Source File' column
                data["Source File"] = file_name

                # Combine the data
                combined_data = pd.concat([combined_data, data], ignore_index=True)
            except Exception as e:
                logging.error(f"Error processing file {file_name}: {e}")

        if combined_data.empty:
            logging.warning("No data found after processing files.")
            return None

        logging.info("Combined data created successfully.")
        return combined_data

    except Exception as e:
        logging.error(f"Error during file processing: {e}")
        return None


def process_and_filter_file(input_data, target_r_times, tolerance):
    """
    Filters rows from the combined data based on R.Time values and selects the largest peak.

    :param input_data: DataFrame containing the combined data.
    :param target_r_times: List of target R.Time values to filter around.
    :param tolerance: Tolerance range for filtering.
    :return: Filtered DataFrame.
    """
    try:
        if 'R.Time' not in input_data.columns:
            raise ValueError("Missing 'R.Time' column in the input data.")

        # Ensure R.Time and Area are numeric
        input_data['R.Time'] = pd.to_numeric(input_data['R.Time'], errors='coerce')
        input_data['Area'] = pd.to_numeric(input_data['Area'], errors='coerce')

        # Add a 'Target R.Time' column to identify matched rows
        def match_r_time(row):
            for target in target_r_times:
                if abs(row['R.Time'] - target) <= tolerance:
                    return target
            return None

        input_data['Target R.Time'] = input_data.apply(match_r_time, axis=1)

        # Filter rows that matched any target R.Time
        filtered_data = input_data[input_data['Target R.Time'].notnull()]

        # Select the largest peak area for each Source File and Target R.Time
        filtered_data = (
            filtered_data.loc[filtered_data.groupby(['Source File', 'Target R.Time'])['Area'].idxmax()]
            .reset_index(drop=True)
        )

        return filtered_data

    except Exception as e:
        logging.error(f"Error filtering data: {e}")
        raise