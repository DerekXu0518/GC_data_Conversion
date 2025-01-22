import pandas as pd

def generate_excel_sheets(combined_data, filtered_data, output_file):
    """
    Save combined and filtered data to an Excel file, using the Hierarchy column for sorting.

    :param combined_data: DataFrame containing combined data.
    :param filtered_data: DataFrame containing filtered data.
    :param output_file: Path to the output Excel file.
    """
    try:
        # Ensure 'Hierarchy' and 'R.Time' sorting
        combined_data = combined_data.sort_values(by=['Hierarchy', 'R.Time'], ascending=[True, True])
        filtered_data = filtered_data.sort_values(by=['Hierarchy', 'R.Time'], ascending=[True, True])

        # Drop the Hierarchy column before exporting
        combined_data = combined_data.drop(columns=['Hierarchy'])
        filtered_data = filtered_data.drop(columns=['Hierarchy'])

        # Write data to Excel
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            combined_data.to_excel(writer, sheet_name="Combined Data", index=False)
            filtered_data.to_excel(writer, sheet_name="Filtered Data", index=False)

    except Exception as e:
        raise RuntimeError(f"Error saving data to Excel: {e}")