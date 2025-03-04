import os
import glob
import numpy as np
import matplotlib.pyplot as plt

class processData:
    """
    A class to handle reading, upsampling, and scaling ground motion data
    from multiple files in a folder, and saving the processed data and plots.

    The script detects the original time-step (dt_input) from the first line of each file.
    If dt_input == dt_new (within a small float tolerance), it will skip interpolation
    and produce only a single plot.
    """

    def __init__(self, input_folder, output_folder, dt_new, scale_factor):
        """
        Initializes the processData with folder paths and parameters.

        Parameters:
        -----------
        input_folder : str
            Path to the folder containing raw ground motion data files.
        output_folder : str
            Path to the folder where processed outputs will be saved.
        dt_new : float
            Desired new time step (seconds) for upsampling.
        scale_factor : float
            Factor by which the acceleration values will be scaled.
        """
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.dt_new = dt_new
        self.scale_factor = scale_factor

        # Ensure the top-level output folder exists
        script_dir = os.path.dirname(os.path.abspath(__file__)) 
        site_path = os.path.join(script_dir, self.output_folder) 
        os.makedirs(site_path, exist_ok=True)

    def process_all_files(self):
        """
        Iterates over all .txt files in the input folder and processes them
        (upsampling, scaling, saving results, and plotting).
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Where this script is located
        site_path = os.path.join(script_dir, self.input_folder)  # Full path to input folder

        # Build a pattern to find .txt files in the specified directory.
        pattern = os.path.join(site_path, "*.txt")
        files_found = list(glob.iglob(pattern, recursive=False))

        # If no files are found, let the user know
        if not files_found:
            print("No .txt files found. Check your folder path or file extensions.")
            return

        for input_file in files_found:
            # Extract the file name from the full path
            file_name = os.path.basename(input_file)
            base_name = os.path.splitext(file_name)[0]

            # Create a sub-folder named after the base name (to store results)
            script_dir = os.path.dirname(os.path.abspath(__file__))  
            site_path = os.path.join(script_dir, self.output_folder) 

            current_output_folder = os.path.join(site_path, base_name)
            os.makedirs(current_output_folder, exist_ok=True)

            # Construct the output file names
            output_file = os.path.join(current_output_folder, f"{base_name}_upscaled.txt")
            png_file = os.path.join(current_output_folder, f"{base_name}_plot.png")

            # Debug info: Show which file is being processed
            print(f"\nProcessing: {input_file}")
            print(f" - Output data file: {output_file}")
            print(f" - Output plot file: {png_file}")

            self.process_file(input_file, output_file, png_file)

    def process_file(self, input_file, output_file, png_file):
        """
        Reads a single file, detects the original time step, performs upsampling and scaling
        (only if needed), saves the processed data, and saves a plot of the results.

        Parameters:
        -----------
        input_file : str
            Path to the input ground motion data file.
        output_file : str
            Path where the processed data will be saved.
        png_file : str
            Path where the plot will be saved.
        """
        # 1. Load the data from the input file
        with open(input_file, 'r') as f:
            lines = f.readlines()

        # If file is empty, just return
        if not lines:
            print(f"No data found in {input_file}.")
            return

        # 2. Parse the first line to get <num_points> <dt_input>
        header_parts = lines[0].strip().split()
        if len(header_parts) != 2:
            print(f"Expected the first line to contain two values (num_points, dt), "
                  f"but got: {lines[0]}")
            return

        try:
            num_points = int(header_parts[0])
            dt_input = float(header_parts[1])
        except ValueError:
            print(f"Could not parse the first line properly: {lines[0]}")
            return

        # 3. Extract the acceleration values from the remaining lines
        acc_data_raw = lines[1:]  # data lines start at line index 1
        if len(acc_data_raw) < num_points:
            print(f"Warning: The file claims {num_points} data points, "
                  f"but only {len(acc_data_raw)} lines of data were found.")
            num_points = len(acc_data_raw)

        # Convert them to float
        acc_data = np.array([float(line.strip()) for line in acc_data_raw[:num_points]])

        # 4. Scale the original data
        acc_data_scaled = acc_data * self.scale_factor

        # 5. Generate the original time vector
        #    length = num_points, time step = dt_input
        t_orig = np.arange(0, num_points * dt_input, dt_input)

        # If no valid data, stop
        if len(t_orig) == 0:
            print(f"No valid data in {input_file}.")
            return

        # Check if dt_input and dt_new are essentially the same
        same_dt = abs(dt_input - self.dt_new) < 1e-12  # small tolerance for float comparison

        if same_dt:

            t_new = t_orig
            acc_upsampled_scaled = acc_data_scaled  # no interpolation needed

            print("No upsampling required. dt_input is the same as dt_new.")

            # Save the data to output file
            with open(output_file, 'w') as f:
                f.write("time (s)\tacceleration (g)\n")
                for t, acc in zip(t_new, acc_upsampled_scaled):
                    f.write(f"{t:.6f}\t{acc:.6e}\n")

            # Plot only a single figure
            plt.figure(figsize=(10, 5))
            plt.plot(t_new, acc_upsampled_scaled, color='blue', linewidth=1,
                     label=f"Data (dt={dt_input}s, scaled x{self.scale_factor})")
            plt.title(f"No Upsampling Needed\n{os.path.basename(input_file)}")
            plt.xlabel("Time (s)")
            plt.ylabel("Acceleration (g)")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(png_file)
            plt.close()

        else:

            # 6. Generate new time vector for upsampling (using self.dt_new)
            t_new = np.arange(0, t_orig[-1] + self.dt_new, self.dt_new)

            # 7. Interpolate (upsample) the data
            acc_upsampled = np.interp(t_new, t_orig, acc_data)

            # 8. Apply the scaling factor to the upsampled data
            acc_upsampled_scaled = acc_upsampled * self.scale_factor

            # Optional Debug
            print("Upsampling performed.")
            print("Form Solution:")
            print(f"  Original Data (scaled): a(t) = original_acc * {self.scale_factor}")
            print(f"  Resampled Data (scaled): a'(t) = interp(t_new, t_orig, original_acc) * {self.scale_factor}")

            # 9. Save the upsampled and scaled data to the output file
            with open(output_file, 'w') as f:
                f.write("time (s)\tacceleration (g)\n")
                for t, acc in zip(t_new, acc_upsampled_scaled):
                    f.write(f"{t:.6f}\t{acc:.6e}\n")

            # 10. Plot the original vs upsampled data in two subplots
            fig, ax = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

            # Plot original data
            ax[0].plot(t_orig, acc_data_scaled,
                       label=f"Original (dt={dt_input}s)",
                       linewidth=1, color='blue')
            ax[0].set_title(f"Original Ground Motion Data\n{os.path.basename(input_file)}")
            ax[0].set_ylabel("Acceleration (g)")
            ax[0].legend()
            ax[0].grid(True)

            # Plot upsampled and scaled data
            ax[1].plot(t_new, acc_upsampled_scaled,
                       label=f"Upsampled & Scaled (dt={self.dt_new}s)",
                       linewidth=1, color='red')
            ax[1].set_title(f"Adjusted Ground Motion Data\n{os.path.basename(input_file)}")
            ax[1].set_xlabel("Time (s)")
            ax[1].set_ylabel("Acceleration (g)")
            ax[1].legend()
            ax[1].grid(True)

            plt.tight_layout()
            plt.savefig(png_file)
            plt.close(fig)


# # ---------------------
# # Example Script Usage:
# # ---------------------
# if __name__ == "__main__":
#     # Update these for your specific folders/paths
#     input_folder = "site"      # e.g., r"/path/to/site"
#     output_folder = "outputs"  # e.g., r"/path/to/outputs"

#     dt_new = 0.01      # new desired time step in seconds
#     scale_factor = 10  # scaling factor

#     processor = processData(
#         input_folder=input_folder,
#         output_folder=output_folder,
#         dt_new=dt_new,
#         scale_factor=scale_factor
#     )
#     processor.process_all_files()

