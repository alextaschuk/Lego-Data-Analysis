"""
Cleans raw Rebrickable CSVs and writes sanitized versions to `data/clean/`.

Changes applied per CSV file:
    colors:          Drops extra stat columns; converts `is_trans` from bool to 1/0.
    themes:          Converts empty `parent_id` to empty string (loaded as NULL by bcp).
    inventories:     Filters to only inventories whose set is kept after theme filtering.
    sets:            Drops `img_url`; filters out non-set themes (Gear, Books, Games, etc.).
    inventory_sets:  Filtered to only sets kept after theme filtering.
    inventory_parts: Drops `img_url` and converts `is_spare` from bool to 1/0;
                     filtered to only inventories kept after theme filtering.

NOTE: We use the bulk copy program utility (bcp) to copy the data to our Azure SQL database.
bcp doesn't handle CSV quoting (e.g. `777,"Bags, Totes, & Luggage",501` splits on every comma).
To fix this, cleaned data is written to TSV files (tab-delimited) with no header row.
"""

import csv
import os

RAW_DIR   = "data/raw"
CLEAN_DIR = "data/clean"

os.makedirs(CLEAN_DIR, exist_ok=True)

# All themes that aren't sets or have < 20 pieces
EXCLUDED_THEMES = {
    "Gear",                     # apparel, bags, accessories
    "Books",                    # books bundled with a minifig
    "Service Packs",            # replacement/spare-part packs
    "LEGO Brand Store",         # store displays and in-store promotions
    "Promotional",              # giveaway/promotional items
    "Other",                    # misc
    "Games",                    # board games
    "Value Packs",              # multi-set bundles sold as one SKU
    "Collectible Minifigures",  # blind-bag single minifigs
    "Clikits",                  # https://brickipedia.fandom.com/wiki/Clikits
    "DOTS",                     # https://en.wikipedia.org/wiki/Lego_DOTS
    "Xtra",                     # https://brickipedia.fandom.com/wiki/Xtra
    "Powered Up",               # Parts for Legos robotics stuff
    "HO 1:87 Vehicles",         # Vehicles from the 50s/60s
    "Power Functions",          # Parts for Legos robotics stuff
    "Rattles",                  # Baby Toys
    "Zooters",                  # Small Duplo Sets
    "Primo",
    "LEGO Originals",
    "Galidor",
    "Little Robots",
    "Dolls",
    "Supplemental",
    "Ben 10",
}


def build_theme_root_map() -> dict[str, str]:
    """Return `{theme_id: root_theme_name}` for every theme in `themes.csv`."""
    themes: dict[str, dict] = {}
    with open(os.path.join(RAW_DIR, "themes.csv"), newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            themes[row["id"]] = {"name": row["name"], "parent_id": row["parent_id"]}

    def get_root_name(tid: str) -> str:
        visited: set[str] = set()
        while themes.get(tid, {}).get("parent_id"):
            if tid in visited:
                break
            visited.add(tid)
            tid = themes[tid]["parent_id"]
        return themes.get(tid, {}).get("name", "")

    return {tid: get_root_name(tid) for tid in themes}


def bool_to_int(val: str) -> int:
    return 1 if val.strip().lower() == "true" else 0


def nullable(val: str) -> str:
    """Return the stripped value. An empty string is loaded as NULL by bcp."""
    return val.strip()


def clean_colors():
    """Clean `colors.csv`."""
    in_path  = os.path.join(RAW_DIR, "colors.csv")
    out_path = os.path.join(CLEAN_DIR, "colors.tsv")
    kept_rows = 0

    with open(in_path, newline="", encoding="utf-8") as fin, \
         open(out_path, "w", newline="", encoding="utf-8") as fout:
        writer = csv.writer(fout, delimiter='\t', lineterminator='\n')
        for row in csv.DictReader(fin):
            writer.writerow([
                row["id"].strip(),
                row["name"].strip(),
                row["rgb"].strip(),
                bool_to_int(row["is_trans"]),
            ])
            kept_rows += 1

    print(f" colors: {kept_rows} rows written to {out_path}")


def clean_themes():
    """Clean `themes.csv`."""
    in_path  = os.path.join(RAW_DIR, "themes.csv")
    out_path = os.path.join(CLEAN_DIR, "themes.tsv")
    kept_rows = 0

    with open(in_path, newline="", encoding="utf-8") as fin, \
         open(out_path, "w", newline="", encoding="utf-8") as fout:
        writer = csv.writer(fout, delimiter='\t', lineterminator='\n')
        for row in csv.DictReader(fin):
            writer.writerow([
                row["id"].strip(),
                row["name"].strip(),
                nullable(row["parent_id"]),
            ])
            kept_rows += 1

    print(f" themes: {kept_rows} rows written to {out_path}")


def clean_sets(theme_root: dict[str, str]) -> set[str]:
    """Clean `sets.csv`, skipping sets whose root theme is in EXCLUDED_THEMES.
    Returns the kept set_nums for downstream filtering."""
    in_path  = os.path.join(RAW_DIR, "sets.csv")
    out_path = os.path.join(CLEAN_DIR, "sets.tsv")
    kept_set_nums: set[str] = set()
    kept_rows = skipped_rows = 0

    with open(in_path, newline="", encoding="utf-8") as fin, \
         open(out_path, "w", newline="", encoding="utf-8") as fout:
        writer = csv.writer(fout, delimiter='\t', lineterminator='\n')
        
        for row in csv.DictReader(fin):
            theme_id = row["theme_id"].strip()
            if theme_root.get(theme_id, "") in EXCLUDED_THEMES:
                skipped_rows += 1
                continue
            if int(row["num_parts"].strip()) < 20:
                skipped_rows += 1
                continue
            writer.writerow([
                row["set_num"].strip(),
                row["name"].strip(),
                row["year"].strip(),
                theme_id,
                row["num_parts"].strip(),
            ])
            kept_set_nums.add(row["set_num"].strip())
            kept_rows += 1

    print(f" sets: {kept_rows} rows written to {out_path} ({skipped_rows} excluded by theme)")
    return kept_set_nums


def clean_inventories(kept_set_nums: set[str]) -> set[str]:
    """
    Clean `inventories.csv`, keeping only inventories for sets in `kept_set_nums`.
    Returns the kept `inventory_ids` for downstream filtering of `inventory_parts`.
    """
    in_path  = os.path.join(RAW_DIR, "inventories.csv")
    out_path = os.path.join(CLEAN_DIR, "inventories.tsv")
    kept_inventory_ids: set[str] = set()
    kept_rows = skipped_rows = 0

    with open(in_path, newline="", encoding="utf-8") as fin, \
         open(out_path, "w", newline="", encoding="utf-8") as fout:
        writer = csv.writer(fout, delimiter='\t', lineterminator='\n')

        for row in csv.DictReader(fin):
            set_num = row["set_num"].strip()
            if set_num not in kept_set_nums:
                skipped_rows += 1
                continue
            inv_id = row["id"].strip()
            writer.writerow([inv_id, row["version"].strip(), set_num])
            kept_inventory_ids.add(inv_id)
            kept_rows += 1

    print(f" inventories: {kept_rows} rows written to {out_path} ({skipped_rows} excluded)")
    return kept_inventory_ids


def clean_inventory_sets(kept_set_nums: set[str]):
    """Clean `inventory_sets.csv`, keeping only entries for sets in `kept_set_nums`."""
    in_path  = os.path.join(RAW_DIR,   "inventory_sets.csv")
    out_path = os.path.join(CLEAN_DIR, "inventory_sets.tsv")
    kept_rows = skipped_rows = 0

    with open(in_path, newline="", encoding="utf-8") as fin, \
         open(out_path, "w", newline="", encoding="utf-8") as fout:
        writer = csv.writer(fout, delimiter='\t', lineterminator='\n')
        
        for row in csv.DictReader(fin):
            set_num = row["set_num"].strip()
            if set_num not in kept_set_nums:
                skipped_rows += 1
                continue
            writer.writerow([
                row["inventory_id"].strip(),
                set_num,
                row["quantity"].strip(),
            ])
            kept_rows += 1

    print(f" inventory_sets: {kept_rows} rows written to {out_path} ({skipped_rows} excluded)")


def clean_inventory_parts(kept_inventory_ids: set[str]):
    """Clean `inventory_parts.csv`, keeping only parts for inventories in `kept_inventory_ids`."""
    in_path  = os.path.join(RAW_DIR,   "inventory_parts.csv")
    out_path = os.path.join(CLEAN_DIR, "inventory_parts.tsv")
    kept_rows = skipped_rows = 0

    with open(in_path, newline="", encoding="utf-8") as fin, \
         open(out_path, "w", newline="", encoding="utf-8") as fout:
        writer = csv.writer(fout, delimiter='\t', lineterminator='\n')
        
        for row in csv.DictReader(fin):
            inv_id = row["inventory_id"].strip()
            if inv_id not in kept_inventory_ids:
                skipped_rows += 1
                continue
            writer.writerow([
                inv_id,
                row["part_num"].strip(),
                row["color_id"].strip(),
                row["quantity"].strip(),
                bool_to_int(row["is_spare"]),
            ])
            kept_rows += 1

    print(f" inventory_parts: {kept_rows} rows written to {out_path} ({skipped_rows} excluded)")


if __name__ == "__main__":
    print("Cleaning CSV files...")
    theme_root = build_theme_root_map()
    clean_colors()
    clean_themes()
    kept_set_nums      = clean_sets(theme_root)
    kept_inventory_ids = clean_inventories(kept_set_nums)
    clean_inventory_sets(kept_set_nums)
    clean_inventory_parts(kept_inventory_ids)
    print("Cleaning complete.")