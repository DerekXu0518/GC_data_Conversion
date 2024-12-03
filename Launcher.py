import os
from tkinter import Tk
from tkinter.filedialog import askdirectory
import logging
from data_processor import process_and_separate_files_naturally_sorted, process_and_filter_file
from calculate_concentration import calculate_concentration
from generate_excel import generate_excel_sheets

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def select_folder():
    """
    Opens a dialog for the user to select a folder containing files to process.

    :return: The selected folder path or None if no folder is selected.
    """
    Tk().withdraw()  # Hide the root tkinter window
    return askdirectory(title="Select the folder containing the files")

def main():
    # Step 1: Select folder
    folder_path = select_folder()
    if not folder_path or not os.path.exists(folder_path) or not os.listdir(folder_path):
        logging.error("The selected folder does not exist or is empty. Exiting.")
        return

    # Step 2: Set peak table identifier
    peak_table = 'Ch1'
    logging.info(f"Using default peak table identifier: {peak_table}")

    # Step 3: Process files with natural sorting
    logging.info("Processing files with natural sorting...")
    combined_data = process_and_separate_files_naturally_sorted(folder_path, peak_table)

    if combined_data.empty:
        raise ValueError("No valid data found in the selected files. Ensure the input files are correctly formatted.")

    # Step 4: Filter combined data
    logging.info("Filtering data based on R.Time values 1.6, 2.3, and 3.6...")
    target_r_times = [1.6, 2.3, 3.6]
    tolerance = 0.1
    filtered_data = process_and_filter_file(combined_data, target_r_times, tolerance)

    if filtered_data.empty:
        raise ValueError("No matching R.Time data found after filtering. Check the target R.Time values or input data.")

    logging.info("Data filtered successfully.")

    # Step 5: Calculate concentrations
    logging.info("Calculating concentrations and updating filtered data...")
    compound_mapping = {1.6: "PO", 2.3: "MIPA", 3.6: "Diglyme"}
    filtered_data, summary = calculate_concentration(filtered_data, compound_mapping)

    # Step 6: Save results to Excel
    output_excel_file = os.path.join(folder_path, "processed_output.xlsx")
    generate_excel_sheets(combined_data, filtered_data, summary, output_excel_file)
    logging.info(f"Data successfully saved to Excel: {output_excel_file}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"An error occurred during processing: {e}")