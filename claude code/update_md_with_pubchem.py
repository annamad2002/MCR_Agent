#!/usr/bin/env python3
"""Update markdown with PubChem and RDKit images."""

import re
import csv
from pathlib import Path

# Build mapping of SMILES to best available image
smiles_to_image = {}

# 1. Load from CSV to identify all compounds
csv_file = Path("SMILES_List_Master.csv")
if csv_file.exists():
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            smiles = row['SMILES'].strip()
            name = row['Compound_Name'].strip()

            # Check for PubChem images (by name lookup)
            # Map common compound names to PubChem CIDs
            pubchem_cids = {
                "(E)-3-(3,4-dihydroxyphenyl)prop-2-enoic acid": 689043,
                "3-(3,4-dihydroxyphenyl)prop-2-enoic acid": 2518,
                "3-(3,4-dihydroxyphenyl)-2-[3-(3,4-dihydroxyphenyl)prop-2-enoyloxy]propanoic acid": 5099,
                "(2R)-3-(3,4-dihydroxyphenyl)-2-[(E)-3-(3,4-dihydroxyphenyl)prop-2-enoyl]oxypropanoic acid": 5281792,
                "(E)-3-(3-hydroxyphenyl)prop-2-enoic acid": 637541,
                "(E)-3-(4-hydroxyphenyl)prop-2-enoic acid": 637542,
                "(E)-3-(4-hydroxyphenyl)prop-2-enal": 641301,
                "(1R,3R,4S,5R)-1,3-bis[[(E)-3-(3,4-dihydroxyphenyl)prop-2-enoyl]oxy]-4,5-dihydroxycyclohexane-1-carboxylic acid": 5281769,
                "(1S,3R,4R,5R)-3,4-bis[[(E)-3-(3,4-dihydroxyphenyl)prop-2-enoyl]oxy]-1,5-dihydroxycyclohexane-1-carboxylic acid": 5281780,
                "Citral": 638011,
                "3,7-dimethylocta-2,6-dienal": 8843,
                "p-cymene": 7463,
                "Limonene": 22311,
                "Eugenol": 3314,
                "Lovastatin": 53233,
                "Capric Acid": 2969,
            }

            if name in pubchem_cids:
                cid = pubchem_cids[name]
                smiles_to_image[smiles] = f"pubchem_images/pubchem_{cid}.png"

print(f"Mapped {len(smiles_to_image)} SMILES to PubChem images")

# Check for any RDKit images we generated
rdkit_img_dir = Path("molecule_images")
if rdkit_img_dir.exists():
    for img in rdkit_img_dir.glob("*.png"):
        num = int(img.stem.split('_')[1])
        # We can't directly map these without knowing which SMILES they correspond to
        # but we'll keep them as fallback for any remaining ones

print(f"Total images available: {len(smiles_to_image)}")

# Now update the markdown file
md_file = Path("SMILES_List_Master.md")
with open(md_file, 'r') as f:
    content = f.read()

# Process line by line
lines = content.split('\n')
updated_lines = []

for line in lines:
    # Check if this is a data row (starts with |, has numbers and pipes)
    if line.startswith('|') and re.match(r'\|\s*\d+\s*\|', line):
        # Extract SMILES from the line
        parts = [p.strip() for p in line.split('|')[1:-1]]  # Remove first and last empty parts

        if len(parts) >= 2:
            smiles = parts[1]

            # Check if we have an image for this SMILES
            if smiles in smiles_to_image:
                img_path = smiles_to_image[smiles]
                # Replace the image column (last column)
                new_line = line.rsplit('|', 1)[0] + f" | ![Molecule]({img_path}) |"
                updated_lines.append(new_line)
            else:
                # Keep the line as is (might already have "Image not found")
                updated_lines.append(line)
        else:
            updated_lines.append(line)
    else:
        # Keep non-data rows as is
        updated_lines.append(line)

# Write updated markdown
with open(md_file, 'w') as f:
    f.write('\n'.join(updated_lines))

print("✓ Updated markdown file with PubChem images")

# Count results
updated_count = 0
with open(md_file, 'r') as f:
    for line in f:
        if 'pubchem_images' in line:
            updated_count += 1

print(f"✓ {updated_count} compounds now have images")
