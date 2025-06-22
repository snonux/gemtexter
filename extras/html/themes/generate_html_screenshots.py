#!/usr/bin/env python3

import os
import subprocess
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

def check_browser_availability():
    """Check which browser is available"""
    browsers = []
    
    # Check for Chrome/Chromium
    for browser in ['google-chrome', 'chromium', 'chromium-browser']:
        try:
            result = subprocess.run([browser, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                browsers.append(('chrome', browser))
                break
        except:
            continue
    
    # Check for Firefox
    try:
        result = subprocess.run(['firefox', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            browsers.append(('firefox', 'firefox'))
    except:
        pass
    
    return browsers

def capture_with_selenium(browser_type, browser_path, html_file, output_file):
    """Capture screenshot using Selenium"""
    if browser_type == 'chrome':
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1200,900')
        
        try:
            driver = webdriver.Chrome(options=options)
        except:
            # Try with chromium
            options.binary_location = browser_path
            driver = webdriver.Chrome(options=options)
    else:  # firefox
        options = FirefoxOptions()
        options.add_argument('--headless')
        options.add_argument('--width=1200')
        options.add_argument('--height=900')
        driver = webdriver.Firefox(options=options)
    
    try:
        # Load the HTML file
        driver.get(f"file://{html_file}")
        
        # Wait for page to load
        time.sleep(2)
        
        # Crop to content area (400x300)
        driver.set_window_size(400, 300)
        
        # Take screenshot
        driver.save_screenshot(str(output_file))
        
    finally:
        driver.quit()

def capture_with_headless_browser(html_file, output_file):
    """Capture screenshot using headless browser directly"""
    browsers = check_browser_availability()
    
    if not browsers:
        return False
    
    for browser_type, browser_path in browsers:
        try:
            if browser_type == 'chrome':
                cmd = [
                    browser_path,
                    '--headless',
                    '--disable-gpu',
                    '--window-size=400,300',
                    '--screenshot=' + str(output_file),
                    '--default-background-color=0',
                    f'file://{html_file}'
                ]
            else:  # firefox
                cmd = [
                    browser_path,
                    '--headless',
                    '--window-size=400,300',
                    '--screenshot=' + str(output_file),
                    f'file://{html_file}'
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and output_file.exists():
                return True
        except Exception as e:
            print(f"Error with {browser_type}: {e}")
            continue
    
    return False

def generate_mini_html(theme_dir, temp_html):
    """Generate a mini HTML file that showcases the theme"""
    theme_name = theme_dir.name
    
    # Read the theme's example.html to get color info
    example_html = theme_dir / "example.html"
    if not example_html.exists():
        return False
    
    # Create a mini version that fits in 400x300
    mini_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="{theme_dir}/style.css">
    <style>
        body {{
            margin: 0;
            padding: 20px;
            min-height: 260px;
            overflow: hidden;
        }}
        .preview-container {{
            max-width: 360px;
            margin: 0 auto;
        }}
        h1 {{
            font-size: 1.8em !important;
            margin: 0.3em 0 !important;
        }}
        h2 {{
            font-size: 1.3em !important;
            margin: 0.5em 0 0.3em 0 !important;
        }}
        p {{
            font-size: 0.9em !important;
            line-height: 1.4 !important;
            margin: 0.5em 0 !important;
        }}
        .quote {{
            font-size: 0.85em !important;
            padding: 0.5em 1em !important;
            margin: 0.5em 0 !important;
        }}
        pre {{
            font-size: 0.75em !important;
            padding: 0.5em !important;
            margin: 0.5em 0 !important;
            max-height: 60px;
            overflow: hidden;
        }}
        a {{
            font-size: 0.9em !important;
        }}
        /* Hide overflow content */
        .preview-container > *:nth-child(n+6) {{
            display: none;
        }}
    </style>
</head>
<body>
    <div class="preview-container">
        <h1>{theme_name.replace('_', ' ').title()}</h1>
        <p>This is a preview of the theme's typography and color scheme.</p>
        <h2>Features</h2>
        <p>Clean design with <a href="#">interactive links</a> and elegant styling.</p>
        <div class="quote">
            "Beautiful themes for Gemtexter"
        </div>
        <pre><code>theme = "{theme_name}"</code></pre>
    </div>
</body>
</html>"""
    
    with open(temp_html, 'w') as f:
        f.write(mini_html)
    
    return True

def main():
    themes_dir = Path("/home/paul/git/gemtexter/extras/html/themes")
    screenshots_dir = themes_dir / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)
    
    # Check browser availability
    browsers = check_browser_availability()
    if not browsers:
        print("No supported browser found. Please install Chrome/Chromium or Firefox.")
        print("For better screenshots, you can also install Selenium:")
        print("  pip install selenium pillow")
        return
    
    print(f"Found browsers: {[b[1] for b in browsers]}")
    
    # Get all theme directories
    theme_dirs = [d for d in themes_dir.iterdir() if d.is_dir() and d.name not in ['screenshots', '.git']]
    valid_themes = [d for d in theme_dirs if (d / "style.css").exists()]
    
    print(f"Generating HTML screenshots for {len(valid_themes)} themes...")
    
    success_count = 0
    temp_html = themes_dir / "temp_preview.html"
    
    for i, theme_dir in enumerate(valid_themes):
        theme_name = theme_dir.name
        output_path = screenshots_dir / f"{theme_name}.png"
        
        print(f"[{i+1}/{len(valid_themes)}] Generating screenshot for {theme_name}...", end='', flush=True)
        
        try:
            # Generate mini HTML
            if not generate_mini_html(theme_dir, temp_html):
                print(" ✗ (no example.html)")
                continue
            
            # Try to capture screenshot
            if capture_with_headless_browser(temp_html, output_path):
                success_count += 1
                print(" ✓")
            else:
                print(" ✗ (capture failed)")
                
        except Exception as e:
            print(f" ✗ ({e})")
    
    # Clean up
    if temp_html.exists():
        temp_html.unlink()
    
    print(f"\nSuccessfully generated {success_count} screenshots!")
    
    # If we have working setup but some failed, offer Selenium option
    if success_count < len(valid_themes):
        print("\nFor better results, you can install Selenium:")
        print("  pip install selenium")
        print("  # Also install ChromeDriver or GeckoDriver")

if __name__ == "__main__":
    main()