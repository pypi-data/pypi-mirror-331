# -----------------------------------------------------------------------------
# seismicprocesspy/trim.py
#
# Python module for ground motion signal processing, including the calculation
# of cumulative Arias Intensity and trimming a ground-motion record based on
# threshold Arias Intensity values.
#
# Copyright (c) 2025, Albert Pamonag
# All rights reserved.
#
# Licensed under the MIT License. See LICENSE file in the project root for
# full license information.
# -----------------------------------------------------------------------------

import math
import numpy as np

def calculate_cumulative_arias_intensity(
    acceleration: np.ndarray,
    dt: float,
    g: float = 9.81
) -> np.ndarray:
    """
    Calculate the cumulative Arias Intensity at each time step.

    Parameters
    ----------
    acceleration : np.ndarray
        Acceleration array in units of g (dimensionless).
    dt : float
        Time step in seconds.
    g : float, optional
        Gravitational acceleration in m/s^2 (default: 9.81).

    Returns
    -------
    cumulative_arias : np.ndarray
        Cumulative Arias Intensity at each time step, in units of m/s.
        Note: This is often reported in m/s, but can be scaled or converted
        as needed.
    """
    # Convert from g to m/s^2
    accel_m_s2 = acceleration * g

    # Square the acceleration
    accel_sq = np.power(accel_m_s2, 2)

    # Arias Intensity = (π / (2*g)) * ∫(a^2 dt)
    # Use cumulative sum to approximate the integral
    cumulative_arias = (math.pi / (2.0 * g)) * np.cumsum(accel_sq) * dt

    return cumulative_arias

def trim_ground_motion(
    acceleration: np.ndarray,
    time: np.ndarray,
    threshold: float = 0.05
) -> tuple[np.ndarray, np.ndarray]:
    """
    Trim the ground motion record between 5% and 95% of Arias Intensity,
    shift the first time to 0.0, and prepend a (0.0, 0.0) point.

    Parameters
    ----------
    acceleration : np.ndarray
        Acceleration array in units of g (dimensionless).
    time : np.ndarray
        Corresponding time array (seconds).
    threshold : float, optional
        Lower/upper fraction for Arias Intensity (default: 0.05).
        i.e., trims data between 5% and 95% of total Arias Intensity.

    Returns
    -------
    trimmed_time : np.ndarray
        Time array, starting at 0.0 plus a row for (0.0).
    trimmed_acceleration : np.ndarray
        Acceleration array in g, with an extra 0.0 at the start.

    Raises
    ------
    ValueError
        If `acceleration` and `time` have different lengths.
    """
    if len(acceleration) != len(time):
        raise ValueError("acceleration and time arrays must have the same length.")

    dt = time[1] - time[0]
    cumulative_arias = calculate_cumulative_arias_intensity(acceleration, dt)
    total_arias = cumulative_arias[-1]

    # Find indices corresponding to 5% and 95% of total Arias Intensity
    lower_idx = np.where(cumulative_arias >= threshold * total_arias)[0][0]
    upper_idx = np.where(cumulative_arias >= (1.0 - threshold) * total_arias)[0][0]

    # Slice the data accordingly
    t_trim = time[lower_idx : upper_idx + 1]
    a_trim = acceleration[lower_idx : upper_idx + 1]

    # Shift time so it starts at 0
    t_trim -= t_trim[0]

    # Insert (0.0, 0.0) at the beginning
    t_trim = np.insert(t_trim, 0, 0.0)
    a_trim = np.insert(a_trim, 0, 0.0)

    return t_trim, a_trim
