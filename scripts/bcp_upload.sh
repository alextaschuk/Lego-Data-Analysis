#!/usr/bin/env bash

###############################################################
# Bulk-loads cleaned Rebrickable CSVs into Azure SQL database
# using bcp.
#
# Prerequisites:
#   - mssql-tools18 (provides the bcp command)
###############################################################

set -euo pipefail
IFS=$'\n\t'

# load the .env file
if [[ ! -f .env ]]; then
    echo "ERROR: .env file not found." >&2
    exit 1
fi

# Parse key = "value" lines (this strips surrounding quotes and spaces)
get_env() {
    grep -E "^$1\s*=" .env | cut -d'=' -f2- | tr -d ' "'
}

DB_HOST=$(get_env DB_HOST)
DB_NAME=$(get_env DB_NAME)
DB_USER=$(get_env DB_USER)
DB_PASSWORD=$(get_env DB_PASSWORD)

CLEAN_DIR="data/clean"

# helper for bcp to load
load_table() {
    local table="$1"
    local csv="$2"

    echo "Loading $table from $csv..."
    bcp "[${DB_NAME}].dbo.${table}" in "${csv}" \
        -S "${DB_HOST}" \
        -U "${DB_USER}" \
        -P "${DB_PASSWORD}" \
        -c \
        -t "\t" \
        -r "\n" \
        -F 1 \
        -k \
        -b 10000 \
        -e "bcp_${table}_errors.log" # log any rows that fail to load and are skipped
    echo "  Done: $table"
}

# upload the tables
load_table "themes"         "${CLEAN_DIR}/themes.tsv"
load_table "colors"         "${CLEAN_DIR}/colors.tsv"
load_table "sets"           "${CLEAN_DIR}/sets.tsv"
load_table "inventory_sets" "${CLEAN_DIR}/inventory_sets.tsv"
load_table "inventory_parts" "${CLEAN_DIR}/inventory_parts.tsv"

echo ""
echo "All tables loaded."
