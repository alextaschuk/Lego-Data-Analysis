#!/usr/bin/env bash

###############################################################
# This file downloads the necessary CSV files from Rebrickable.
###############################################################

# Error handling
set -euo pipefail
IFS=$'\n\t'

urls=(
    "https://cdn.rebrickable.com/media/downloads/inventory_sets.csv.zip?1775032522.244372"
    "https://cdn.rebrickable.com/media/downloads/sets.csv.zip?1775032491.8036342"
    "https://cdn.rebrickable.com/media/downloads/themes.csv.zip?1775032487.1835225"
    "https://cdn.rebrickable.com/media/downloads/inventory_parts.csv.zip?1775032522.0643675"
    "https://cdn.rebrickable.com/media/downloads/colors.csv.zip?1775032487.2275236"
)

mkdir -p data/raw # download files to this directory

for url in "${urls[@]}"; do
    file=$(basename "${url%%\?*}")
    dest="data/raw/$file"

    if [[ -f "$dest" ]]; then
    echo "Skipping existing file: $dest"
    continue
    fi

    echo "Downloading $url -> $dest"
    curl --fail --location --progress-bar --output "$dest" "$url"
    echo "Downloaded: $dest"

    echo "Unzipping $dest -> data/raw/"
    unzip -o "$dest" -d data/raw/
    echo "Unzipped: $dest"

    rm -f "$dest"

done

echo "All downloads done."
