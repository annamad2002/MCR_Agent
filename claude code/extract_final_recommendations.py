#!/usr/bin/env python3
"""Extract only FINAL RECOMMENDATIONS from chat logs."""

import os
import re
import csv
from pathlib import Path
from collections import defaultdict

base_dir = Path("/Users/annalevison/Library/CloudStorage/OneDrive-UniversityofReading/chem/ollama_prompts/Prompts/MCR_Agent")

final_data = []
stats = defaultdict(int)

# Process each prompt
for prompt_num in range(1, 14):
    prompt_dir = base_dir / str(prompt_num)
    if not prompt_dir.exists():
        continue

    chat_files = sorted([f for f in prompt_dir.iterdir() if f.is_file() and not f.name.startswith('.')])

    for chat_file in chat_files:
        if chat_file.is_dir() or "docking" in chat_file.name:
            continue

        try:
            with open(chat_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Look for the final selection table
            if "Final selection:" not in content:
                continue

            # Extract everything after "Final selection:"
            final_idx = content.rfind("Final selection:")  # Use rfind to get the LAST occurrence
            if final_idx == -1:
                continue

            final_section = content[final_idx:final_idx+5000]

            # Look for table rows with SMILES
            # Pattern: | compound_name | SMILES | docking_score | residues | QED | NP | SAS | availability |
            smiles_pattern = r'\|\s*\*?\*?([^|]+?)\*?\*?\s*\|\s*`?([A-Z0-9\[\]\@\#=\-\\/\(\)C]+?)`?\s*\|'

            matches = re.finditer(smiles_pattern, final_section)

            for match in matches:
                compound_name = match.group(1).strip()
                smiles = match.group(2).strip()

                # Skip header row
                if compound_name.lower() == "compound" or smiles.lower() == "smiles":
                    continue

                # Valid SMILES should be longer than just a symbol
                if len(smiles) > 5 and compound_name:
                    model_name = extract_model_name(chat_file.name)
                    final_data.append({
                        'Rank': len(final_data) + 1,
                        'Prompt': prompt_num,
                        'Model': model_name,
                        'SMILES': smiles,
                        'Compound_Name': compound_name.replace('**', ''),
                        'Source_File': chat_file.name
                    })
                    stats['found'] += 1

                    print(f"✓ P{prompt_num} {model_name}: {compound_name[:40]:40} | {smiles[:40]}")

        except Exception as e:
            stats['errors'] += 1

print(f"\n{'='*80}")
print(f"EXTRACTION COMPLETE")
print(f"{'='*80}")
print(f"Total final recommendations extracted: {stats['found']}")
print(f"Errors: {stats['errors']}")

# Write to CSV
output_csv = base_dir / "SMILES_Final_Recommendations_VALIDATED.csv"
with open(output_csv, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Rank', 'Prompt', 'Model', 'SMILES', 'Compound_Name', 'Source_File'])
    writer.writeheader()
    for i, row in enumerate(final_data, 1):
        row['Rank'] = i
        writer.writerow(row)

print(f"\n✓ Saved to: {output_csv}")
print(f"✓ Total records: {len(final_data)}")

# Compare with current master CSV
current_csv = base_dir / "SMILES_List_Master.csv"
if current_csv.exists():
    with open(current_csv, 'r') as f:
        current_smiles = set(row['SMILES'] for row in csv.DictReader(f))

    final_smiles = set(row['SMILES'] for row in final_data)

    missing = final_smiles - current_smiles
    extra = current_smiles - final_smiles

    print(f"\n{'='*80}")
    print(f"COMPARISON WITH CURRENT MASTER CSV")
    print(f"{'='*80}")
    print(f"Final recommendations (unique SMILES): {len(final_smiles)}")
    print(f"Current master (unique SMILES): {len(current_smiles)}")
    print(f"Missing from master CSV: {len(missing)}")
    print(f"Extra in master CSV: {len(extra)}")

    if missing:
        print(f"\nMissing SMILES (should be added):")
        for smiles in sorted(list(missing))[:10]:
            print(f"  - {smiles[:60]}")

    if extra:
        print(f"\nExtra SMILES in master (non-final-recommendation): {len(extra)} compounds")

def extract_model_name(filename):
    """Extract model name from filename."""
    if " - " in filename:
        return " - ".join(filename.split(" - ")[1:]).replace(".md", "").replace(".ini", "").strip()
    return filename.replace(".md", "").replace(".ini", "").strip()
