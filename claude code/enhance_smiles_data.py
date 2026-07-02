#!/usr/bin/env python3
"""
Enhance SMILES data with compound names from PubChem and binding residues from chat logs.
"""

import pandas as pd
import pubchempy as pcp
import re
from pathlib import Path

base_dir = Path("/Users/annalevison/Library/CloudStorage/OneDrive-UniversityofReading/chem/ollama_prompts/Prompts/MCR_Agent")

# Load master CSV
df = pd.read_csv(base_dir / "SMILES_List_Master.csv")

print("=" * 80)
print("Enhancing compound data...")
print("=" * 80)

# 1. Fetch compound names from PubChem for empty entries
print("\n1. Fetching compound names from PubChem...")

def get_compound_name(smiles):
    """Fetch compound name from PubChem using SMILES."""
    try:
        results = pcp.get_compounds(smiles, namespace='smiles')
        if results:
            compound = results[0]
            # Try to get IUPAC name, fallback to synonym
            if hasattr(compound, 'iupac_name') and compound.iupac_name:
                return compound.iupac_name
            elif hasattr(compound, 'synonyms') and compound.synonyms:
                return compound.synonyms[0]
            elif hasattr(compound, 'cid'):
                return f"PubChem CID: {compound.cid}"
    except Exception as e:
        pass
    return ""

# Fill in missing compound names
missing_count = 0
for idx, row in df.iterrows():
    if pd.isna(row['Compound_Name']) or row['Compound_Name'] == '' or row['Compound_Name'] == 'nan':
        smiles = row['SMILES']
        print(f"  Looking up: {smiles[:50]}...", end=" ")
        name = get_compound_name(smiles)
        if name:
            df.at[idx, 'Compound_Name'] = name
            missing_count += 1
            print(f"✓ Found: {name[:50]}")
        else:
            print("✗ No name found")

print(f"✓ Updated {missing_count} compound names")

# 2. Extract binding residues from chat logs
print("\n2. Extracting binding residues from chat logs...")

def extract_residues_from_chatlog(prompt_num, model_name):
    """Extract binding residues for a specific compound from chat logs."""
    # Look for mentions of residues like PHE360, TYR366, F43602, etc.
    residue_pattern = r'(PHE\d+|TYR\d+|SER\d+|LEU\d+|VAL\d+|ASP\d+|GLU\d+|LYS\d+|ARG\d+|GLY\d+|ALA\d+|PRO\d+|ASN\d+|GLN\d+|HIS\d+|CYS\d+|MET\d+|TRP\d+|ILE\d+|THR\d+|F\d+|UNK\d+)'

    # Try to find the chat log file
    prompt_dir = base_dir / str(prompt_num)
    if not prompt_dir.exists():
        return ""

    for filepath in prompt_dir.iterdir():
        if filepath.is_dir():
            continue
        # Check if this file matches the model name
        if model_name.replace('.md', '') in filepath.name or str(prompt_num) in filepath.name:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Find residue mentions
                    residues = re.findall(residue_pattern, content)
                    if residues:
                        # Remove duplicates and specific ones mentioned in prompts
                        unique_residues = list(set(residues))
                        # Filter to known target residues
                        target_residues = ['F43602', 'PHE360', 'PHE440', 'TYR366', 'UNK0']
                        found_targets = [r for r in unique_residues if r in target_residues]
                        if found_targets:
                            return ', '.join(found_targets)
            except Exception as e:
                pass

    return ""

# Add binding_residues column
df['Binding_Residues'] = df.apply(
    lambda row: extract_residues_from_chatlog(int(row['Prompt']), row['Model']),
    axis=1
)

residue_count = df['Binding_Residues'].str.len().sum()
print(f"✓ Extracted residue information ({residue_count} entries with data)")

# Save updated CSV
df.to_csv(base_dir / "SMILES_List_Master.csv", index=False)
print("\n✓ Updated CSV saved")

# 3. Create enhanced markdown
print("\n3. Creating enhanced markdown file...")

md_content = "# MCR Inhibitor Compounds - Master List\n\n"
md_content += f"**Total Unique Compounds:** {len(df)}\n\n"
md_content += f"**Binding Affinity Range:** {df['Binding_Affinity_kcal_mol'].min()} to {df['Binding_Affinity_kcal_mol'].max()} kcal/mol\n\n"
md_content += f"**Average Binding Affinity:** {df['Binding_Affinity_kcal_mol'].mean():.2f} kcal/mol\n\n"

previously_found_count = df['Previously_Found'].sum()
md_content += f"**Previously Found Compounds:** {int(previously_found_count)}\n\n"
md_content += f"**New Compounds:** {len(df) - int(previously_found_count)}\n\n"

md_content += "---\n\n"

# Create enhanced table
md_content += "| Rank | SMILES | Compound Name | Binding Affinity (kcal/mol) | Binding Residues | Model | Prompt | Previously Found |\n"
md_content += "|------|--------|---------------|-----|------------------|-------|--------|------------------|\n"

for rank, (idx, row) in enumerate(df.iterrows(), 1):
    smiles = row['SMILES']
    smiles_escaped = smiles.replace('|', '\\|')
    compound_name = row['Compound_Name'] if pd.notna(row['Compound_Name']) and row['Compound_Name'] != 'nan' else ""
    affinity = row['Binding_Affinity_kcal_mol']
    residues = row['Binding_Residues'] if pd.notna(row['Binding_Residues']) and row['Binding_Residues'] else "—"
    model = row['Model']
    prompt = int(row['Prompt'])
    prev_found = "✓ Yes" if row['Previously_Found'] else "No"

    # Truncate long compound names for table readability
    if len(compound_name) > 40:
        compound_name = compound_name[:37] + "..."

    md_content += f"| {rank} | `{smiles_escaped[:60]}...` | {compound_name} | {affinity} | {residues} | {model} | {prompt} | {prev_found} |\n"

# Write markdown
with open(base_dir / "SMILES_List_Master.md", 'w') as f:
    f.write(md_content)

print(f"✓ Enhanced markdown file created")

# Print summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"✓ Compound names: {df['Compound_Name'].notna().sum() - df['Compound_Name'].isin(['nan', '']).sum()} found")
print(f"✓ Binding residues: {(df['Binding_Residues'].str.len() > 0).sum()} compounds with residue data")
print(f"✓ CSV updated: {base_dir / 'SMILES_List_Master.csv'}")
print(f"✓ Markdown updated: {base_dir / 'SMILES_List_Master.md'}")
