# COSC 301 End-to-End Data Analytics Pipeline Project

## Setup

**Prerequisites**

- Python 3.13
- [Homebrew](https://brew.sh)


**1. Install Homebrew Dependencies**

`bcp` is provided by `mssql-tools18`:

```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew install mssql-tools18
bcp -v # Verify the install
```

`bcp` is used in `scripts/bcp_upload.sh` to bulk-load data to our Azure SQL database.


**2. Make a Python Virtual Environment & Install Dependencies**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Configure environment variables**

Use `.env.example` to create a `.env` with the Azure database credentials.

---

## Stage One: Data Prep

The first stage of our project's pipeline involves four steps.

**1. Downloading the Data**

To download the necessary CSV files from Rebrickable, run:

```bash
bash scripts/get_data.sh
```

A new `/data/` directory will be created, which will contain two sub-directories by the end of this stage. When the `get_data` script is ran, a new `/raw/` sub-directory is created, and the CSV files are downloaded, placed into `/data/raw`, and unzipped.

**2. Cleaning the Data**

The data needs to be cleaned for two reasons:

1. Some of the rows contain invalid data or need to be converted to a SQL-friendly format (e.g., converting empty strings `""` to `NULL`).
2. `bcp` doesn't handle CSV-style quoting (e.g, a row like `777,"Bags, Totes, & Luggage",501`) will be split on every comma, so we need to convert the data to a tab-delimited format (`\t`).

To clean the data, run:

```bash
python3 clean_data.py
```

The program will create a new directory,  `/data/clean`, and write the cleaned data to `.tsv` files in that directory.
- E.g., The cleaned up version of `/data/raw/colors.csv` will be written to `/data/clean/colors.tsv`.

**3. Create the SQL Tables on the Azure Database**

Copy the contents of `create_tables.sql`, go to the **Query editor (preview)** page of the Azure database's dashboard, paste in the SQL statements, and run the query. 

**4. Upload the Clean TSV Data to Azure**

To upload the cleaned data, run:

```bash
bash scripts/bcp_upload.sh
```

---

## Data Dictionary

Source: [Rebrickable's LEGO Catalog Database Download](https://rebrickable.com/downloads/)

<figure>
  <img src="https://rebrickable.com/static/img/diagrams/downloads_schema_v3.png" alt="Schema Diagram for LEGO datafiles">
  <figcaption align="center">Rebrickable's Schema Diagram for LEGO datafiles</figcaption>
</figure>

**_Note_:** We only use the following tables from this database:

- colors
- inventories
- inventory_parts
- inventory_sets
- sets
- themes

---

### `themes`

Theme categories (e.g., Star Wars and Technic).

| Field | Type | Nullable | Description | Transformation |
|---|---|---|---|---|
| `id` | INT | No | Unique theme id (PK) |   |
| `name` | VARCHAR(256) | No | Display name of the theme |   |
| `parent_id` | INT | Yes | References `themes.id` for sub-themes; NULL if top-level | Empty string → `NULL` |

---

### `colors`

Brick colors.

| Field | Type | Nullable | Description | Transformation |
|---|---|---|---|---|
| `id` | INT | No | Unique color id (PK) |   |
| `name` | VARCHAR(200) | No | Human-readable color name (e.g., "Bright Red") |   |
| `rgb` | VARCHAR(6) | No | Hex RGB value without `#` prefix|   |
| `is_trans` | BIT | No | 1 if the color is transparent, 0 otherwise | `True`/`False` → `1`/`0` |

---

### `sets`

Individual LEGO sets.

| Field | Type | Nullable | Description | Transformation |
|---|---|---|---|---|
| `set_num` | VARCHAR(20) | No | Unique set id (PK) |   |
| `name` | VARCHAR(256) | No | Official set name |   |
| `year` | INT | No | Year the set was released |   |
| `theme_id` | INT | No | FK to `themes.id` |   |
| `num_parts` | INT | No | Total number of parts in the set |   |

---

### `inventories`

Versioned part lists associated with a set. A set may have multiple inventory versions.

| Field | Type | Nullable | Description | Transformation |
|---|---|---|---|---|
| `id` | INT | No | Unique inventory id (PK) |   |
| `version` | INT | No | Version number of this inventory |   |
| `set_num` | VARCHAR(20) | No | FK to `sets.set_num` |   |

---

### `inventory_sets`

Sets that are included inside other sets.

| Field | Type | Nullable | Description | Transformation |
|---|---|---|---|---|
| `inventory_id` | INT | No | FK to `inventories.id` |   |
| `set_num` | VARCHAR(20) | No | FK to `sets.set_num` of the included set |   |
| `quantity` | INT | No | Number of times the set appears in the inventory |   |

---

### `part_categories`

Top-level groupings of LEGO parts by type (e.g., "Bricks", "Plates").

| Field | Type | Nullable | Description | Transformation |
|---|---|---|---|---|
| `id` | INT | No | Unique category id (PK) |   |
| `name` | VARCHAR(200) | No | Category name |   |

---

### `parts`

Individual LEGO part molds, independent of color.

| Field | Type | Nullable | Description | Transformation |
|---|---|---|---|---|
| `part_num` | VARCHAR(20) | No | Unique part id (PK) |   |
| `name` | VARCHAR(250) | No | Descriptive part name |   |
| `part_cat_id` | INT | No | FK to `part_categories.id` |   |

---

### `inventory_parts`

The specific parts (with colors and quantities) that make up each inventory.

| Field | Type | Nullable | Description | Transformation |
|---|---|---|---|---|
| `inventory_id` | INT | No | FK to `inventories.id` |   |
| `part_num` | VARCHAR(20) | No | FK to `parts.part_num` |   |
| `color_id` | INT | No | FK to `colors.id` |   |
| `quantity` | INT | No | Number of this part/color combination in the inventory |   |
| `is_spare` | BIT | No | 1 if this is a spare part, 0 otherwise | `True`/`False` → `1`/`0` |

---

### `minifigs`

LEGO minifigures, which can be included in set inventories.

| Field | Type | Nullable | Description | Transformation |
|---|---|---|---|---|
| `fig_num` | VARCHAR(20) | No | Unique minifigure id (PK) |   |
| `name` | VARCHAR(256) | No | Minifigure name |   |
| `num_parts` | INT | No | Number of parts that make up the minifigure |   |

---

### `inventory_minifigs`

Minifigures included in a given inventory.

| Field | Type | Nullable | Description | Transformation |
|---|---|---|---|---|
| `inventory_id` | INT | No | FK to `inventories.id` |   |
| `fig_num` | VARCHAR(20) | No | FK to `minifigs.fig_num` |   |
| `quantity` | INT | No | Number of this minifigure in the inventory |   |

---

### `elements`

Maps physical LEGO element IDs (as printed on bags/boxes) to a part + color combination.

| Field | Type | Nullable | Description | Transformation |
|---|---|---|---|---|
| `element_id` | VARCHAR(10) | No | Official LEGO element ID (PK) |   |
| `part_num` | VARCHAR(20) | No | FK to `parts.part_num` |   |
| `color_id` | INT | No | FK to `colors.id` |   |

---

### `part_relationships`

Describes mold/print/alternate relationships between parts.

| Field | Type | Nullable | Description | Transformation |
|---|---|---|---|---|
| `rel_type` | VARCHAR(1) | No | Relationship type code: `A` = Alternate, `M` = Mold, `P` = Print, `R` = Pair, `T` = Sub |   |
| `child_part_num` | VARCHAR(20) | No | FK to `parts.part_num` of the derived/child part |   |
| `parent_part_num` | VARCHAR(20) | No | FK to `parts.part_num` of the base/parent part |   |
