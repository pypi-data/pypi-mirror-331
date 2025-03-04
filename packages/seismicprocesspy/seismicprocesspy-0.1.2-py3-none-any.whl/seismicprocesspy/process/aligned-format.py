#!/usr/bin/env python3
"""
process_peer.py

Reads a PEER NGA–format ground-motion file that has a header line like:
    NPTS=  6962, DT=   .0100 SEC,
Then extracts the time-step (DT) and number of points (NPTS),
reads the subsequent acceleration (in g), multiplies by a user-specified scale,
and writes an output (time, accel) file. Also optionally saves a PNG plot.

Adjust 'input_file', 'output_file', 'png_file', and 'scale' in main().
"""

import numpy as np
import matplotlib.pyplot as plt

def process_peer_file(
    input_file: str,
    output_file: str,
    scale: float = 1.0,
    png_file: str = None
):
    """
    Processes a PEER NGA–format file, extracting 'NPTS' and 'DT' from
    a header line containing both (e.g., "NPTS=  6962, DT=   .0100 SEC,").
    Reads the acceleration data (in g) from lines after the header, multiplies
    by 'scale', then writes out time vs. scaled acceleration. Optionally
    generates a PNG plot if 'png_file' is provided.

    Parameters
    ----------
    input_file : str
        Path to the PEER-format file.
    output_file : str
        Path to save the scaled (time, accel) data.
    scale : float, optional
        Factor to multiply the acceleration. (Default=1.0 means no change.)
    png_file : str, optional
        If provided, save a plot of Acceleration vs. Time to this file.

    Raises
    ------
    ValueError : if we cannot find the required header line with 'NPTS' and 'DT',
                 or if we do not find enough data points after that line.
    """
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # ------------------------------------------------------
    # 1) Find the header line containing 'NPTS' and 'DT'
    # ------------------------------------------------------
    header_line = None
    header_idx = None
    for idx, line in enumerate(lines):
        if "NPTS" in line and "DT" in line:
            header_line = line
            header_idx = idx
            break

    if header_line is None:
        raise ValueError(
            f"No header line with 'NPTS' and 'DT' found in {input_file}."
        )

    # ------------------------------------------------------
    # 2) Parse NPTS and DT
    #    e.g. "NPTS=  6962, DT=   .0100 SEC,"
    # ------------------------------------------------------
    # We'll replace '=' and ',' with spaces, then split
    line_parts = header_line.replace("=", " ").replace(",", " ").split()
    try:
        npts_index = line_parts.index("NPTS") + 1
        dt_index = line_parts.index("DT") + 1
        npts = int(line_parts[npts_index])
        dt = float(line_parts[dt_index])
    except (ValueError, IndexError) as exc:
        raise ValueError(
            f"Unable to parse NPTS/DT from header line:\n{header_line}"
        ) from exc

    # ------------------------------------------------------
    # 3) Gather the acceleration data (in g)
    #    from lines AFTER the header line
    # ------------------------------------------------------
    # The data might span multiple lines, possibly multiple columns.
    # We'll read numeric values from all lines after header_idx, until we have npts.
    data_vals = []
    for line in lines[header_idx + 1:]:
        # Attempt to parse all floats from the line
        for val in line.split():
            try:
                data_vals.append(float(val))
            except ValueError:
                # skip if not numeric
                pass
        if len(data_vals) >= npts:
            break

    if len(data_vals) < npts:
        raise ValueError(
            f"Expected at least {npts} data points, but found only {len(data_vals)} "
            f"in {input_file}."
        )

    # Keep only the first npts:
    acc_g = np.array(data_vals[:npts], dtype=float)

    # ------------------------------------------------------
    # 4) Scale the acceleration
    # ------------------------------------------------------
    # If you want to convert from g to m/s², you could do:
    #   scale_factor = scale * 9.80665
    # but if you just want to multiply by 'scale', do:
    acc_scaled = acc_g * scale

    # ------------------------------------------------------
    # 5) Construct the time array
    # ------------------------------------------------------
    # from 0 to (npts-1)*dt
    time = np.arange(0, npts * dt, dt)

    # In case of floating rounding, ensure they match up
    time = time[:npts]

    # ------------------------------------------------------
    # 6) Write out a two-column text file with time, scaled accel
    # ------------------------------------------------------
    with open(output_file, 'w') as fout:
        # Optional header lines if you like:
        fout.write("# NEW FORMAT")
        fout.write(f"# NPTS={npts}, DT={dt}, SCALE={scale}\n")
        fout.write("# time(s)\tacceleration\n")
        for t, a in zip(time, acc_scaled):
            fout.write(f"{t:.6f}\t{a:.6e}\n")

    # ------------------------------------------------------
    # 7) (Optional) Plot time vs. scaled acceleration
    # ------------------------------------------------------
    if png_file:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(time, acc_scaled, 'b-', lw=1, label="Scaled Accel")
        ax.set_title(f"Acceleration vs Time\n{input_file}")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Acceleration (scaled)")
        ax.grid(True)
        ax.legend()
        plt.tight_layout()
        plt.savefig(png_file)
        plt.close()

    print(f"[OK] Processed {input_file} -> {output_file}")
    if png_file:
        print(f"     Plot saved to {png_file}")
