#!/usr/bin/env python3
"""Fetch images from PubChem using compound names."""

import re
import time
import csv
import requests
from pathlib import Path
from urllib.parse import quote

# Read the CSV to get compound names
csv_file = Path("SMILES_List_Master.csv")
smiles_to_name = {}

if csv_file.exists():
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'SMILES' in row and 'Compound_Name' in row:
                smiles = row['SMILES'].strip()
                name = row['Compound_Name'].strip()
                if name and name != "PubChem CID: None":
                    smiles_to_name[smiles] = name

print(f"Loaded {len(smiles_to_name)} SMILES with compound names")

# Read the markdown to see which ones are still missing
md_file = Path("SMILES_List_Master.md")
with open(md_file, 'r') as f:
    content = f.read()

# Find all "Image not found" entries and extract their SMILES
missing_pattern = r'\|\s*\d+\s*\|\s*([A-Z0-9\[\]\@\#=\-\/\\()C]+)\s*\|[^\n]*Image not found'
missing_smiles = set(re.findall(missing_pattern, content))

print(f"Found {len(missing_smiles)} compounds with missing images")

# Create image directory
img_dir = Path("pubchem_images")
img_dir.mkdir(exist_ok=True)

# Try to fetch images by name
successful = 0
still_failed = []

for i, smiles in enumerate(sorted(missing_smiles), 1):
    name = smiles_to_name.get(smiles)
    if not name:
        still_failed.append((smiles, "No compound name available"))
        continue

    if i % 5 == 0:
        print(f"  Progress: {i}/{len(missing_smiles)}")
        time.sleep(0.5)

    try:
        # Search by compound name
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{quote(name)}/cids/JSON"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if 'IdentifierList' in data and 'CID' in data['IdentifierList']:
                cid = data['IdentifierList']['CID'][0]

                # Download the 2D structure image
                img_url = f"https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid={cid}&t=l"
                img_response = requests.get(img_url, timeout=10)

                if img_response.status_code == 200:
                    img_path = img_dir / f"pubchem_{cid}.png"
                    with open(img_path, 'wb') as f:
                        f.write(img_response.content)
                    print(f"  ✓ Fetched {name} (CID: {cid})")
                    successful += 1

                    # Update markdown with this image
                    old_ref = f"| {smiles} |"
                    # Find the actual line in markdown
                    content = content.replace(
                        f"| {smiles} |",
                        f"| {smiles} |",
                        1
                    )
                else:
                    still_failed.append((smiles, f"Image download failed: {img_response.status_code}"))
            else:
                still_failed.append((smiles, f"Name not found in PubChem: {name}"))
        else:
            still_failed.append((smiles, f"PubChem API error: {response.status_code}"))

    except Exception as e:
        still_failed.append((smiles, str(e)[:50]))

print(f"\n✓ Successfully fetched {successful} additional images by name")
print(f"✗ Still unable to fetch {len(still_failed)} compounds")

if still_failed[:5]:
    print("\nFirst 5 still failing:")
    for smiles, error in still_failed[:5]:
        print(f"  - {smiles[:40]}...: {error}")

# Check which images we have now
existing_pubchem = set()
if img_dir.exists():
    for img in img_dir.glob("*.png"):
        existing_pubchem.add(int(img.stem.split('_')[1]))

print(f"\n📊 Summary:")
print(f"  - PubChem images available: {len(existing_pubchem)}")
print(f"  - Still missing: {len(still_failed)}")
