import pandas as pd
import logging
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def calculate_concentration(filtered_data, compound_mapping, diglyme_amount=0.00014):
    """
    Calculates concentrations for PO and MIPA using Diglyme as an internal standard.

    :param filtered_data: DataFrame containing the filtered data.
    :param compound_mapping: A dictionary mapping Target R.Time values to compound names.
    :param diglyme_amount: The known amount of Diglyme (default: 0.00014).
    :return: DataFrame with concentrations calculated and a summary DataFrame.
    """
    try:
        filtered_data = filtered_data.copy()

        # Map Target R.Time to compound names
        filtered_data['Compound'] = filtered_data['Target R.Time'].map(compound_mapping).fillna("Unknown")

        # Extract collection time from Source File
        def extract_collection_time(filename):
            match = re.search(r'-(\\d+\\.\\d+)ct-', filename)
            return float(match.group(1)) if match else None

        filtered_data['Collection Time'] = filtered_data['Source File'].apply(extract_collection_time)

        # Convert relevant columns to numeric
        filtered_data['Area'] = pd.to_numeric(filtered_data['Area'], errors='coerce')
        filtered_data['Collection Time'] = pd.to_numeric(filtered_data['Collection Time'], errors='coerce')

        # Extract Diglyme area
        diglyme_areas = filtered_data[filtered_data['Compound'] == 'Diglyme'].set_index('Source File')['Area']

        # Relative response factors
        relative_response_factors = {'PO': 0.42, 'MIPA': 0.5}

        # Calculate concentrations
        def calculate(row):
            if row['Compound'] in relative_response_factors:
                rrf = relative_response_factors[row['Compound']]
                diglyme_area = diglyme_areas.get(row['Source File'], None)
                collection_time = row['Collection Time']

                if pd.notna(diglyme_area) and diglyme_area > 0 and pd.notna(collection_time) and collection_time > 0:
                    return row['Area'] / diglyme_area / rrf * diglyme_amount / collection_time
            return None

        filtered_data['Concentration'] = filtered_data.apply(calculate, axis=1)

        # Generate summary for concentrations
        summary = filtered_data[filtered_data['Compound'].isin(['PO', 'MIPA'])]
        summary = summary.pivot(index='Source File', columns='Compound', values='Concentration').reset_index()

        return filtered_data, summary

    except Exception as e:
        logging.error(f"Error during concentration calculation: {e}")
        raise