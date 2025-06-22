#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import re
import json

def extract_theme_colors(css_file):
    """Extract color scheme from CSS file"""
    with open(css_file, 'r') as f:
        css_content = f.read()
    
    colors = {
        'primary': '#667eea',
        'secondary': '#764ba2', 
        'accent': '#667eea',
        'background': '#ffffff',
        'text': '#333333'
    }
    
    # Extract CSS variables
    patterns = {
        'primary': r'--color-primary:\s*([#\w]+);',
        'secondary': r'--color-secondary:\s*([#\w]+);',
        'accent': r'--color-accent:\s*([#\w]+);',
        'background': r'--color-bg:\s*([#\w]+);',
        'text': r'--color-text:\s*([#\w]+);'
    }
    
    for name, pattern in patterns.items():
        match = re.search(pattern, css_content)
        if match:
            colors[name] = match.group(1)
    
    # Extract layout
    layout_match = re.search(r'/\* Layout: (\w+) \*/', css_content)
    layout = layout_match.group(1) if layout_match else 'default'
    
    return colors, layout

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def is_dark_theme(bg_color):
    """Check if theme is dark based on background color"""
    r, g, b = hex_to_rgb(bg_color)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return luminance < 0.5

def create_realistic_preview(theme_name, colors, layout, output_path):
    """Create a realistic preview of the theme"""
    width, height = 400, 300
    
    # Convert colors
    bg_rgb = hex_to_rgb(colors['background'])
    text_rgb = hex_to_rgb(colors['text'])
    primary_rgb = hex_to_rgb(colors['primary'])
    secondary_rgb = hex_to_rgb(colors['secondary'])
    accent_rgb = hex_to_rgb(colors['accent'])
    is_dark = is_dark_theme(colors['background'])
    
    # Create base image
    img = Image.new('RGB', (width, height), color=bg_rgb)
    draw = ImageDraw.Draw(img)
    
    # Try to load better fonts
    font_paths = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:\\Windows\\Fonts\\arial.ttf"
    ]
    
    title_font = None
    body_font = None
    small_font = None
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                title_font = ImageFont.truetype(font_path, 22)
                body_font = ImageFont.truetype(font_path, 13)
                small_font = ImageFont.truetype(font_path, 11)
                break
            except:
                continue
    
    if not title_font:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Layout-specific rendering
    if layout == 'hero':
        # Hero layout with gradient
        for y in range(120):
            factor = y / 120
            r = int(primary_rgb[0] * (1 - factor) + bg_rgb[0] * factor)
            g = int(primary_rgb[1] * (1 - factor) + bg_rgb[1] * factor)
            b = int(primary_rgb[2] * (1 - factor) + bg_rgb[2] * factor)
            draw.rectangle([(0, y), (width, y+1)], fill=(r, g, b))
        
        # Title on gradient
        title_color = bg_rgb if not is_dark else (255, 255, 255)
        draw.text((20, 40), theme_name.replace('_', ' ').title(), 
                  fill=title_color, font=title_font)
        content_start = 130
        
    elif layout == 'sidebar':
        # Sidebar layout
        draw.rectangle([(0, 0), (100, height)], fill=primary_rgb)
        draw.text((10, 20), "MENU", fill=bg_rgb, font=small_font)
        draw.line([(10, 40), (90, 40)], fill=bg_rgb, width=1)
        draw.text((10, 50), "Home", fill=bg_rgb, font=small_font)
        draw.text((10, 70), "About", fill=bg_rgb, font=small_font)
        draw.text((10, 90), "Blog", fill=bg_rgb, font=small_font)
        
        # Main content area
        draw.text((120, 20), theme_name.replace('_', ' ').title(), 
                  fill=primary_rgb, font=title_font)
        content_start = 60
        content_x = 120
        
    elif layout == 'card':
        # Card layout
        margin = 20
        # Main card
        draw.rectangle([(margin, margin), (width-margin, height-margin)], 
                      fill=bg_rgb, outline=None)
        # Shadow effect
        shadow = Image.new('RGB', (width, height), bg_rgb)
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rectangle([(margin+3, margin+3), (width-margin+3, height-margin+3)], 
                            fill=(200, 200, 200) if not is_dark else (50, 50, 50))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=3))
        img = Image.alpha_composite(img.convert('RGBA'), shadow.convert('RGBA')).convert('RGB')
        draw = ImageDraw.Draw(img)
        draw.rectangle([(margin, margin), (width-margin, height-margin)], 
                      fill=bg_rgb, outline=primary_rgb, width=2)
        
        draw.text((margin+15, margin+15), theme_name.replace('_', ' ').title(), 
                  fill=primary_rgb, font=title_font)
        content_start = margin + 55
        content_x = margin + 15
        
    elif layout == 'terminal':
        # Terminal layout
        draw.rectangle([(0, 0), (width, height)], fill=(0, 0, 0))
        draw.rectangle([(0, 0), (width, 25)], fill=(40, 40, 40))
        # Window controls
        draw.ellipse([(10, 8), (18, 16)], fill=(255, 95, 86))
        draw.ellipse([(25, 8), (33, 16)], fill=(255, 189, 46))
        draw.ellipse([(40, 8), (48, 16)], fill=(39, 201, 63))
        
        # Terminal text
        draw.text((10, 30), "$ theme --preview " + theme_name, 
                  fill=(0, 255, 0), font=body_font)
        draw.text((10, 50), "> Loading theme...", fill=(0, 255, 0), font=small_font)
        content_start = 80
        content_x = 10
        text_rgb = (0, 255, 0)
        
    elif layout == 'brutalist':
        # Brutalist layout
        draw.rectangle([(0, 0), (width, 60)], fill=primary_rgb)
        draw.polygon([(0, 60), (width, 60), (width, 80), (0, 100)], fill=primary_rgb)
        draw.text((20, 15), theme_name.replace('_', ' ').upper(), 
                  fill=bg_rgb, font=title_font)
        content_start = 110
        
    elif layout == 'magazine':
        # Magazine layout - multi-column
        draw.line([(width//3, 60), (width//3, height-20)], fill=text_rgb, width=1)
        draw.line([(2*width//3, 60), (2*width//3, height-20)], fill=text_rgb, width=1)
        draw.text((20, 15), theme_name.replace('_', ' ').title(), 
                  fill=primary_rgb, font=title_font)
        content_start = 60
        
    else:
        # Default layout
        draw.text((20, 20), theme_name.replace('_', ' ').title(), 
                  fill=primary_rgb, font=title_font)
        content_start = 60
    
    # Common content elements
    if layout not in ['terminal', 'sidebar', 'card']:
        content_x = 20
    
    if layout != 'terminal':
        # Heading
        draw.text((content_x, content_start), "Modern Design", 
                  fill=secondary_rgb, font=body_font)
        
        # Paragraph lines
        y = content_start + 25
        line_height = 12
        paragraph_lines = [
            "This theme features beautiful typography",
            "and a carefully crafted color palette.",
            "Perfect for blogs and documentation."
        ]
        
        for line in paragraph_lines:
            if y < height - 60:
                draw.text((content_x, y), line, fill=text_rgb, font=small_font)
                y += line_height
        
        # Link
        if y < height - 40:
            draw.text((content_x, y + 10), "→ Learn more", 
                      fill=secondary_rgb, font=body_font)
        
        # Button or accent element
        if layout in ['hero', 'card', 'gradient'] and y < height - 50:
            button_y = height - 50
            draw.rectangle([(content_x, button_y), (content_x + 80, button_y + 30)], 
                          fill=accent_rgb, outline=None)
            button_text_color = bg_rgb if is_dark_theme(colors['accent']) else (255, 255, 255)
            draw.text((content_x + 15, button_y + 8), "Preview", 
                      fill=button_text_color, font=body_font)
    
    # Add theme info
    info_y = height - 20
    theme_type = "Dark" if is_dark else "Light"
    info_color = tuple(int(c * 0.6) for c in text_rgb) if not is_dark else tuple(int(c * 0.8) for c in text_rgb)
    draw.text((10, info_y), f"{theme_type} • {layout}", fill=info_color, font=small_font)
    
    # Save image
    img.save(output_path, quality=95, optimize=True)

def generate_fallback_preview(theme_name, output_path):
    """Generate a simple fallback preview"""
    width, height = 400, 300
    img = Image.new('RGB', (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # Simple text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw.text((width//2 - 100, height//2 - 20), theme_name.replace('_', ' ').title(), 
              fill=(100, 100, 100), font=font)
    draw.text((width//2 - 50, height//2 + 10), "Theme Preview", 
              fill=(150, 150, 150), font=font)
    
    img.save(output_path, quality=85)

def main():
    themes_dir = Path("/home/paul/git/gemtexter/extras/html/themes")
    screenshots_dir = themes_dir / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)
    
    # Get all theme directories
    theme_dirs = [d for d in themes_dir.iterdir() if d.is_dir() and d.name not in ['screenshots', '.git']]
    valid_themes = [d for d in theme_dirs if (d / "style.css").exists()]
    
    print(f"Creating realistic previews for {len(valid_themes)} themes...")
    
    success_count = 0
    for i, theme_dir in enumerate(valid_themes):
        theme_name = theme_dir.name
        css_file = theme_dir / "style.css"
        output_path = screenshots_dir / f"{theme_name}.png"
        
        try:
            # Extract theme information
            colors, layout = extract_theme_colors(css_file)
            
            # Create preview
            create_realistic_preview(theme_name, colors, layout, output_path)
            success_count += 1
            print(f"✓ [{i+1}/{len(valid_themes)}] {theme_name}")
            
        except Exception as e:
            print(f"✗ [{i+1}/{len(valid_themes)}] {theme_name}: {e}")
            # Generate fallback
            try:
                generate_fallback_preview(theme_name, output_path)
            except:
                pass
    
    print(f"\nSuccessfully created {success_count} theme previews!")
    print(f"Preview images saved to: {screenshots_dir}")

if __name__ == "__main__":
    main()