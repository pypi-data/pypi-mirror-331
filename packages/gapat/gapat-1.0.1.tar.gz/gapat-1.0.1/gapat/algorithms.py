import multiprocessing
import os

import numpy as np
import taichi as ti


def recon_single(
    signal_backproj,
    detector_location,
    detector_normal,
    x_range,
    y_range,
    z_range,
    res,
    vs,
    fs,
    delay=0,
    method="das",
    device="gpu",
    device_no=0,
    block_dim=512,
):
    if device == "cpu":
        ti.init(arch=ti.cpu)
    elif device == "gpu":
        os.environ["CUDA_VISIBLE_DEVICES"] = str(device_no)
        ti.init(arch=ti.gpu)
    else:
        raise ValueError(f"Invalid device: {device}")

    x_start, x_end = x_range
    y_start, y_end = y_range
    z_start, z_end = z_range
    num_detectors, num_times = signal_backproj.shape
    num_x = round((x_end - x_start) / res)
    num_y = round((y_end - y_start) / res)
    num_z = round((z_end - z_start) / res)
    factor = fs / vs
    bandary = num_times - 2

    @ti.kernel
    def recon_kernel_das(
        signal_backproj: ti.types.ndarray(),
        detector_location: ti.types.ndarray(),
        detector_normal: ti.types.ndarray(),
        signal_recon: ti.types.ndarray(),
    ):
        ti.loop_config(block_dim=block_dim)
        for i, j, k in ti.ndrange(num_x, num_y, num_z):
            point_vector = ti.Vector([x_start + i * res, y_start + j * res, z_start + k * res])
            temp_signal_recon = 0.0
            total_solid_angle = 0.0
            for n in ti.ndrange(num_detectors):
                detector_vector = ti.Vector([detector_location[n, 0], detector_location[n, 1], detector_location[n, 2]])
                normal_vector = ti.Vector([detector_normal[n, 0], detector_normal[n, 1], detector_normal[n, 2]])
                detector_to_point_vector = point_vector - detector_vector
                distance = detector_to_point_vector.norm()
                d_solid_angle = detector_to_point_vector.dot(normal_vector.normalized()) / distance**3
                idx = ti.min(ti.cast(distance * factor, ti.i32) - delay, bandary)
                temp_signal_recon += signal_backproj[n, idx] * d_solid_angle
                total_solid_angle += d_solid_angle
            signal_recon[i, j, k] = temp_signal_recon / total_solid_angle

    @ti.kernel
    def recon_kernel_ubp(
        signal_backproj: ti.types.ndarray(),
        detector_location: ti.types.ndarray(),
        detector_normal: ti.types.ndarray(),
        signal_recon: ti.types.ndarray(),
    ):
        ti.loop_config(block_dim=block_dim)
        for i, j, k in ti.ndrange(num_x, num_y, num_z):
            point_vector = ti.Vector([x_start + i * res, y_start + j * res, z_start + k * res])
            temp_signal_recon = 0.0
            total_solid_angle = 0.0
            for n in ti.ndrange(num_detectors):
                detector_vector = ti.Vector([detector_location[n, 0], detector_location[n, 1], detector_location[n, 2]])
                normal_vector = ti.Vector([detector_normal[n, 0], detector_normal[n, 1], detector_normal[n, 2]])
                detector_to_point_vector = point_vector - detector_vector
                distance = detector_to_point_vector.norm()
                d_solid_angle = detector_to_point_vector.dot(normal_vector.normalized()) / distance**3
                idx = ti.min(ti.cast(distance * factor, ti.i32) - delay, bandary)
                temp_signal_recon += (
                    signal_backproj[n, idx] - idx * (signal_backproj[n, idx + 1] - signal_backproj[n, idx])
                ) * d_solid_angle
                total_solid_angle += d_solid_angle
            signal_recon[i, j, k] = temp_signal_recon / total_solid_angle

    signal_recon = np.zeros((num_x, num_y, num_z), dtype=np.float32)
    if method == "das":
        recon_kernel_das(signal_backproj, detector_location, detector_normal, signal_recon)
    elif method == "ubp":
        recon_kernel_ubp(signal_backproj, detector_location, detector_normal, signal_recon)
    else:
        raise ValueError(f"Invalid method: {method}")
    return signal_recon


def recon_multi(
    signal_backproj,
    detector_location,
    detector_normal,
    x_range,
    y_range,
    z_range,
    res,
    vs,
    fs,
    delay=0,
    method="das",
    device="gpu",
    num_devices=1,
    block_dim=512,
):
    z_ranges = [
        [
            z_range[0] + i * (z_range[1] - z_range[0]) / num_devices,
            z_range[0] + (i + 1) * (z_range[1] - z_range[0]) / num_devices,
        ]
        for i in range(num_devices)
    ]
    results = []
    pool = multiprocessing.Pool(processes=num_devices)
    for device_no in range(num_devices):
        results.append(
            pool.apply_async(
                recon_single,
                args=(
                    signal_backproj,
                    detector_location,
                    detector_normal,
                    x_range,
                    y_range,
                    z_ranges[device_no],
                    res,
                    vs,
                    fs,
                    delay,
                    method,
                    device,
                    device_no,
                    block_dim,
                ),
            )
        )
    pool.close()
    pool.join()
    signal_recon = np.concatenate([result.get() for result in results], axis=2)
    return signal_recon


def recon(
    signal_backproj,
    detector_location,
    detector_normal,
    x_range,
    y_range,
    z_range,
    res,
    vs,
    fs,
    delay=0,
    method="das",
    device="gpu",
    num_devices=1,
    device_no=0,
    block_dim=512,
):
    """
    Reconstruction of photoacoustic computed tomography.
    Warning: When using multi-device reconstruction, the function must be called on the main process.

    Parameters
    ----------
    signal_backproj : np.ndarray
        The input signal. Each row is a signal of a detector.
        Shape: (num_detectors, num_times). Dtype: np.float32.
    detector_location : np.ndarray
        The location of the detectors. Each row is the coordinates of a detector.
        Shape: (num_detectors, 3). Dtype: np.float32.
    detector_normal : np.ndarray
        The normal of the detectors. Each row is the normal of a detector which points to the volume.
        Shape: (num_detectors, 3). Dtype: np.float32.
    x_range : list
        The range of the reconstruction volume. The first is the start x and the second is the end x. Example: [0, 1].
        Shape: (2,). Dtype: float.
    y_range : list
        The range of the reconstruction volume. The first is the start y and the second is the end y. Example: [0, 1].
        Shape: (2,). Dtype: float.
    z_range : list
        The range of the reconstruction volume. The first is the start z and the second is the end z. Example: [0, 1].
        Shape: (2,). Dtype: float.
    res : float
        The resolution of the volume.
    vs : float
        The speed of sound in the volume.
    fs : float
        The sampling frequency.
    delay : int
        The delay of the detectors. Default: 0.
    method : str
        The method to use. Default: "das". Options: "das", "ubp".
    device : str
        The device to use. Default: "gpu". Options: "cpu", "gpu".
    num_devices : int
        The number of devices to use. When = 1, the device set by device_no will be used.
        When > 1, the first n devices will be used. Default: 1.
    device_no : int
        The device number to use when num_devices = 1. Default: 0.
    block_dim : int
        The block dimension. Default: 512.

    Returns
    -------
    signal_recon : np.ndarray
        The reconstructed signal.
        Shape: (num_x, num_y, num_z). Dtype: np.float32.
    """

    if num_devices == 1:
        return recon_single(
            signal_backproj,
            detector_location,
            detector_normal,
            x_range,
            y_range,
            z_range,
            res,
            vs,
            fs,
            delay,
            method,
            device,
            device_no,
            block_dim,
        )
    elif num_devices > 1:
        return recon_multi(
            signal_backproj,
            detector_location,
            detector_normal,
            x_range,
            y_range,
            z_range,
            res,
            vs,
            fs,
            delay,
            method,
            device,
            num_devices,
            block_dim,
        )
    else:
        raise ValueError(f"Invalid number of devices: {num_devices}")
