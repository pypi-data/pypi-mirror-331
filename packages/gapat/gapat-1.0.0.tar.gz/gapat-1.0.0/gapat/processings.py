import numpy as np
import scipy.signal as signal


def bandpass_filter(signal_matrix, fs, band_range, order=2, axis=0):
    """
    Bandpass filter the signal matrix.

    Parameters
    ----------
    signal_matrix : np.ndarray
        The signal matrix to be filtered.
        Shape: (num_detectors, num_times). Dtype: np.float32.
    fs : float
        The sampling frequency (Hz).
    band_range : list
        The band range to filter (Hz). The first is the low frequency and the second is the high frequency. Example: [10e6, 100e6].
        Shape: (2,). Dtype: float.
    order : int
        The order of the filter. Default: 2.
    axis : int
        The axis to filter. Default: 0. (Which will be applied to each detector.)

    Returns
    -------
    filtered_signal_matrix : np.ndarray
        The filtered signal matrix.
        Shape: (num_detectors, num_times). Dtype: np.float32.
    """
    nyq = 0.5 * fs
    low, high = band_range[0] / nyq, band_range[1] / nyq
    b, a = signal.butter(order, [low, high], btype="band")
    return signal.filtfilt(b, a, signal_matrix, axis=axis)


def negetive_processing(signal_recon, method="zero", axis=0):
    """
    Process the negative signal.

    Parameters
    ----------
    signal_recon : np.ndarray
        The reconstructed signal to be processed.
        Shape: (num_x, num_y, num_z). Dtype: np.float32.
    method : str
        The method to process the negative signal. Default: "zero". Options: "zero", "abs", "hilbert".
        "zero": Set the negative signal to zero.
        "abs": Take the absolute value of the negative signal.
        "hilbert": Use the hilbert transform to get the envelope of the signal.
    axis : int
        The axis to process when method is "hilbert". Default: 0.

    Returns
    -------
    processed_signal_recon : np.ndarray
        The processed signal reconstruction.
        Shape: (num_x, num_y, num_z). Dtype: np.float32.
    """
    if method == "zero":
        return np.where(signal_recon < 0.0, 0.0, signal_recon)
    elif method == "abs":
        return np.abs(signal_recon)
    elif method == "hilbert":
        return np.abs(signal.hilbert(signal_recon, axis=axis))
    else:
        raise ValueError(f"Invalid method: {method}")
