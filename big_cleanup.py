import pandas as pd
import numpy as np
import json
import os
from pathlib import Path

# ---------------- FLATTEN HEADERS ---------------- #
def flatten_xlsx_headers(xlsx_path, output_csv, dict_json):
    df_raw = pd.read_excel(xlsx_path, header=[0, 1, 2])
    header_df = pd.DataFrame(df_raw.columns.tolist())
    header_df = header_df.fillna(method="ffill", axis=1)

    merged_headers = []
    for row in header_df.itertuples(index=False, name=None):
        parts = [str(x).strip() for x in row if pd.notna(x) and not str(x).startswith("Unnamed")]
        long_name = " | ".join(parts)
        merged_headers.append(long_name)

    prefix_map = {
        "Total Geographical Area": "TGA",
        "Recharge Worthy Area": "RWA",
        "Ground Water Recharge": "GWR",
        "Inflows and Outflows": "IFO",
        "Annual Ground water Recharge": "AGR",
        "Environmental Flows": "EFR",
        "Annual Extractable Ground water Resource": "AER",
        "Ground Water Extraction": "GWE",
        "Stage of Ground Water Extraction": "SGE",
        "Allocation of Ground Water Resource": "DOM",
        "Net Annual Ground Water Availability": "NAG",
        "Quality Tagging": "QT",
        "Additional Potential Resources": "APR",
        "Coastal Areas": "CSA",
        "Unconfined": "UCA",
        "Confined": "CFA",
        "Semi Confined": "SCA",
        "Total Ground Water Availability": "TGAH"
    }

    sub_map = {
        "Rainfall": "RR", "Canals": "CI", "Surface Water": "SWI", "Ground Water Irrigation": "GWI",
        "Tanks": "TP", "Conservation": "WCS", "Pipelines": "PL", "Sewages": "SF",
        "Base Flow": "BF", "Stream Recharges": "SR", "Lateral Flows": "LF", "Vertical Flows": "VF",
        "Evaporation": "EV", "Transpiration": "TR", "Evapotranspiration": "ET",
        "Domestic": "DOM", "Industrial": "IND", "Irrigation": "IRR",
        "Major Parameter Present": "MP", "Other Parameters Present": "OP",
        "Waterlogged": "WL", "Flood Prone": "FP", "Spring Discharge": "SD",
        "Fresh": "FR", "Saline": "SL"
    }

    def make_short(name: str) -> str:
        prefix = ""
        for key, val in prefix_map.items():
            if key in name:
                prefix = val
                break
            
        code_parts = [val for key, val in sub_map.items() if key in name]
    
        # Handle suffixes
        if name.endswith("C"): code_parts.append("C")
        if name.endswith("NC"): code_parts.append("NC")
        if name.endswith("PQ"): code_parts.append("PQ")
        if name.endswith("Total"): code_parts.append("Tot")
    
        if prefix and code_parts:
            return prefix + "_" + "_".join(code_parts)
        elif prefix:
            return prefix
        elif code_parts:
            return "_".join(code_parts)
        else:
            return name.replace(" ", "")
    
    
    short_headers = []
    header_map = {}
    for long_name in merged_headers:
        short_name = make_short(long_name)
        short_headers.append(short_name)
        header_map[short_name] = long_name

    df_raw.columns = short_headers
    df_raw.to_csv(output_csv, index=False)
    with open(dict_json, "w") as f:
        json.dump(header_map, f, indent=4)

    print(f"✅ Flattened CSV saved as {output_csv}")
    print(f"✅ Header dictionary saved as {dict_json}")

# ---------------- CLEAN NULLS ---------------- #
def replace_zeros_and_blanks(csv_in, csv_out):
    df = pd.read_csv(csv_in, dtype=object)
    replaced = {"count": 0}

    def fix_cell(x):
        if pd.isna(x):
            replaced["count"] += 1
            return "NA"
        s = str(x).strip()
        if s == "":
            replaced["count"] += 1
            return "NA"
        s_clean = s.replace(",", "")
        try:
            val = float(s_clean)
            if val == 0.0:
                replaced["count"] += 1
                return "NA"
            return s
        except Exception:
            return s

    df_clean = df.applymap(fix_cell)
    df_clean.to_csv(csv_out, index=False)
    print(f"✅ Cleaned CSV saved as {csv_out}")

# ---------------- PIPELINE ---------------- #
def process_pipeline(input_folder, flattened_folder, cleaned_folder):
    os.makedirs(flattened_folder, exist_ok=True)
    os.makedirs(cleaned_folder, exist_ok=True)

    for file in Path(input_folder).glob("*.xlsx"):
        base = file.stem

        # Step 1: Flatten
        flattened_csv = Path(flattened_folder) / f"{base}.csv"
        dict_json = Path(flattened_folder) / f"{base}_header_map.json"
        flatten_xlsx_headers(file, flattened_csv, dict_json)

        # Step 2: Clean
        cleaned_csv = Path(cleaned_folder) / f"{base}_cleaned.csv"
        replace_zeros_and_blanks(flattened_csv, cleaned_csv)

# ---------------- MAIN ---------------- #
if __name__ == "__main__":
    # 👇 just change these three folder names as needed
    input_folder = "raw_xlsx_data"
    flattened_folder = "header_flat_csv"
    cleaned_folder = "clean_csv"

    process_pipeline(input_folder, flattened_folder, cleaned_folder)
