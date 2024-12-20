import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def generate_excel_sheets(combined_data, filtered_data, output_file):
    """
    Generate an Excel file with the provided data and save it to the specified output file.
    Ensures the sheet order: PO, Amino Alcohol, Diglyme.

    :param combined_data: DataFrame for the combined output.
    :param filtered_data: DataFrame for the filtered data.
    :param output_file: Path to save the Excel file.
    """
    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        # Sort the filtered_data columns to ensure the correct order of compounds
        filtered_data = filtered_data[['Source File', 'PO Area', 'Amino Alcohol Area', 'Diglyme Area']]

        # Write data to Excel
        combined_data.to_excel(writer, sheet_name="Combined Output", index=False)
        filtered_data.to_excel(writer, sheet_name="Filtered Data", index=False)