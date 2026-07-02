#!/usr/bin/env python3
"""Filter to only novel compounds, remove known inhibitors, rank by binding affinity."""

import json
from pathlib import Path

base_dir = Path("/Users/annalevison/Library/CloudStorage/OneDrive-UniversityofReading/chem/ollama_prompts/Prompts/MCR_Agent")

# Known inhibitors to exclude (case-insensitive)
# Includes: validated MCR inhibitors + natural phenolic acids + amino acids + well-known plant compounds
known_inhibitors = {
    # Previously validated MCR inhibitors
    'Lovastatin', 'Capric Acid', 'Capric acid',
    'Citral', 'citral',
    'Eugenol', 'eugenol',
    'Limonene', 'limonene',
    'p-cymene', 'p-Cymene',
    'Bromoform', 'bromoform',
    'Rosmarinic acid', 'rosmarinic acid',
    'Alliin', 'alliin',
    'a-pinene', 'alpha-pinene', 'α-pinene',

    # Natural phenolic acids (well-studied in literature)
    'p-Coumaric acid', 'p-coumaric acid',
    'p-Coumaryl alcohol', 'p-coumaryl alcohol',
    'Caffeic acid', 'caffeic acid',
    'Chlorogenic acid', 'chlorogenic acid',
    'Dicaffeoylquinic acid', 'dicaffeoylquinic acid',
    'Ferulic acid', 'ferulic acid',
    'Rosmarinic acid',

    # Terpenes (well-characterized essential oil components)
    'Geraniol', 'geraniol',
    'Cinnamic acid', 'cinnamic acid',
    'Isoeugenol', 'isoeugenol',

    # Amino acids (not novel MCR inhibitor candidates)
    'Homocysteine', 'homocysteine',
    'Cysteine', 'cysteine',
    '2-amino-4-sulfanylbutanoic acid',
    '2-amino-3-sulfanylpropanoic acid',
}

# Load JSON
json_file = base_dir / "final_extraction_comprehensive.json"
with open(json_file, 'r') as f:
    data = json.load(f)

print("Filtering for NOVEL compounds only (removing known inhibitors)...")

# Collect all compounds with their metadata
all_compounds = []
summary_by_prompt = data.get("summary_by_prompt", {})

for prompt_key, prompt_data in summary_by_prompt.items():
    prompt_num = prompt_data.get("prompt_number")
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

        # Get compound name
        compound_name = ""
        for key in ["Compound", "Compound name", "compound_name"]:
            if key in comp:
                compound_name = str(comp[key]).strip()
                break

        # Strip markdown formatting from compound name
        compound_name_clean = compound_name.replace("**", "").replace("*", "").strip()

        # Check if it's a known inhibitor
        is_known = any(k.lower() == compound_name_clean.lower() for k in known_inhibitors)

        if is_known:
            print(f"  Skipping known: {compound_name} ({smiles[:40]}...)")
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

        # Get residues
        residues = ""
        for key in comp.keys():
            if "residue" in key.lower() or "target" in key.lower():
                residues = str(comp[key]).strip()
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

        all_compounds.append({
            "Prompt": prompt_num,
            "SMILES": smiles,
            "Compound_Name": compound_name_clean,
            "Docking_Score": docking_score,
            "Binding_Residues": residues,
            "QED": qed,
            "NP_Score": np_score,
            "SAS_Score": sas_score,
            "MW": mw,
            "LogP": logp,
        })

# Deduplicate by SMILES, keep best docking score
seen_smiles = {}
for comp in all_compounds:
    smiles = comp["SMILES"]
    if smiles not in seen_smiles:
        seen_smiles[smiles] = comp
    else:
        # Keep the one with better docking score
        existing = seen_smiles[smiles]
        if comp["Docking_Score"] and existing["Docking_Score"]:
            if comp["Docking_Score"] < existing["Docking_Score"]:
                seen_smiles[smiles] = comp

novel_compounds = list(seen_smiles.values())

# Sort by docking score (lower = better binding)
novel_compounds.sort(key=lambda x: (x["Docking_Score"] if x["Docking_Score"] else 999))

print(f"\n✓ Novel compounds identified: {len(novel_compounds)}")

# Write CSV
output_csv = base_dir / "MCR_Novel_Compounds_Final.csv"
with open(output_csv, 'w') as f:
    f.write("Rank,SMILES,Compound_Name,Docking_Score,Binding_Residues,QED,NP_Score,SAS_Score,MW,LogP,Prompt\n")

    rank = 1
    for comp in novel_compounds:
        name = comp['Compound_Name'].replace('"', '""')
        residues = comp['Binding_Residues'].replace('"', '""')
        f.write(f'{rank},"{comp["SMILES"]}","{name}",{comp["Docking_Score"] if comp["Docking_Score"] else ""},"{residues}",{comp["QED"]},{comp["NP_Score"]},{comp["SAS_Score"]},{comp["MW"]},{comp["LogP"]},{comp["Prompt"]}\n')
        rank += 1

print(f"✓ CSV saved: {output_csv}")

# Show top 20
print(f"\n=== TOP 20 NOVEL COMPOUNDS BY BINDING AFFINITY ===\n")
for i, comp in enumerate(novel_compounds[:20], 1):
    docking = f"{comp['Docking_Score']:.1f}" if comp['Docking_Score'] else "?"
    print(f"{i:2}. [{docking:6}] P{comp['Prompt']} | {comp['Compound_Name']:45} | {comp['SMILES'][:50]}")
