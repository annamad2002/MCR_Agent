#!/usr/bin/env python3
"""
Test the master SMILES list against known binders and flag them.
"""

import pandas as pd
from pathlib import Path

# Known binders list
known_binders = {
    'C(Br)(Br)Br': 'Bromoform',
    'CC1=CCC(CC1)C(=C)C': 'Limonene',
    'CC1=C[C@H]2C[C@@H](C1)C2(C)C': 'a-pinene',
    'COC1=C(C=CC(=C1)CC=C)O': 'Eugenol',
    'CC1=CC=C(C=C1)C(C)C': 'p-cymene',
    'CC(=CCC/C(=C/C=O)/C)C': 'Citral',
    'CC[C@H](C)C(=O)O[C@H]1C[C@H](C=C2[C@H]1[C@H]([C@H](C=C2)C)CC[C@@H]3C[C@H](CC(=O)O3)O)C': 'Lovastatin',
    'CCCCCCCCCC(=O)O': 'Capric Acid',
}

# Load master CSV
base_dir = Path("/Users/annalevison/Library/CloudStorage/OneDrive-UniversityofReading/chem/ollama_prompts/Prompts/MCR_Agent")
df = pd.read_csv(base_dir / "SMILES_List_Master.csv")

# Add a column to flag previously found compounds
df['Previously_Found'] = df['SMILES'].isin(known_binders.keys())
df['Compound_Name'] = df['SMILES'].map(lambda x: known_binders.get(x, ''))

# Save the updated CSV
output_file = base_dir / "SMILES_List_Master.csv"
df.to_csv(output_file, index=False)

# Print results
print("Known Binders Check Results")
print("=" * 80)
print(f"\nTotal compounds in master list: {len(df)}")
print(f"Known binders tested: {len(known_binders)}")

# Check which known binders were found
found_count = 0
print("\n" + "=" * 80)
print("KNOWN BINDERS FOUND IN MASTER LIST:")
print("=" * 80)
for smiles, name in known_binders.items():
    if smiles in df['SMILES'].values:
        found_count += 1
        entry = df[df['SMILES'] == smiles].iloc[0]
        print(f"\n✓ {name}")
        print(f"  SMILES: {smiles}")
        print(f"  Binding Affinity: {entry['Binding_Affinity_kcal_mol']} kcal/mol")
        print(f"  Model: {entry['Model']}")
        print(f"  Prompt: {entry['Prompt']}")
    else:
        print(f"\n✗ {name} - NOT FOUND in master list")
        print(f"  SMILES: {smiles}")

print("\n" + "=" * 80)
print(f"Summary: {found_count}/{len(known_binders)} known binders found")
print("=" * 80)

# Show top new candidates (those not in known list)
print("\n\nTOP NEW CANDIDATES (not in known binders list):")
print("=" * 80)
new_compounds = df[~df['Previously_Found']].head(10)
for idx, row in new_compounds.iterrows():
    print(f"\n{idx+1}. Binding Affinity: {row['Binding_Affinity_kcal_mol']} kcal/mol")
    print(f"   SMILES: {row['SMILES']}")
    print(f"   Model: {row['Model']}, Prompt: {row['Prompt']}")
