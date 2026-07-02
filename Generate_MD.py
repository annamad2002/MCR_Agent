"""
generate_compound_md.py

Reads a CSV of compounds and produces a Markdown file with a table:
    SMILES | IUPAC Name | Common Name | Binding Affinity | Structure Image | Prompt | Model

Structure images are rendered from SMILES using RDKit and saved as PNGs in an
'images/' folder next to the output .md file. The .md file references them
with relative paths, so keep the .md and images/ folder together.

USAGE:
    python generate_compound_md.py input_csv output_md

Expected CSV columns (case-insensitive, order doesn't matter):
    SMILES, Affinity, Prompt, Model, IUPAC_Name, Common_Name
"""

import sys
import csv
from pathlib import Path

from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D

# internal_field_name : exact CSV header text to look for (case-insensitive)
COLUMN_MAP = {
    "SMILES": "SMILES",
    "IUPAC_Name": "IUPAC_Name",
    "Common_Name": "Common_Name",
    "Affinity": "Affinity",
    "Prompt": "Prompt",
    "Model": "Model",
}

IMG_SIZE = (300, 300)


def sanitise_filename(s: str) -> str:
    keep = "-_."
    return "".join(c if c.isalnum() or c in keep else "_" for c in str(s))


def render_structure(smiles: str, out_path: Path) -> bool:
    """Render a SMILES string to a PNG file. Returns True on success, False on failure."""
    if not smiles:
        return False
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return False
    drawer = rdMolDraw2D.MolDraw2DCairo(*IMG_SIZE)
    rdMolDraw2D.PrepareAndDrawMolecule(drawer, mol)
    drawer.FinishDrawing()
    with open(out_path, "wb") as f:
        f.write(drawer.GetDrawingText())
    return True


def main(csv_path: str, md_path: str):
    csv_path = Path(csv_path)
    md_path = Path(md_path)
    images_dir = md_path.parent / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # utf-8-sig strips a BOM if present (common in CSVs exported from Excel/Numbers
    # on Mac), and behaves identically to utf-8 if there's no BOM.
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print("ERROR: could not read any column headers from the file.")
            sys.exit(1)
        print(f"Found columns: {reader.fieldnames}")

        headers_lookup = {h.lower().strip(): h for h in reader.fieldnames}
        rows = []
        for raw_row in reader:
            row = {}
            for field, expected_header in COLUMN_MAP.items():
                actual_header = headers_lookup.get(expected_header.lower())
                row[field] = raw_row.get(actual_header, "").strip() if actual_header else ""
            rows.append(row)

    md_lines = [
        "# Compound Tracker",
        "",
        "| SMILES | IUPAC Name | Common Name | Binding Affinity | Structure Image | Prompt | Model |",
        "|--------|------------|-------------|-------------------|------------------|--------|-------|",
    ]

    # Sort by binding affinity: most negative (strongest binding) first.
    # Rows with missing/non-numeric affinity are pushed to the end.
    def affinity_sort_key(row):
        try:
            return (0, float(row["Affinity"]))
        except (ValueError, TypeError):
            return (1, 0.0)

    rows.sort(key=affinity_sort_key)

    failed = []
    skipped_empty = 0
    for row in rows:
        smiles = row["SMILES"]  # no "?" fallback here — keep it empty if missing
        iupac_name = row["IUPAC_Name"] or "-"
        common_name = row["Common_Name"] or "-"
        affinity = row["Affinity"] or "-"
        prompt = row["Prompt"] or "-"
        model = row["Model"] or "-"

        if not smiles:
            skipped_empty += 1
            continue  # no SMILES at all in this row, skip it entirely

        img_filename = f"{sanitise_filename(smiles)}.png"
        img_path = images_dir / img_filename

        if render_structure(smiles, img_path):
            img_md = f"![{common_name or iupac_name}](images/{img_filename})"
        else:
            img_md = "*(could not render)*"
            failed.append((smiles, iupac_name))

        md_lines.append(
            f"| `{smiles}` | {iupac_name} | {common_name} | {affinity} | {img_md} | {prompt} | {model} |"
        )

    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"\nWrote {md_path} with {len(rows) - skipped_empty} compounds.")
    print(f"Images saved to {images_dir}/")
    if skipped_empty:
        print(f"{skipped_empty} rows skipped (no SMILES found).")
    if failed:
        print(f"\n{len(failed)} SMILES failed to render (invalid SMILES string):")
        for smiles, name in failed:
            print(f"  {smiles} ({name})")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_compound_md.py input_csv output_md")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])