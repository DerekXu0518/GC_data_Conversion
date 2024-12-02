import os
from natural_sort_processor import process_and_separate_files_naturally_sorted
from peak_table_processor import process_and_separate_files, select_folder

def main():
    print("Choose a processing method:")
    print("1: Process files in alphabetical order")
    print("2: Process files with natural sorting (handles decimals)")
    choice = input("Enter your choice (1 or 2): ").strip()

    # Step 1: Let the user select a folder
    folder_path = select_folder()
    if not folder_path:
        print("No folder selected. Exiting.")
        return

    # Step 2: Set the output file location
    output_csv = os.path.join(folder_path, "combined_output_with_separators.csv")

    # Step 3: Ask for the peak table identifier
    peak_table = input("Enter the peak table identifier (default 'Ch1'): ").strip() or 'Ch1'

    # Step 4: Process based on the user's choice
    if choice == "1":
        process_and_separate_files(folder_path, output_csv, peak_table)
    elif choice == "2":
        process_and_separate_files_naturally_sorted(folder_path, output_csv, peak_table)
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()