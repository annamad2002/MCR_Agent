#!/usr/bin/env python3
"""Build mapping of compound names to CIDs for all PubChem images."""

import csv
import json
from pathlib import Path

# Get all available CIDs from the images directory
pubchem_cids = set()
pubchem_dir = Path("pubchem_images")
if pubchem_dir.exists():
    for img in pubchem_dir.glob("*.png"):
        cid = int(img.stem.split('_')[1])
        pubchem_cids.add(cid)

print(f"Found {len(pubchem_cids)} images in pubchem_images/")
print(f"CIDs: {sorted(pubchem_cids)}")

# Read the CSV to get all compound names
csv_file = Path("SMILES_List_Master.csv")
name_to_cid = {}

with open(csv_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row['Compound_Name'].strip()

        # Try common CID mappings based on the names we fetched
        cid_map = {
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
            "Lovastatin": 53232,  # Checked - this is the right CID
            "Capric Acid": 2969,
            "(1S,3R,4R,5R)-1,3,4-trihydroxy-5-[(E)-3-(4-hydroxy-3-methoxyphenyl)prop-2-enoyl]oxycyclohexane-1-carboxylic acid": 54454,
        }

        if name in cid_map:
            cid = cid_map[name]
            if cid in pubchem_cids:
                name_to_cid[name] = cid

print(f"\nMapped {len(name_to_cid)} compound names to available images")
print("\nMapping:")
for name, cid in sorted(name_to_cid.items()):
    print(f"  {name}: {cid}")

# Save mapping to JSON for use in other scripts
mapping_file = Path("name_to_cid_mapping.json")
with open(mapping_file, 'w') as f:
    json.dump(name_to_cid, f, indent=2)

print(f"\n✓ Saved mapping to {mapping_file}")
