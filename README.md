# **GC Data Conversion**

A Python-based tool for processing, filtering, and analyzing GC (Gas Chromatography) data. This tool allows users to extract peak table data, filter based on retention times, calculate concentrations using internal standards, and export the results to a structured Excel file.

---

## **Features**

1. **File Processing**:
   - Reads and processes GC data files with natural sorting.
   - Extracts peak table data from specified sections in `.TXT` files.

2. **Data Filtering**:
   - Filters data based on target retention times (`R.Time`) with a configurable tolerance.
   - Automatically selects the largest peak for each retention time in each file.

3. **Concentration Calculation**:
   - Calculates concentrations for compounds using Diglyme as the internal standard.
   - Supports customizable relative response factors (RRFs) and Diglyme amounts.

4. **Excel Export**:
   - Exports processed data into a single Excel file with three sheets:
     - **Combined Output**: All processed data.
     - **Filtered Data**: Filtered rows based on retention times.
     - **Summary**: Concentration data for compounds.

---

## **Requirements**

- Python 3.8+
- Required Python packages:
  - `pandas`
  - `openpyxl`
  - `xlsxwriter`
  - `tkinter` (built-in with Python)

To install missing packages, run:
```bash
pip install pandas openpyxl xlsxwriter

## **Usage**

### **Step 1: Prepare Your Files**
- Ensure your GC data files are in `.TXT` format and stored in a folder.
- The filenames must include collection time information in the format `*-X.Xct-*` (e.g., `20241202-0.1PO-1NH3-0.2ct-20.0min.TXT`).

### **Step 2: Run the Tool**
1. Open a terminal and navigate to the project directory.
2. Run the `Launcher.py` script:
   ```bash
   python Launcher.py

### **Step 3: Follow the Prompts**
- A file dialog will appear, prompting you to select the folder containing your GC data files.
- The tool will process the files with the following steps:
  1. Extract data from `.TXT` files with natural sorting.
  2. Filter data based on specified retention times (`1.6`, `2.3`, `3.6`).
  3. Calculate concentrations using Diglyme as an internal standard.
- The results will be saved in an Excel file with three sheets:
  - **Combined Output**: Contains all processed data.
  - **Filtered Data**: Includes rows filtered by retention times.
  - **Summary**: Displays calculated concentrations for compounds.

## **Output**

The tool saves the results as an Excel file in the same folder as the input data. The output file is named `processed_output.xlsx` and includes the following sheets:

1. **Combined Output**:
   - Contains all extracted and processed data, including columns like `R.Time`, `Area`, `Height`, and `Source File`.

2. **Filtered Data**:
   - Displays rows filtered by retention times (`1.6`, `2.3`, `3.6`), with the largest peak for each retention time in each dataset.

3. **Summary**:
   - Shows calculated concentrations for compounds (`PO`, `MIPA`, and `Diglyme`) based on the filtered data, using Diglyme as the internal standard.

## **Configuration**

### **Peak Table Identifier**
- The default peak table identifier is `'Ch1'`.
- You can modify this by updating the `peak_table` variable in the `Launcher.py` file.

### **Retention Times**
- The tool filters data based on the following default retention times and tolerance:
  ```python
  target_r_times = [1.6, 2.3, 3.6]
  tolerance = 0.1

- These values can be changed in the `Launcher.py` file.

### **Relative Response Factors (RRFs)**
- The default relative response factors and Diglyme amount are set in the `calculate_concentration.py` file:
  ```python
  relative_response_factors = {'PO': 0.42, 'MIPA': 0.5}
  diglyme_amount = 0.00014

## **Troubleshooting**

### **Common Issues**

1. **No Files Found**:
   - Ensure the selected folder contains `.TXT` files with properly formatted data.

2. **Missing `R.Time` Column**:
   - Check the input file format to ensure the `R.Time` column is included in the extracted data.

3. **Filtered Data is Empty**:
   - Adjust the retention times or the tolerance value in the configuration to match the data in the input files.

---

## **Acknowledgments**

This tool was developed to streamline the processing and analysis of GC data files, providing an efficient and user-friendly solution for handling and analyzing chromatographic data.
