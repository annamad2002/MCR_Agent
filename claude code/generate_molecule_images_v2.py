#!/usr/bin/env python3
"""Generate molecule images from SMILES strings and embed them in markdown."""

import os
import re
import csv
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import Draw, AllChem

# Create directory for images
img_dir = Path("molecule_images")
img_dir.mkdir(exist_ok=True)

# Read the original CSV to get SMILES
csv_file = Path("SMILES_List_Master.csv")
smiles_data = {}

if csv_file.exists():
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'SMILES' in row:
                smiles = row['SMILES'].strip()
                smiles_data[smiles] = row

print(f"Loaded {len(smiles_data)} SMILES from CSV")

# Generate images for all SMILES
generated_images = {}
failed_smiles = []

for i, smiles in enumerate(smiles_data.keys(), 1):
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            print(f"  ✗ Failed to parse SMILES {i}: {smiles[:50]}...")
            failed_smiles.append(smiles)
            continue

        # Generate 2D coordinates
        AllChem.Compute2DCoords(mol)

        # Generate image
        img_path = img_dir / f"molecule_{i}.png"
        img = Draw.MolToImage(mol, size=(150, 150))
        img.save(img_path)

        generated_images[smiles] = i

        if i % 50 == 0:
            print(f"  ✓ Generated {i} images...")

    except Exception as e:
        print(f"  ✗ Error generating image for SMILES {i}: {str(e)[:60]}")
        failed_smiles.append(smiles)

print(f"\n✓ Successfully generated {len(generated_images)} images")
if failed_smiles:
    print(f"✗ Failed to generate images for {len(failed_smiles)} SMILES")

# Now update the markdown file
md_file = Path("SMILES_List_Master.md")
with open(md_file, 'r') as f:
    content = f.read()

# Create a mapping of SMILES to image numbers
smiles_to_img_num = generated_images

# Replace SMILES in tables with SMILES + image reference
def replace_smiles_with_image(match):
    """Replace SMILES in table with SMILES and image reference."""
    rank = match.group(1)
    smiles = match.group(2).strip()
    rest = match.group(3)

    if smiles in smiles_to_img_num:
        img_num = smiles_to_img_num[smiles]
        return f"| {rank} | ![Molecule](molecule_images/molecule_{img_num}.png) {smiles} |{rest}"
    else:
        return match.group(0)

# Pattern to match table rows: | rank | smiles | rest
pattern = r'\|\s*(\d+)\s*\|\s*([A-Z0-9\[\]\@\#=\-\/\\()]+)\s*\|([^\n]+)'
updated_content = re.sub(pattern, replace_smiles_with_image, content)

# Write updated markdown
with open(md_file, 'w') as f:
    f.write(updated_content)

print(f"\n✓ Updated {md_file}")
print(f"✓ Images embedded in molecule structure column")
print(f"✓ Images saved to {img_dir}/")
