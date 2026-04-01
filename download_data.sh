#!/usr/bin/env bash

# Error handling
set -euo pipefail
IFS=$'\n\t'

# Download only the needed csv files from the rebrickable website
urls=(
    "https://cdn.rebrickable.com/media/downloads/inventory_sets.csv.zip?1775032522.244372"
    "https://cdn.rebrickable.com/media/downloads/sets.csv.zip?1775032491.8036342"
    "https://cdn.rebrickable.com/media/downloads/themes.csv.zip?1775032487.1835225"
    "https://cdn.rebrickable.com/media/downloads/inventory_parts.csv.zip?1775032522.0643675"
    "https://cdn.rebrickable.com/media/downloads/colors.csv.zip?1775032487.2275236"
)

# Extra, not needed URLs
#
# "https://cdn.rebrickable.com/media/downloads/part_categories.csv.zip?1775032487.3395262"
# "https://cdn.rebrickable.com/media/downloads/parts.csv.zip?1775032488.7635608"
# "https://cdn.rebrickable.com/media/downloads/part_relationships.csv.zip?1775032523.5804045"
# "https://cdn.rebrickable.com/media/downloads/elements.csv.zip?1775032490.2955978"
# "https://cdn.rebrickable.com/media/downloads/minifigs.csv.zip?1775032492.3116465"
# "https://cdn.rebrickable.com/media/downloads/inventories.csv.zip?1775032491.051616"
# "https://cdn.rebrickable.com/media/downloads/inventory_minifigs.csv.zip?1775032522.9203885"

mkdir -p data/raw

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

done

echo "All downloads done."
