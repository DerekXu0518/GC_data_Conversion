import os
from combined_processor import process_and_separate_files_naturally_sorted, process_and_filter_file
from calculate_concentration import calculate_and_update_concentration_with_ct
from tkinter import Tk
from tkinter.filedialog import askdirectory


def select_folder():
    root = Tk()
    root.withdraw()  # Hide the main tkinter window
    folder_path = askdirectory(title="Select the folder containing the files.")
    return folder_path


def main():
    # Step 1: Let the user select a folder
    folder_path = select_folder()
    if not folder_path:
        print("No folder selected. Exiting.")
        return

    # Step 2: Set the peak table identifier
    peak_table = 'Ch1'

    # Step 3: Process files with natural sorting and store in memory
    print("Processing files with natural sorting...")
    combined_data = process_and_separate_files_naturally_sorted(folder_path, peak_table)

    # Debugging combined data
    if combined_data is None or combined_data.empty:
        print("Debug: Combined data is empty or invalid.")
        raise ValueError("Combined data is empty or invalid. Check the input files or processing logic.")

    print("Debug: Combined data columns:", combined_data.columns)
    print("Debug: Combined data sample:\n", combined_data.head())

    if 'R.Time' not in combined_data.columns:
        raise ValueError("'R.Time' column missing in combined data. Check the input files or processing logic.")

    # Step 4: Filter the combined data in memory
    print("Filtering data based on R.Time values 1.6, 2.3, and 3.6...")
    target_r_times = [1.6, 2.3, 3.6]
    tolerance = 0.1  # Define the tolerance
    filtered_data = process_and_filter_file(combined_data, target_r_times, tolerance)

    # Debug filtered data
    if filtered_data is None or filtered_data.empty:
        print("Debug: Filtered data is empty. Exiting.")
        raise ValueError("Filtered data is empty. Check the input files or filtering logic.")

    print("Debug: Filtered data columns:", filtered_data.columns)
    print("Debug: Filtered data sample:\n", filtered_data.head())

    # Step 5: Calculate and update concentrations and generate Excel file
    print("Calculating concentrations and updating filtered data...")
    compound_mapping = {1.6: "PO", 2.3: "MIPA", 3.6: "Diglyme"}
    output_excel_file = os.path.join(folder_path, "processed_output.xlsx")
    calculate_and_update_concentration_with_ct(
        combined_data=combined_data,
        filtered_data=filtered_data,
        compound_mapping=compound_mapping,
        output_file=output_excel_file
    )


if __name__ == "__main__":
    main()