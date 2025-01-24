import os
import json
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Directory containing the JSON files
directory = '.'

# Function to map a story level to a grayscale color
def story_to_color(story, min_story, max_story):
    """
    Map a story level to a grayscale color.
    Story 0 should be white, and lower stories (-1, -2, etc.) should be darker.
    """
    if story is None:
        return 'white'  # Default color for unassigned stories
    # Normalize so that 0 is white (1.0) and min_story is black (0.0)
    normalized = (story - min_story) / (max_story - min_story) if max_story > min_story else 1
    grayscale_value = normalized  # Higher values closer to 0 become lighter
    return (grayscale_value, grayscale_value, grayscale_value)  # RGB tuple

# Function to draw walls based on the walls array
def draw_walls(walls, ax):
    for wall in walls:
        start_x, start_y = wall['x'], wall['y']
        dir_x, dir_y = wall['dir']['x'], wall['dir']['y']
        end_x, end_y = start_x + dir_x, start_y + dir_y
        
        ax.plot([start_x, end_x], [start_y, end_y], color='black', linewidth=1)

# Function to fill a room with a given color
def fill_room(room, color, ax):
    rect = Rectangle((room['x'], room['y']), room['w'], room['h'], facecolor=color, edgecolor='black', linewidth=1)
    ax.add_patch(rect)

# Process each JSON file in the directory
for filename in os.listdir(directory):
    if filename.endswith('.json'):
        filepath = os.path.join(directory, filename)
        
        with open(filepath) as f:
            data = json.load(f)
        
        # Determine the range of stories in the dungeon
        stories = [room['story'] for room in data['rects'] if room.get('story') is not None]
        if not stories:
            print(f"No valid stories in {filename}, skipping.")
            continue
        min_story, max_story = min(stories), max(stories)
        
        # Create a plot for the dungeon layout
        fig, ax = plt.subplots()
        ax.set_aspect('equal')
        ax.set_title(filename)
        
        # Draw the rooms with their appropriate fill colors
        for room in data['rects']:
            if room.get('type') == 'ramp':
                fill_room(room, 'red', ax)  # Fill ramp rooms with red
            elif room.get('story') is not None:
                # Fill regular rooms with grayscale based on their story
                color = story_to_color(room['story'], min_story, max_story)
                fill_room(room, color, ax)
            
            # Draw the walls for each room
            if 'walls' in room:
                draw_walls(room['walls'], ax)
        
        # Set plot limits
        ax.autoscale()
        ax.margins(0.1)
        
        # Save the plot as a PNG file
        png_filename = filename.replace('.json', '.png')
        plt.savefig(png_filename)
        plt.close(fig)

print("PNG files created for all JSON files with rooms filled based on stories.")

