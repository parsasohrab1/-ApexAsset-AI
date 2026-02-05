"""
Synthetic image data generator for asset lifecycle dataset.
Generates thermography, core sample, seismic section, and summary visualization images
suitable for CNN training and analysis (e.g. fault detection, thermography analysis).
Uses procedural generation (no GAN/CNN training required).
"""

from pathlib import Path
from datetime import datetime
import json
import numpy as np

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

try:
    from PIL import Image
except ImportError:
    Image = None


# Default image dimensions
THERMOGRAPHY_SHAPE = (256, 256)
CORE_IMAGE_SHAPE = (128, 512)   # width x height (core strip)
SEISMIC_SLICE_SHAPE = (256, 384)  # time/depth x trace
VIZ_FIGSIZE = (15, 10)
VIZ_DPI = 150


def _ensure_pil():
    if Image is None:
        raise ImportError("Pillow is required for core image generation. pip install Pillow")


def _ensure_matplotlib():
    if plt is None:
        raise ImportError("matplotlib is required for image generation. pip install matplotlib")


def generate_thermography_image(
    shape=THERMOGRAPHY_SHAPE,
    hot_spots=3,
    ambient_temp=85.0,
    max_temp=200.0,
    seed=None,
):
    """
    Generate a synthetic thermography (IR) image as 2D heat map.
    Suitable for MNT-001.2 thermography image analysis / CNN.
    """
    _ensure_matplotlib()
    rng = np.random.default_rng(seed)
    h, w = shape
    # Base gradient (equipment surface)
    y, x = np.ogrid[:h, :w]
    base = ambient_temp + 5 * np.sin(0.02 * x) * np.cos(0.02 * y)
    # Add hot spots (e.g. bearing, connection)
    for _ in range(hot_spots):
        cx = rng.integers(w // 4, 3 * w // 4)
        cy = rng.integers(h // 4, 3 * h // 4)
        radius = rng.integers(8, 25)
        dist = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        hotspot = (max_temp - ambient_temp) * np.exp(-dist ** 2 / (2 * (radius ** 2)))
        base = np.maximum(base, hotspot)
    # Add noise
    base += rng.normal(0, 2, (h, w))
    base = np.clip(base, ambient_temp - 5, max_temp + 10)
    return base.astype(np.float32)


def generate_core_sample_image(
    shape=CORE_IMAGE_SHAPE,
    num_layers=6,
    grain_scale=4,
    seed=None,
):
    """
    Generate a synthetic core photo (rock strip) with layered lithology.
    Suitable for EXP-002.4 core photo integration and CNN facies/defect detection.
    """
    _ensure_pil()
    rng = np.random.default_rng(seed)
    w, h = shape
    # Grayscale base (dark = deeper)
    img = np.zeros((h, w), dtype=np.float32)
    layer_heights = np.linspace(0, h, num_layers + 1).astype(int)
    base_colors = rng.uniform(80, 200, num_layers)
    for i in range(num_layers):
        y0, y1 = layer_heights[i], layer_heights[i + 1]
        layer_val = base_colors[i]
        # Add horizontal banding (bedding)
        band = rng.normal(0, 12, (y1 - y0, w))
        img[y0:y1, :] = np.clip(layer_val + band, 40, 255)
    # Grain texture (high-freq noise)
    grain = rng.normal(0, grain_scale, (h, w))
    img = np.clip(img + grain, 0, 255).astype(np.uint8)
    # Optional vertical cracks (thin dark lines)
    for _ in range(rng.integers(0, 3)):
        xc = rng.integers(0, w)
        thickness = rng.integers(1, 3)
        img[:, max(0, xc - thickness) : min(w, xc + thickness)] = np.minimum(
            img[:, max(0, xc - thickness) : min(w, xc + thickness)], 60
        )
    return img


def generate_seismic_section_image(
    shape=SEISMIC_SLICE_SHAPE,
    num_reflectors=8,
    num_faults=2,
    seed=None,
):
    """
    Generate a synthetic 2D seismic section (time/depth vs trace).
    Suitable for EXP-005.1 fault detection and facies CNN.
    """
    _ensure_matplotlib()
    rng = np.random.default_rng(seed)
    depth_dim, trace_dim = shape
    # Random reflectors with wavelet-like response
    section = np.zeros((depth_dim, trace_dim), dtype=np.float32)
    for _ in range(num_reflectors):
        depth_base = rng.integers(20, depth_dim - 40)
        amp = rng.uniform(0.3, 1.0)
        freq = rng.uniform(0.02, 0.08)
        for t in range(trace_dim):
            d = depth_base + int(15 * np.sin(freq * t + rng.uniform(0, 6)))
            if 0 <= d < depth_dim:
                # Ricker-like wavelet in depth
                for w in range(-5, 6):
                    idx = d + w
                    if 0 <= idx < depth_dim:
                        section[idx, t] += amp * np.exp(-(w / 2) ** 2) * (1 - (w / 2) ** 2)
    # Faults (discontinuity)
    for _ in range(num_faults):
        trace_pos = rng.integers(trace_dim // 4, 3 * trace_dim // 4)
        shift = rng.integers(-15, 15)
        section[:, trace_pos:] = np.roll(section[:, trace_pos:], shift, axis=0)
    # Normalize to 0-255 for image
    section = section - section.min()
    if section.max() > 0:
        section = section / section.max() * 255
    section = np.clip(section, 0, 255).astype(np.uint8)
    return section


def save_thermography_as_png(arr, path, colormap="hot"):
    """Save thermography array as PNG with colormap."""
    _ensure_matplotlib()
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(arr, cmap=colormap, aspect="auto")
    plt.colorbar(im, ax=ax, label="Temperature (°F)")
    ax.set_title("Synthetic Thermography")
    ax.set_xlabel("X"); ax.set_ylabel("Y")
    plt.tight_layout()
    plt.savefig(path, dpi=100, bbox_inches="tight")
    plt.close()
    # Also save raw array as grayscale for CNN
    raw_path = path.parent / (path.stem + "_raw.png")
    a = np.clip(arr, arr.min(), arr.max())
    a = (a - a.min()) / (a.max() - a.min() + 1e-8) * 255
    if Image is not None:
        Image.fromarray(a.astype(np.uint8)).convert("L").save(raw_path)
    else:
        plt.imsave(raw_path, a.astype(np.uint8), cmap="gray")
        plt.close("all")


def generate_all_thermography_images(
    output_dir,
    count=10,
    seed=42,
):
    """Generate multiple thermography images and metadata."""
    _ensure_matplotlib()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    meta = []
    for i in range(count):
        img = generate_thermography_image(
            seed=int(rng.integers(0, 2**31)),
            hot_spots=rng.integers(2, 5),
        )
        path = output_dir / f"thermography_{i+1:03d}.png"
        save_thermography_as_png(img, path)
        meta.append({
            "path": str(path.name),
            "shape": list(THERMOGRAPHY_SHAPE),
            "index": i + 1,
        })
    with open(output_dir / "thermography_metadata.json", "w") as f:
        json.dump({"images": meta, "count": count}, f, indent=2)
    return list(output_dir.glob("thermography_*.png"))


def generate_all_core_images(
    output_dir,
    count=5,
    seed=42,
):
    """Generate core sample images (align with 5 cores in data set)."""
    _ensure_pil()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    meta = []
    for i in range(count):
        img = generate_core_sample_image(
            seed=int(rng.integers(0, 2**31)),
            num_layers=rng.integers(4, 8),
        )
        path = output_dir / f"core_{i+1:03d}.png"
        Image.fromarray(img).save(path)
        meta.append({
            "path": str(path.name),
            "core_id": f"CORE-{i+1:03d}",
            "shape": list(CORE_IMAGE_SHAPE),
        })
    with open(output_dir / "core_metadata.json", "w") as f:
        json.dump({"images": meta, "count": count}, f, indent=2)
    return list(output_dir.glob("core_*.png"))


def generate_all_seismic_section_images(
    output_dir,
    count=6,
    seed=42,
):
    """Generate seismic section images (inline/crossline/depth slices)."""
    _ensure_matplotlib()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    meta = []
    for i in range(count):
        img = generate_seismic_section_image(
            seed=int(rng.integers(0, 2**31)),
            num_reflectors=rng.integers(6, 12),
            num_faults=rng.integers(1, 3),
        )
        path = output_dir / f"seismic_section_{i+1:03d}.png"
        plt.imsave(path, img, cmap="seismic", vmin=0, vmax=255)
        plt.close("all")
        meta.append({
            "path": str(path.name),
            "shape": list(SEISMIC_SLICE_SHAPE),
            "index": i + 1,
        })
    with open(output_dir / "seismic_metadata.json", "w") as f:
        json.dump({"images": meta, "count": count}, f, indent=2)
    return list(output_dir.glob("seismic_section_*.png"))


def generate_data_visualization_image(
    data_dir,
    output_path,
    sample_csv_name="sample_data_24h.csv",
):
    """
    Create summary visualization (6-panel plot) from sample CSV.
    If CSV does not exist, creates a minimal placeholder plot.
    """
    _ensure_matplotlib()
    data_dir = Path(data_dir)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sample_path = data_dir / sample_csv_name

    plt.figure(figsize=VIZ_FIGSIZE)
    if sample_path.exists():
        try:
            import pandas as pd
            df = pd.read_csv(sample_path, index_col=0, parse_dates=True)
        except Exception:
            df = None
    else:
        df = None

    if df is not None and not df.empty:
        # Plot 1
        plt.subplot(3, 2, 1)
        for col in ["plant_throughput", "inlet_separation_feed_pressure"]:
            if col in df.columns:
                plt.plot(df.index, df[col], label=col, alpha=0.7)
        plt.title("Key Process Parameters (24h)")
        plt.legend()
        plt.xticks(rotation=45)
        # Plot 2
        plt.subplot(3, 2, 2)
        vib = [c for c in df.columns if "vibration" in c]
        for c in vib[:3]:
            plt.plot(df.index, df[c], label=c, alpha=0.7)
        plt.title("Equipment Vibration")
        plt.legend()
        plt.xticks(rotation=45)
        # Plot 3
        plt.subplot(3, 2, 3)
        if "temperature_C" in df.columns:
            plt.plot(df.index, df["temperature_C"], color="red", alpha=0.7)
        plt.title("Ambient Temperature")
        plt.xticks(rotation=45)
        # Plot 4
        plt.subplot(3, 2, 4)
        if "plant_throughput" in df.columns:
            plt.hist(df["plant_throughput"].dropna(), bins=50, alpha=0.7, edgecolor="black")
        plt.title("Throughput Distribution")
        # Plot 5
        plt.subplot(3, 2, 5)
        corr_cols = [c for c in df.columns if any(x in c for x in ["pressure", "temp", "flow"])][:8]
        if len(corr_cols) > 1:
            try:
                import seaborn as sns
                sns.heatmap(df[corr_cols].corr(), annot=True, cmap="coolwarm", center=0)
            except Exception:
                plt.text(0.5, 0.5, "Correlation (no seaborn)", ha="center")
        plt.title("Parameter Correlations")
        # Plot 6
        plt.subplot(3, 2, 6)
        fail_cols = [c for c in df.columns if any(x in c for x in ["vibration", "bearing"])][:2]
        for c in fail_cols:
            plt.plot(df.index, df[c], label=c, alpha=0.7)
        plt.title("Failure Indicators")
        plt.legend()
        plt.xticks(rotation=45)
    else:
        plt.suptitle("Data Visualization (no sample CSV found – run data generation first)")
        for i in range(1, 7):
            plt.subplot(3, 2, i)
            t = np.linspace(0, 10, 100)
            plt.plot(t, np.sin(t + i) + np.random.randn(100) * 0.1)
            plt.title(f"Placeholder plot {i}")

    plt.tight_layout()
    plt.savefig(output_path, dpi=VIZ_DPI, bbox_inches="tight")
    plt.close("all")
    return output_path


def generate_and_export_all_image_data(
    base_output_dir="complete_asset_data",
    thermography_count=10,
    core_count=5,
    seismic_count=6,
    data_dir_for_viz=None,
    seed=42,
):
    """
    Generate all image data types and save under base_output_dir/images/.
    Returns manifest of created paths.
    """
    base = Path(base_output_dir)
    images_dir = base / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    thermo_dir = images_dir / "thermography"
    core_dir = images_dir / "core"
    seismic_dir = images_dir / "seismic"

    manifest = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "thermography": [],
        "core": [],
        "seismic": [],
        "visualization": None,
    }

    # Thermography
    thermo_paths = generate_all_thermography_images(thermo_dir, count=thermography_count, seed=seed)
    manifest["thermography"] = [str(p.relative_to(base)) for p in thermo_paths]

    # Core
    core_paths = generate_all_core_images(core_dir, count=core_count, seed=seed)
    manifest["core"] = [str(p.relative_to(base)) for p in core_paths]

    # Seismic sections
    seismic_paths = generate_all_seismic_section_images(seismic_dir, count=seismic_count, seed=seed)
    manifest["seismic"] = [str(p.relative_to(base)) for p in seismic_paths]

    # Summary visualization
    viz_dir = data_dir_for_viz or (base / "production")
    viz_path = images_dir / "data_visualization.png"
    generate_data_visualization_image(viz_dir, viz_path)
    manifest["visualization"] = str(viz_path.relative_to(base))

    manifest_path = images_dir / "image_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    return manifest


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate synthetic image data for dataset")
    parser.add_argument("--output", default="complete_asset_data", help="Base output directory")
    parser.add_argument("--thermo", type=int, default=10, help="Number of thermography images")
    parser.add_argument("--core", type=int, default=5, help="Number of core images")
    parser.add_argument("--seismic", type=int, default=6, help="Number of seismic section images")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    manifest = generate_and_export_all_image_data(
        base_output_dir=args.output,
        thermography_count=args.thermo,
        core_count=args.core,
        seismic_count=args.seismic,
        seed=args.seed,
    )
    print("Image data generated. Manifest:", json.dumps(manifest, indent=2))
