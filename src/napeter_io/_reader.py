"""
this module ignores the api and calls viewer.open
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

import napari



def napari_get_reader(path):
    _ = path
    viewer = napari.current_viewer()
    if viewer is None:
        warn("could not find viewer")
        return None
    return reader_function


def reader_function(path):
    _ = path
    viewer = napari.current_viewer()
    assert viewer is not None

    with zipfile.ZipFile(path, "r") as z:
        if "cell_type_configs.pickle" in z.namelist():
            try:
                cell_type_configs = pickle.loads(z.read("cell_type_configs.pickle"))
            except Exception as e:
                warnings.warn(str(e))
                cell_type_configs = None
            from napari_3d_counter import Count3D
            c3d = Count3D(viewer, cell_type_configs)
            import pandas as pd
            viewer.window.add_dock_widget(c3d)
            file = z.read("n3d_counter_cells.csv")
            c3d.read_points_from_df(pd.read_csv(z.open("n3d_counter_cells.csv")))
        attrs_dict = json.loads(z.read("attrs.json"))
        with TemporaryDirectory() as tempdir:
            for name,layer_attrs in attrs_dict.items():
                zipped_name, = [n for n in z.namelist() if Path(n).stem == name]
                temp_path = Path(tempdir) / zipped_name
                with z.open(zipped_name) as src, temp_path.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
                viewer.open(temp_path, **layer_attrs)
    return [None]
