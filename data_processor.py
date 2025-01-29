import os
import pandas as pd
import re
from file_extractor import extract_and_validate_peak_table
import logging


def generate_hierarchy_column(data):
    """
    Generates a hierarchy column for sorting based on Source File and R.Time.
    Ensures numeric values are properly sorted within hierarchical structure.
    """

    def extract_sort_key(string):
        """
        Extracts a hierarchical sort key from the source file name.
        - Splits by dashes ("-") and sorts numbers numerically while keeping text-based identifiers.
        """
        parts = string.split('-')
        sort_key = []

        for part in parts:
            num_matches = re.findall(r'\d+', part)  # Extract all numeric values
            non_num_part = re.sub(r'\d+', '', part).lower()  # Extract non-numeric text

            if num_matches:
                sort_key.extend([int(num) for num in num_matches])  # Convert numbers to integers for sorting
            if non_num_part:
                sort_key.append(non_num_part)  # Keep text parts in order

        return tuple(sort_key)

    # Generate hierarchy based on the Source File first
    data['Hierarchy'] = data['Source File'].map(extract_sort_key)

    # Append R.Time to the hierarchy for final sorting
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
    Filters and processes GC data to retain only the highest peak for each compound in each dataset.

    :param input_data: DataFrame containing the combined data.
    :param target_r_times: List of target R.Time values.
    :param tolerance: Tolerance range for filtering.
    :param compound_mapping: Dictionary mapping R.Time to compound names.
    :return: Filtered DataFrame with one row per dataset.
    """
    try:
        if "R.Time" not in input_data.columns or "Area" not in input_data.columns:
            raise ValueError("Missing required columns: 'R.Time' or 'Area'")

        # Convert Area to numeric to prevent string comparison issues
        input_data["Area"] = pd.to_numeric(input_data["Area"], errors="coerce")

        # Step 1: Apply tolerance filtering to find relevant R.Time values
        filtered = input_data[
            input_data["R.Time"].apply(lambda x: any(abs(x - target) <= tolerance for target in target_r_times))
        ].copy()

        if filtered.empty:
            logging.warning("No matching R.Time data found after filtering.")
            return pd.DataFrame()

        # Step 2: Assign nearest target R.Time for each filtered entry
        filtered["Target R.Time"] = filtered["R.Time"].apply(
            lambda x: min(target_r_times, key=lambda target: abs(x - target))
        )

        # Step 3: Map R.Time values to compound names
        filtered["Compound"] = filtered["Target R.Time"].map(compound_mapping)

        # Ensure compounds are in the correct order (PO, MIPA, Diglyme)
        compound_order = ["PO", "MIPA", "Diglyme"]
        filtered["Compound"] = pd.Categorical(filtered["Compound"], categories=compound_order, ordered=True)

        # Step 4: Select the highest area peak for each compound per dataset
        filtered = filtered.sort_values(by=["Source File", "Compound", "Area"], ascending=[True, True, False])

        # **Fixing the duplicate issue**: Group by "Source File" and "Compound" to ensure unique entries
        filtered = filtered.groupby(["Source File", "Compound"], as_index=False).first()

        # Step 5: Pivot table to ensure one row per dataset
        pivoted_data = filtered.pivot(index="Source File", columns="Compound", values="Area").reset_index()

        # Rename columns for clarity
        pivoted_data.rename(columns={"PO": "PO Area", "MIPA": "MIPA Area", "Diglyme": "Diglyme Area"}, inplace=True)

        # Step 6: Merge with hierarchy for final sorting
        hierarchy_data = input_data[['Source File', 'Hierarchy']].drop_duplicates()
        pivoted_data = pivoted_data.merge(hierarchy_data, on="Source File", how="left")

        # Sort based on hierarchy
        pivoted_data = pivoted_data.sort_values(by=["Hierarchy"], ascending=True)

        # **Final Fix:** Remove duplicates again just in case
        pivoted_data = pivoted_data.drop_duplicates(subset=["Source File"])

        # Remove the hierarchy column before exporting
        return pivoted_data.drop(columns=["Hierarchy"], errors="ignore")

    except Exception as e:
        logging.error(f"Error filtering and restructuring data: {e}")
        return pd.DataFrame()