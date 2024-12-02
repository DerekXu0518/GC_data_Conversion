import pandas as pd
import os
from tkinter import Tk
from tkinter.filedialog import askdirectory


def extract_and_validate_peak_table(file_path, peak_table='Ch1'):
    """
    Extracts the R.Time, Area, and Height columns from the specified peak table section in a file.
    """
    # Read file contents
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

    # Return as DataFrame
    return pd.DataFrame(extracted_data)


def process_and_separate_files(folder_path, output_csv, peak_table='Ch1'):
    """
    Processes all .txt or .TXT files in a folder and writes the combined data to a CSV
    with each file's data separated by a title row.
    """
    with open(output_csv, 'w') as output_file:
        # Write combined data with separators
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            # Process files with .txt or .TXT extensions
            if os.path.isfile(file_path) and filename.lower().endswith('.txt'):
                print(f"Processing {filename}...")
                df = extract_and_validate_peak_table(file_path, peak_table)

                if not df.empty:
                    # Add a separator row with the file name
                    output_file.write(f"Source File: {filename}\n")
                    df.to_csv(output_file, index=False)
                    output_file.write("\n")  # Add an empty line as a separator

    print(f"Combined data with file separators saved to {output_csv}")


def select_folder():
    """
    Opens a dialog for the user to select a folder and returns the selected path.
    """
    print("Select the folder containing the files.")
    Tk().withdraw()  # Hide the root window
    folder_path = askdirectory(title="Select Folder")
    return folder_path


if __name__ == "__main__":
    # Interactive folder selection
    folder_path = select_folder()
    if not folder_path:
        print("No folder selected. Exiting.")
    else:
        output_csv = os.path.join(folder_path, "combined_output_with_separators.csv")  # Output CSV
        peak_table = input("Enter the peak table identifier (default 'Ch1'): ").strip() or 'Ch1'
        process_and_separate_files(folder_path, output_csv, peak_table)