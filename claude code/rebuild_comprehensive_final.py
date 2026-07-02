#!/usr/bin/env python3
"""Rebuild comprehensive final recommendations from full extraction JSON."""

import json
import csv
from pathlib import Path

base_dir = Path("/Users/annalevison/Library/CloudStorage/OneDrive-UniversityofReading/chem/ollama_prompts/Prompts/MCR_Agent")

# Load comprehensive extraction
json_file = base_dir / "final_extraction_comprehensive.json"
with open(json_file, 'r') as f:
    data = json.load(f)

print("Building comprehensive final recommendations from full extraction...")

# Flatten all compounds from all prompts
all_compounds = []
for prompt_key, prompt_data in data.items():
    if prompt_key.startswith("Prompt_"):
        prompt_num = prompt_data.get("prompt_number")
        compounds = prompt_data.get("compounds", [])

        for comp in compounds:
            # Extract and clean SMILES
            smiles = None
            if "SMILES_clean" in comp:
                smiles = comp["SMILES_clean"]
            elif "SMILES" in comp:
                smiles_raw = comp.get("SMILES", "")
                # Clean markdown formatting
                smiles = smiles_raw.replace("`", "").replace("**", "").strip()

            if smiles:
                # Extract binding affinity
                docking_score = None
                for key in comp.keys():
                    if "docking" in key.lower() or "score" in key.lower():
                        val = comp[key]
                        # Clean the value
                        val_str = str(val).replace("**", "").replace("−", "-").replace("‐", "-").strip()
                        try:
                            docking_score = float(val_str)
                            break
                        except:
                            pass

                compound_name = None
                for key in ["Compound name", "compound_name", "Compound", "compound"]:
                    if key in comp:
                        compound_name = comp[key]
                        break

                residues = None
                for key in ["Target Residues Engaged", "Interacting Residues", "residues", "Binding Residues"]:
                    if key in comp:
                        residues = comp[key]
                        break

                availability = None
                for key in ["Commercial Availability", "Rumen Suitability", "Availability"]:
                    if key in comp:
                        availability = comp[key]
                        break

                all_compounds.append({
                    "Prompt": prompt_num,
                    "SMILES": smiles,
                    "Compound_Name": compound_name or "",
                    "Docking_Score": docking_score,
                    "Binding_Residues": residues or "",
                    "Availability": availability or "Unknown",
                    "QED": comp.get("QED", ""),
                    "NP_Score": comp.get("NP Score", ""),
                    "SAS_Score": comp.get("SAS Score", ""),
                    "MW": comp.get("MW", "") or comp.get("MW (g·mol⁻¹)", ""),
                    "LogP": comp.get("LogP", ""),
                })

print(f"Extracted {len(all_compounds)} total compound entries")

# Deduplicate by SMILES, keep best docking score
seen_smiles = {}
deduplicated = []
for comp in all_compounds:
    smiles = comp["SMILES"]
    if smiles not in seen_smiles:
        seen_smiles[smiles] = comp
        deduplicated.append(comp)
    else:
        # Keep the one with better docking score
        existing = seen_smiles[smiles]
        if comp["Docking_Score"] and existing["Docking_Score"]:
            if comp["Docking_Score"] < existing["Docking_Score"]:
                # Better score (lower = better)
                seen_smiles[smiles] = comp
                # Find and replace in list
                for i, c in enumerate(deduplicated):
                    if c["SMILES"] == smiles:
                        deduplicated[i] = comp
                        break

print(f"After deduplication: {len(deduplicated)} unique SMILES")

# Sort by docking score
deduplicated.sort(key=lambda x: (x["Docking_Score"] if x["Docking_Score"] else 999))

# Separate known from new
known_names = {'Lovastatin', 'Capric Acid', 'Capric acid', 'Citral', 'citral', 'Eugenol', 'eugenol', 'Limonene', 'limonene', 'p-cymene', 'Bromoform', 'p-Coumaric acid', 'p-coumaric acid', 'Caffeic acid', 'caffeic acid'}
known = [c for c in deduplicated if any(k.lower() == (c["Compound_Name"] or "").lower() for k in known_names)]
new = [c for c in deduplicated if not any(k.lower() == (c["Compound_Name"] or "").lower() for k in known_names)]

print(f"Known: {len(known)}, New: {len(new)}")

# Write CSV
output_csv = base_dir / "SMILES_Final_Recommendations_Comprehensive.csv"
with open(output_csv, 'w', newline='') as f:
    fieldnames = ['Rank', 'SMILES', 'Compound_Name', 'Docking_Score', 'Binding_Residues', 'Prompt', 'QED', 'NP_Score', 'SAS_Score', 'MW', 'LogP', 'Availability', 'Category']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    rank = 1
    for comp in deduplicated:
        writer.writerow({
            'Rank': rank,
            'SMILES': comp['SMILES'],
            'Compound_Name': comp['Compound_Name'],
            'Docking_Score': comp['Docking_Score'] if comp['Docking_Score'] else '',
            'Binding_Residues': comp['Binding_Residues'],
            'Prompt': comp['Prompt'],
            'QED': comp['QED'],
            'NP_Score': comp['NP_Score'],
            'SAS_Score': comp['SAS_Score'],
            'MW': comp['MW'],
            'LogP': comp['LogP'],
            'Availability': comp['Availability'],
            'Category': 'Known' if any(k.lower() == (comp['Compound_Name'] or '').lower() for k in known_names) else 'Novel',
        })
        rank += 1

print(f"\n✓ Comprehensive CSV saved: {output_csv}")
print(f"✓ Total compounds: {len(deduplicated)} (Known: {len(known)}, Novel: {len(new)})")
