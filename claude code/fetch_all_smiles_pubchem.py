#!/usr/bin/env python3
"""Fetch images from PubChem for ALL compounds using SMILES strings."""

import csv
import time
import requests
from pathlib import Path
from urllib.parse import quote

# Read CSV to get all SMILES
csv_file = Path("SMILES_List_Master.csv")
compounds = []

with open(csv_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        compounds.append({
            'rank': row['Rank'],
            'smiles': row['SMILES'].strip(),
            'name': row['Compound_Name'].strip(),
        })

print(f"Processing {len(compounds)} compounds...")

# Create image directory
img_dir = Path("pubchem_images")
img_dir.mkdir(exist_ok=True)

# Track results
successful = 0
failed = []
smiles_to_cid = {}

for i, compound in enumerate(compounds, 1):
    smiles = compound['smiles']
    name = compound['name']

    if i % 20 == 0:
        print(f"  Progress: {i}/{len(compounds)}")

    try:
        # Use PubChem PUG REST API to convert SMILES to CID
        # URL encode the SMILES properly
        encoded_smiles = quote(smiles, safe='')
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{encoded_smiles}/cids/JSON"

        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if 'IdentifierList' in data and 'CID' in data['IdentifierList']:
                cid = data['IdentifierList']['CID'][0]
                smiles_to_cid[smiles] = cid

                # Download the 2D structure image
                img_url = f"https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid={cid}&t=l"
                img_response = requests.get(img_url, timeout=10)

                if img_response.status_code == 200:
                    # Check if it's actually an image (has reasonable size)
                    if len(img_response.content) > 1000:  # At least 1KB
                        img_path = img_dir / f"pubchem_{cid}.png"

                        # Don't overwrite if already exists
                        if not img_path.exists():
                            with open(img_path, 'wb') as f:
                                f.write(img_response.content)

                        successful += 1
                        print(f"  ✓ {i}: {name[:50]:<50} (CID: {cid})")
                    else:
                        failed.append((smiles, f"Image too small: {len(img_response.content)} bytes"))
                else:
                    failed.append((smiles, f"Image download failed: {img_response.status_code}"))
            else:
                failed.append((smiles, "SMILES not found in PubChem"))
        elif response.status_code == 400:
            failed.append((smiles, "PubChem API: Invalid SMILES"))
        else:
            failed.append((smiles, f"PubChem API error: {response.status_code}"))

    except requests.exceptions.Timeout:
        failed.append((smiles, "Request timeout"))
    except Exception as e:
        failed.append((smiles, str(e)[:60]))

    # Rate limiting - be nice to the server
    time.sleep(0.1)

print(f"\n✓ Successfully fetched {successful} images from PubChem")
print(f"✗ Failed for {len(failed)} SMILES")

if failed[:10]:
    print("\nFirst 10 failures:")
    for smiles, error in failed[:10]:
        print(f"  - {smiles[:40]}...: {error}")

print(f"\n✓ Saved images to {img_dir}/")
print(f"✓ SMILES-to-CID mapping: {len(smiles_to_cid)} compounds")

# Save the mapping
import json
mapping_file = Path("smiles_to_cid_mapping.json")
with open(mapping_file, 'w') as f:
    json.dump(smiles_to_cid, f, indent=2)

print(f"✓ Saved mapping to {mapping_file}")
