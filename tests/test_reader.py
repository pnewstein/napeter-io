import numpy as np

from napeter_io._reader import napari_get_reader


# tmp_path is a pytest fixture
def test_reader(tmp_path, make_napari_viewer):
    """An example of how you might test your plugin."""
    viewer = make_napari_viewer()

    # write some fake data using your supported file format
    # we make the array an integer type to be compatible with the reader
    my_test_file = str(tmp_path / 'myfile.napeter')
    original_data = np.random.rand(20, 20).astype(np.int_)
    np.save(my_test_file, original_data)

    reader = napari_get_reader(my_test_file)
    assert callable(reader)

