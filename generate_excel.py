import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def generate_excel_sheets(combined_data, filtered_data, summary, output_file):
    """
    Saves the provided data into an Excel file with separate sheets.

    :param combined_data: DataFrame for the combined output.
    :param filtered_data: DataFrame for the filtered output.
    :param summary: DataFrame for the summary output.
    :param output_file: Path to save the Excel file.
    """
    try:
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            combined_data.to_excel(writer, sheet_name='Combined Output', index=False)
            filtered_data.to_excel(writer, sheet_name='Filtered Data', index=False)
            summary.to_excel(writer, sheet_name='Summary', index=False)

    except Exception as e:
        logging.error(f"Error saving data to Excel: {e}")
        raise