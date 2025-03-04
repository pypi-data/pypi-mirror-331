import numpy as np
import matplotlib.pyplot as plt

def upsample_and_scale(input_file, output_file, dt_input, dt_new, scale_factor, png_file):
    """
    Upsamples and scales the ground motion data from the input file.

    Parameters:
    input_file (str): Path to the input file with ground motion data.
    output_file (str): Path to save the upsampled and scaled data.
    dt_input (float): Original time step from the input data.
    dt_new (float): Desired new time step for upsampling.
    scale_factor (float): Scaling factor to multiply the acceleration values.
    png_file (str): Path to save the PNG plot image.
    """
    # Load the data from the input file
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Extract the acceleration values from the file
    acc_data = np.array([float(line.strip()) for line in lines[1:]])

    # Scale the original data
    acc_data_scaled = acc_data * scale_factor

    # Generate the original time vector
    t_orig = np.arange(0, len(acc_data) * dt_input, dt_input)

    # Define new time step and upsample
    t_new = np.arange(0, t_orig[-1] + dt_new, dt_new)
    acc_upsampled = np.interp(t_new, t_orig, acc_data)
    acc_upsampled_scaled = acc_upsampled * scale_factor

    # Show mathematical form solution before plotting
    print("Form Solution:")
    print(f"Original Data (scaled): a(t) = original_acc * {scale_factor}")
    print(f"Resampled Data (scaled): a'(t) = interp(t_new, t_orig, original_acc) * {scale_factor}")

    # Save the upsampled and scaled data to the output file
    with open(output_file, 'w') as f:
        for t, acc in zip(t_new, acc_upsampled_scaled):
            f.write(f"{t:.6f}\t{acc:.6e}\n")

    # Plot the original and upsampled data
    fig, ax = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Plot original data in the first subplot
    ax[0].plot(t_orig, acc_data_scaled, label=f"Original Data (dt={dt_input}s)", linewidth=1, color='blue')
    ax[0].set_title("Original Ground Motion Data " + input_file)
    ax[0].set_ylabel("Acceleration")
    ax[0].legend()
    ax[0].grid(True)

    # Plot upsampled and scaled data in the second subplot
    ax[1].plot(t_new, acc_upsampled_scaled, label=f"Upsampled & Scaled Data (dt={dt_new}s)", linewidth=1, color='red')
    ax[1].set_title("Adjusted Ground Motion Data" + input_file)
    ax[1].set_xlabel("Time (s)")
    ax[1].set_ylabel("Acceleration")
    ax[1].legend()
    ax[1].grid(True)

    # Adjust layout, save the plot as a PNG file, and show the plot
    plt.tight_layout()
    plt.savefig(png_file)
    plt.show()