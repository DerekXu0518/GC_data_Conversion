from natsort import natsorted
import pandas as pd
import os


def extract_and_validate_peak_table(file_path, peak_table='Ch1'):
    """
    Extracts the R.Time, Area, and Height columns from the specified peak table section in a file.
    """
    with open(file_path, 'r', encoding='ISO-8859-1') as file:
        lines = file.readlines()

    # Locate the peak table section
    section_header = f"[Peak Table ({peak_table})]"
    start_index = None
    for i, line in enumerate(lines):
        if section_header in line:
            start_index = i
            break

    # Return an empty DataFrame if the section is not found
    if start_index is None:
        print(f"Section {section_header} not found in {file_path}.")
        return pd.DataFrame(columns=['R.Time', 'Area', 'Height'])

    # Extract the header and data
    header_line = lines[start_index + 2].strip().split("\t")
    data_lines = lines[start_index + 3:]
    relevant_columns = ['R.Time', 'Area', 'Height']
    column_indices = {col: header_line.index(col) for col in relevant_columns if col in header_line}

    # Extract the rows with relevant columns
    extracted_data = []
    for line in data_lines:
        if line.strip() == "":
            break  # Stop at the first empty line
        row = line.strip().split("\t")
        extracted_row = {col: row[idx] for col, idx in column_indices.items()}
        extracted_data.append(extracted_row)

    return pd.DataFrame(extracted_data)


def process_and_separate_files_naturally_sorted(folder_path, output_csv, peak_table='Ch1'):
    """
    Processes all .txt or .TXT files in a folder, sorting them naturally by file name,
    including decimal numbers, and writes the combined data to a CSV with each file's
    data separated by a title row.
    """
    with open(output_csv, 'w') as output_file:
        # Get and naturally sort the file names
        sorted_files = natsorted(
            [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith('.txt')]
        )

        # Write combined data with separators
        for filename in sorted_files:
            file_path = os.path.join(folder_path, filename)
            print(f"Processing {filename}...")

            # Extract data from the file
            df = extract_and_validate_peak_table(file_path, peak_table)
            if not df.empty:
                # Add a separator row with the file name
                output_file.write(f"Source File: {filename}\n")
                df.to_csv(output_file, index=False)
                output_file.write("\n")  # Add an empty line as a separator

    print(f"Combined data with file separators saved to {output_csv}")