import pandas as pd
import logging
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def calculate_and_update_concentration_with_ct(
    combined_data, filtered_data, compound_mapping, output_file, diglyme_amount=0.00014
):
    """
    Calculates concentrations for PO and MIPA using Diglyme as an internal standard,
    and writes the results to an Excel file.

    :param combined_data: DataFrame containing the combined data.
    :param filtered_data: DataFrame containing the pre-filtered data.
    :param compound_mapping: A dictionary mapping Target R.Time values to compound names.
    :param output_file: Path to save the resulting Excel file.
    :param diglyme_amount: The known amount of Diglyme (default: 0.00014).
    """
    try:
        # Ensure filtered_data is explicitly a copy to avoid SettingWithCopyWarning
        filtered_data = filtered_data.copy()

        # Map Target R.Time to compound names
        filtered_data['Compound'] = filtered_data['Target R.Time'].map(compound_mapping).fillna("Unknown")

        # Extract collection time from Source File name
        def extract_collection_time(filename):
            match = re.search(r'-(\d+\.\d+)ct-', filename)
            return float(match.group(1)) if match else None

        filtered_data['Collection Time'] = filtered_data['Source File'].apply(extract_collection_time)

        # Ensure collection time is valid
        if filtered_data['Collection Time'].isnull().any():
            raise ValueError("Collection time could not be extracted from one or more source file names.")

        # Convert Area and Collection Time to numeric
        filtered_data['Area'] = pd.to_numeric(filtered_data['Area'], errors='coerce')
        filtered_data['Collection Time'] = pd.to_numeric(filtered_data['Collection Time'], errors='coerce')

        # Extract Diglyme area for each Source File
        diglyme_areas = filtered_data[filtered_data['Compound'] == 'Diglyme'].set_index('Source File')['Area']

        if diglyme_areas.empty:
            raise ValueError("Diglyme area is missing from the data.")

        # Relative response factors
        relative_response_factors = {
            'PO': 0.42,
            'MIPA': 0.5,
        }

        # Calculate concentrations for PO and MIPA
        def calculate_concentration(row):
            if row['Compound'] in relative_response_factors:
                rrf = relative_response_factors[row['Compound']]
                diglyme_area = diglyme_areas.get(row['Source File'], None)
                collection_time = row['Collection Time']

                # Ensure values are valid
                if pd.notna(diglyme_area) and diglyme_area > 0 and pd.notna(collection_time) and collection_time > 0:
                    return row['Area'] / diglyme_area / rrf * diglyme_amount / collection_time
            return None

        filtered_data['Concentration'] = filtered_data.apply(calculate_concentration, axis=1)

        # Prepare data for second sheet: Summarized concentrations
        summary = filtered_data[filtered_data['Compound'].isin(['PO', 'MIPA'])]  # Filter PO and MIPA rows
        summary = summary.pivot(index='Source File', columns='Compound', values='Concentration').reset_index()

        # Save to an Excel file with three sheets
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            combined_data.to_excel(writer, sheet_name='Combined Output', index=False)
            filtered_data.to_excel(writer, sheet_name='Filtered Data', index=False)
            summary.to_excel(writer, sheet_name='Summary', index=False)

        logging.info(f"Updated data with concentrations saved to: {output_file}")

    except Exception as e:
        logging.error(f"Error during concentration calculation: {e}")
        raise