import os
import pandas as pd
import re
from file_extractor import extract_and_validate_peak_table


def generate_hierarchy_column(data):
    """
    Generate a hierarchy column for sorting based on Source File and R.Time.

    :param data: DataFrame containing 'Source File' and 'R.Time'.
    :return: Modified DataFrame with a hierarchy column added.
    """
    def extract_sort_key(string):
        """
        Generate a hierarchical sort key from the source file name.
        Splits by '-' and sorts numerically wherever possible.
        """
        parts = string.split('-')
        sort_key = []
        for part in parts:
            match = re.match(r'(\d+)', part)
            if match:
                sort_key.append(int(match.group(1)))  # Convert numbers to integers
            else:
                sort_key.append(part.lower())  # Keep text parts as lowercase
        return tuple(sort_key)

    # Generate hierarchy based on Source File first
    data['Hierarchy'] = data['Source File'].map(extract_sort_key)

    # Append R.Time as the final level of hierarchy
    data['Hierarchy'] = data.apply(lambda row: row['Hierarchy'] + (row['R.Time'],), axis=1)

    return data


def process_and_separate_files_naturally_sorted(folder_path, peak_table):
    """
    Process files in hierarchical order, ensuring R.Time is naturally sorted within hierarchy.

    :param folder_path: Path to the folder containing files.
    :param peak_table: Identifier for the peak table section in the files.
    :return: Combined DataFrame with correctly sorted retention times.
    """
    try:
        file_list = sorted(
            [f for f in os.listdir(folder_path) if f.endswith(".TXT")]
        )

        combined_data = pd.DataFrame()

        for file_name in file_list:
            file_path = os.path.join(folder_path, file_name)
            extracted_data = extract_and_validate_peak_table(file_path, peak_table)

            if extracted_data.empty:
                continue  # Skip empty datasets

            extracted_data["Source File"] = file_name
            extracted_data["R.Time"] = pd.to_numeric(extracted_data["R.Time"], errors="coerce")

            # Sort R.Time within each dataset
            extracted_data = extracted_data.sort_values(by="R.Time", ascending=True)

            combined_data = pd.concat([combined_data, extracted_data], ignore_index=True)

        if combined_data.empty:
            raise ValueError("No valid data found in the selected files.")

        # Generate new hierarchy with R.Time embedded
        combined_data = generate_hierarchy_column(combined_data)

        # Sort using the new hierarchy, which includes R.Time
        combined_data = combined_data.sort_values(by=["Hierarchy"], ascending=True)

        return combined_data

    except Exception as e:
        raise RuntimeError(f"Error processing files: {e}")


def process_and_filter_file(input_data, target_r_times, tolerance, compound_mapping):
    """
    Filters and restructures data based on the largest peak area within specified R.Time values.

    :param input_data: DataFrame containing combined data.
    :param target_r_times: List of target R.Time values to filter around.
    :param tolerance: Tolerance range for filtering.
    :param compound_mapping: Dictionary mapping target R.Time values to compound names.
    :return: Filtered and restructured DataFrame.
    """
    try:
        # Ensure numeric conversion
        input_data['R.Time'] = pd.to_numeric(input_data['R.Time'], errors='coerce')
        input_data['Area'] = pd.to_numeric(input_data['Area'], errors='coerce')

        # Ensure deep copy to avoid SettingWithCopyWarning
        input_data = input_data.copy()

        # Assign Target R.Time for filtering
        input_data['Target R.Time'] = input_data['R.Time'].apply(
            lambda x: next((target for target in target_r_times if abs(x - target) <= tolerance), None)
        )
        input_data = input_data.dropna(subset=['Target R.Time'])

        # Ensure Compound column is created before filtering
        input_data.loc[:, "Compound"] = input_data["Target R.Time"].map(compound_mapping)

        # Ensure Hierarchy column exists before pivoting
        if 'Hierarchy' not in input_data.columns:
            raise ValueError("Hierarchy column missing before filtering")

        # Group and select largest Area
        grouped = input_data.groupby(['Source File', 'Target R.Time'])
        largest_area_idx = grouped['Area'].idxmax()
        filtered_data = input_data.loc[largest_area_idx]

        # Keep necessary columns, including Hierarchy
        filtered_data = filtered_data[['Source File', 'R.Time', 'Compound', 'Area', 'Hierarchy']]

        # Pivot Data while retaining Hierarchy
        pivoted_data = filtered_data.pivot(index=['Source File', 'Hierarchy'], columns='Compound', values='Area').reset_index()
        pivoted_data.columns.name = None
        pivoted_data = pivoted_data.rename(columns={f"{compound}": f"{compound} Area" for compound in compound_mapping.values()})

        # Merge R.Time and Hierarchy for reference
        pivoted_data = pd.merge(
            pivoted_data,
            filtered_data[['Source File', 'R.Time', 'Hierarchy']].drop_duplicates(),
            on=['Source File', 'Hierarchy'],
            how='left'
        )

        return pivoted_data

    except Exception as e:
        raise RuntimeError(f"Error filtering and restructuring data: {e}")