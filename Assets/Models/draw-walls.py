import os
import json
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Directory containing the JSON files
directory = '.'

# Function to draw walls based on the walls array
def draw_walls(walls, ax):
    for wall in walls:
        start_x, start_y = wall['x'], wall['y']
        dir_x, dir_y = wall['dir']['x'], wall['dir']['y']
        end_x, end_y = start_x + dir_x, start_y + dir_y
        
        ax.plot([start_x, end_x], [start_y, end_y], color='black')

# Function to fill ramp rooms with black
def fill_ramp(room, ax):
    rect = Rectangle((room['x'], room['y']), room['w'], room['h'], facecolor='black', edgecolor='black', linewidth=1)
    ax.add_patch(rect)

# Process each JSON file in the directory
for filename in os.listdir(directory):
    if filename.endswith('.json'):
        filepath = os.path.join(directory, filename)
        
        with open(filepath) as f:
            data = json.load(f)
        
        # Create a plot for the walls
        fig, ax = plt.subplots()
        ax.set_aspect('equal')
        
        # Draw the walls and fill ramps
        for room in data['rects']:
            if room.get('type') == 'ramp':
                fill_ramp(room, ax)  # Fill ramp rooms with black
            
            if 'walls' in room:
                draw_walls(room['walls'], ax)
        
        # Set plot limits
        ax.autoscale()
        ax.margins(0.1)
        
        # Save the plot as a PNG file
        png_filename = filename.replace('.json', '.png')
        plt.savefig(png_filename)
        plt.close(fig)

print("PNG files created for all JSON files with ramp rooms filled in black.")

