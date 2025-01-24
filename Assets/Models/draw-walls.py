import os
import json
import matplotlib.pyplot as plt

# Directory containing the JSON files
directory = '.'

# Function to draw walls based on the walls array
def draw_walls(walls, ax):
    for wall in walls:
        start_x, start_y = wall['x'], wall['y']
        dir_x, dir_y = wall['dir']['x'], wall['dir']['y']
        end_x, end_y = start_x + dir_x, start_y + dir_y
        
        ax.plot([start_x, end_x], [start_y, end_y], color='black')

# Process each JSON file in the directory
for filename in os.listdir(directory):
    if filename.endswith('.json'):
        filepath = os.path.join(directory, filename)
        
        with open(filepath) as f:
            data = json.load(f)
        
        # Create a plot for the walls
        fig, ax = plt.subplots()
        ax.set_aspect('equal')
        
        # Draw the walls for each room
        for room in data['rects']:
            if 'walls' in room:
                draw_walls(room['walls'], ax)
        
        # Set plot limits
        ax.autoscale()
        ax.margins(0.1)
        
        # Save the plot as a PNG file
        png_filename = filename.replace('.json', '.png')
        plt.savefig(png_filename)
        plt.close(fig)

print("PNG files created for all JSON files with wall arrays.")

