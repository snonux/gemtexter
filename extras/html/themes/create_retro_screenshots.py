#!/usr/bin/env python3

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import re
import json

def extract_theme_colors(css_file):
    """Extract color scheme from CSS file"""
    with open(css_file, 'r') as f:
        css_content = f.read()
    
    colors = {}
    patterns = {
        'background': r'--color-bg:\s*([#\w]+);',
        'text': r'--color-text:\s*([#\w]+);',
        'primary': r'--color-primary:\s*([#\w]+);',
        'secondary': r'--color-secondary:\s*([#\w]+);',
        'accent': r'--color-accent:\s*([#\w]+);',
        'glow': r'--color-glow:\s*([#\w]+);'
    }
    
    for name, pattern in patterns.items():
        match = re.search(pattern, css_content)
        if match:
            colors[name] = match.group(1)
    
    return colors

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_retro_preview(theme_name, colors, effect_type, output_path):
    """Create a retro-themed preview"""
    width, height = 400, 300
    
    # Convert colors
    bg_rgb = hex_to_rgb(colors.get('background', '#000000'))
    text_rgb = hex_to_rgb(colors.get('text', '#00ff00'))
    primary_rgb = hex_to_rgb(colors.get('primary', '#00ff00'))
    secondary_rgb = hex_to_rgb(colors.get('secondary', '#00cc00'))
    
    # Create base image
    img = Image.new('RGB', (width, height), color=bg_rgb)
    draw = ImageDraw.Draw(img)
    
    # Load monospace font
    font_paths = [
        "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        "/System/Library/Fonts/Monaco.ttf",
        "C:\\Windows\\Fonts\\consola.ttf"
    ]
    
    title_font = None
    body_font = None
    small_font = None
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                title_font = ImageFont.truetype(font_path, 20)
                body_font = ImageFont.truetype(font_path, 12)
                small_font = ImageFont.truetype(font_path, 10)
                break
            except:
                continue
    
    if not title_font:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Add effect overlay
    if effect_type == "scanlines":
        for y in range(0, height, 4):
            draw.line([(0, y), (width, y)], fill=(255, 255, 255, 10), width=1)
    elif effect_type == "grid":
        for x in range(0, width, 20):
            draw.line([(x, 0), (x, height)], fill=(255, 255, 255, 8), width=1)
        for y in range(0, height, 20):
            draw.line([(0, y), (width, y)], fill=(255, 255, 255, 8), width=1)
    elif effect_type == "dots":
        for x in range(10, width, 20):
            for y in range(10, height, 20):
                draw.ellipse([(x-1, y-1), (x+1, y+1)], fill=primary_rgb + (30,))
    elif effect_type == "crt":
        # Curved edges effect
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        for i in range(20):
            alpha = int(255 * (i / 20))
            overlay_draw.rectangle([(i, i), (width-i, height-i)], 
                                 fill=(0, 0, 0, 0), 
                                 outline=(0, 0, 0, alpha), 
                                 width=2)
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)
    
    # Terminal prompt style header
    if effect_type == "terminal" or "terminal" in theme_name:
        draw.text((10, 10), f"$ theme --preview {theme_name}", 
                  fill=primary_rgb, font=body_font)
        draw.text((10, 30), "> LOADING...", fill=secondary_rgb, font=small_font)
        y_offset = 60
    else:
        # Regular header
        draw.text((10, 10), theme_name.replace('_', ' ').upper(), 
                  fill=primary_rgb, font=title_font)
        y_offset = 40
    
    # Draw retro-style content
    draw.text((10, y_offset), "SYSTEM: RETRO THEME", 
              fill=secondary_rgb, font=body_font)
    
    # Status lines
    y_offset += 30
    status_lines = [
        "WIDTH: 1200PX MIN",
        "LAYOUT: SINGLE COLUMN",
        f"EFFECT: {effect_type.upper()}",
        "STATUS: ACTIVE"
    ]
    
    for line in status_lines:
        draw.text((10, y_offset), f"> {line}", fill=text_rgb, font=small_font)
        y_offset += 15
    
    # Draw some decorative elements
    y_offset += 20
    draw.rectangle([(10, y_offset), (width-10, y_offset+2)], fill=primary_rgb)
    
    # Footer
    draw.text((10, height-30), f"[{effect_type.upper()}]", 
              fill=secondary_rgb, font=small_font)
    draw.text((width-100, height-30), "RETRO MODE", 
              fill=secondary_rgb, font=small_font)
    
    # Add glow effect to text
    if colors.get('glow'):
        # Create a glow layer
        glow_layer = Image.new('RGB', (width, height), bg_rgb)
        glow_draw = ImageDraw.Draw(glow_layer)
        glow_draw.text((10, 10), theme_name.replace('_', ' ').upper(), 
                      fill=primary_rgb, font=title_font)
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=2))
        img = Image.blend(img, glow_layer, 0.3)
    
    # Save image
    img.save(output_path, quality=95, optimize=True)

def main():
    themes_dir = Path("/home/paul/git/gemtexter/extras/html/themes")
    screenshots_dir = themes_dir / "screenshots"
    
    # Load metadata
    with open(themes_dir / "retro_themes_metadata.json", "r") as f:
        themes_metadata = json.load(f)
    
    print(f"Creating screenshots for {len(themes_metadata)} retro themes...")
    
    for i, theme_info in enumerate(themes_metadata):
        theme_name = theme_info['name']
        theme_dir = themes_dir / theme_name
        
        if not theme_dir.exists():
            continue
        
        # Extract colors from CSS
        css_file = theme_dir / "style.css"
        if css_file.exists():
            colors = extract_theme_colors(css_file)
            effect_type = theme_info.get('effect', 'none')
            
            # Create screenshot
            output_path = screenshots_dir / f"{theme_name}.png"
            create_retro_preview(theme_name, colors, effect_type, output_path)
            
            print(f"✓ [{i+1}/{len(themes_metadata)}] {theme_name}")
    
    print("\nRetro theme screenshots created!")

if __name__ == "__main__":
    # Import after checking
    try:
        from PIL import ImageFilter
    except ImportError:
        print("Installing Pillow for image filtering...")
        os.system("pip install Pillow")
        from PIL import ImageFilter
    
    main()