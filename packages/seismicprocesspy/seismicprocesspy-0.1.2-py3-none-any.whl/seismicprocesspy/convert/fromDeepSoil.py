# excel_processor/processor.py

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

class processData:
    """
    A class to process Excel files, scale acceleration data,
    and generate plots & text outputs.

    Parameters
    ----------
    folder_name : str
        Name (or path) of the folder that contains Excel files.
    sheet_name : str, optional
        Name of the sheet to read from each Excel file, by default 'Layer 1'.
    scale_factor : float, optional
        The scale factor to apply to acceleration data, by default 10.
    output_dir : str, optional
        Custom output directory if desired. If None, will use `folder_name`.
    """

    def __init__(self, folder_name, sheet_name="Layer 1", scale_factor=10, output_dir=None):
        self.folder_name = folder_name
        self.sheet_name = sheet_name
        self.scale_factor = scale_factor
        self.output_dir = output_dir or folder_name

        # Make sure the output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

    def process_files(self):
        """
        Process all Excel (.xlsx) files in the specified folder.
        Reads the sheet, extracts Time & Acceleration, applies scaling,
        writes to text files, and saves plots.
        """

        # Verify that folder_name exists
        if not os.path.exists(self.folder_name):
            print(f"The folder {self.folder_name} does not exist.")
            return

        # Loop over all .xlsx files in the folder
        excel_files = glob.glob(os.path.join(self.folder_name, "*.xlsx"))
        if not excel_files:
            print(f"No .xlsx files found in folder: {self.folder_name}")
            return

        for excel_file in excel_files:
            print(f"Processing file: {excel_file}")

            # Read the specified sheet
            df = pd.read_excel(excel_file, sheet_name=self.sheet_name)

            # 1) Extract the Time and Acceleration columns
            time = df.iloc[:, 0]            # Column 1 = Time
            accel_unscaled = df.iloc[:, 1]  # Column 2 = Acceleration

            # 2) Apply the scale factor
            accel_scaled = accel_unscaled * self.scale_factor

            # Generate a base name for outputs (e.g., "EQ1X" if file is "EQ1X.xlsx")
            base_name = os.path.splitext(os.path.basename(excel_file))[0]

            # 3a) Save UNscaled data to a text file
            txt_filename_unscaled = os.path.join(self.output_dir, f"{base_name}_unscaled.txt")
            print(f"Writing unscaled data to: {txt_filename_unscaled}")
            with open(txt_filename_unscaled, "w") as f_unscaled:
                f_unscaled.write("# Time(s)\tAcceleration(g)\n")
                for t, acc_u in zip(time, accel_unscaled):
                    f_unscaled.write(f"{t}\t{acc_u}\n")

            # 3b) Save SCALED data to a text file
            txt_filename_scaled = os.path.join(self.output_dir, f"{base_name}_scaled.txt")
            print(f"Writing scaled data to: {txt_filename_scaled}")
            with open(txt_filename_scaled, "w") as f_scaled:
                f_scaled.write(f"# Time(s)\tAcceleration(g) x {self.scale_factor}\n")
                for t, acc_s in zip(time, accel_scaled):
                    f_scaled.write(f"{t}\t{acc_s}\n")

            # 4) PLOTS (separate figures)

            # -- (a) Unscaled plot --
            plt.figure(figsize=(6,4))
            plt.plot(time, accel_unscaled, label="Unscaled")
            plt.title(f"Unscaled Acceleration: {base_name}")
            plt.xlabel("Time (s)")
            plt.ylabel("Acceleration (g)")
            plt.legend()
            plot_filename_unscaled = os.path.join(self.output_dir, f"{base_name}_unscaled.png")
            plt.savefig(plot_filename_unscaled, dpi=150)
            plt.close()

            # -- (b) Scaled plot --
            plt.figure(figsize=(6,4))
            plt.plot(time, accel_scaled, label=f"Scaled x {self.scale_factor}")
            plt.title(f"Scaled Acceleration: {base_name}")
            plt.xlabel("Time (s)")
            plt.ylabel("Acceleration (g)")
            plt.legend()
            plot_filename_scaled = os.path.join(self.output_dir, f"{base_name}_scaled.png")
            plt.savefig(plot_filename_scaled, dpi=150)
            plt.close()

            print(f"Saved plots:\n  {plot_filename_unscaled}\n  {plot_filename_scaled}\n")
