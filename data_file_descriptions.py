"""
Merged data file descriptions extracted from the "data set" document.
This file lists all output data files and their descriptions.
"""

COMPLETE_ASSET_DATA_FILES = [
    {
        "path": "complete_asset_data/exploration/exploration_data.json",
        "description": "Full exploration data (synthetic).",
        "phase": "exploration",
    },
    {
        "path": "complete_asset_data/exploration/seismic_data.h5",
        "description": "Seismic data (optional HDF5 output).",
        "phase": "exploration",
    },
    {
        "path": "complete_asset_data/development/development_data.json",
        "description": "Development and planning data.",
        "phase": "development",
    },
    {
        "path": "complete_asset_data/production/production_data.json",
        "description": "Production and operations data.",
        "phase": "production",
    },
    {
        "path": "complete_asset_data/production/csv_data/PROD-001_sample.csv",
        "description": "Sample time-series CSV for production data (example).",
        "phase": "production",
    },
    {
        "path": "complete_asset_data/production/csv_data/PROD-002_sample.csv",
        "description": "Sample time-series CSV for production data (example).",
        "phase": "production",
    },
    {
        "path": "complete_asset_data/maintenance/maintenance_data.json",
        "description": "Maintenance and revamp data.",
        "phase": "maintenance",
    },
    {
        "path": "complete_asset_data/decommissioning/decommissioning_data.json",
        "description": "Decommissioning data.",
        "phase": "decommissioning",
    },
    {
        "path": "complete_asset_data/common/common_data.json",
        "description": "Common shared data across phases.",
        "phase": "common",
    },
    {
        "path": "complete_asset_data/metadata.json",
        "description": "Complete metadata for the generated dataset.",
        "phase": "common",
    },
    {
        "path": "complete_asset_data/generation_summary.txt",
        "description": "Generation summary report.",
        "phase": "common",
    },
    {
        "path": "complete_asset_data/images/thermography/",
        "description": "Thermography images (synthetic) for MNT-001.2 / CNN analysis.",
        "phase": "maintenance",
    },
    {
        "path": "complete_asset_data/images/core/",
        "description": "Core sample images (synthetic) for EXP-002.4 core photo integration.",
        "phase": "exploration",
    },
    {
        "path": "complete_asset_data/images/seismic/",
        "description": "Seismic section images (synthetic) for EXP-005.1 fault detection / CNN.",
        "phase": "exploration",
    },
    {
        "path": "complete_asset_data/images/data_visualization.png",
        "description": "Summary visualization image of generated data.",
        "phase": "common",
    },
    {
        "path": "complete_asset_data/images/image_manifest.json",
        "description": "Manifest of generated image paths and metadata.",
        "phase": "common",
    },
]

GAS_PLANT_OUTPUT_FILES = [
    {
        "path": "synthetic_data_output/csv_files/plant_data_main.csv",
        "description": "First 100,000 rows of plant data (demo sample).",
        "phase": "production",
    },
    {
        "path": "synthetic_data_output/plant_data_full.parquet",
        "description": "Full plant dataset (about 15.7M points).",
        "phase": "production",
    },
    {
        "path": "synthetic_data_output/gas_composition.csv",
        "description": "Gas composition data.",
        "phase": "production",
    },
    {
        "path": "synthetic_data_output/failure_events.csv",
        "description": "Failure event log.",
        "phase": "maintenance",
    },
    {
        "path": "synthetic_data_output/gas_plant_data.db",
        "description": "Full SQLite database of the gas plant data.",
        "phase": "production",
    },
    {
        "path": "synthetic_data_output/text_data/shift_reports.csv",
        "description": "Shift reports (text data).",
        "phase": "operations",
    },
    {
        "path": "synthetic_data_output/text_data/work_orders.csv",
        "description": "Work orders (text data).",
        "phase": "maintenance",
    },
    {
        "path": "synthetic_data_output/text_data/alarm_logs.csv",
        "description": "Alarm logs (text data).",
        "phase": "operations",
    },
    {
        "path": "synthetic_data_output/sample_data_24h.csv",
        "description": "First 24 hours of data (sample).",
        "phase": "production",
    },
    {
        "path": "synthetic_data_output/metadata.json",
        "description": "Complete metadata for the gas plant dataset.",
        "phase": "common",
    },
    {
        "path": "synthetic_data_output/generation_summary.txt",
        "description": "Generation summary report.",
        "phase": "common",
    },
    {
        "path": "synthetic_data_output/data_visualization.png",
        "description": "Visualization image created by the optional visualizer.",
        "phase": "common",
    },
]

ALL_DATA_FILES = COMPLETE_ASSET_DATA_FILES + GAS_PLANT_OUTPUT_FILES

if __name__ == "__main__":
    print("Total data files:", len(ALL_DATA_FILES))
    for entry in ALL_DATA_FILES:
        print(f"- {entry['path']}: {entry['description']}")
