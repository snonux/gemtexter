#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import time

def generate_screenshots():
    """Generate screenshots for all themes using headless browser or create preview images"""
    themes_dir = Path("/home/paul/git/gemtexter/extras/html/themes")
    screenshots_dir = themes_dir / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)
    
    # Get all theme directories
    theme_dirs = [d for d in themes_dir.iterdir() if d.is_dir() and d.name not in ['screenshots', '.git']]
    
    print(f"Generating screenshots for {len(theme_dirs)} themes...")
    
    for theme_dir in theme_dirs:
        theme_name = theme_dir.name
        example_html = theme_dir / "example.html"
        screenshot_path = screenshots_dir / f"{theme_name}.png"
        
        if not example_html.exists():
            continue
            
        print(f"Generating screenshot for {theme_name}...")
        
        try:
            # Try to use Playwright or Puppeteer if available
            if check_playwright():
                generate_with_playwright(example_html, screenshot_path)
            # Try Firefox in headless mode
            elif check_firefox():
                generate_with_firefox(example_html, screenshot_path)
            # Try Chrome/Chromium in headless mode
            elif check_chrome():
                generate_with_chrome(example_html, screenshot_path)
            # Fallback to creating a preview image with PIL
            else:
                generate_preview_image(theme_dir, screenshot_path)
                
        except Exception as e:
            print(f"Error generating screenshot for {theme_name}: {e}")
            # Fallback to preview image
            generate_preview_image(theme_dir, screenshot_path)

def check_playwright():
    """Check if Playwright is available"""
    try:
        import playwright
        return True
    except ImportError:
        return False

def check_firefox():
    """Check if Firefox is available"""
    try:
        result = subprocess.run(['firefox', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def check_chrome():
    """Check if Chrome/Chromium is available"""
    for browser in ['google-chrome', 'chromium', 'chromium-browser']:
        try:
            result = subprocess.run([browser, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                return browser
        except:
            continue
    return False

def generate_with_playwright(html_path, output_path):
    """Generate screenshot using Playwright"""
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1200, 'height': 800})
        page.goto(f"file://{html_path}")
        page.screenshot(path=str(output_path), clip={'x': 0, 'y': 0, 'width': 1200, 'height': 800})
        browser.close()

def generate_with_firefox(html_path, output_path):
    """Generate screenshot using Firefox"""
    cmd = [
        'firefox',
        '--headless',
        '--window-size=1200,800',
        '--screenshot=' + str(output_path),
        f'file://{html_path}'
    ]
    subprocess.run(cmd, capture_output=True)
    time.sleep(1)  # Give it time to render

def generate_with_chrome(html_path, output_path):
    """Generate screenshot using Chrome/Chromium"""
    browser = check_chrome()
    cmd = [
        browser,
        '--headless',
        '--disable-gpu',
        '--window-size=1200,800',
        '--screenshot=' + str(output_path),
        f'file://{html_path}'
    ]
    subprocess.run(cmd, capture_output=True)
    time.sleep(1)  # Give it time to render

def generate_preview_image(theme_dir, output_path):
    """Generate a preview image using PIL when browser is not available"""
    # Read theme information
    theme_name = theme_dir.name
    
    # Try to extract colors from CSS
    colors = extract_colors_from_css(theme_dir / "style.css")
    
    # Create preview image
    width, height = 400, 300
    img = Image.new('RGB', (width, height), color=colors.get('background', '#ffffff'))
    draw = ImageDraw.Draw(img)
    
    # Try to use system fonts
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 32)
        body_font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 16)
    except:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
    
    # Draw theme name
    title = theme_name.replace('_', ' ').title()
    text_color = colors.get('text', '#000000')
    
    # Draw background pattern
    if colors.get('is_dark'):
        # Dark theme - add subtle grid
        for x in range(0, width, 20):
            draw.line([(x, 0), (x, height)], fill=colors.get('primary', '#666666') + '22', width=1)
        for y in range(0, height, 20):
            draw.line([(0, y), (width, y)], fill=colors.get('primary', '#666666') + '22', width=1)
    
    # Draw header area
    header_height = 100
    draw.rectangle([(0, 0), (width, header_height)], fill=colors.get('primary', '#667eea') + 'CC')
    
    # Draw title
    draw.text((20, 30), title, fill='white', font=title_font)
    
    # Draw some sample elements
    y_offset = header_height + 20
    
    # Sample heading
    draw.text((20, y_offset), "Sample Heading", fill=colors.get('primary', '#667eea'), font=body_font)
    y_offset += 30
    
    # Sample lines to represent text
    for i in range(3):
        line_width = width - 40 if i < 2 else width - 100
        draw.rectangle([(20, y_offset), (line_width, y_offset + 3)], fill=text_color + '66')
        y_offset += 10
    
    y_offset += 10
    
    # Sample link
    draw.rectangle([(20, y_offset), (120, y_offset + 3)], fill=colors.get('secondary', '#764ba2'))
    y_offset += 20
    
    # Sample button
    button_color = colors.get('accent', '#667eea')
    draw.rectangle([(20, y_offset), (140, y_offset + 35)], fill=button_color, outline=None)
    draw.text((40, y_offset + 10), "Preview", fill='white', font=body_font)
    
    # Add layout indicator
    layout_type = extract_layout_from_css(theme_dir / "style.css")
    if layout_type:
        draw.text((width - 150, height - 30), f"Layout: {layout_type}", fill=text_color + '99', font=body_font)
    
    # Save image
    img.save(output_path, quality=95)

def extract_colors_from_css(css_path):
    """Extract color information from CSS file"""
    colors = {
        'background': '#ffffff',
        'text': '#000000',
        'primary': '#667eea',
        'secondary': '#764ba2',
        'accent': '#667eea',
        'is_dark': False
    }
    
    try:
        with open(css_path, 'r') as f:
            css_content = f.read()
            
        import re
        
        # Extract CSS variables
        bg_match = re.search(r'--color-bg:\s*([#\w]+);', css_content)
        if bg_match:
            colors['background'] = bg_match.group(1)
            # Determine if dark theme
            if bg_match.group(1).startswith('#0') or bg_match.group(1).startswith('#1'):
                colors['is_dark'] = True
        
        text_match = re.search(r'--color-text:\s*([#\w]+);', css_content)
        if text_match:
            colors['text'] = text_match.group(1)
            
        primary_match = re.search(r'--color-primary:\s*([#\w]+);', css_content)
        if primary_match:
            colors['primary'] = primary_match.group(1)
            
        secondary_match = re.search(r'--color-secondary:\s*([#\w]+);', css_content)
        if secondary_match:
            colors['secondary'] = secondary_match.group(1)
            
        accent_match = re.search(r'--color-accent:\s*([#\w]+);', css_content)
        if accent_match:
            colors['accent'] = accent_match.group(1)
    except:
        pass
    
    return colors

def extract_layout_from_css(css_path):
    """Extract layout type from CSS file"""
    try:
        with open(css_path, 'r') as f:
            css_content = f.read()
            
        import re
        layout_match = re.search(r'/\* Layout: (\w+) \*/', css_content)
        if layout_match:
            return layout_match.group(1)
    except:
        pass
    
    return None

if __name__ == "__main__":
    generate_screenshots()