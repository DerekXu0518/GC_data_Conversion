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
