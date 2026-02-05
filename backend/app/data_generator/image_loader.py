"""
Image data loader for generated dataset images.
Loads thermography, core, seismic, and visualization images for use in
CNN training, APIs, or analysis (e.g. EXP-005.1, MNT-001.2, EXP-002.4).
"""

from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import json

try:
    import numpy as np
except ImportError:
    np = None

try:
    from PIL import Image as PILImage
except ImportError:
    PILImage = None


def _ensure_numpy():
    if np is None:
        raise ImportError("numpy is required. pip install numpy")


def _ensure_pil():
    if PILImage is None:
        raise ImportError("Pillow is required for image loading. pip install Pillow")


def load_image_as_array(path: Path) -> "np.ndarray":
    """Load a single image file as numpy array (H, W) or (H, W, C)."""
    _ensure_numpy()
    _ensure_pil()
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(str(path))
    img = PILImage.open(path)
    return np.array(img)


def load_thermography_images(
    images_dir: str | Path,
    include_raw: bool = True,
    max_count: Optional[int] = None,
) -> Tuple[List["np.ndarray"], List[Dict[str, Any]]]:
    """
    Load thermography images from directory.
    Returns (list of arrays, list of metadata per image).
    """
    _ensure_numpy()
    _ensure_pil()
    images_dir = Path(images_dir)
    if not images_dir.is_dir():
        return [], []
    pattern = "*_raw.png" if include_raw else "thermography_*.png"
    if include_raw:
        paths = sorted(images_dir.glob("*_raw.png"))
        if not paths and max_count != 0:
            paths = sorted(images_dir.glob("thermography_*.png"))
    else:
        paths = sorted([p for p in images_dir.glob("thermography_*.png") if "_raw" not in p.name])
    if max_count is not None:
        paths = paths[:max_count]
    meta_path = images_dir / "thermography_metadata.json"
    meta_list = []
    if meta_path.exists():
        with open(meta_path) as f:
            meta_list = json.load(f).get("images", [])
    arrays = [load_image_as_array(p) for p in paths]
    infos = [{"path": str(p), "name": p.name} for p in paths]
    return arrays, infos


def load_core_images(
    images_dir: str | Path,
    max_count: Optional[int] = None,
) -> Tuple[List["np.ndarray"], List[Dict[str, Any]]]:
    """Load core sample images. Returns (list of arrays, list of metadata)."""
    _ensure_numpy()
    _ensure_pil()
    images_dir = Path(images_dir)
    if not images_dir.is_dir():
        return [], []
    paths = sorted(images_dir.glob("core_*.png"))
    if max_count is not None:
        paths = paths[:max_count]
    meta_path = images_dir / "core_metadata.json"
    meta_list = []
    if meta_path.exists():
        with open(meta_path) as f:
            meta_list = json.load(f).get("images", [])
    arrays = [load_image_as_array(p) for p in paths]
    infos = [{"path": str(p), "name": p.name, "core_id": meta_list[i].get("core_id", "") if i < len(meta_list) else ""}
             for i, p in enumerate(paths)]
    return arrays, infos


def load_seismic_section_images(
    images_dir: str | Path,
    max_count: Optional[int] = None,
) -> Tuple[List["np.ndarray"], List[Dict[str, Any]]]:
    """Load seismic section images. Returns (list of arrays, list of metadata)."""
    _ensure_numpy()
    _ensure_pil()
    images_dir = Path(images_dir)
    if not images_dir.is_dir():
        return [], []
    paths = sorted(images_dir.glob("seismic_section_*.png"))
    if max_count is not None:
        paths = paths[:max_count]
    meta_path = images_dir / "seismic_metadata.json"
    meta_list = []
    if meta_path.exists():
        with open(meta_path) as f:
            meta_list = json.load(f).get("images", [])
    arrays = [load_image_as_array(p) for p in paths]
    infos = [{"path": str(p), "name": p.name} for p in paths]
    return arrays, infos


def load_visualization_image(images_dir: str | Path) -> Optional["np.ndarray"]:
    """Load the single data_visualization.png if present."""
    _ensure_numpy()
    _ensure_pil()
    images_dir = Path(images_dir)
    path = images_dir / "data_visualization.png"
    if not path.exists():
        return None
    return load_image_as_array(path)


def load_all_image_data(
    base_dir: str | Path,
    thermography_max: Optional[int] = None,
    core_max: Optional[int] = None,
    seismic_max: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Load all image data from base_dir/images/ (thermography, core, seismic, visualization).
    Returns dict with keys: thermography, core, seismic, visualization, manifest.
    """
    base_dir = Path(base_dir)
    images_dir = base_dir / "images"
    result = {
        "thermography": {"arrays": [], "meta": []},
        "core": {"arrays": [], "meta": []},
        "seismic": {"arrays": [], "meta": []},
        "visualization": None,
        "manifest": None,
    }
    if not images_dir.is_dir():
        return result

    arrs, metas = load_thermography_images(images_dir / "thermography", max_count=thermography_max)
    result["thermography"] = {"arrays": arrs, "meta": metas}

    arrs, metas = load_core_images(images_dir / "core", max_count=core_max)
    result["core"] = {"arrays": arrs, "meta": metas}

    arrs, metas = load_seismic_section_images(images_dir / "seismic", max_count=seismic_max)
    result["seismic"] = {"arrays": arrs, "meta": metas}

    result["visualization"] = load_visualization_image(images_dir)

    manifest_path = images_dir / "image_manifest.json"
    if manifest_path.exists():
        with open(manifest_path) as f:
            result["manifest"] = json.load(f)
    return result


def get_image_manifest(base_dir: str | Path) -> Optional[Dict[str, Any]]:
    """Return image_manifest.json content if present."""
    base_dir = Path(base_dir)
    path = base_dir / "images" / "image_manifest.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)
