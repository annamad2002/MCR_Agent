#!/usr/bin/env python3
"""Extract all 82+ unique compounds from agent's comprehensive JSON extraction."""

import json
import csv
from pathlib import Path

base_dir = Path("/Users/annalevison/Library/CloudStorage/OneDrive-UniversityofReading/chem/ollama_prompts/Prompts/MCR_Agent")

# Load JSON
json_file = base_dir / "final_extraction_comprehensive.json"
with open(json_file, 'r') as f:
    data = json.load(f)

print("Extracting all compounds from comprehensive JSON...")

# Collect all compounds
all_compounds = []
seen_smiles = {}

summary_by_prompt = data.get("summary_by_prompt", {})
for prompt_key, prompt_data in summary_by_prompt.items():
    prompt_num = prompt_data.get("prompt_number")
    sample_compounds = prompt_data.get("sample_compounds", [])

    for comp in sample_compounds:
        # Get clean SMILES
        smiles = comp.get("SMILES_clean", "").strip()
        if not smiles:
            # Try other SMILES fields
            for key in comp.keys():
                if "smiles" in key.lower():
                    val = comp[key]
                    smiles = val.replace("`", "").replace("**", "").strip()
                    if smiles:
                        break

        if not smiles or len(smiles) < 5:
            continue

        # Get docking score
        docking_score = None
        for key in comp.keys():
            if "docking" in key.lower() and "score" in key.lower():
                val_str = str(comp[key]).replace("**", "").replace("−", "-").replace("‐", "-").strip()
                try:
                    docking_score = float(val_str)
                    break
                except:
                    pass

        # Get compound name
        compound_name = ""
        for key in ["Compound", "Compound name", "compound_name"]:
            if key in comp:
                compound_name = str(comp[key])
                break

        # Get residues
        residues = ""
        for key in ["Target Residues", "Interacting Residues", "residues"]:
            if key in comp:
                residues = str(comp[key])
                break

        # Get QED
        qed = comp.get("QED", "")

        # Get MW
        mw = ""
        for key in ["MW", "MW (g·mol⁻¹)", "MW (g mol⁻¹)"]:
            if key in comp:
                mw = str(comp[key])
                break

        # Get LogP
        logp = comp.get("LogP", "")

        # Get NP Score
        np_score = comp.get("NP Score", "")

        # Get SAS Score
        sas_score = comp.get("SAS Score", "")

        # Track if we've seen this SMILES before
        if smiles in seen_smiles:
            # Update with better docking score if available
            existing = seen_smiles[smiles]
            if docking_score and (not existing.get("Docking_Score") or docking_score < existing["Docking_Score"]):
                seen_smiles[smiles] = {
                    "Prompt": prompt_num,
                    "SMILES": smiles,
                    "Compound_Name": compound_name,
                    "Docking_Score": docking_score,
                    "Binding_Residues": residues,
                    "QED": qed,
                    "NP_Score": np_score,
                    "SAS_Score": sas_score,
                    "MW": mw,
                    "LogP": logp,
                }
        else:
            seen_smiles[smiles] = {
                "Prompt": prompt_num,
                "SMILES": smiles,
                "Compound_Name": compound_name,
                "Docking_Score": docking_score,
                "Binding_Residues": residues,
                "QED": qed,
                "NP_Score": np_score,
                "SAS_Score": sas_score,
                "MW": mw,
                "LogP": logp,
            }

all_compounds = list(seen_smiles.values())
print(f"Extracted {len(all_compounds)} unique compounds from all prompts")

# Sort by docking score
all_compounds.sort(key=lambda x: (x["Docking_Score"] if x["Docking_Score"] else 999))

# Separate known from new
known_names = {'Lovastatin', 'Capric Acid', 'Capric acid', 'Citral', 'citral',
               'Eugenol', 'eugenol', 'Limonene', 'limonene', 'p-cymene', 'Bromoform',
               'p-Coumaric acid', 'p-coumaric acid', 'Caffeic acid', 'caffeic acid',
               'Rosmarinic acid', 'Alliin', 'a-pinene', 'alpha-pinene'}

known = [c for c in all_compounds if any(k.lower() == (c["Compound_Name"] or "").lower() for k in known_names)]
new = [c for c in all_compounds if not any(k.lower() == (c["Compound_Name"] or "").lower() for k in known_names)]

print(f"Known: {len(known)}, Novel: {len(new)}")

# Write comprehensive CSV
output_csv = base_dir / "MCR_Final_Recommendations_All_Compounds.csv"
with open(output_csv, 'w', newline='') as f:
    fieldnames = ['Rank', 'Category', 'SMILES', 'Compound_Name', 'Docking_Score', 'Binding_Residues', 'QED', 'NP_Score', 'SAS_Score', 'MW', 'LogP', 'Prompt']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    rank = 1
    for comp in all_compounds:
        category = 'Known' if any(k.lower() == (comp['Compound_Name'] or '').lower() for k in known_names) else 'Novel'
        writer.writerow({
            'Rank': rank,
            'Category': category,
            'SMILES': comp['SMILES'],
            'Compound_Name': comp['Compound_Name'],
            'Docking_Score': comp['Docking_Score'] if comp['Docking_Score'] else '',
            'Binding_Residues': comp['Binding_Residues'],
            'QED': comp['QED'],
            'NP_Score': comp['NP_Score'],
            'SAS_Score': comp['SAS_Score'],
            'MW': comp['MW'],
            'LogP': comp['LogP'],
            'Prompt': comp['Prompt'],
        })
        rank += 1

print(f"\n✓ Comprehensive CSV saved: {output_csv}")
print(f"✓ Total unique compounds: {len(all_compounds)}")
print(f"✓ Range: {len(known)} known + {len(new)} novel")

# Show top 10
print(f"\nTop 10 compounds by docking score:")
for i, comp in enumerate(all_compounds[:10], 1):
    print(f"{i:2}. [{comp['Category']:6}] {comp['Compound_Name']:40} | Docking: {str(comp['Docking_Score']):6} | P{comp['Prompt']}")
