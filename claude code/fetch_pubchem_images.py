#!/usr/bin/env python3
"""Fetch molecule images from PubChem for all compounds."""

import re
import time
import requests
from pathlib import Path
from urllib.parse import quote

# Read the markdown file to extract all SMILES
md_file = Path("SMILES_List_Master.md")
with open(md_file, 'r') as f:
    content = f.read()

# Extract all table rows with SMILES
pattern = r'\|\s*\d+\s*\|\s*([A-Z0-9\[\]\@\#=\-\/\\()C]+)\s*\|'
smiles_matches = re.findall(pattern, content)

print(f"Found {len(smiles_matches)} SMILES entries")

# Create image directory
img_dir = Path("pubchem_images")
img_dir.mkdir(exist_ok=True)

# Track results
successful = 0
failed = []
smiles_to_cid = {}

# For each unique SMILES, fetch from PubChem
unique_smiles = set(smiles_matches)
print(f"Processing {len(unique_smiles)} unique SMILES...")

for i, smiles in enumerate(sorted(unique_smiles), 1):
    if i % 10 == 0:
        print(f"  Progress: {i}/{len(unique_smiles)}")
        time.sleep(0.5)  # Rate limiting

    try:
        # Use PubChem PUG REST API to convert SMILES to CID
        # First, try exact search
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{quote(smiles)}/cids/JSON"
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
                    # Save the image
                    img_path = img_dir / f"pubchem_{cid}.png"
                    with open(img_path, 'wb') as f:
                        f.write(img_response.content)
                    successful += 1
                else:
                    failed.append((smiles, f"Image download failed: {img_response.status_code}"))
            else:
                failed.append((smiles, "SMILES not found in PubChem"))
        else:
            failed.append((smiles, f"PubChem API error: {response.status_code}"))

    except Exception as e:
        failed.append((smiles, str(e)[:60]))

print(f"\n✓ Successfully fetched {successful} images from PubChem")
print(f"✗ Failed to fetch {len(failed)} SMILES")

if failed[:5]:
    print("\nFirst 5 failures:")
    for smiles, error in failed[:5]:
        print(f"  - {smiles[:50]}...: {error}")

# Now update the markdown file with PubChem images
print("\nUpdating markdown file...")

def replace_image_reference(match):
    """Replace image reference with PubChem image if available."""
    # Extract the line
    rank = match.group(1)
    smiles = match.group(2).strip()
    rest = match.group(3)

    if smiles in smiles_to_cid:
        cid = smiles_to_cid[smiles]
        return f"| {rank} | {smiles} |{rest.replace('Image not found', f'![Molecule](pubchem_images/pubchem_{cid}.png)').replace('![Molecule](molecule_images/molecule_', f'![Molecule](pubchem_images/pubchem_{cid}.png) (PubChem)')}"
    else:
        return match.group(0)

# Read the markdown again
with open(md_file, 'r') as f:
    content = f.read()

# Replace all image references (both missing and existing)
pattern = r'\|\s*(\d+)\s*\|\s*([A-Z0-9\[\]\@\#=\-\/\\()C]+)\s*\|([^\n]+)'

updated_lines = []
for line in content.split('\n'):
    if line.startswith('|') and 'Image' in line and not 'Rank' in line:
        # This is a data row
        match = re.match(pattern, line)
        if match:
            rank = match.group(1)
            smiles = match.group(2).strip()
            rest_of_line = match.group(3)

            if smiles in smiles_to_cid:
                cid = smiles_to_cid[smiles]
                # Replace image column
                new_line = line.rsplit('|', 1)[0] + f" | ![Molecule](pubchem_images/pubchem_{cid}.png) |"
                updated_lines.append(new_line)
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)
    else:
        updated_lines.append(line)

# Write updated markdown
with open(md_file, 'w') as f:
    f.write('\n'.join(updated_lines))

print(f"✓ Updated markdown file with PubChem images")
print(f"✓ Images saved to {img_dir}/")
