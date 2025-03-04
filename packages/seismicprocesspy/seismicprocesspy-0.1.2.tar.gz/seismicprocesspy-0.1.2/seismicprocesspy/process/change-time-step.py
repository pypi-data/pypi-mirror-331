#!/usr/bin/env python3
"""
convert_time_step.py

Standalone script to:
1) Parse a PEER NGA–format ground-motion file for NPTS and DT.
2) Read acceleration data (in g).
3) Resample to a new time step.
4) Optionally convert g to m/s^2.
5) Write out a two-column ASCII file (time, acceleration).
6) Produce a PNG plot comparing the original and resampled data.

Usage:
    python convert_time_step.py

Dependencies:
    numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
# import sys

def convert_time_step(
    input_file: str,
    output_file: str,
    dt_new: float,
    png_file: str,
    convert_g_to_m: bool = True
) -> None:
    """
    Convert the time step of ground-motion data from a PEER NGA text file.

    Parameters
    ----------
    input_file : str
        Path to the PEER NGA–format file (e.g., '1000eq1x.txt').
    output_file : str
        Path to the output file (two-column: time, acceleration).
    dt_new : float
        Desired new time step in seconds.
    png_file : str
        Path to the PNG file to save the comparison plot.
    convert_g_to_m : bool, optional
        If True, convert from g to m/s^2 (default True).

    Raises
    ------
    ValueError : if the header does not contain 'NPTS' and 'DT',
                 or if data lines are fewer than NPTS indicates,
                 or if the file cannot be parsed.
    """
    # -- 1) Read lines, locate header with "NPTS" and "DT" --
    with open(input_file, 'r') as f:
        lines = f.readlines()

    header_line = None
    for line in lines:
        if "NPTS" in line and "DT" in line:
            header_line = line
            break

    if not header_line:
        raise ValueError(
            f"Could not find a header line containing 'NPTS' and 'DT' in {input_file}"
        )

    # -- 2) Parse out NPTS and DT from that line --
    # Example: NPTS=   12390, DT=   .0050 SEC,
    parts = header_line.replace("=", " ").replace(",", " ").split()
    try:
        npts_index = parts.index("NPTS") + 1
        dt_index = parts.index("DT") + 1
        npts_original = int(parts[npts_index])
        dt_original = float(parts[dt_index])
    except (ValueError, IndexError) as exc:
        raise ValueError(
            f"Could not parse NPTS or DT from header in {input_file}.\nLine was:\n{header_line}"
        ) from exc

    # -- 3) Gather acceleration data from the lines that follow --
    data_start_idx = lines.index(header_line) + 1
    raw_values = []
    for line in lines[data_start_idx:]:
        for val in line.split():
            try:
                raw_values.append(float(val))
            except ValueError:
                pass  # skip any non-numerics

    if len(raw_values) < npts_original:
        raise ValueError(
            f"Expected NPTS={npts_original}, but found only {len(raw_values)} data points in file."
        )

    # We only need the first npts_original values:
    acc_g = np.array(raw_values[:npts_original], dtype=float)

    # -- 4) Convert from g to m/s^2 if requested --
    if convert_g_to_m:
        acc_data = acc_g * 9.80665
        accel_units = "m/s^2"
    else:
        acc_data = acc_g
        accel_units = "g"

    # -- 5) Original time vector --
    t_orig = np.arange(0, npts_original * dt_original, dt_original)
    # clamp just in case floating error
    t_orig = t_orig[:npts_original]

    # -- 6) Resample using numpy.interp onto new time vector --
    t_new = np.arange(0, t_orig[-1] + dt_new, dt_new)
    acc_resampled = np.interp(t_new, t_orig, acc_data)

    # -- 7) Write resampled data to output file --
    with open(output_file, 'w') as fout:
        fout.write(f"# Resampled from dt={dt_original}s to dt={dt_new}s.\n")
        fout.write(f"# Units: {accel_units}\n")
        fout.write("# time(accel)\n")
        for tt, aa in zip(t_new, acc_resampled):
            fout.write(f"{tt:.6f}\t{aa:.6e}\n")

    # -- 8) Plot original vs. resampled --
    fig, ax = plt.subplots(2, 1, figsize=(10, 7), sharex=True)

    ax[0].plot(t_orig, acc_data, 'b-', lw=1,
               label=f"Original (dt={dt_original}s)")
    ax[0].grid(True)
    ax[0].legend()
    ax[0].set_title(f"Original Ground Motion: {input_file}")
    ax[0].set_ylabel(f"Acceleration [{accel_units}]")

    ax[1].plot(t_new, acc_resampled, 'r-', lw=1,
               label=f"Resampled (dt={dt_new}s)")
    ax[1].grid(True)
    ax[1].legend()
    ax[1].set_title("Resampled Ground Motion")
    ax[1].set_xlabel("Time [s]")
    ax[1].set_ylabel(f"Acceleration [{accel_units}]")

    plt.tight_layout()
    plt.savefig(png_file)
    plt.close()

    print(f"[DONE] {input_file} -> {output_file}")
    print(f"  Original dt = {dt_original}s, new dt = {dt_new}s")
    print(f"  Output: {output_file}")
    print(f"  Plot:   {png_file}")


