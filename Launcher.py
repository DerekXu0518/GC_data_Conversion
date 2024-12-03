import os
from combined_processor import process_and_separate_files_naturally_sorted, process_and_filter_file
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

    # Step 2: Set the output file locations
    combined_output_csv = os.path.join(folder_path, "combined_output_with_separators.csv")
    filtered_output_csv = os.path.join(folder_path, "filtered_output.csv")

    # Step 3: Set the peak table identifier
    peak_table = 'Ch1'

    # Step 4: Automatically process with natural sorting
    print("Processing files with natural sorting...")
    process_and_separate_files_naturally_sorted(folder_path, combined_output_csv, peak_table)

    # Step 5: Automatically filter the combined CSV
    print(f"Generating filtered CSV based on R.Time values 1.6, 2.3, and 3.6...")
    target_r_times = [1.6, 2.3, 3.6]
    tolerance = 0.1  # Define the tolerance

    process_and_filter_file(combined_output_csv, target_r_times, tolerance, filtered_output_csv)


if __name__ == "__main__":
    main()
