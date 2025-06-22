#!/usr/bin/env python3

import os
import json
import random
import requests
import concurrent.futures
import colorsys
from pathlib import Path
import zipfile
import io

# Google Fonts API - Popular fonts with clear licenses
GOOGLE_FONTS = [
    {"family": "Roboto", "variants": ["300", "regular", "700"], "category": "sans-serif", "license": "Apache License 2.0"},
    {"family": "Open Sans", "variants": ["300", "regular", "700"], "category": "sans-serif", "license": "Apache License 2.0"},
    {"family": "Lato", "variants": ["300", "regular", "700"], "category": "sans-serif", "license": "OFL"},
    {"family": "Montserrat", "variants": ["300", "regular", "700"], "category": "sans-serif", "license": "OFL"},
    {"family": "Poppins", "variants": ["300", "regular", "700"], "category": "sans-serif", "license": "OFL"},
    {"family": "Raleway", "variants": ["300", "regular", "700"], "category": "sans-serif", "license": "OFL"},
    {"family": "Inter", "variants": ["300", "regular", "700"], "category": "sans-serif", "license": "OFL"},
    {"family": "Nunito", "variants": ["300", "regular", "700"], "category": "sans-serif", "license": "OFL"},
    {"family": "Work Sans", "variants": ["300", "regular", "700"], "category": "sans-serif", "license": "OFL"},
    {"family": "Quicksand", "variants": ["300", "regular", "700"], "category": "sans-serif", "license": "OFL"},
    
    {"family": "Playfair Display", "variants": ["regular", "700"], "category": "serif", "license": "OFL"},
    {"family": "Merriweather", "variants": ["300", "regular", "700"], "category": "serif", "license": "OFL"},
    {"family": "Lora", "variants": ["regular", "700"], "category": "serif", "license": "OFL"},
    {"family": "Source Serif Pro", "variants": ["regular", "700"], "category": "serif", "license": "OFL"},
    {"family": "Crimson Text", "variants": ["regular", "700"], "category": "serif", "license": "OFL"},
    {"family": "Libre Baskerville", "variants": ["regular", "700"], "category": "serif", "license": "OFL"},
    {"family": "EB Garamond", "variants": ["regular", "700"], "category": "serif", "license": "OFL"},
    {"family": "Cormorant", "variants": ["300", "regular", "700"], "category": "serif", "license": "OFL"},
    
    {"family": "Space Mono", "variants": ["regular", "700"], "category": "monospace", "license": "OFL"},
    {"family": "Fira Code", "variants": ["regular", "700"], "category": "monospace", "license": "OFL"},
    {"family": "JetBrains Mono", "variants": ["regular", "700"], "category": "monospace", "license": "OFL"},
    {"family": "Source Code Pro", "variants": ["regular", "700"], "category": "monospace", "license": "OFL"},
    {"family": "Ubuntu Mono", "variants": ["regular", "700"], "category": "monospace", "license": "Ubuntu Font License"},
    
    {"family": "Dancing Script", "variants": ["regular", "700"], "category": "handwriting", "license": "OFL"},
    {"family": "Pacifico", "variants": ["regular"], "category": "handwriting", "license": "OFL"},
    {"family": "Caveat", "variants": ["regular", "700"], "category": "handwriting", "license": "OFL"},
    {"family": "Satisfy", "variants": ["regular"], "category": "handwriting", "license": "OFL"},
    {"family": "Great Vibes", "variants": ["regular"], "category": "handwriting", "license": "OFL"},
    
    {"family": "Bebas Neue", "variants": ["regular"], "category": "display", "license": "OFL"},
    {"family": "Righteous", "variants": ["regular"], "category": "display", "license": "OFL"},
    {"family": "Fredoka One", "variants": ["regular"], "category": "display", "license": "OFL"},
    {"family": "Rubik", "variants": ["300", "regular", "700"], "category": "sans-serif", "license": "OFL"},
    {"family": "Oswald", "variants": ["300", "regular", "700"], "category": "sans-serif", "license": "OFL"},
    {"family": "Barlow", "variants": ["300", "regular", "700"], "category": "sans-serif", "license": "OFL"},
    {"family": "Archivo", "variants": ["regular", "700"], "category": "sans-serif", "license": "OFL"},
    {"family": "Exo 2", "variants": ["300", "regular", "700"], "category": "sans-serif", "license": "OFL"},
    {"family": "Karla", "variants": ["300", "regular", "700"], "category": "sans-serif", "license": "OFL"},
    {"family": "Bitter", "variants": ["regular", "700"], "category": "serif", "license": "OFL"},
    {"family": "Josefin Sans", "variants": ["300", "regular", "700"], "category": "sans-serif", "license": "OFL"},
    {"family": "Abril Fatface", "variants": ["regular"], "category": "display", "license": "OFL"},
    {"family": "Anton", "variants": ["regular"], "category": "sans-serif", "license": "OFL"},
    {"family": "Comfortaa", "variants": ["300", "regular", "700"], "category": "display", "license": "OFL"},
    {"family": "Lexend", "variants": ["300", "regular", "700"], "category": "sans-serif", "license": "OFL"},
    {"family": "DM Sans", "variants": ["regular", "700"], "category": "sans-serif", "license": "OFL"},
    {"family": "Space Grotesk", "variants": ["300", "regular", "700"], "category": "sans-serif", "license": "OFL"},
    {"family": "Sora", "variants": ["300", "regular", "700"], "category": "sans-serif", "license": "OFL"},
    {"family": "Manrope", "variants": ["300", "regular", "700"], "category": "sans-serif", "license": "OFL"},
    {"family": "Figtree", "variants": ["300", "regular", "700"], "category": "sans-serif", "license": "OFL"}
]

# Color palette generators
def generate_complementary_palette():
    base_hue = random.random()
    base_saturation = random.uniform(0.3, 0.9)
    base_lightness = random.uniform(0.3, 0.7)
    
    # Base color
    base_rgb = colorsys.hls_to_rgb(base_hue, base_lightness, base_saturation)
    base_color = '#{:02x}{:02x}{:02x}'.format(int(base_rgb[0]*255), int(base_rgb[1]*255), int(base_rgb[2]*255))
    
    # Complementary color
    comp_hue = (base_hue + 0.5) % 1.0
    comp_rgb = colorsys.hls_to_rgb(comp_hue, base_lightness, base_saturation * 0.8)
    comp_color = '#{:02x}{:02x}{:02x}'.format(int(comp_rgb[0]*255), int(comp_rgb[1]*255), int(comp_rgb[2]*255))
    
    # Background - very light or very dark
    if random.random() > 0.5:  # Light theme
        bg_lightness = random.uniform(0.92, 0.98)
        text_lightness = random.uniform(0.1, 0.2)
    else:  # Dark theme
        bg_lightness = random.uniform(0.05, 0.15)
        text_lightness = random.uniform(0.85, 0.95)
    
    bg_rgb = colorsys.hls_to_rgb(base_hue, bg_lightness, 0.1)
    bg_color = '#{:02x}{:02x}{:02x}'.format(int(bg_rgb[0]*255), int(bg_rgb[1]*255), int(bg_rgb[2]*255))
    
    text_rgb = colorsys.hls_to_rgb(0, text_lightness, 0)
    text_color = '#{:02x}{:02x}{:02x}'.format(int(text_rgb[0]*255), int(text_rgb[1]*255), int(text_rgb[2]*255))
    
    return {
        "primary": base_color,
        "secondary": comp_color,
        "background": bg_color,
        "text": text_color,
        "is_dark": bg_lightness < 0.5
    }

def generate_triadic_palette():
    base_hue = random.random()
    base_saturation = random.uniform(0.4, 0.8)
    base_lightness = random.uniform(0.4, 0.6)
    
    colors = []
    for i in range(3):
        hue = (base_hue + i * 0.333) % 1.0
        rgb = colorsys.hls_to_rgb(hue, base_lightness + random.uniform(-0.1, 0.1), base_saturation)
        color = '#{:02x}{:02x}{:02x}'.format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        colors.append(color)
    
    # Background
    if random.random() > 0.5:  # Light theme
        bg_lightness = random.uniform(0.94, 0.99)
        text_lightness = random.uniform(0.05, 0.15)
    else:  # Dark theme
        bg_lightness = random.uniform(0.02, 0.12)
        text_lightness = random.uniform(0.88, 0.98)
    
    bg_rgb = colorsys.hls_to_rgb(base_hue, bg_lightness, 0.05)
    bg_color = '#{:02x}{:02x}{:02x}'.format(int(bg_rgb[0]*255), int(bg_rgb[1]*255), int(bg_rgb[2]*255))
    
    text_rgb = colorsys.hls_to_rgb(0, text_lightness, 0)
    text_color = '#{:02x}{:02x}{:02x}'.format(int(text_rgb[0]*255), int(text_rgb[1]*255), int(text_rgb[2]*255))
    
    return {
        "primary": colors[0],
        "secondary": colors[1],
        "accent": colors[2],
        "background": bg_color,
        "text": text_color,
        "is_dark": bg_lightness < 0.5
    }

def generate_analogous_palette():
    base_hue = random.random()
    hue_shift = random.uniform(0.05, 0.12)
    base_saturation = random.uniform(0.3, 0.8)
    base_lightness = random.uniform(0.35, 0.65)
    
    colors = []
    for i in range(-2, 3):
        hue = (base_hue + i * hue_shift) % 1.0
        saturation = base_saturation + random.uniform(-0.1, 0.1)
        lightness = base_lightness + random.uniform(-0.1, 0.1)
        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        color = '#{:02x}{:02x}{:02x}'.format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        colors.append(color)
    
    # Background
    if random.random() > 0.5:  # Light theme
        bg_lightness = random.uniform(0.95, 0.99)
        text_lightness = random.uniform(0.08, 0.18)
    else:  # Dark theme
        bg_lightness = random.uniform(0.03, 0.10)
        text_lightness = random.uniform(0.90, 0.97)
    
    bg_rgb = colorsys.hls_to_rgb(base_hue, bg_lightness, 0.08)
    bg_color = '#{:02x}{:02x}{:02x}'.format(int(bg_rgb[0]*255), int(bg_rgb[1]*255), int(bg_rgb[2]*255))
    
    text_rgb = colorsys.hls_to_rgb(0, text_lightness, 0)
    text_color = '#{:02x}{:02x}{:02x}'.format(int(text_rgb[0]*255), int(text_rgb[1]*255), int(text_rgb[2]*255))
    
    return {
        "primary": colors[2],
        "secondary": colors[1],
        "accent": colors[3],
        "background": bg_color,
        "text": text_color,
        "is_dark": bg_lightness < 0.5
    }

# Layout generators
LAYOUTS = [
    "centered",
    "wide",
    "magazine",
    "card",
    "asymmetric",
    "minimal_grid",
    "brutalist",
    "newspaper",
    "terminal",
    "book",
    "sidebar",
    "hero",
    "masonry",
    "split",
    "overlap"
]

def generate_layout_css(layout_type, colors):
    base_css = f"""
body {{
    background-color: {colors['background']};
    color: {colors['text']};
    margin: 0;
    padding: 0;
    min-height: 100vh;
}}

h1, h2, h3 {{
    color: {colors['primary']};
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}}

a {{
    color: {colors['secondary']};
    text-decoration: none;
    transition: all 0.3s ease;
}}

a:hover {{
    opacity: 0.8;
    text-decoration: underline;
}}

.quote {{
    border-left: 4px solid {colors['secondary']};
    padding: 1em 1.5em;
    margin: 1.5em 0;
    background-color: {colors['primary']}11;
    font-style: italic;
}}

pre {{
    background-color: {colors['text']}11;
    border: 1px solid {colors['text']}22;
    padding: 1em;
    overflow-x: auto;
    border-radius: 4px;
}}

.inlinecode {{
    background-color: {colors['text']}11;
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-family: var(--font-mono);
}}
"""

    if layout_type == "centered":
        layout_css = """
body {
    max-width: 65ch;
    margin: 0 auto;
    padding: 2em 1em;
    line-height: 1.6;
}

.header {
    text-align: center;
    margin-bottom: 3em;
    padding-bottom: 2em;
    border-bottom: 1px solid currentColor;
}
"""
    elif layout_type == "wide":
        layout_css = """
body {
    max-width: 90%;
    margin: 0 auto;
    padding: 2em;
    line-height: 1.6;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 3em;
    padding-bottom: 1em;
    border-bottom: 2px solid currentColor;
}

p {
    max-width: 75ch;
}
"""
    elif layout_type == "magazine":
        layout_css = """
body {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2em;
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 3em;
    line-height: 1.6;
}

.header {
    grid-column: 1 / -1;
    text-align: center;
    margin-bottom: 2em;
    padding: 2em 0;
    background: linear-gradient(45deg, transparent 30%, currentColor 30%, currentColor 70%, transparent 70%);
    background-size: 10px 10px;
}

.header h1 {
    background-color: var(--bg-color);
    padding: 0.5em 1em;
    display: inline-block;
}

h1, h2, h3 {
    grid-column: 1 / -1;
}

p, ul, pre, .quote {
    grid-column: 1;
}
"""
    elif layout_type == "card":
        layout_css = f"""
body {{
    padding: 2em;
    line-height: 1.6;
    background-color: {colors['text']}08;
}}

.header {{
    background-color: {colors['background']};
    padding: 3em;
    margin: -2em -2em 2em -2em;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}}

h1, h2, h3 {{
    background-color: {colors['background']};
    padding: 1em;
    margin-left: -1em;
    margin-right: -1em;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}}

p, ul, pre, .quote {{
    background-color: {colors['background']};
    padding: 1.5em;
    margin: 1em 0;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}}
"""
    elif layout_type == "asymmetric":
        layout_css = """
body {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2em;
    line-height: 1.6;
}

.header {
    margin-left: 20%;
    margin-bottom: 3em;
}

h1 {
    margin-left: -5%;
    font-size: 3em;
}

h2 {
    margin-left: 10%;
}

h3 {
    margin-left: 25%;
}

p:nth-child(odd) {
    margin-left: 5%;
    margin-right: 15%;
}

p:nth-child(even) {
    margin-left: 15%;
    margin-right: 5%;
}
"""
    elif layout_type == "minimal_grid":
        layout_css = """
body {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: 1em;
    padding: 2em;
    line-height: 1.8;
}

.header {
    grid-column: 3 / 11;
    text-align: center;
    margin-bottom: 2em;
}

h1 {
    grid-column: 2 / 12;
}

h2 {
    grid-column: 3 / 11;
}

h3 {
    grid-column: 4 / 10;
}

p, ul, pre, .quote {
    grid-column: 3 / 10;
}
"""
    elif layout_type == "brutalist":
        layout_css = f"""
body {{
    padding: 0;
    line-height: 1.4;
}}

.header {{
    background-color: {colors['primary']};
    color: {colors['background']};
    padding: 2em;
    transform: skewY(-2deg);
    margin-bottom: 3em;
}}

.header h1 {{
    color: {colors['background']};
    font-size: 4em;
    margin: 0;
}}

h1, h2, h3 {{
    text-transform: uppercase;
    letter-spacing: 0.1em;
}}

p, ul, pre, .quote {{
    margin: 2em;
    padding: 1em;
    border: 4px solid {colors['text']};
}}

a {{
    background-color: {colors['secondary']};
    color: {colors['background']};
    padding: 0.2em 0.5em;
}}
"""
    elif layout_type == "newspaper":
        layout_css = """
body {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1em;
    column-count: 3;
    column-gap: 2em;
    column-rule: 1px solid currentColor;
    line-height: 1.5;
}

.header {
    column-span: all;
    text-align: center;
    border-top: 4px double currentColor;
    border-bottom: 4px double currentColor;
    padding: 1em 0;
    margin-bottom: 2em;
}

h1, h2 {
    column-span: all;
    text-align: center;
}

h3 {
    break-after: avoid;
}

p {
    text-align: justify;
    hyphens: auto;
}
"""
    elif layout_type == "terminal":
        layout_css = f"""
body {{
    background-color: #000;
    color: #0f0;
    padding: 1em;
    font-family: var(--font-mono);
    line-height: 1.4;
}}

.header {{
    border: 1px solid #0f0;
    padding: 1em;
    margin-bottom: 2em;
}}

.header::before {{
    content: "$ ";
}}

h1, h2, h3 {{
    color: #0f0;
}}

h1::before {{
    content: "### ";
}}

h2::before {{
    content: "## ";
}}

h3::before {{
    content: "# ";
}}

a {{
    color: #0ff;
}}

.quote {{
    border-left-color: #0f0;
    background-color: #0f01;
}}

pre {{
    border-color: #0f0;
    background-color: #0f01;
}}
"""
    elif layout_type == "book":
        layout_css = """
body {
    max-width: 40em;
    margin: 4em auto;
    padding: 2em;
    line-height: 1.8;
    text-align: justify;
    hyphens: auto;
}

.header {
    text-align: center;
    margin-bottom: 4em;
    page-break-after: always;
}

h1 {
    text-align: center;
    margin: 3em 0 2em 0;
}

h2 {
    margin-top: 2em;
}

p {
    text-indent: 1.5em;
}

p:first-of-type {
    text-indent: 0;
}

p:first-of-type::first-letter {
    font-size: 3em;
    line-height: 1;
    float: left;
    margin-right: 0.1em;
}
"""
    elif layout_type == "sidebar":
        layout_css = """
body {
    display: grid;
    grid-template-columns: 250px 1fr;
    min-height: 100vh;
    margin: 0;
}

.header {
    grid-column: 1;
    position: sticky;
    top: 0;
    height: 100vh;
    padding: 2em;
    border-right: 2px solid currentColor;
}

h1, h2, h3, p, ul, pre, .quote {
    grid-column: 2;
    margin-left: 2em;
    margin-right: 2em;
    max-width: 65ch;
}
"""
    elif layout_type == "hero":
        layout_css = f"""
body {{
    margin: 0;
    padding: 0;
}}

.header {{
    min-height: 70vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: linear-gradient(135deg, {colors['primary']}22, {colors['secondary']}22);
    margin-bottom: 3em;
}}

.header h1 {{
    font-size: 4em;
    margin: 0;
}}

h1, h2, h3, p, ul, pre, .quote {{
    max-width: 65ch;
    margin-left: auto;
    margin-right: auto;
    padding: 0 1em;
}}
"""
    elif layout_type == "masonry":
        layout_css = """
body {
    padding: 2em;
    columns: 300px auto;
    column-gap: 2em;
}

.header {
    column-span: all;
    text-align: center;
    margin-bottom: 3em;
}

h1, h2 {
    column-span: all;
}

p, ul, pre, .quote, h3 {
    break-inside: avoid;
    margin-bottom: 2em;
}
"""
    elif layout_type == "split":
        layout_css = f"""
body {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    min-height: 100vh;
    margin: 0;
}}

.header {{
    grid-column: 1;
    background-color: {colors['primary']};
    color: {colors['background']};
    padding: 3em;
    position: sticky;
    top: 0;
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
}}

.header h1 {{
    color: {colors['background']};
}}

h1, h2, h3, p, ul, pre, .quote {{
    grid-column: 2;
    padding: 0 3em;
}}
"""
    elif layout_type == "overlap":
        layout_css = f"""
body {{
    padding: 2em;
    position: relative;
}}

.header {{
    position: relative;
    z-index: 10;
    background-color: {colors['background']};
    padding: 2em;
    margin-bottom: -2em;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}}

h1 {{
    font-size: 3em;
    margin-top: 1em;
    position: relative;
    z-index: 5;
}}

h2 {{
    margin-left: 2em;
    position: relative;
    z-index: 4;
}}

h3 {{
    margin-left: 4em;
    position: relative;
    z-index: 3;
}}

p, ul, pre, .quote {{
    position: relative;
    background-color: {colors['background']};
    padding: 1.5em;
    margin: 1em 0 1em 3em;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}}

p:nth-child(even) {{
    margin-left: 0;
    margin-right: 3em;
}}
"""
    
    return base_css + "\n" + layout_css

def download_font(font_info):
    """Download font files from Google Fonts"""
    font_dir = Path("fonts_cache")
    font_dir.mkdir(exist_ok=True)
    
    downloaded_files = []
    
    for variant in font_info['variants']:
        # Construct Google Fonts download URL
        family_param = font_info['family'].replace(' ', '+')
        weight = '400' if variant == 'regular' else variant
        
        # Try to download from Google Fonts API
        url = f"https://fonts.google.com/download?family={family_param}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Extract font files from zip
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    for file in z.namelist():
                        if file.endswith('.ttf') and weight in file:
                            font_data = z.read(file)
                            filename = f"{font_info['family'].replace(' ', '_')}_{weight}.ttf"
                            filepath = font_dir / filename
                            with open(filepath, 'wb') as f:
                                f.write(font_data)
                            downloaded_files.append(filepath)
                            break
        except Exception as e:
            print(f"Error downloading {font_info['family']} {variant}: {e}")
    
    return downloaded_files

def create_theme(theme_name, fonts, colors, layout):
    """Create a single theme with fonts, colors, and layout"""
    theme_dir = Path(theme_name)
    theme_dir.mkdir(exist_ok=True)
    
    # Copy font files
    theme_fonts_dir = theme_dir / "fonts"
    theme_fonts_dir.mkdir(exist_ok=True)
    
    font_paths = {}
    for font_type, font_info in fonts.items():
        if font_info['files']:
            # Copy first available font file
            src = font_info['files'][0]
            dst = theme_fonts_dir / src.name
            os.system(f"cp '{src}' '{dst}'")
            font_paths[font_type] = f"./fonts/{src.name}"
    
    # Create theme.conf
    theme_conf = f"""#!/bin/bash
# Font configuration for {theme_name} theme
# Font licenses:
# - {fonts['heading']['family']}: {fonts['heading']['license']}
# - {fonts['body']['family']}: {fonts['body']['license']}

declare -xr HTML_WEBFONT_HEADING="{font_paths.get('heading', './fonts/default.ttf')}"
declare -xr HTML_WEBFONT_TEXT="{font_paths.get('body', './fonts/default.ttf')}"
"""
    
    with open(theme_dir / "theme.conf", "w") as f:
        f.write(theme_conf)
    
    # Create LICENSE file with font information
    license_content = f"""Theme: {theme_name}
Generated: {os.popen('date').read().strip()}

Font Licenses:
==============

Heading Font: {fonts['heading']['family']}
License: {fonts['heading']['license']}
Category: {fonts['heading']['category']}

Body Font: {fonts['body']['family']}
License: {fonts['body']['license']}
Category: {fonts['body']['category']}

Color Scheme:
=============
Primary: {colors['primary']}
Secondary: {colors['secondary']}
Background: {colors['background']}
Text: {colors['text']}
Theme Type: {'Dark' if colors['is_dark'] else 'Light'}

Layout: {layout}
"""
    
    with open(theme_dir / "LICENSE", "w") as f:
        f.write(license_content)
    
    # Create style.css
    css_content = f"""/* {theme_name} theme - {layout} layout */
@font-face {{
    font-family: 'HeadingFont';
    src: url('{font_paths.get('heading', './fonts/default.ttf')}') format('truetype');
    font-weight: normal;
    font-style: normal;
}}

@font-face {{
    font-family: 'BodyFont';
    src: url('{font_paths.get('body', './fonts/default.ttf')}') format('truetype');
    font-weight: normal;
    font-style: normal;
}}

:root {{
    --font-heading: 'HeadingFont', serif;
    --font-body: 'BodyFont', sans-serif;
    --font-mono: 'Courier New', monospace;
    --bg-color: {colors['background']};
}}

body {{
    font-family: var(--font-body);
}}

h1, h2, h3, h4, h5, h6 {{
    font-family: var(--font-heading);
    font-weight: normal;
}}

{generate_layout_css(layout, colors)}
"""
    
    with open(theme_dir / "style.css", "w") as f:
        f.write(css_content)
    
    # Create example.html
    example_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{theme_name.replace('_', ' ').title()} Theme - Gemtexter</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="header">
        <h1>{theme_name.replace('_', ' ').title()} Theme</h1>
        <p>A unique combination of {fonts['heading']['family']} and {fonts['body']['family']}</p>
    </div>

    <h1>Welcome to {theme_name.replace('_', ' ').title()}</h1>
    <p>This theme features a {layout.replace('_', ' ')} layout with a {'dark' if colors['is_dark'] else 'light'} color scheme. The typography combines {fonts['heading']['family']} for headings with {fonts['body']['family']} for body text, creating a unique reading experience.</p>

    <h2>Color Palette</h2>
    <p>The carefully selected colors work together to create visual harmony. Primary color <span style="color: {colors['primary']}">{colors['primary']}</span> pairs beautifully with secondary <span style="color: {colors['secondary']}">{colors['secondary']}</span>.</p>

    <h3>Typography Showcase</h3>
    <p>The {fonts['body']['family']} font family ({fonts['body']['category']}) provides excellent readability for body text, while {fonts['heading']['family']} ({fonts['heading']['category']}) adds character to headings.</p>

    <h2>Interactive Elements</h2>
    <p>Links like <a href="#">this example link</a> use the secondary color for clear visual distinction. Longer text links demonstrate the theme's approach to navigation:</p>
    <a href="#" class="textlink">Explore more about this theme's unique design choices and color combinations</a>

    <h2>Content Examples</h2>
    <div class="quote">
        "Good typography is invisible; great typography is unforgettable." This theme strives to balance both principles with its careful font selection and layout design.
    </div>

    <h3>Code Display</h3>
    <p>Inline code like <span class="inlinecode">theme.configure()</span> stands out clearly. Larger code blocks maintain readability:</p>
    <pre>const theme = {{
    name: "{theme_name}",
    layout: "{layout}",
    fonts: {{
        heading: "{fonts['heading']['family']}",
        body: "{fonts['body']['family']}"
    }},
    isDark: {str(colors['is_dark']).lower()}
}};</pre>

    <h2>Lists and Structure</h2>
    <p>This theme handles various content types elegantly:</p>
    <ul>
        <li>Clean typography with {fonts['body']['family']}</li>
        <li>Distinctive headings using {fonts['heading']['family']}</li>
        <li>{layout.replace('_', ' ').title()} layout for optimal content flow</li>
        <li>{'Dark' if colors['is_dark'] else 'Light'} theme with carefully chosen colors</li>
    </ul>

    <h2>Final Thoughts</h2>
    <p>Every element of this theme has been crafted to work in harmony. From the {layout.replace('_', ' ')} layout to the font pairing of {fonts['heading']['family']} and {fonts['body']['family']}, each choice enhances the reading experience.</p>

    <p>The color scheme creates the perfect backdrop for your content, ensuring that whether you're writing technical documentation, creative prose, or anything in between, your words will shine through with clarity and style.</p>
</body>
</html>"""
    
    with open(theme_dir / "example.html", "w") as f:
        f.write(example_html)
    
    return theme_name

def generate_random_theme():
    """Generate a complete random theme"""
    # Random theme name
    adjectives = ["cosmic", "serene", "vibrant", "minimal", "bold", "elegant", "modern", "classic", "dynamic", "subtle", "refined", "crisp", "warm", "cool", "fresh", "clean", "sharp", "smooth", "bright", "deep", "light", "rich", "soft", "strong", "pure", "clear", "radiant", "muted", "vivid", "gentle"]
    nouns = ["wave", "sky", "forest", "ocean", "mountain", "valley", "desert", "river", "lake", "field", "garden", "meadow", "storm", "breeze", "mist", "frost", "flame", "spark", "glow", "shadow", "light", "dawn", "dusk", "night", "day", "season", "horizon", "vista", "peak", "flow"]
    
    theme_name = f"{random.choice(adjectives)}_{random.choice(nouns)}"
    
    # Random fonts
    heading_font = random.choice([f for f in GOOGLE_FONTS if f['category'] in ['serif', 'display', 'sans-serif']])
    body_font = random.choice([f for f in GOOGLE_FONTS if f['category'] in ['serif', 'sans-serif']])
    
    # Download fonts
    heading_files = download_font(heading_font)
    body_files = download_font(body_font)
    
    fonts = {
        'heading': {
            'family': heading_font['family'],
            'license': heading_font['license'],
            'category': heading_font['category'],
            'files': heading_files
        },
        'body': {
            'family': body_font['family'],
            'license': body_font['license'],
            'category': body_font['category'],
            'files': body_files
        }
    }
    
    # Random color palette
    palette_generators = [generate_complementary_palette, generate_triadic_palette, generate_analogous_palette]
    colors = random.choice(palette_generators)()
    
    # Random layout
    layout = random.choice(LAYOUTS)
    
    return create_theme(theme_name, fonts, colors, layout)

def main():
    print("Generating 50 random themes with web fonts...")
    
    # Generate themes in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(generate_random_theme) for _ in range(50)]
        
        themes = []
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            try:
                theme_name = future.result()
                themes.append(theme_name)
                print(f"Created theme {i+1}/50: {theme_name}")
            except Exception as e:
                print(f"Error creating theme {i+1}: {e}")
    
    print(f"\nSuccessfully created {len(themes)} themes!")
    
    # Clean up font cache
    os.system("rm -rf fonts_cache")
    
    return themes

if __name__ == "__main__":
    main()