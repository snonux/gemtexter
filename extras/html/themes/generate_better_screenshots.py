#!/usr/bin/env python3

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import re
import colorsys

def extract_theme_info(theme_dir):
    """Extract colors and layout from theme CSS"""
    css_file = theme_dir / "style.css"
    if not css_file.exists():
        return None
    
    with open(css_file, 'r') as f:
        css_content = f.read()
    
    # Extract colors
    colors = {}
    color_vars = {
        'primary': r'--color-primary:\s*([#\w]+);',
        'secondary': r'--color-secondary:\s*([#\w]+);',
        'accent': r'--color-accent:\s*([#\w]+);',
        'background': r'--color-bg:\s*([#\w]+);',
        'text': r'--color-text:\s*([#\w]+);'
    }
    
    for name, pattern in color_vars.items():
        match = re.search(pattern, css_content)
        if match:
            colors[name] = match.group(1)
    
    # Extract layout type
    layout_match = re.search(r'/\* Layout: (\w+) \*/', css_content)
    layout = layout_match.group(1) if layout_match else 'default'
    
    # Determine if dark theme
    if colors.get('background', '#fff').startswith('#0') or colors.get('background', '#fff').startswith('#1'):
        colors['is_dark'] = True
    else:
        colors['is_dark'] = False
    
    return {'colors': colors, 'layout': layout}

def hex_to_rgb(hex_color):
    """Convert hex to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_theme_preview(theme_name, theme_info, output_path):
    """Create a preview image for the theme"""
    width, height = 400, 300
    
    # Get colors
    colors = theme_info['colors']
    bg_color = hex_to_rgb(colors.get('background', '#ffffff'))
    text_color = hex_to_rgb(colors.get('text', '#000000'))
    primary_color = hex_to_rgb(colors.get('primary', '#667eea'))
    secondary_color = hex_to_rgb(colors.get('secondary', '#764ba2'))
    accent_color = hex_to_rgb(colors.get('accent', '#667eea'))
    
    # Create image
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to load fonts
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 24)
        body_font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 14)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 11)
    except:
        # Fallback to default font
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Draw based on layout type
    layout = theme_info['layout']
    
    if layout in ['hero', 'gradient', 'floating']:
        # Draw gradient background
        for y in range(height):
            r = int(bg_color[0] + (primary_color[0] - bg_color[0]) * (y / height) * 0.3)
            g = int(bg_color[1] + (primary_color[1] - bg_color[1]) * (y / height) * 0.3)
            b = int(bg_color[2] + (primary_color[2] - bg_color[2]) * (y / height) * 0.3)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Header area
    if layout == 'sidebar':
        # Sidebar layout
        draw.rectangle([(0, 0), (100, height)], fill=primary_color)
        draw.text((110, 20), theme_name.replace('_', ' ').title(), fill=text_color, font=title_font)
    elif layout == 'card':
        # Card layout
        draw.rectangle([(20, 20), (width-20, 80)], fill=bg_color, outline=primary_color, width=2)
        draw.text((40, 35), theme_name.replace('_', ' ').title(), fill=primary_color, font=title_font)
    else:
        # Default header
        if layout in ['brutalist', 'terminal']:
            draw.rectangle([(0, 0), (width, 60)], fill=primary_color)
            draw.text((20, 15), theme_name.replace('_', ' ').title(), fill=bg_color, font=title_font)
        else:
            draw.text((20, 20), theme_name.replace('_', ' ').title(), fill=primary_color, font=title_font)
    
    # Content area simulation
    y_offset = 80 if layout != 'sidebar' else 60
    
    # Heading
    draw.text((20 if layout != 'sidebar' else 110, y_offset), "Sample Heading", fill=primary_color, font=body_font)
    y_offset += 25
    
    # Text lines
    line_color = tuple(c + (255-c)//3 if colors['is_dark'] else c - c//3 for c in text_color)
    for i in range(4):
        line_width = width - 40 if i < 3 else width - 100
        if layout == 'sidebar':
            draw.rectangle([(110, y_offset), (line_width, y_offset + 2)], fill=line_color)
        else:
            draw.rectangle([(20, y_offset), (line_width, y_offset + 2)], fill=line_color)
        y_offset += 8
    
    y_offset += 10
    
    # Link simulation
    link_x = 110 if layout == 'sidebar' else 20
    draw.rectangle([(link_x, y_offset), (link_x + 80, y_offset + 2)], fill=secondary_color)
    y_offset += 15
    
    # Button or accent element
    if layout in ['card', 'floating', 'gradient']:
        # Rounded button
        button_x = 110 if layout == 'sidebar' else 20
        draw.rectangle([(button_x, y_offset), (button_x + 100, y_offset + 30)], fill=accent_color)
        draw.text((button_x + 20, y_offset + 8), "Preview", fill=bg_color, font=body_font)
    elif layout == 'terminal':
        # Terminal prompt
        draw.text((20, y_offset), "$ theme --preview", fill=(0, 255, 0), font=body_font)
    
    # Layout indicator
    draw.text((width - 100, height - 25), f"{layout}", fill=text_color, font=small_font)
    
    # Theme type indicator
    theme_type = "Dark" if colors['is_dark'] else "Light"
    draw.text((20, height - 25), theme_type, fill=text_color, font=small_font)
    
    # Add some visual interest based on layout
    if layout == 'geometric':
        # Add geometric shapes
        draw.polygon([(width-50, 100), (width-30, 110), (width-50, 120), (width-70, 110)], fill=accent_color)
    elif layout == 'organic':
        # Add organic shapes
        draw.ellipse([(width-80, 80), (width-40, 120)], fill=accent_color, outline=None)
    elif layout == 'newspaper':
        # Add column lines
        draw.line([(width//3, 100), (width//3, height-40)], fill=text_color, width=1)
        draw.line([(2*width//3, 100), (2*width//3, height-40)], fill=text_color, width=1)
    
    # Save image
    img.save(output_path, quality=95)

def main():
    themes_dir = Path("/home/paul/git/gemtexter/extras/html/themes")
    screenshots_dir = themes_dir / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)
    
    # Get all theme directories
    theme_dirs = [d for d in themes_dir.iterdir() if d.is_dir() and d.name not in ['screenshots', '.git']]
    
    print(f"Generating preview screenshots for {len(theme_dirs)} themes...")
    
    success_count = 0
    for theme_dir in theme_dirs:
        theme_name = theme_dir.name
        
        # Skip if it's not a theme directory
        if not (theme_dir / "style.css").exists():
            continue
        
        try:
            # Extract theme information
            theme_info = extract_theme_info(theme_dir)
            if theme_info:
                # Create preview
                output_path = screenshots_dir / f"{theme_name}.png"
                create_theme_preview(theme_name, theme_info, output_path)
                success_count += 1
                print(f"✓ Generated preview for {theme_name}")
            else:
                print(f"✗ Could not extract info for {theme_name}")
        except Exception as e:
            print(f"✗ Error generating preview for {theme_name}: {e}")
    
    print(f"\nSuccessfully generated {success_count} theme previews!")

if __name__ == "__main__":
    main()