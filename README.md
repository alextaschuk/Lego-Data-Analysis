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
