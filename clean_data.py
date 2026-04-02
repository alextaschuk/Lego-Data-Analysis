"""
Cleans raw Rebrickable CSVs and writes sanitized versions to `data/clean/`.

Changes applied per CSV file:
    colors: Drops extra stat columns (num_parts, num_sets, y1, y2) and converts `is_trans` from True/False to 1/0
    themes: Converts empty `parent_id`s (empty string in CSV) to NULL
    sets: Drops `img_url`
    inventory_sets: No cleaning needed
    inventory_parts: Drops `img_url` and converts `is_spare` from True/False to 1/0

NOTE: We use the bulk copy program utility (bcp) to copy the data in the CSV files to our Azure SQL database.
bcp doesn't handle CSV quoting (e.g, the row `777,"Bags, Totes, & Luggage",501`) will be split on every comma. 
To fix this, during cleaning, the headers are stripped from the input, and the cleaned data is writted to a TSV
file (tab separated, uses '\t' as the delimiter instead of ',').
"""

import csv
import os

RAW_DIR   = "data/raw"
CLEAN_DIR = "data/clean"

os.makedirs(CLEAN_DIR, exist_ok=True)

def bool_to_int(val: str) -> int:
    return 1 if val.strip().lower() == "true" else 0


def nullable(val: str) -> str:
    """
    Return empty string (written as
    NULL by the uploader) for blank values.
    """
    return val.strip()


def clean_colors():
    '''Clean the `colors.csv` file.'''
    in_path  = os.path.join(RAW_DIR, "colors.csv")
    out_path = os.path.join(CLEAN_DIR, "colors.tsv")
    cleaned_rows = 0

    with open(in_path, newline="", encoding="utf-8") as fin, \
         open(out_path, "w", newline="", encoding="utf-8") as fout:
        reader = csv.DictReader(fin)
        writer = csv.writer(fout, delimiter=' ')
        writer.writerow(["id", "name", "rgb", "is_trans"])

        for row in reader:
            writer.writerow([
                row["id"].strip(),
                row["name"].strip(),
                row["rgb"].strip(),
                bool_to_int(row["is_trans"]), # T/F is the brick transparent?
            ])
            cleaned_rows += 1

    print(f" colors: {cleaned_rows} rows written to {out_path}")


def clean_themes():
    '''Clean the `themes.csv` file.'''
    in_path  = os.path.join(RAW_DIR, "themes.csv")
    out_path = os.path.join(CLEAN_DIR, "themes.tsv")
    cleaned_rows = 0
    
    with open(in_path, newline="", encoding="utf-8") as fin, \
         open(out_path, "w", newline="", encoding="utf-8") as fout:
        reader = csv.DictReader(fin)
        writer = csv.writer(fout, delimiter=' ')
        writer.writerow(["id", "name", "parent_id"])
        
        for row in reader:
            writer.writerow([
                row["id"].strip(),
                row["name"].strip(),
                nullable(row["parent_id"]),
            ])
            cleaned_rows += 1

    print(f" themes: {cleaned_rows} rows written to {out_path}")


def clean_sets():
    '''Clean the `sets.csv` file.'''
    in_path  = os.path.join(RAW_DIR, "sets.csv")
    out_path = os.path.join(CLEAN_DIR, "sets.tsv")
    cleaned_rows = 0
    
    with open(in_path, newline="", encoding="utf-8") as fin, \
         open(out_path, "w", newline="", encoding="utf-8") as fout:
        reader = csv.DictReader(fin)
        writer = csv.writer(fout, delimiter=' ')
        writer.writerow(["set_num", "name", "year", "theme_id", "num_parts"])

        for row in reader:
            writer.writerow([
                row["set_num"].strip(),
                row["name"].strip(),
                row["year"].strip(),
                row["theme_id"].strip(),
                row["num_parts"].strip(),
            ])
            cleaned_rows += 1

    print(f" sets: {cleaned_rows} rows written to {out_path}")


def clean_inventory_sets():
    '''Clean the `inventory_sets.csv` file.'''
    in_path  = os.path.join(RAW_DIR,   "inventory_sets.csv")
    out_path = os.path.join(CLEAN_DIR, "inventory_sets.tsv")
    cleaned_rows = 0

    with open(in_path, newline="", encoding="utf-8") as fin, \
         open(out_path, "w", newline="", encoding="utf-8") as fout:
        reader = csv.DictReader(fin)
        writer = csv.writer(fout, delimiter=' ')
        writer.writerow(["inventory_id", "set_num", "quantity"])

        for row in reader:
            writer.writerow([
                row["inventory_id"].strip(),
                row["set_num"].strip(),
                row["quantity"].strip(),
            ])
            cleaned_rows += 1

    print(f" inventory_sets: {cleaned_rows} rows written to {out_path}")


def clean_inventory_parts():
    '''Clean the `inventory_parts.csv file.'''
    in_path  = os.path.join(RAW_DIR,   "inventory_parts.csv")
    out_path = os.path.join(CLEAN_DIR, "inventory_parts.tsv")
    cleaned_rows = 0

    with open(in_path, newline="", encoding="utf-8") as fin, \
         open(out_path, "w", newline="", encoding="utf-8") as fout:
        reader = csv.DictReader(fin)
        writer = csv.writer(fout, delimiter=' ')
        writer.writerow(["inventory_id", "part_num", "color_id", "quantity", "is_spare"])

        for row in reader:
            writer.writerow([
                row["inventory_id"].strip(),
                row["part_num"].strip(),
                row["color_id"].strip(),
                row["quantity"].strip(),
                bool_to_int(row["is_spare"]),
            ])
            cleaned_rows += 1

    print(f" inventory_parts: {cleaned_rows} rows written to {out_path}")


if __name__ == "__main__":
    print("Cleaning CSV files...")
    clean_colors()
    clean_themes()
    clean_sets()
    clean_inventory_sets()
    clean_inventory_parts()
    print("Cleaning complete.")
