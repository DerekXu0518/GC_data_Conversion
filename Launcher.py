import os
from tkinter import Tk
from tkinter.filedialog import askdirectory
import logging
from data_processor import process_and_separate_files_naturally_sorted, process_and_filter_file
from generate_excel import generate_excel_sheets

# Configure logging
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
        logging.error("No valid data found in the selected files. Ensure the input files are correctly formatted.")
        return

    # Step 4: Filter combined data
    logging.info("Filtering data based on R.Time values 1.6, 2.3, and 3.6...")
    target_r_times = [1.6, 2.3, 3.6]
    compound_mapping = {1.6: "PO", 2.3: "MIPA", 3.6: "Diglyme"}
    tolerance = 0.1
    filtered_data = process_and_filter_file(combined_data, target_r_times, tolerance, compound_mapping)

    if filtered_data.empty:
        logging.error("No matching R.Time data found after filtering. Check the target R.Time values or input data.")
        return

    logging.info("Data filtered successfully.")

    # Step 5: Skip concentration calculation
    logging.info("Skipping concentration calculation. Output will only include combined and filtered data.")

    # Step 6: Save results to Excel
    output_excel_file = os.path.join(folder_path, "processed_output.xlsx")
    generate_excel_sheets(combined_data, filtered_data, output_file=output_excel_file)
    logging.info(f"Data successfully saved to Excel: {output_excel_file}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"An error occurred during processing: {e}")