import pandas as pd
import os


def extract_and_validate_peak_table(file_path, peak_table='Ch1'):
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

    # Verify column mappings
    print(f"Column Indices: {column_indices}")

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


def process_and_combine_files(folder_path, output_csv, peak_table='Ch1'):
    all_data = []  # To store extracted data from all files

    # Iterate over all files in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Process files with .txt or .TXT extensions
        if os.path.isfile(file_path) and filename.lower().endswith('.txt'):
            print(f"Processing {filename}...")
            df = extract_and_validate_peak_table(file_path, peak_table)

            # Add a title column with the file name for context
            if not df.empty:
                df['Source File'] = filename
                all_data.append(df)

    # Combine all extracted data into a single DataFrame
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df.to_csv(output_csv, index=False)
        print(f"Combined data saved to {output_csv}")
        return combined_df
    else:
        print("No data extracted from the files.")
        return pd.DataFrame()


if __name__ == "__main__":
    folder_path = input("Enter the folder path containing the files: ").strip()
    output_csv = os.path.join(folder_path, "combined_output.csv")  # Output CSV in the same folder
    peak_table = input("Enter the peak table identifier (default 'Ch1'): ").strip() or 'Ch1'

    process_and_combine_files(folder_path, output_csv, peak_table)