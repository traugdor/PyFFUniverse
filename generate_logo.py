from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import os
import math
import random

# Create a directory for assets if it doesn't exist
assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
os.makedirs(assets_dir, exist_ok=True)

# Set up the image
width, height = 500, 500
background_color = (220, 240, 220, 0)  # Pale green background with transparency
logo = Image.new('RGBA', (width, height), (0, 0, 0, 0))  # Fully transparent background
draw = ImageDraw.Draw(logo)

# Draw a pale green coin as the background
coin_color = (180, 230, 180, 230)  # Pale green with some transparency
coin_border = (100, 180, 100)  # Darker green for border
coin_center = (width // 2, height // 2)
coin_radius = 200

# Draw the main coin
draw.ellipse(
    [(coin_center[0] - coin_radius, coin_center[1] - coin_radius),
     (coin_center[0] + coin_radius, coin_center[1] + coin_radius)],
    fill=coin_color,
    outline=coin_border,
    width=5
)

# Add a smaller inner circle for coin detail
inner_radius = 170
draw.ellipse(
    [(coin_center[0] - inner_radius, coin_center[1] - inner_radius),
     (coin_center[0] + inner_radius, coin_center[1] + inner_radius)],
    outline=coin_border,
    width=3
)

# Function to draw circuit lines
def draw_circuit_lines(draw_obj, center, radius, num_lines=8, color=(80, 150, 80, 180)):
    # Create a grid to track where lines have been drawn
    grid_size = 10  # Size of each grid cell
    grid_dim = int(radius * 2.2 / grid_size) + 1  # Extend grid beyond circle radius
    grid = [[False for _ in range(grid_dim)] for _ in range(grid_dim)]
    
    # Convert actual coordinates to grid coordinates
    def to_grid(x, y):
        grid_x = int((x - (center[0] - radius * 1.1)) / grid_size)
        grid_y = int((y - (center[1] - radius * 1.1)) / grid_size)
        return max(0, min(grid_dim-1, grid_x)), max(0, min(grid_dim-1, grid_y))
    
    # Convert grid coordinates to actual coordinates
    def to_coords(grid_x, grid_y):
        x = center[0] - radius * 1.1 + grid_x * grid_size + grid_size // 2
        y = center[1] - radius * 1.1 + grid_y * grid_size + grid_size // 2
        return x, y
    
    # Define a safe zone for the P (assume P takes up central 30% of radius)
    p_safe_radius = radius * 0.3
    
    # Starting points around the center, evenly distributed
    start_points = []
    for i in range(num_lines):
        angle = (2 * math.pi / num_lines) * i
        # Start from just outside the P safe zone
        start_x = center[0] + int(p_safe_radius * math.cos(angle))
        start_y = center[1] + int(p_safe_radius * math.sin(angle))
        
        # Snap to grid
        grid_x, grid_y = to_grid(start_x, start_y)
        start_x, start_y = to_coords(grid_x, grid_y)
        
        # Mark this grid cell as occupied
        grid[grid_y][grid_x] = True
        
        start_points.append((start_x, start_y, angle))
    
    # Draw each circuit line
    for start_x, start_y, angle in start_points:
        # Create a path with 3-7 segments (longer paths to reach the edge)
        segments = random.randint(3, 7)
        points = [(start_x, start_y)]
        
        # Direction preference based on starting angle
        horizontal_pref = abs(math.cos(angle)) > abs(math.sin(angle))
        
        curr_x, curr_y = start_x, start_y
        grid_x, grid_y = to_grid(curr_x, curr_y)
        
        # Direction of travel (alternating horizontal and vertical)
        for s in range(segments):
            # Choose direction: horizontal or vertical, alternating
            horizontal = (horizontal_pref and s % 2 == 0) or (not horizontal_pref and s % 2 == 1)
            
            if horizontal:
                # Horizontal movement
                direction = 1 if math.cos(angle) > 0 else -1
                steps = random.randint(3, 6)  # Longer steps to reach edge
                
                # Check if path is clear and within bounds
                new_grid_x = grid_x + steps * direction
                
                # Ensure we don't go too far outside the grid
                if new_grid_x < 0 or new_grid_x >= grid_dim:
                    # Adjust to stay within grid
                    new_grid_x = max(0, min(grid_dim-1, new_grid_x))
                
                # Check for crossing other lines
                path_clear = True
                for check_x in range(min(grid_x, new_grid_x), max(grid_x, new_grid_x) + 1):
                    if 0 <= check_x < grid_dim and 0 <= grid_y < grid_dim:
                        if grid[grid_y][check_x]:
                            if check_x != grid_x:  # Skip the current position
                                path_clear = False
                                break
                
                if not path_clear:
                    # Try the other direction
                    direction *= -1
                    new_grid_x = grid_x + steps * direction
                    
                    # Check bounds again
                    if new_grid_x < 0 or new_grid_x >= grid_dim:
                        # Adjust to stay within grid
                        new_grid_x = max(0, min(grid_dim-1, new_grid_x))
                    
                    # Check for crossing again
                    path_clear = True
                    for check_x in range(min(grid_x, new_grid_x), max(grid_x, new_grid_x) + 1):
                        if 0 <= check_x < grid_dim and 0 <= grid_y < grid_dim:
                            if grid[grid_y][check_x]:
                                if check_x != grid_x:  # Skip the current position
                                    path_clear = False
                                    break
                    
                    if not path_clear:
                        # No clear path in either direction
                        break
                
                # Mark the path as occupied
                for check_x in range(min(grid_x, new_grid_x), max(grid_x, new_grid_x) + 1):
                    if 0 <= check_x < grid_dim and 0 <= grid_y < grid_dim:
                        grid[grid_y][check_x] = True
                
                # Add the new point
                new_x, new_y = to_coords(new_grid_x, grid_y)
                points.append((new_x, new_y))
                
                # Update current position
                curr_x, curr_y = new_x, new_y
                grid_x, grid_y = new_grid_x, grid_y
                
            else:
                # Vertical movement
                direction = 1 if math.sin(angle) > 0 else -1
                steps = random.randint(3, 6)  # Longer steps to reach edge
                
                # Check if path is clear and within bounds
                new_grid_y = grid_y + steps * direction
                
                # Ensure we don't go too far outside the grid
                if new_grid_y < 0 or new_grid_y >= grid_dim:
                    # Adjust to stay within grid
                    new_grid_y = max(0, min(grid_dim-1, new_grid_y))
                
                # Check for crossing other lines
                path_clear = True
                for check_y in range(min(grid_y, new_grid_y), max(grid_y, new_grid_y) + 1):
                    if 0 <= check_y < grid_dim and 0 <= grid_x < grid_dim:
                        if grid[check_y][grid_x]:
                            if check_y != grid_y:  # Skip the current position
                                path_clear = False
                                break
                
                if not path_clear:
                    # Try the other direction
                    direction *= -1
                    new_grid_y = grid_y + steps * direction
                    
                    # Check bounds again
                    if new_grid_y < 0 or new_grid_y >= grid_dim:
                        # Adjust to stay within grid
                        new_grid_y = max(0, min(grid_dim-1, new_grid_y))
                    
                    # Check for crossing again
                    path_clear = True
                    for check_y in range(min(grid_y, new_grid_y), max(grid_y, new_grid_y) + 1):
                        if 0 <= check_y < grid_dim and 0 <= grid_x < grid_dim:
                            if grid[check_y][grid_x]:
                                if check_y != grid_y:  # Skip the current position
                                    path_clear = False
                                    break
                    
                    if not path_clear:
                        # No clear path in either direction
                        break
                
                # Mark the path as occupied
                for check_y in range(min(grid_y, new_grid_y), max(grid_y, new_grid_y) + 1):
                    if 0 <= check_y < grid_dim and 0 <= grid_x < grid_dim:
                        grid[check_y][grid_x] = True
                
                # Add the new point
                new_x, new_y = to_coords(grid_x, new_grid_y)
                points.append((new_x, new_y))
                
                # Update current position
                curr_x, curr_y = new_x, new_y
                grid_x, grid_y = grid_x, new_grid_y
            
            # Check if we've reached or gone beyond the edge of the circle
            dist_from_center = math.sqrt((curr_x - center[0])**2 + (curr_y - center[1])**2)
            if dist_from_center >= radius * 0.95:
                # We're at the edge, add one more segment to drift off if needed
                if random.random() > 0.5:
                    # Add one more segment in the same direction
                    if horizontal:
                        final_x = curr_x + direction * random.randint(10, 30)
                        final_y = curr_y
                    else:
                        final_x = curr_x
                        final_y = curr_y + direction * random.randint(10, 30)
                    points.append((final_x, final_y))
                break
        
        # Draw the circuit line if we have at least 2 points
        if len(points) >= 2:
            # Draw the line segments with thicker lines and rounded corners
            line_width = 4  # Thicker lines
            
            # Draw rounded corners by adding small circles at each joint
            for j in range(len(points) - 1):
                # Draw the line segment
                draw_obj.line([points[j], points[j+1]], fill=color, width=line_width)
                
                # Add a circle at each joint for rounded corners
                if j > 0:  # Skip the first point as it's already rounded by the previous segment
                    draw_obj.ellipse(
                        [(points[j][0] - line_width/2, points[j][1] - line_width/2),
                         (points[j][0] + line_width/2, points[j][1] + line_width/2)],
                        fill=color
                    )
            
            # Add a soldering pad at the end of the line (slightly larger)
            draw_obj.ellipse(
                [(points[-1][0] - line_width, points[-1][1] - line_width),
                 (points[-1][0] + line_width, points[-1][1] + line_width)],
                fill=color
            )

# Function to create WordArt-style text
def create_wordart(img, text, position, font_size, color1=(180, 60, 60), color2=(220, 100, 100), shadow_color=(50, 50, 50, 150)):
    # Create a new transparent image for the text
    text_img = Image.new('RGBA', img.size, (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_img)
    
    # Try to load a bold font for WordArt
    try:
        font = ImageFont.truetype('arial.ttf', font_size)
    except IOError:
        font = ImageFont.load_default()
    
    # Calculate text size to center it
    text_width, text_height = text_draw.textsize(text, font=font) if hasattr(text_draw, 'textsize') else (font_size * len(text) * 0.6, font_size)
    
    # Create shadow effect (offset text in dark color)
    shadow_offset = int(font_size * 0.05)  # 5% of font size
    for i in range(3):  # Multiple layers for thicker shadow
        offset = (i + 1) * shadow_offset
        text_draw.text(
            (position[0] - text_width/2 + offset, position[1] - text_height/2 + offset),
            text,
            font=font,
            fill=shadow_color
        )
    
    # Draw the main text with gradient effect
    for i in range(font_size):
        # Calculate color for this line of the gradient
        ratio = i / font_size
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        
        # Draw a slightly offset version of the text for each line of the gradient
        offset_y = int(font_size * 0.5) - i  # Start from bottom, move up
        text_draw.text(
            (position[0] - text_width/2, position[1] - text_height/2 + offset_y),
            text,
            font=font,
            fill=(r, g, b, 255)
        )
    
    # Apply a slight blur for smoother edges
    text_img = text_img.filter(ImageFilter.GaussianBlur(1))
    
    # Composite the text onto the original image
    img.paste(text_img, (0, 0), text_img)
    
    return img

# Draw circuit patterns
draw_circuit_lines(draw, coin_center, coin_radius, num_lines=12)

# Add WordArt-style 'P' in the center
create_wordart(logo, "P", (width // 2, height // 2 - 10), 180, 
              color1=(180, 60, 60), color2=(240, 120, 120))

# Add WordArt-style application name at the bottom
create_wordart(logo, "PyFFUniverse", (width // 2, height // 2 + 10), 50,
              color1=(180, 60, 60), color2=(240, 120, 120))

# Save the logo
logo_path = os.path.join(assets_dir, 'pyffuniverse_logo.png')
logo.save(logo_path)
print(f"Logo saved to {os.path.abspath(logo_path)}")

# Create a separate icon version with just the symbol (no text)
icon = Image.new('RGBA', (width, height), (0, 0, 0, 0))  # Fully transparent background
icon_draw = ImageDraw.Draw(icon)

# Draw the main coin for the icon
icon_draw.ellipse(
    [(coin_center[0] - coin_radius, coin_center[1] - coin_radius),
     (coin_center[0] + coin_radius, coin_center[1] + coin_radius)],
    fill=coin_color,
    outline=coin_border,
    width=5
)

# Add a smaller inner circle for coin detail
icon_draw.ellipse(
    [(coin_center[0] - inner_radius, coin_center[1] - inner_radius),
     (coin_center[0] + inner_radius, coin_center[1] + inner_radius)],
    outline=coin_border,
    width=3
)

# Draw circuit patterns for the icon
draw_circuit_lines(icon_draw, coin_center, coin_radius, num_lines=12)

# Add WordArt-style 'P' in the center of the icon
create_wordart(icon, "P", (width // 2, height // 2), 240,
              color1=(180, 60, 60), color2=(240, 120, 120))

# Save the icon in full size
full_icon_path = os.path.join(assets_dir, 'pyffuniverse_full_icon.png')
icon.save(full_icon_path)
print(f"Full icon saved to {os.path.abspath(full_icon_path)}")

# Create a smaller version for favicon/icon use
small_icon = icon.resize((64, 64), Image.Resampling.LANCZOS)
small_icon_path = os.path.join(assets_dir, 'pyffuniverse_icon.png')
small_icon.save(small_icon_path)
print(f"Small icon saved to {os.path.abspath(small_icon_path)}")
