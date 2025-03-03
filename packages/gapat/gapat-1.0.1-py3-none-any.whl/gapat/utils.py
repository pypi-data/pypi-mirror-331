from concurrent.futures import ThreadPoolExecutor
import glob
import os

import numpy as np
import scipy.io as sio


def load_mat(filename):
    """
    Load .mat file and return a dictionary with variable names as keys, and loaded matrices as values.

    Parameters
    ----------
    filename : str
        The path to the .mat file.

    Returns
    -------
    data : dict
        A dictionary with variable names as keys, and loaded matrices as values.
    """
    return sio.loadmat(filename)


def save_mat(filename, varname, data):
    """
    Save data to .mat file with the given variable name.

    Parameters
    ----------
    filename : str
        The path to the .mat file.
    varname : str
        The variable name to save the data to.
    data : np.ndarray
        The data to save.
    """
    sio.savemat(filename, {varname: data})


def load_dat(data_path, num_channels, num_times, dtype=np.int16, order="F", zero_set=True):
    """
    Load all .dat files in the given directory and return a numpy array.

    Parameters
    ----------
    data_path : str
        The path to the .dat files.
    num_channels : int
        The number of channels.
    num_times : int
        The number of times.
    dtype : np.dtype
        The data type of the data needed to be loaded. Default: np.int16.
    order : str
        The order of the loaded data. Same as numpy.reshape order. "F" for Fortran order, "C" for C order. Default: "F".
    zero_set : bool
        Whether to set the first and last two rows to 0.0. Default: True.

    Returns
    -------
    data : np.ndarray
        The loaded data.
        Shape: (num_channels \* num_files, num_times). Dtype: np.float32.
    """
    dat_files = sorted(glob.glob(os.path.join(data_path, "*.dat")))  # Ensure consistent order
    data = np.empty((num_channels * len(dat_files), num_times), dtype=np.float32)  # Preallocate memory

    def _load_single_dat(args):
        idx, file_path = args
        start_row = idx * num_channels
        data[start_row : start_row + num_channels, :] = (
            np.fromfile(file_path, dtype=dtype).reshape(num_channels, num_times, order=order).astype(np.float32)
        )

    with ThreadPoolExecutor() as executor:
        list(executor.map(_load_single_dat, enumerate(dat_files)))
    if zero_set:
        data[:, [0, 1, -2, -1]] = 0.0
    return data


def calculate_detector_location(num_detectors, num_channels, detector_interval_x, detector_interval_y):
    """
    Calculate the location of the synthetic matrix array detectors.

    Parameters
    ----------
    num_detectors : int
        The number of total detectors. Equivalent to num_channels * num_steps.
    num_channels : int
        The number of channels.
    detector_interval_x : float
        The interval of the detectors in the x direction (scanning direction).
    detector_interval_y : float
        The interval of the detectors in the y direction (linear array direction).

    Returns
    -------
    detector_location : np.ndarray
        The location of the detectors.
        Shape: (num_detectors, 3). Dtype: np.float32.
    """
    detector_location = np.zeros((num_detectors, 3), dtype=np.float32)
    for i in range(num_detectors):
        detector_location[i, 0] = detector_interval_x * (i // num_channels)
        detector_location[i, 1] = detector_interval_y * (i % num_channels)
    return detector_location
