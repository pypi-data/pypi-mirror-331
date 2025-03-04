# seismicprocesspy 🌏🚀

**seismicprocesspy** is a Python package designed for performing and processing ground motion data obtained from Probabilistic Seismic Hazard Analysis (PSHA). It provides convenient utilities to handle seismic data time steps, convert varying formats to a uniform standard, and trim ground motion signals based on Arias Intensity criteria.

**Note:** This is an internal tool developed by Albert Pamonag.

## Disclaimer

This software is provided **as-is**, without any express or implied warranties. While efforts have been made to ensure accuracy, **the author and contributors are not responsible for any errors, omissions, or damages arising from the use of this tool**. Users should **verify outputs independently** before applying them to critical engineering or research applications.

This package is intended for **internal use** and may not be suitable for general distribution or commercial purposes.


## Key Features :sparkles:
- **Process Time Steps**: Easily handle irregular time steps in your seismic signals.
# Theoretical Reference


## Deepsoil format 
Deepsoil should be formated as follows
```
<no of sample><time step>
<time> <acceleration>
```

- **Unified Format Conversion**: Standardize multiple ground motion formats into one consistent structure.
- **Arias Intensity Trimming**: Automate the trimming of ground motion records based on Arias Intensity thresholds.

## Installation :package:
Install the latest release of seismicprocesspy from PyPI:
