import pandas as pd
import numpy as np
import os


def extract_peak_table(file_path, peak_table='Ch1'):
    valid_columns = ['R.Time', 'Area', 'Height']  # Define valid columns here
    with open(file_path, 'r', encoding='ISO-8859-1') as file:  # Handle different encoding
        lines = file.readlines()

    # Find the start of the peak table section
    start_index = None
    section = f'[Peak Table ({peak_table})]'
    for i, line in enumerate(lines):
        if section in line:
            start_index = i
            break

    if start_index is not None:
        # Extract the header and filter to keep only 'R.Time', 'Area', and 'Height'
        peak_table_header = lines[start_index + 2].strip().split("\t")
        selected_columns = [col for col in peak_table_header if col in valid_columns]

        if len(selected_columns) < 3:
            print(f"Missing one or more of the required columns in {file_path}.")
            return pd.DataFrame(columns=valid_columns, data=[[np.nan, np.nan, np.nan]])

        peak_table_data = []
        for line in lines[start_index + 3:]:
            if line.strip() == "":
                break
            row = line.strip().split("\t")
            row_data = {header: value for header, value in zip(peak_table_header, row)}

            # Only keep values for 'R.Time', 'Area', and 'Height'
            row_data_filtered = {key: row_data.get(key, np.nan) for key in valid_columns}
            peak_table_data.append(row_data_filtered)

        return pd.DataFrame(peak_table_data, columns=valid_columns)
    else:
        print(f"Section {section} not found in {file_path}.")
        return pd.DataFrame(columns=valid_columns, data=[[np.nan, np.nan, np.nan]])


def process_folder(folder_path, peak_table='Ch1'):
    # Create an empty list to store DataFrames
    all_data = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            print(f"Processing {filename}...")
            df = extract_peak_table(file_path, peak_table)
            all_data.append(df)

    # Combine all DataFrames into a single DataFrame
    combined_df = pd.concat(all_data, ignore_index=True)

    # Generate output file path in the input folder
    output_file = os.path.join(folder_path, "combined_output.csv")

    # Save the combined DataFrame to the output file
    combined_df.to_csv(output_file, index=False)
    print(f"All files combined and saved to {output_file}")


if __name__ == "__main__":
    folder_path = input("Enter the folder path containing the files: ").strip()
    peak_table = input("Enter the peak table identifier (default 'Ch1'): ").strip() or 'Ch1'

    process_folder(folder_path, peak_table)