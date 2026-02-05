#!/usr/bin/env python3
"""
Generate all synthetic image data for the dataset and optionally load for verification.
Run from project root: python -m backend.scripts.generate_image_data
Or from backend: python scripts/generate_image_data.py
"""
from pathlib import Path
import sys

# Ensure backend is on path so "app" is found
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.data_generator.image_data_generator import generate_and_export_all_image_data
from app.data_generator.image_loader import load_all_image_data, get_image_manifest


def main():
    # Output under project root (parent of backend) by default
    project_root = backend_dir.parent
    output_dir = project_root / "complete_asset_data"

    print("Generating image data (thermography, core, seismic, visualization)...")
    manifest = generate_and_export_all_image_data(
        base_output_dir=str(output_dir),
        thermography_count=10,
        core_count=5,
        seismic_count=6,
        data_dir_for_viz=str(output_dir / "production"),
        seed=42,
    )
    print("Generated:")
    print("  Thermography:", len(manifest["thermography"]), "images")
    print("  Core:", len(manifest["core"]), "images")
    print("  Seismic:", len(manifest["seismic"]), "images")
    print("  Visualization:", manifest["visualization"])

    # Load and verify
    print("\nVerifying load...")
    data = load_all_image_data(output_dir)
    print("  Thermography loaded:", len(data["thermography"]["arrays"]))
    print("  Core loaded:", len(data["core"]["arrays"]))
    print("  Seismic loaded:", len(data["seismic"]["arrays"]))
    print("  Visualization loaded:", data["visualization"] is not None)
    print("\nDone. Images are in:", output_dir / "images")


if __name__ == "__main__":
    main()
