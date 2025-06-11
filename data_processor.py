import os
import pandas as pd
import re
from file_extractor import extract_and_validate_peak_table
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def generate_hierarchy_column(data):
    """
    Generates a hierarchy column for sorting based on Source File and R.Time.
    Ensures numeric values are properly sorted within hierarchical structure.
    """

    def extract_sort_key(string):
        """
        Extracts a hierarchical sort key from the source file name.
        Splits on dashes and creates a uniform tuple of (type_flag, value) pairs:
          - type_flag = 0 for numbers, 1 for text.
          - value = int(number) or lowercase string.
        """

        parts = string.split('-')
        sort_key = []

        for part in parts:
            # Pull out any sequences of digits…
            num_matches = re.findall(r'\d+', part)
            # …and any leftover letters
            non_num_part = re.sub(r'\d+', '', part).lower()

            if num_matches and non_num_part:
                # “Mixed” segment like “10RT”: first the numbers, then the letters
                for nm in num_matches:
                    sort_key.append((0, int(nm)))
                sort_key.append((1, non_num_part))
            elif num_matches:
                # Purely numeric segment
                for nm in num_matches:
                    sort_key.append((0, int(nm)))
            elif non_num_part:
                # Purely text segment
                sort_key.append((1, non_num_part))

        return tuple(sort_key)

    # Generate hierarchy based on the Source File first
    data['Hierarchy'] = data['Source File'].map(extract_sort_key)

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

        # Generate new hierarchy for sorting
        combined_data = generate_hierarchy_column(combined_data)

        # Sort using the new hierarchy
        combined_data = combined_data.sort_values(by=["Hierarchy", "R.Time"], ascending=True)

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
        # Ensure R.Time is numeric and drop invalid entries to avoid type comparison errors
        input_data["R.Time"] = pd.to_numeric(input_data["R.Time"], errors="coerce")
        input_data = input_data.dropna(subset=["R.Time"])
        if "R.Time" not in input_data.columns or "Area" not in input_data.columns:
            raise ValueError("Missing required columns: 'R.Time' or 'Area'")

        # Convert Area to numeric to prevent string comparison issues
        input_data["Area"] = pd.to_numeric(input_data["Area"], errors="coerce")

        # Step 1: Apply tolerance filtering to find relevant R.Time values
        filtered = input_data[
            input_data["R.Time"].apply(lambda x: any(abs(x - target) <= tolerance for target in target_r_times))
        ].copy()

        if filtered.empty:
            logging.warning("No matching R.Time… returning zeros.")
            # use the pivot logic to build a zero‐row
            zero_df = pd.DataFrame([{"Source File": None, **{c: 0 for c in compound_mapping.values()}}])
            zero_df["Hierarchy"] = ()  # so subsequent sort/drop won't fail
            return zero_df.drop(columns=["Hierarchy"])

        # Step 2: Assign nearest target R.Time for each filtered entry
        filtered["Target R.Time"] = filtered["R.Time"].apply(
            lambda x: min(target_r_times, key=lambda target: abs(x - target))
        )

        # Step 3: Map R.Time values to compound names
        filtered["Compound"] = filtered["Target R.Time"].map(compound_mapping)

        # Ensure compound order is consistent and sorted
        compound_order = sorted(filtered["Compound"].unique(), key=lambda x: (x is None, x))
        filtered["Compound"] = pd.Categorical(filtered["Compound"], categories=compound_order, ordered=True)

        # Step 4: Select the highest area peak for each compound per dataset
        filtered = filtered.sort_values(by=["Source File", "Compound", "Area"], ascending=[True, True, False])

        # **Fixing the duplicate issue**: Group by "Source File" and "Compound" to ensure unique entries
        filtered = filtered.groupby(["Source File", "Compound"], as_index=False).first()

        # Merge hierarchy from input_data so that 'Hierarchy' exists in filtered
        filtered = filtered.merge(
            input_data[['Source File', 'Hierarchy']].drop_duplicates(),
            on='Source File',
            how='left'
        )

        # Step 5: Create full set of source-compound pairs
        source_files = filtered["Source File"].unique()
        compound_names = list(compound_mapping.values())
        all_combinations = pd.MultiIndex.from_product([source_files, compound_names], names=["Source File", "Compound"])

        # Set index for filtered to prepare for reindexing
        filtered.set_index(["Source File", "Compound"], inplace=True)
        filtered = filtered.reindex(all_combinations, fill_value=0).reset_index()

        # Merge hierarchy again after reindex
        filtered = filtered.merge(
            input_data[['Source File', 'Hierarchy']].drop_duplicates(),
            on='Source File',
            how='left'
        )

        # Pivot the table with all expected compounds
        pivoted_data = filtered.pivot_table(
            index=["Source File", "Hierarchy"],
            columns="Compound",
            values="Area",
            aggfunc="first",
            fill_value=0
        ).reset_index()

        # Sort based on hierarchy and remove the hierarchy column before exporting
        return pivoted_data.sort_values(by=["Hierarchy"], ascending=True).drop(columns=["Hierarchy"], errors="ignore")

    except Exception as e:
        logging.error(f"Error filtering and restructuring data: {e}")
        return pd.DataFrame()