import pandas as pd
import numpy as np
import os
import time

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
        
        df_peak_table = pd.DataFrame(peak_table_data, columns=peak_table_header)
        if 'R.Time' in df_peak_table.columns and 'Area' in df_peak_table.columns:
            return df_peak_table[['R.Time', 'Area']]
        else:
            print(f"'R.Time' or 'Area' not found in {file_path}. Returning NaN.")
            return pd.DataFrame(columns=['R.Time', 'Area'], data=[[np.nan, np.nan]])
    else:
        print(f"{section} section not found in {file_path}. Filling with NaN.")
        return pd.DataFrame(columns=['R.Time', 'Area'], data=[[np.nan, np.nan]])


def combine_files(file_list, peak_table='Ch1'):
    combined_data = []
    for file_path in file_list:
        print(f"Processing file: {file_path}")
        df = extract_peak_table(file_path, peak_table=peak_table)
        if not df.empty:
            df.columns = [f"{col}_{os.path.basename(file_path).replace('.TXT', '').replace('.txt', '')}" for col in df.columns]
            combined_data.append(df)
        else:
            print(f"No valid data in {file_path}")

    if combined_data:
        combined_df = pd.concat(combined_data, axis=1)
        combined_df.reset_index(inplace=True)
        return combined_df
    else:
        print("No data to combine.")
        return None


def reorder_columns_by_index(df):
    """
    Reorder columns of the dataframe by the index (X) in 'R.Time_X' and 'Area_X'.
    """
    # Separate R.Time and Area columns
    rtime_columns = sorted([col for col in df.columns if col.startswith("R.Time")], key=lambda x: int(x.split("_")[1]))
    area_columns = sorted([col for col in df.columns if col.startswith("Area")], key=lambda x: int(x.split("_")[1]))
    
    # Combine the sorted columns
    sorted_columns = []
    for rtime, area in zip(rtime_columns, area_columns):
        sorted_columns.extend([rtime, area])
    
    # Reorder the dataframe columns
    return df[sorted_columns]


print("Start")
start = time.time()

#Path setting
input_path = '/Users/a1/촉매방 Dropbox/찡루트/Northwestern/Reaction/Data processing/Input'
output_path = '/Users/a1/촉매방 Dropbox/찡루트/Northwestern/Reaction/Data processing/Output'

# Read everything in the folder
file_list = [os.path.join(input_path, file) for file in os.listdir(input_path) if file.endswith('.TXT') or file.endswith('.txt')]
print("File list found:", file_list)

# Combine data from all files for the 'Ch1' peak table
combined_df_1 = combine_files(file_list, peak_table='Ch1')

if combined_df_1 is not None and not combined_df_1.empty:

    print("Reordering Ch1 columns by X index...")
    combined_df_1 = reorder_columns_by_index(combined_df_1)
    combined_csv_path = os.path.join(output_path, 'dataset_Ch1.csv')
    combined_df_1.to_csv(combined_csv_path, index=False)
    print(f"Saved sorted data for Ch1 to {combined_csv_path}")

