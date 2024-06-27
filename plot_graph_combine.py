import os
from PIL import Image
import matplotlib.pyplot as plt

# Directory containing the PNG files
input_dir = "plots"

# List of PNG files in the directory
png_files = [f for f in os.listdir(input_dir) if f.endswith('.png') and f in ['plot3.png', 'plot4.png', 'plot7.png', 'plot8.png', 'plot2.png', 'plot5.png', 'plot6.png', 'plot9.png']]
assert len(png_files) == 8, "There should be exactly 8 PNG files in the directory."
png_files = ['plot3.png', 'plot4.png', 'plot7.png', 'plot8.png', 'plot2.png', 'plot5.png', 'plot6.png', 'plot9.png']

# Ensure there are exactly 8 PNG files
assert len(png_files) == 8, "There should be exactly 8 PNG files in the directory."

# Read the images
images = [Image.open(os.path.join(input_dir, file)) for file in png_files]

# Create a figure to combine the images
fig, axs = plt.subplots(2, 4, figsize=(21, 7))

# Plot each image in the figure
for ax, img in zip(axs.flatten(), images):
    ax.imshow(img)
    ax.axis('off')

# Save the combined figure
output_path = f"{input_dir}/combined_figure.png"
plt.savefig(output_path, bbox_inches='tight')
plt.close()

print(f"Combined figure saved as {output_path}")