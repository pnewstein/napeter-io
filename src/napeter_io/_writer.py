"""
ignores the api and writes all layers
"""

import zipfile
import pickle
import pickle
import shutil
import json
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast
from tempfile import TemporaryDirectory
from io import TextIOWrapper
from warnings import warn

import napari.utils.colormaps

if TYPE_CHECKING:
    from napari import Viewer
    from napari_3d_counter import Count3D, CellTypeConfig


def _save(path: Path, viewer: "Viewer"):
    try:
        c3d: "Count3D | None" = next(
            w
            for w in viewer.window.dock_widgets.values()
            if w.__class__.__name__ == "Count3D"
        )  # type: ignore
    except StopIteration:
        c3d = None
    layers = viewer.layers.copy()
    attrs_dict: dict[str, dict[str, Any]] = {}
    for layer in layers:
        if layer.__class__.__name__ == "Image":
            layer_dict = {
                "projection_mode": str(layer.projection_mode),
                "blending": str(layer.blending),
            }
            colormap_name = layer.colormap.name  # type: ignore
            if colormap_name in napari.utils.colormaps.ALL_COLORMAPS:
                layer_dict["colormap"] = colormap_name

        else:
            layer_dict = {}
        attrs_dict[layer.name] = layer_dict
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        if c3d is not None:
            z.writestr(
                "cell_type_configs.pickle",
                pickle.dumps(
                    [
                        d.get_calculated_config(c3d.out_of_slice_points.current_size)
                        for d in c3d.cell_type_gui_and_data
                    ]
                ),
            )
            for ctgd in c3d.cell_type_gui_and_data:
                del attrs_dict[ctgd.layer.name]
            del attrs_dict[c3d.out_of_slice_points.name]
            del attrs_dict[c3d.pointer.name]
            z.writestr("n3d_counter_cells.csv", c3d.save_points_to_df().to_csv())
        z.writestr("attrs.json", json.dumps(attrs_dict))
        with TemporaryDirectory() as tempdir:
            for layer_name in attrs_dict:
                print(layer_name)
                layer = viewer.layers[layer_name]
                ext = ".tiff" if layer.__class__.__name__ == "Image" else ".csv"
                layer_path = (Path(tempdir) / layer_name).with_suffix(ext)
                layer.save(str(layer_path))
                z.write(layer_path, layer_path.name)


def write_single_image(path: str, data: Any, meta: dict) -> list[str]:
    _ = data
    _ = meta
    viewer = napari.current_viewer()
    if viewer is None:
        warn("could not find viewer")
        return []
    _save(Path(path), viewer)
    return [path]


def write_multiple(path: str, data) -> list[str]:
    _ = data
    viewer = napari.current_viewer()
    if viewer is None:
        warn("could not find viewer")
        return []
    _save(Path(path), viewer)
    return [path]
