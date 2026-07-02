#!/usr/bin/env python3
"""Comprehensive extraction of final recommendations from all prompts."""

import re
import csv
from pathlib import Path
from collections import defaultdict

def extract_model(filename):
    """Extract model name from filename."""
    if ' - ' in filename:
        parts = filename.split(' - ')[1:]
        return ' - '.join(parts).replace('.md', '').replace('.ini', '').strip()
    return filename.replace('.md', '').replace('.ini', '').strip()

base_dir = Path("/Users/annalevison/Library/CloudStorage/OneDrive-UniversityofReading/chem/ollama_prompts/Prompts/MCR_Agent")

# Load existing data for matching
existing_csv = base_dir / "SMILES_List_Master.csv"
existing_data = {}
with open(existing_csv, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        existing_data[row['SMILES'].strip()] = row

print(f"Loaded {len(existing_data)} compounds from existing CSV")

final_recs = []
seen_smiles = set()

# Section headers to look for
section_patterns = [
    r"###?\s*(?:Final\s+)?(?:Selection|Recommendations?|Candidates?)",
    r"##?\s*(?:Top|Best)\s+(?:Compounds|Candidates)",
    r"Based on the (?:analysis|screening)",
]

for prompt_num in range(1, 14):
    prompt_dir = base_dir / str(prompt_num)
    if not prompt_dir.exists():
        continue

    chat_files = sorted([f for f in prompt_dir.iterdir() if f.is_file() and not f.name.startswith('.') and 'docking' not in f.name])

    for chat_file in chat_files:
        try:
            with open(chat_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Find recommendation sections
            # Look for multiple patterns
            found_section = False

            # Try to find sections starting with recommendation-like headers
            for section_start in re.finditer(r"(?:### |## |# )(?:Recommended|Final Selection|Top Candidates|Based on)", content):
                section_start_idx = section_start.start()
                # Get next 3000 characters
                section_text = content[section_start_idx:section_start_idx+3000]

                # Extract table rows
                table_lines = section_text.split('\n')
                in_table = False
                col_count = None

                for line_idx, line in enumerate(table_lines):
                    # Start of table
                    if line.startswith('|') and '|' in line:
                        cells = [c.strip() for c in line.split('|')[1:-1]]

                        # Check if this is a header-like row
                        if any(h in ' '.join(cells).lower() for h in ['smiles', 'compound', 'docking', 'residue']):
                            in_table = True
                            col_count = len(cells)
                            # Try to identify column positions
                            col_text = '|'.join(cells).lower()
                            compound_idx = next((i for i, c in enumerate(cells) if 'compound' in c.lower()), 0)
                            smiles_idx = next((i for i, c in enumerate(cells) if 'smiles' in c.lower()), 1)
                            continue

                        # Data row in table
                        if in_table and col_count and len(cells) >= col_count:
                            # Extract SMILES (usually 2nd column)
                            if len(cells) > smiles_idx:
                                smiles = cells[smiles_idx].replace('`', '').replace('**', '').strip()

                                # Extract compound name (usually 1st column)
                                if len(cells) > compound_idx:
                                    compound = cells[compound_idx].replace('`', '').replace('**', '').strip()

                                    # Validate SMILES
                                    if len(smiles) > 5 and any(c in smiles for c in ['C', 'N', 'O', 'S', '=']):
                                        if smiles not in seen_smiles:
                                            seen_smiles.add(smiles)
                                            model = extract_model(chat_file.name)

                                            # Get data from existing CSV if available
                                            if smiles in existing_data:
                                                row = existing_data[smiles].copy()
                                            else:
                                                row = {
                                                    'Prompt': prompt_num,
                                                    'Model': model,
                                                    'SMILES': smiles,
                                                    'Compound_Name': compound,
                                                    'Binding_Affinity_kcal_mol': '-',
                                                    'Binding_Residues': '-',
                                                    'Previously_Found': 'False',
                                                }

                                            if 'Prompt' not in row:
                                                row['Prompt'] = prompt_num
                                            if 'Model' not in row:
                                                row['Model'] = model

                                            final_recs.append(row)
                                            found_section = True
                                            print(f"✓ P{prompt_num:2} {model:20} | {compound:40} | {smiles[:50]}")

        except Exception as e:
            print(f"✗ P{prompt_num} {chat_file.name}: {str(e)[:50]}")

print(f"\n{'='*120}")
print(f"EXTRACTION COMPLETE")
print(f"{'='*120}")
print(f"Total final recommendations found: {len(final_recs)}")

# Separate into known and new
known_names = {'Lovastatin', 'Capric Acid', 'Citral', 'Eugenol', 'Limonene', 'p-cymene', 'Bromoform'}
known = [r for r in final_recs if any(k.lower() == r.get('Compound_Name', '').lower() for k in known_names)]
new = [r for r in final_recs if not any(k.lower() == r.get('Compound_Name', '').lower() for k in known_names)]

print(f"Known inhibitors: {len(known)}")
print(f"New compounds: {len(new)}")

# Sort by binding affinity
def sort_key(row):
    try:
        return float(row.get('Binding_Affinity_kcal_mol', '999'))
    except:
        return 999

known.sort(key=sort_key)
new.sort(key=sort_key)

# Write CSV
output_csv = base_dir / "SMILES_Final_Recommendations_Only.csv"
with open(output_csv, 'w', newline='') as f:
    fieldnames = ['Rank', 'SMILES', 'Compound_Name', 'Binding_Affinity_kcal_mol', 'Binding_Residues', 'Model', 'Prompt', 'Previously_Found']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    rank = 1
    for row in known + new:
        writer.writerow({
            'Rank': rank,
            'SMILES': row.get('SMILES', ''),
            'Compound_Name': row.get('Compound_Name', ''),
            'Binding_Affinity_kcal_mol': row.get('Binding_Affinity_kcal_mol', ''),
            'Binding_Residues': row.get('Binding_Residues', ''),
            'Model': row.get('Model', ''),
            'Prompt': row.get('Prompt', ''),
            'Previously_Found': row.get('Previously_Found', ''),
        })
        rank += 1

print(f"\n✓ Saved CSV: {output_csv}")
