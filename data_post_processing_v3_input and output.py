import pandas as pd
import numpy as np
import os


def extract_peak_table(file_path, peak_table='Ch1'):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Find the start of the peak table section
    start_index = None
    section = f'[Peak Table ({peak_table})]'
    for i, line in enumerate(lines):
        if section in line:
            start_index = i
            break

    if start_index is not None:
        peak_table_header = lines[start_index + 2].strip().split("\t")
        if len(peak_table_header) < 2:
            print(f"Invalid header in {file_path}. Filling with NaN.")
            return pd.DataFrame(columns=['R.Time', 'Area'], data=[[np.nan, np.nan]])

        peak_table_data = []
        for line in lines[start_index + 3:]:
            if line.strip() == "":
                break
            row = line.strip().split("\t")
            while len(row) < len(peak_table_header):
                row.append(np.nan)
            peak_table_data.append(row)

        return pd.DataFrame(peak_table_data, columns=peak_table_header)
    else:
        print(f"Section {section} not found in {file_path}.")
        return pd.DataFrame(columns=['R.Time', 'Area'], data=[[np.nan, np.nan]])


def process_folder(folder_path, output_folder, peak_table='Ch1'):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            print(f"Processing {filename}...")
            df = extract_peak_table(file_path, peak_table)
            output_file = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_output.csv")
            df.to_csv(output_file, index=False)
            print(f"Saved to {output_file}")


if __name__ == "__main__":
    folder_path = input("Enter the folder path containing the files: ").strip()
    output_folder = input("Enter the folder path for saving outputs: ").strip()
    peak_table = input("Enter the peak table identifier (default 'Ch1'): ").strip() or 'Ch1'

    process_folder(folder_path, output_folder, peak_table)