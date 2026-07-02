#!/usr/bin/env python3
"""Extract final recommendations from prompts 11-13 with comprehensive metadata."""

import json
from pathlib import Path
from collections import defaultdict

base_dir = Path("/Users/annalevison/Library/CloudStorage/OneDrive-UniversityofReading/chem/ollama_prompts/Prompts/MCR_Agent")

# Known compounds to exclude (exact SMILES match)
known_smiles = {
    'C=CC[S@](=O)C[C@@H](C(=O)O)N',  # Alliin
    'C1=CC(=C(C=C1C[C@H](C(=O)O)OC(=O)/C=C/C2=CC(=C(C=C2)O)O)O)O',  # Rosmarinic Acid
    'C1=CC(=CC=C1/C=C/C(=O)O)O',  # p-coumaric acid
    'C1=CC=C(C(=C1)/C=C/C(=O)O)O',  # o-coumaric acid
    'C1=CC(=CC(=C1)O)/C=C/C(=O)O',  # m-coumaric acid
    'C(Br)(Br)Br',  # Bromoform
    'CC1=CCC(CC1)C(=C)C',  # Limonene
    'CC1=C[C@H]2C[C@@H](C1)C2(C)C',  # a-pinene
    'COC1=C(C=CC(=C1)CC=C)O',  # Eugenol
    'CC1=CC=C(C=C1)C(C)C',  # p-cymene
    'CC(=CCC/C(=C/C=O)/C)C',  # Citral
    'CC[C@H](C)C(=O)O[C@H]1C[C@H](C=C2[C@H]1[C@H]([C@H](C=C2)C)CC[C@@H]3C[C@H](CC(=O)O3)O)C',  # Lovastatin
    'CCCCCCCCCC(=O)O',  # Capric Acid
}

# Load JSON
json_file = base_dir / "final_extraction_comprehensive.json"
with open(json_file, 'r') as f:
    data = json.load(f)

print("Extracting final recommendations from Prompts 11-13...\n")

# Collect all compounds from prompts 11-13
compounds_dict = defaultdict(list)  # SMILES -> list of occurrences
summary_by_prompt = data.get("summary_by_prompt", {})

for prompt_key, prompt_data in summary_by_prompt.items():
    prompt_num = prompt_data.get("prompt_number")

    # Only prompts 11-13
    if prompt_num not in [11, 12, 13]:
        continue

    print(f"Processing Prompt {prompt_num}...")
    sample_compounds = prompt_data.get("sample_compounds", [])

    for comp in sample_compounds:
        # Get clean SMILES
        smiles = comp.get("SMILES_clean", "").strip()
        if not smiles:
            for key in comp.keys():
                if "smiles" in key.lower():
                    val = comp[key]
                    smiles = val.replace("`", "").replace("**", "").strip()
                    if smiles:
                        break

        if not smiles or len(smiles) < 5:
            continue

        # Check if it's a known compound
        if smiles in known_smiles:
            print(f"  ⊗ Skipping known: {smiles[:50]}...")
            continue

        # Extract all metadata
        compound_name = ""
        for key in ["Compound", "Compound name", "compound_name"]:
            if key in comp:
                compound_name = str(comp[key]).strip().replace("**", "").replace("*", "")
                break

        docking_score = None
        for key in comp.keys():
            if "docking" in key.lower() and "score" in key.lower():
                val_str = str(comp[key]).replace("**", "").replace("−", "-").replace("‐", "-").strip()
                try:
                    docking_score = float(val_str)
                    break
                except:
                    pass

        residues = ""
        for key in comp.keys():
            if "residue" in key.lower() or "target" in key.lower():
                residues = str(comp[key]).strip()
                break

        qed = comp.get("QED", "")
        np_score = comp.get("NP Score", "")
        sas_score = comp.get("SAS Score", "")
        mw = ""
        for key in ["MW", "MW (g·mol⁻¹)", "MW (g mol⁻¹)"]:
            if key in comp:
                mw = str(comp[key])
                break
        logp = comp.get("LogP", "")

        availability = comp.get("Commercial Availability", "")
        for key in ["Availability", "Rumen Suitability"]:
            if key in comp and not availability:
                availability = str(comp[key]).strip()

        # Store compound with all metadata
        compounds_dict[smiles].append({
            "Prompt": prompt_num,
            "Compound_Name": compound_name,
            "Docking_Score": docking_score,
            "Binding_Residues": residues,
            "QED": qed,
            "NP_Score": np_score,
            "SAS_Score": sas_score,
            "MW": mw,
            "LogP": logp,
            "Availability": availability,
        })

# Deduplicate: for each SMILES, keep the one with best docking score
final_compounds = []
for smiles, occurrences in compounds_dict.items():
    # Sort by docking score, take the best one
    best = max(occurrences, key=lambda x: -999 if x["Docking_Score"] is None else -x["Docking_Score"])
    best["SMILES"] = smiles
    best["Frequency"] = len(occurrences)
    final_compounds.append(best)

# Sort by docking score (best first = lowest/most negative)
final_compounds.sort(key=lambda x: (999 if x["Docking_Score"] is None else x["Docking_Score"]))

print(f"\n✓ Total unique compounds: {len(final_compounds)}")
print(f"✓ Total occurrences: {sum(c['Frequency'] for c in final_compounds)}")

# Write CSV
output_csv = base_dir / "Prompts_11_13_Final_Recommendations.csv"
with open(output_csv, 'w') as f:
    header = "Rank,SMILES,Compound_Name,Docking_Score,Binding_Residues,Frequency,Commercial_Availability,QED,NP_Score,SAS_Score,MW,LogP,Prompt\n"
    f.write(header)

    for rank, comp in enumerate(final_compounds, 1):
        name = comp['Compound_Name'].replace('"', '""')
        residues = comp['Binding_Residues'].replace('"', '""')
        avail = comp['Availability'].replace('"', '""')
        f.write(f'{rank},"{comp["SMILES"]}","{name}",{comp["Docking_Score"] if comp["Docking_Score"] else ""},"{residues}",{comp["Frequency"]},"{avail}",{comp["QED"]},{comp["NP_Score"]},{comp["SAS_Score"]},{comp["MW"]},{comp["LogP"]},{comp["Prompt"]}\n')

print(f"✓ CSV saved: {output_csv}\n")

# Display results
print(f"{'='*150}")
print(f"FINAL RECOMMENDATIONS - PROMPTS 11-13")
print(f"{'='*150}\n")
print(f"{'Rank':<5} {'Affinity':<10} {'Freq':<5} {'Compound':<40} {'Residues':<20} {'Avail':<15}")
print(f"{'-'*150}")

for rank, comp in enumerate(final_compounds, 1):
    aff = f"{comp['Docking_Score']:.1f}" if comp['Docking_Score'] else "?"
    freq = comp['Frequency']
    name = comp['Compound_Name'][:38] if comp['Compound_Name'] else comp['SMILES'][:38]
    res = comp['Binding_Residues'][:18] if comp['Binding_Residues'] else "-"
    avail = comp['Availability'][:13] if comp['Availability'] else "Unknown"
    print(f"{rank:<5} {aff:<10} {freq:<5} {name:<40} {res:<20} {avail:<15}")

print(f"\n{'='*150}")
