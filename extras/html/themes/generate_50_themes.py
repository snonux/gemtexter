#!/usr/bin/env python3

import os
import random
import colorsys
from pathlib import Path
import shutil
import subprocess
from datetime import datetime
import concurrent.futures
from PIL import Image, ImageDraw, ImageFont
import json

# Theme names components
ADJECTIVES = [
    "cosmic", "serene", "vibrant", "minimal", "bold", "elegant", "modern", "classic",
    "dynamic", "subtle", "refined", "crisp", "warm", "cool", "fresh", "clean",
    "sharp", "smooth", "bright", "deep", "light", "rich", "soft", "strong",
    "pure", "clear", "radiant", "muted", "vivid", "gentle", "sleek", "cozy",
    "ethereal", "mystic", "zen", "urban", "rustic", "electric", "pastel", "neon",
    "aurora", "twilight", "frost", "ember", "jade", "sapphire", "ruby", "amber"
]

NOUNS = [
    "wave", "sky", "forest", "ocean", "mountain", "valley", "desert", "river",
    "lake", "field", "garden", "meadow", "storm", "breeze", "mist", "frost",
    "flame", "spark", "glow", "shadow", "light", "dawn", "dusk", "night",
    "day", "season", "horizon", "vista", "peak", "flow", "cascade", "canyon",
    "oasis", "glacier", "nebula", "cosmos", "prism", "crystal", "ember", "aurora",
    "echo", "whisper", "dream", "voyage", "odyssey", "zen", "pulse", "rhythm"
]

# Font combinations with licensing info
FONT_COMBINATIONS = [
    # Sans-serif combinations
    {"heading": ("Abril_Fatface", "OFL", "display"), "body": ("Lato", "OFL", "sans-serif"), "code": ("consola-mono", "OFL", "monospace")},
    {"heading": ("oxygen", "OFL", "sans-serif"), "body": ("Lato", "OFL", "sans-serif"), "code": ("hack", "MIT", "monospace")},
    {"heading": ("roboto-slab", "Apache", "serif"), "body": ("oxygen", "OFL", "sans-serif"), "code": ("intelone-mono", "OFL", "monospace")},
    {"heading": ("Merriweather", "OFL", "serif"), "body": ("oxygen", "OFL", "sans-serif"), "code": ("hack", "MIT", "monospace")},
    {"heading": ("higher-jump", "Free", "display"), "body": ("Lato", "OFL", "sans-serif"), "code": ("consola-mono", "OFL", "monospace")},
    {"heading": ("pixelon", "Free", "display"), "body": ("oxygen", "OFL", "sans-serif"), "code": ("hack", "MIT", "monospace")},
    {"heading": ("repetition-scrolling", "Free", "display"), "body": ("Merriweather", "OFL", "serif"), "code": ("intelone-mono", "OFL", "monospace")},
    {"heading": ("zai-aeg-mignon-typewriter-1924", "Free", "display"), "body": ("roboto-slab", "Apache", "serif"), "code": ("hack", "MIT", "monospace")},
    {"heading": ("khand", "Free", "handwriting"), "body": ("Lato", "OFL", "sans-serif"), "code": ("consola-mono", "OFL", "monospace")},
    {"heading": ("Abril_Fatface", "OFL", "display"), "body": ("Merriweather", "OFL", "serif"), "code": ("hack", "MIT", "monospace")},
    # More variations
    {"heading": ("roboto-slab", "Apache", "serif"), "body": ("Lato", "OFL", "sans-serif"), "code": ("consola-mono", "OFL", "monospace")},
    {"heading": ("oxygen", "OFL", "sans-serif"), "body": ("Merriweather", "OFL", "serif"), "code": ("intelone-mono", "OFL", "monospace")},
    {"heading": ("Merriweather", "OFL", "serif"), "body": ("roboto-slab", "Apache", "serif"), "code": ("hack", "MIT", "monospace")},
    {"heading": ("higher-jump", "Free", "display"), "body": ("oxygen", "OFL", "sans-serif"), "code": ("intelone-mono", "OFL", "monospace")},
    {"heading": ("pixelon", "Free", "display"), "body": ("roboto-slab", "Apache", "serif"), "code": ("consola-mono", "OFL", "monospace")},
]

# Layout types
LAYOUTS = [
    "centered", "wide", "magazine", "card", "asymmetric", "minimal_grid",
    "brutalist", "newspaper", "terminal", "book", "sidebar", "hero",
    "masonry", "split", "overlap", "floating", "gradient", "geometric",
    "swiss", "retro", "future", "organic", "technical", "artistic"
]

def generate_color_palette():
    """Generate a harmonious color palette"""
    palette_type = random.choice(["complementary", "triadic", "analogous", "monochromatic", "split_complementary"])
    
    base_hue = random.random()
    base_saturation = random.uniform(0.3, 0.9)
    base_lightness = random.uniform(0.3, 0.7)
    
    # Determine if dark or light theme
    is_dark = random.random() > 0.5
    
    if is_dark:
        bg_lightness = random.uniform(0.05, 0.15)
        text_lightness = random.uniform(0.85, 0.95)
    else:
        bg_lightness = random.uniform(0.92, 0.98)
        text_lightness = random.uniform(0.05, 0.15)
    
    # Generate colors based on palette type
    if palette_type == "complementary":
        primary_rgb = colorsys.hls_to_rgb(base_hue, base_lightness, base_saturation)
        secondary_hue = (base_hue + 0.5) % 1.0
        secondary_rgb = colorsys.hls_to_rgb(secondary_hue, base_lightness, base_saturation * 0.8)
        accent_rgb = colorsys.hls_to_rgb(base_hue, base_lightness * 0.8, base_saturation * 0.6)
    elif palette_type == "triadic":
        primary_rgb = colorsys.hls_to_rgb(base_hue, base_lightness, base_saturation)
        secondary_hue = (base_hue + 0.333) % 1.0
        secondary_rgb = colorsys.hls_to_rgb(secondary_hue, base_lightness, base_saturation)
        accent_hue = (base_hue + 0.667) % 1.0
        accent_rgb = colorsys.hls_to_rgb(accent_hue, base_lightness, base_saturation)
    elif palette_type == "analogous":
        primary_rgb = colorsys.hls_to_rgb(base_hue, base_lightness, base_saturation)
        secondary_hue = (base_hue + 0.08) % 1.0
        secondary_rgb = colorsys.hls_to_rgb(secondary_hue, base_lightness, base_saturation * 0.9)
        accent_hue = (base_hue - 0.08) % 1.0
        accent_rgb = colorsys.hls_to_rgb(accent_hue, base_lightness * 0.9, base_saturation)
    elif palette_type == "monochromatic":
        primary_rgb = colorsys.hls_to_rgb(base_hue, base_lightness, base_saturation)
        secondary_rgb = colorsys.hls_to_rgb(base_hue, base_lightness * 0.7, base_saturation * 0.8)
        accent_rgb = colorsys.hls_to_rgb(base_hue, base_lightness * 1.2, base_saturation * 0.6)
    else:  # split_complementary
        primary_rgb = colorsys.hls_to_rgb(base_hue, base_lightness, base_saturation)
        secondary_hue = (base_hue + 0.42) % 1.0
        secondary_rgb = colorsys.hls_to_rgb(secondary_hue, base_lightness, base_saturation * 0.8)
        accent_hue = (base_hue + 0.58) % 1.0
        accent_rgb = colorsys.hls_to_rgb(accent_hue, base_lightness, base_saturation * 0.8)
    
    # Background and text colors
    bg_rgb = colorsys.hls_to_rgb(base_hue, bg_lightness, 0.1)
    text_rgb = colorsys.hls_to_rgb(0, text_lightness, 0)
    
    # Convert to hex
    primary = '#{:02x}{:02x}{:02x}'.format(int(primary_rgb[0]*255), int(primary_rgb[1]*255), int(primary_rgb[2]*255))
    secondary = '#{:02x}{:02x}{:02x}'.format(int(secondary_rgb[0]*255), int(secondary_rgb[1]*255), int(secondary_rgb[2]*255))
    accent = '#{:02x}{:02x}{:02x}'.format(int(accent_rgb[0]*255), int(accent_rgb[1]*255), int(accent_rgb[2]*255))
    background = '#{:02x}{:02x}{:02x}'.format(int(bg_rgb[0]*255), int(bg_rgb[1]*255), int(bg_rgb[2]*255))
    text = '#{:02x}{:02x}{:02x}'.format(int(text_rgb[0]*255), int(text_rgb[1]*255), int(text_rgb[2]*255))
    
    return {
        "primary": primary,
        "secondary": secondary,
        "accent": accent,
        "background": background,
        "text": text,
        "is_dark": is_dark,
        "palette_type": palette_type
    }

def generate_layout_css(layout_type, colors, font_sizes):
    """Generate CSS for different layout types"""
    base_css = f"""/* Base styles */
@font-face {{
    font-family: 'text';
    src: url("./text.ttf") format("truetype");
}}

@font-face {{
    font-family: 'heading';
    src: url("./heading.ttf") format("truetype");
}}

@font-face {{
    font-family: 'code';
    src: url("./code.ttf") format("truetype");
}}

@font-face {{
    font-family: 'handnotes';
    src: url("./handnotes.ttf") format("truetype");
}}

:root {{
    --color-primary: {colors['primary']};
    --color-secondary: {colors['secondary']};
    --color-accent: {colors['accent']};
    --color-bg: {colors['background']};
    --color-text: {colors['text']};
    --font-size-base: {font_sizes['base']}px;
    --font-size-h1: {font_sizes['h1']}em;
    --font-size-h2: {font_sizes['h2']}em;
    --font-size-h3: {font_sizes['h3']}em;
    --line-height: {font_sizes['line_height']};
}}

* {{
    box-sizing: border-box;
}}

html {{
    font-size: var(--font-size-base);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}}

body {{
    font-family: text, sans-serif;
    background-color: var(--color-bg);
    color: var(--color-text);
    line-height: var(--line-height);
    margin: 0;
    padding: 0;
    word-wrap: break-word;
}}

h1, h2, h3 {{
    font-family: heading, serif;
    line-height: 1.2;
    margin-top: 1em;
    margin-bottom: 0.5em;
}}

h1 {{
    font-size: var(--font-size-h1);
    color: var(--color-primary);
}}

h2 {{
    font-size: var(--font-size-h2);
    color: var(--color-primary);
}}

h3 {{
    font-size: var(--font-size-h3);
    color: var(--color-secondary);
}}

a {{
    font-family: code, monospace;
    color: var(--color-secondary);
    text-decoration: none;
    transition: all 0.3s ease;
}}

a:hover {{
    color: var(--color-accent);
    text-decoration: underline;
}}

.textlink {{
    font-family: text, sans-serif;
}}

.quote {{
    font-family: handnotes, cursive;
    border-left: 4px solid var(--color-accent);
    padding: 1em 1.5em;
    margin: 1.5em 0;
    background-color: {colors['primary']}11;
    font-style: italic;
}}

pre {{
    font-family: code, monospace;
    background-color: {colors['text']}0A;
    border: 1px solid {colors['text']}22;
    padding: 1em;
    overflow-x: auto;
    border-radius: 4px;
    font-size: 0.9em;
}}

code {{
    font-family: code, monospace;
    background-color: {colors['text']}0A;
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-size: 0.9em;
}}

ul, ol {{
    padding-left: 2em;
    margin: 1em 0;
}}

li {{
    margin: 0.5em 0;
}}

img {{
    max-width: 100%;
    height: auto;
}}

hr {{
    border: none;
    border-top: 1px solid {colors['text']}33;
    margin: 2em 0;
}}
"""

    # Layout-specific CSS
    layout_css = ""
    
    if layout_type == "centered":
        layout_css = """
body {
    max-width: 65ch;
    margin: 0 auto;
    padding: 2em 1em;
}

.header {
    text-align: center;
    margin-bottom: 3em;
    padding-bottom: 2em;
    border-bottom: 2px solid var(--color-primary);
}
"""
    elif layout_type == "wide":
        layout_css = """
body {
    max-width: 90%;
    margin: 0 auto;
    padding: 3em 2em;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 4em;
    padding-bottom: 2em;
    border-bottom: 3px solid var(--color-primary);
}

.content {
    max-width: 75ch;
    margin: 0 auto;
}
"""
    elif layout_type == "magazine":
        layout_css = """
body {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2em;
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 2em;
}

.header {
    grid-column: 1 / -1;
    text-align: center;
    margin-bottom: 2em;
    padding: 3em 0;
    background: linear-gradient(135deg, var(--color-primary)22, var(--color-secondary)22);
}

h1, h2 {
    grid-column: 1 / -1;
}

p, ul, pre, .quote {
    grid-column: span 1;
}

p:first-of-type {
    grid-column: 1 / 3;
    font-size: 1.2em;
    line-height: 1.6;
}
"""
    elif layout_type == "card":
        layout_css = f"""
body {{
    padding: 2em;
    background: linear-gradient(135deg, {colors['primary']}11, {colors['secondary']}11);
    min-height: 100vh;
}}

.header {{
    background-color: var(--color-bg);
    padding: 3em;
    margin-bottom: 3em;
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    text-align: center;
}}

h1, h2, h3, p, ul, pre, .quote {{
    background-color: var(--color-bg);
    padding: 2em;
    margin: 1em 0;
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.05);
}}

h1, h2, h3 {{
    padding: 1em 2em;
}}
"""
    elif layout_type == "asymmetric":
        layout_css = """
body {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2em;
}

.header {
    margin-left: 20%;
    margin-bottom: 4em;
}

h1 {
    margin-left: -5%;
    font-size: calc(var(--font-size-h1) * 1.2);
}

h2 {
    margin-left: 10%;
}

h3 {
    margin-left: 25%;
}

p:nth-child(odd) {
    margin-left: 5%;
    margin-right: 20%;
}

p:nth-child(even) {
    margin-left: 20%;
    margin-right: 5%;
}

.quote {
    margin-left: 15%;
    margin-right: 15%;
    text-align: center;
}
"""
    elif layout_type == "minimal_grid":
        layout_css = """
body {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: 1.5em;
    padding: 3em 2em;
    max-width: 1400px;
    margin: 0 auto;
}

.header {
    grid-column: 2 / 12;
    text-align: center;
    margin-bottom: 3em;
    padding-bottom: 2em;
    border-bottom: 1px solid var(--color-text);
}

h1 {
    grid-column: 1 / 13;
    text-align: center;
}

h2 {
    grid-column: 2 / 12;
}

h3 {
    grid-column: 3 / 11;
}

p, ul, pre {
    grid-column: 3 / 11;
}

.quote {
    grid-column: 2 / 12;
    text-align: center;
}
"""
    elif layout_type == "brutalist":
        layout_css = f"""
body {{
    background-color: {colors['text']};
    color: {colors['background']};
    padding: 0;
}}

.header {{
    background-color: var(--color-primary);
    color: var(--color-bg);
    padding: 4em 2em;
    transform: skewY(-3deg);
    margin-bottom: 4em;
}}

.header * {{
    transform: skewY(3deg);
}}

h1, h2, h3 {{
    background-color: var(--color-bg);
    color: var(--color-text);
    padding: 1em;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    margin: 0;
}}

p, ul, pre, .quote {{
    background-color: var(--color-bg);
    color: var(--color-text);
    margin: 0;
    padding: 2em;
    border: 8px solid var(--color-primary);
}}

a {{
    background-color: var(--color-secondary);
    color: var(--color-bg);
    padding: 0.3em 0.6em;
    text-decoration: none;
}}

a:hover {{
    background-color: var(--color-accent);
}}
"""
    elif layout_type == "newspaper":
        layout_css = """
body {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2em;
    columns: 3;
    column-gap: 2em;
    column-rule: 1px solid var(--color-text);
}

.header {
    column-span: all;
    text-align: center;
    border-top: 6px double var(--color-text);
    border-bottom: 6px double var(--color-text);
    padding: 2em 0;
    margin-bottom: 3em;
}

.header h1 {
    font-size: 4em;
    margin: 0;
    letter-spacing: 0.1em;
}

h1, h2 {
    column-span: all;
    text-align: center;
    margin: 2em 0 1em 0;
}

h3 {
    break-after: avoid;
}

p {
    text-align: justify;
    hyphens: auto;
}

.quote {
    column-span: all;
    text-align: center;
    font-size: 1.5em;
    margin: 2em 0;
}
"""
    elif layout_type == "terminal":
        layout_css = f"""
@import url('https://fonts.googleapis.com/css2?family=Source+Code+Pro:wght@400;700&display=swap');

body {{
    background-color: #000;
    color: #0f0;
    font-family: 'Source Code Pro', code, monospace;
    padding: 1em;
    line-height: 1.4;
}}

.header {{
    border: 2px solid #0f0;
    padding: 1em;
    margin-bottom: 2em;
    position: relative;
}}

.header::before {{
    content: "[SYSTEM] ";
    color: #ff0;
}}

h1, h2, h3 {{
    color: #0f0;
    font-family: 'Source Code Pro', code, monospace;
}}

h1::before {{
    content: "### ";
    color: #f0f;
}}

h2::before {{
    content: "## ";
    color: #0ff;
}}

h3::before {{
    content: "# ";
    color: #ff0;
}}

p::before {{
    content: "> ";
    color: #666;
}}

a {{
    color: #0ff;
    text-decoration: underline;
}}

a:hover {{
    background-color: #0ff;
    color: #000;
}}

.quote {{
    border: 1px dashed #0f0;
    background-color: #0f0111;
    color: #0f0;
}}

pre {{
    background-color: #111;
    border: 1px solid #0f0;
    color: #0f0;
    overflow-x: scroll;
}}

pre::before {{
    content: "$ cat output.log\\A";
    color: #666;
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
    margin-bottom: 6em;
    page-break-after: always;
}

.header h1 {
    font-size: 3em;
    margin-bottom: 0.5em;
}

h1 {
    text-align: center;
    margin: 3em 0 2em 0;
    page-break-before: always;
}

h2 {
    margin-top: 2em;
    text-align: left;
}

p {
    text-indent: 1.5em;
    margin: 0;
}

p:first-of-type {
    text-indent: 0;
}

p:first-of-type::first-letter {
    font-size: 4em;
    line-height: 1;
    float: left;
    margin: 0 0.1em 0 0;
    font-family: heading, serif;
    color: var(--color-primary);
}

.quote {
    margin: 2em 2em;
    text-align: center;
    font-style: italic;
}
"""
    elif layout_type == "sidebar":
        layout_css = """
body {
    display: grid;
    grid-template-columns: 300px 1fr;
    min-height: 100vh;
    margin: 0;
}

.header {
    grid-column: 1;
    position: sticky;
    top: 0;
    height: 100vh;
    padding: 3em 2em;
    background-color: var(--color-primary);
    color: var(--color-bg);
    overflow-y: auto;
}

.header h1 {
    color: var(--color-bg);
}

.content {
    grid-column: 2;
    padding: 3em;
    max-width: 65ch;
}

h1, h2, h3, p, ul, pre, .quote {
    grid-column: 2;
}
"""
    elif layout_type == "hero":
        layout_css = f"""
body {{
    margin: 0;
    padding: 0;
}}

.header {{
    min-height: 80vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: linear-gradient(135deg, {colors['primary']}CC, {colors['secondary']}CC),
                linear-gradient(45deg, {colors['accent']}22, transparent);
    color: var(--color-bg);
    text-align: center;
    position: relative;
}}

.header h1 {{
    font-size: 5em;
    margin: 0;
    color: var(--color-bg);
    text-shadow: 0 4px 8px rgba(0,0,0,0.3);
}}

.header p {{
    font-size: 1.5em;
    opacity: 0.9;
}}

.content {{
    max-width: 65ch;
    margin: 4em auto;
    padding: 0 2em;
}}
"""
    elif layout_type == "masonry":
        layout_css = """
body {
    padding: 2em;
    columns: 320px;
    column-gap: 2em;
}

.header {
    column-span: all;
    text-align: center;
    margin-bottom: 3em;
    padding: 2em;
    background: var(--color-primary);
    color: var(--color-bg);
}

.header h1 {
    color: var(--color-bg);
}

h1, h2 {
    column-span: all;
    text-align: center;
    margin: 2em 0;
}

p, ul, pre, .quote, h3 {
    break-inside: avoid;
    margin-bottom: 2em;
    padding: 1.5em;
    background-color: var(--color-bg);
    border: 1px solid var(--color-text)11;
    border-radius: 8px;
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
    background: linear-gradient(135deg, {colors['primary']}, {colors['secondary']});
    color: var(--color-bg);
    padding: 4em;
    position: sticky;
    top: 0;
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
}}

.header h1 {{
    color: var(--color-bg);
    font-size: 3.5em;
}}

.content {{
    grid-column: 2;
    padding: 4em;
    overflow-y: auto;
}}

h1, h2, h3, p, ul, pre, .quote {{
    grid-column: 2;
}}
"""
    elif layout_type == "overlap":
        layout_css = f"""
body {{
    padding: 2em;
    position: relative;
    max-width: 1200px;
    margin: 0 auto;
}}

.header {{
    position: relative;
    z-index: 10;
    background-color: var(--color-bg);
    padding: 3em;
    margin-bottom: -2em;
    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    border: 2px solid var(--color-primary);
}}

h1 {{
    font-size: 3.5em;
    margin-top: 1em;
    position: relative;
    z-index: 5;
}}

h2 {{
    margin-left: 2em;
    position: relative;
    z-index: 4;
    background-color: var(--color-bg);
    padding: 1em;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}}

h3 {{
    margin-left: 4em;
    position: relative;
    z-index: 3;
}}

p, ul, pre, .quote {{
    position: relative;
    background-color: var(--color-bg);
    padding: 2em;
    margin: 1em 0 1em 3em;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    border-left: 4px solid var(--color-accent);
}}

p:nth-child(even), ul:nth-child(even) {{
    margin-left: 0;
    margin-right: 3em;
    border-left: none;
    border-right: 4px solid var(--color-secondary);
}}
"""
    elif layout_type == "floating":
        layout_css = f"""
body {{
    padding: 4em 2em;
    background: linear-gradient(45deg, {colors['primary']}11, {colors['secondary']}11);
    min-height: 100vh;
}}

.header {{
    text-align: center;
    margin-bottom: 4em;
    animation: float 6s ease-in-out infinite;
}}

@keyframes float {{
    0%, 100% {{ transform: translateY(0); }}
    50% {{ transform: translateY(-20px); }}
}}

h1, h2, h3, p, ul, pre, .quote {{
    background-color: var(--color-bg);
    padding: 2em;
    margin: 2em auto;
    max-width: 65ch;
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    transition: transform 0.3s ease;
}}

h1:hover, h2:hover, h3:hover, p:hover, ul:hover, pre:hover, .quote:hover {{
    transform: translateY(-4px);
    box-shadow: 0 12px 48px rgba(0,0,0,0.15);
}}
"""
    elif layout_type == "gradient":
        layout_css = f"""
body {{
    margin: 0;
    padding: 0;
    background: linear-gradient(180deg, 
        {colors['primary']}22 0%, 
        {colors['secondary']}22 50%, 
        {colors['accent']}22 100%);
    min-height: 100vh;
}}

.header {{
    text-align: center;
    padding: 6em 2em;
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    margin-bottom: 4em;
}}

h1, h2, h3, p, ul, pre, .quote {{
    max-width: 65ch;
    margin: 2em auto;
    padding: 2em;
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}}
"""
    elif layout_type == "geometric":
        layout_css = f"""
body {{
    padding: 2em;
    background-color: var(--color-bg);
    background-image: 
        repeating-linear-gradient(45deg, 
            {colors['primary']}11 0, 
            {colors['primary']}11 10px, 
            transparent 10px, 
            transparent 20px),
        repeating-linear-gradient(-45deg, 
            {colors['secondary']}11 0, 
            {colors['secondary']}11 10px, 
            transparent 10px, 
            transparent 20px);
}}

.header {{
    background-color: var(--color-bg);
    border: 4px solid var(--color-primary);
    padding: 3em;
    margin-bottom: 3em;
    position: relative;
    clip-path: polygon(0 0, 100% 0, 95% 100%, 5% 100%);
}}

h1, h2, h3 {{
    position: relative;
    padding-left: 2em;
}}

h1::before, h2::before, h3::before {{
    content: "";
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 1em;
    height: 1em;
    background-color: var(--color-accent);
    clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
}}

p, ul, pre, .quote {{
    background-color: var(--color-bg);
    padding: 2em;
    margin: 2em 0;
    border-left: 4px solid var(--color-secondary);
    position: relative;
}}

p::after, ul::after, pre::after, .quote::after {{
    content: "";
    position: absolute;
    right: -10px;
    top: 50%;
    transform: translateY(-50%);
    width: 20px;
    height: 20px;
    background-color: var(--color-accent);
    clip-path: polygon(0% 0%, 100% 50%, 0% 100%);
}}
"""
    elif layout_type == "swiss":
        layout_css = """
body {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2em;
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 2em;
}

.header {
    grid-column: 1 / -1;
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 2em;
    margin-bottom: 4em;
    padding-bottom: 2em;
    border-bottom: 4px solid var(--color-text);
}

.header h1 {
    grid-column: 1 / 4;
    font-size: 4em;
    margin: 0;
    line-height: 0.9;
}

.header p {
    grid-column: 4 / -1;
    align-self: end;
}

h1 {
    grid-column: 1 / -1;
    font-size: 3em;
    margin: 1em 0 0.5em 0;
}

h2 {
    grid-column: 1 / 5;
    margin-top: 2em;
}

h3 {
    grid-column: 2 / 6;
}

p, ul, pre {
    grid-column: 2 / 6;
}

.quote {
    grid-column: 1 / -1;
    font-size: 1.5em;
    text-align: center;
    margin: 2em 0;
}
"""
    elif layout_type == "retro":
        layout_css = f"""
@import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap');

body {{
    background-color: #f4e8d0;
    color: #2a2a2a;
    padding: 2em;
    position: relative;
}}

body::before {{
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
        repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(0,0,0,0.03) 2px,
            rgba(0,0,0,0.03) 4px
        );
    pointer-events: none;
    z-index: 1;
}}

.header {{
    background-color: {colors['primary']};
    color: #f4e8d0;
    padding: 2em;
    margin: -2em -2em 2em -2em;
    text-align: center;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    position: relative;
    z-index: 2;
}}

.header h1 {{
    font-family: 'Courier Prime', monospace;
    font-size: 3em;
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #f4e8d0;
}}

h1, h2, h3 {{
    font-family: 'Courier Prime', monospace;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    position: relative;
    z-index: 2;
}}

p, ul, pre, .quote {{
    background-color: rgba(255,255,255,0.8);
    padding: 1.5em;
    margin: 1em 0;
    box-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    position: relative;
    z-index: 2;
}}

a {{
    color: {colors['secondary']};
    text-decoration: underline;
    text-decoration-style: wavy;
}}
"""
    elif layout_type == "future":
        layout_css = f"""
body {{
    background-color: #000;
    color: #fff;
    padding: 0;
    margin: 0;
    position: relative;
    overflow-x: hidden;
}}

body::before {{
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
        radial-gradient(circle at 20% 50%, {colors['primary']}44 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, {colors['secondary']}44 0%, transparent 50%),
        radial-gradient(circle at 40% 20%, {colors['accent']}44 0%, transparent 50%);
    z-index: -1;
}}

.header {{
    padding: 6em 2em;
    text-align: center;
    position: relative;
}}

.header h1 {{
    font-size: 5em;
    margin: 0;
    background: linear-gradient(45deg, {colors['primary']}, {colors['secondary']}, {colors['accent']});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-transform: uppercase;
    letter-spacing: 0.2em;
}}

h1, h2, h3, p, ul, pre, .quote {{
    max-width: 65ch;
    margin: 2em auto;
    padding: 2em;
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}}

a {{
    color: {colors['accent']};
    text-decoration: none;
    position: relative;
}}

a::after {{
    content: "";
    position: absolute;
    bottom: -2px;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, {colors['primary']}, {colors['secondary']});
    transform: scaleX(0);
    transition: transform 0.3s ease;
}}

a:hover::after {{
    transform: scaleX(1);
}}
"""
    elif layout_type == "organic":
        layout_css = f"""
body {{
    padding: 2em;
    background-color: {colors['background']};
    background-image: 
        radial-gradient(circle at 10% 20%, {colors['primary']}11 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, {colors['secondary']}11 0%, transparent 50%);
}}

.header {{
    text-align: center;
    margin-bottom: 4em;
    padding: 3em;
    background: {colors['background']};
    border-radius: 50% 20% 30% 70% / 30% 60% 40% 70%;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}}

h1, h2, h3 {{
    position: relative;
    padding-left: 3em;
}}

h1::before, h2::before, h3::before {{
    content: "🌿";
    position: absolute;
    left: 0;
    font-size: 2em;
    opacity: 0.3;
}}

p, ul, pre, .quote {{
    background-color: {colors['background']};
    padding: 2em;
    margin: 2em 0;
    border-radius: 20px 5px 20px 5px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.05);
    position: relative;
    overflow: hidden;
}}

p::before, ul::before, pre::before, .quote::before {{
    content: "";
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, {colors['accent']}11 0%, transparent 70%);
    z-index: -1;
}}
"""
    elif layout_type == "technical":
        layout_css = f"""
body {{
    font-family: code, monospace;
    background-color: #0a0a0a;
    color: #e0e0e0;
    padding: 2em;
    background-image: 
        linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
    background-size: 20px 20px;
}}

.header {{
    border: 2px solid {colors['primary']};
    padding: 2em;
    margin-bottom: 3em;
    position: relative;
    background: linear-gradient(135deg, transparent 10px, #0a0a0a 10px);
}}

.header::before {{
    content: "//";
    position: absolute;
    top: 10px;
    left: 10px;
    color: {colors['primary']};
    font-size: 2em;
}}

h1, h2, h3 {{
    font-family: code, monospace;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    border-left: 4px solid {colors['accent']};
    padding-left: 1em;
}}

h1::before {{ content: "001 "; color: {colors['primary']}; }}
h2::before {{ content: "010 "; color: {colors['secondary']}; }}
h3::before {{ content: "011 "; color: {colors['accent']}; }}

p, ul, pre, .quote {{
    background-color: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 1.5em;
    margin: 1.5em 0;
    position: relative;
}}

p::before, ul::before, .quote::before {{
    content: ">";
    position: absolute;
    left: -1em;
    color: {colors['accent']};
}}

a {{
    color: {colors['accent']};
    text-decoration: none;
    padding: 0.2em 0.4em;
    background-color: rgba(255,255,255,0.05);
    border: 1px solid {colors['accent']}33;
    transition: all 0.3s ease;
}}

a:hover {{
    background-color: {colors['accent']}22;
    border-color: {colors['accent']};
}}
"""
    elif layout_type == "artistic":
        layout_css = f"""
body {{
    padding: 4em 2em;
    background: linear-gradient(45deg, {colors['background']}, {colors['background']}DD);
    min-height: 100vh;
    position: relative;
}}

body::before, body::after {{
    content: "";
    position: fixed;
    width: 300px;
    height: 300px;
    border-radius: 50%;
    filter: blur(100px);
    z-index: -1;
}}

body::before {{
    top: -150px;
    left: -150px;
    background: {colors['primary']}44;
}}

body::after {{
    bottom: -150px;
    right: -150px;
    background: {colors['secondary']}44;
}}

.header {{
    text-align: center;
    margin-bottom: 4em;
    position: relative;
}}

.header h1 {{
    font-size: 4em;
    margin: 0;
    transform: perspective(500px) rotateY(-15deg);
    text-shadow: 
        3px 3px 0 {colors['primary']},
        6px 6px 0 {colors['secondary']},
        9px 9px 20px rgba(0,0,0,0.2);
}}

h2, h3 {{
    position: relative;
    display: inline-block;
}}

h2::after, h3::after {{
    content: "";
    position: absolute;
    bottom: -5px;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, {colors['primary']}, {colors['secondary']}, {colors['accent']});
    border-radius: 2px;
}}

p, ul, pre, .quote {{
    max-width: 65ch;
    margin: 2em auto;
    padding: 2em;
    background: rgba(255,255,255,0.9);
    box-shadow: 
        0 8px 32px rgba(0,0,0,0.1),
        inset 0 1px 0 rgba(255,255,255,0.5);
    border-radius: 20px;
    transform: rotate(-1deg);
}}

p:nth-child(even), ul:nth-child(even), .quote:nth-child(even) {{
    transform: rotate(1deg);
}}

a {{
    color: {colors['secondary']};
    text-decoration: none;
    background-image: linear-gradient(90deg, {colors['primary']}, {colors['secondary']});
    background-size: 100% 2px;
    background-position: 0 100%;
    background-repeat: no-repeat;
    transition: all 0.3s ease;
}}

a:hover {{
    background-size: 100% 100%;
    color: white;
    padding: 0.2em 0.4em;
    margin: -0.2em -0.4em;
}}
"""
    
    return base_css + "\n\n/* Layout: " + layout_type + " */\n" + layout_css

def generate_font_sizes():
    """Generate harmonious font size combinations"""
    base_sizes = [14, 15, 16, 17, 18]
    base = random.choice(base_sizes)
    
    scale_ratios = [1.125, 1.2, 1.25, 1.333, 1.414, 1.5, 1.618]
    scale = random.choice(scale_ratios)
    
    return {
        'base': base,
        'h1': round(scale ** 3, 2),
        'h2': round(scale ** 2, 2),
        'h3': round(scale, 2),
        'line_height': round(random.uniform(1.4, 1.8), 2)
    }

def create_theme(theme_name, fonts, colors, layout, font_sizes):
    """Create a complete theme directory with all files"""
    theme_dir = Path(f"/home/paul/git/gemtexter/extras/html/themes/{theme_name}")
    theme_dir.mkdir(exist_ok=True)
    
    # Generate theme.conf
    theme_conf = f"""declare -xr HTML_HEADER=./extras/html/header.html.part
declare -xr HTML_FOOTER=./extras/html/footer.html.part
declare -xr HTML_CSS_STYLE=$HTML_THEME_DIR/style.css
declare -xr HTML_WEBFONT_HEADING=./extras/html/fonts/{fonts['heading'][0]}/{fonts['heading'][0]}-Bold.ttf
declare -xr HTML_WEBFONT_TEXT=./extras/html/fonts/{fonts['body'][0]}/{fonts['body'][0]}-Regular.ttf
declare -xr HTML_WEBFONT_CODE=./extras/html/fonts/{fonts['code'][0]}/{fonts['code'][0]}-Regular.ttf
declare -xr HTML_WEBFONT_HANDNOTES=./extras/html/fonts/khand/khand.ttf
declare -xr SOURCE_HIGHLIGHT_CSS=./extras/html/source-highlight-styles/mono.css
"""
    
    with open(theme_dir / "theme.conf", "w") as f:
        f.write(theme_conf)
    
    # Copy fonts and generate style.css
    css_content = generate_layout_css(layout, colors, font_sizes)
    
    # Add font file references
    font_mapping = {
        'heading': fonts['heading'][0],
        'text': fonts['body'][0],
        'code': fonts['code'][0],
        'handnotes': 'khand'
    }
    
    # Copy font files
    for font_type, font_name in font_mapping.items():
        if font_name == "Abril_Fatface":
            src = f"/home/paul/git/gemtexter/extras/html/fonts/{font_name}/AbrilFatface-Regular.ttf"
            dst = theme_dir / f"{font_type}.ttf"
        elif font_name in ["Lato", "Merriweather", "oxygen", "roboto-slab"]:
            weight = "Bold" if font_type == "heading" else "Regular"
            src = f"/home/paul/git/gemtexter/extras/html/fonts/{font_name}/{font_name}-{weight}.ttf"
            dst = theme_dir / f"{font_type}.ttf"
        elif font_name == "consola-mono":
            weight = "Bold" if font_type == "heading" else "Book"
            src = f"/home/paul/git/gemtexter/extras/html/fonts/{font_name}/ConsolaMono-{weight}.ttf"
            dst = theme_dir / f"{font_type}.ttf"
        elif font_name == "hack":
            src = f"/home/paul/git/gemtexter/extras/html/fonts/{font_name}/Hack-Regular.ttf"
            dst = theme_dir / f"{font_type}.ttf"
        elif font_name == "intelone-mono":
            src = f"/home/paul/git/gemtexter/extras/html/fonts/{font_name}/intelone-mono-font-family-regular.ttf"
            dst = theme_dir / f"{font_type}.ttf"
        elif font_name == "higher-jump":
            src = f"/home/paul/git/gemtexter/extras/html/fonts/{font_name}/Higher Jump.ttf"
            dst = theme_dir / f"{font_type}.ttf"
        elif font_name == "pixelon":
            src = f"/home/paul/git/gemtexter/extras/html/fonts/{font_name}/Pixelon.ttf"
            dst = theme_dir / f"{font_type}.ttf"
        elif font_name == "repetition-scrolling":
            src = f"/home/paul/git/gemtexter/extras/html/fonts/{font_name}/repet___.ttf"
            dst = theme_dir / f"{font_type}.ttf"
        elif font_name == "zai-aeg-mignon-typewriter-1924":
            src = f"/home/paul/git/gemtexter/extras/html/fonts/{font_name}/zai_AEGMignonTypewriter1924.ttf"
            dst = theme_dir / f"{font_type}.ttf"
        else:
            src = f"/home/paul/git/gemtexter/extras/html/fonts/{font_name}/{font_name}.ttf"
            dst = theme_dir / f"{font_type}.ttf"
        
        try:
            shutil.copy(src, dst)
        except FileNotFoundError:
            # Try alternative path
            print(f"Warning: Could not find {src}")
    
    with open(theme_dir / "style.css", "w") as f:
        f.write(css_content)
    
    # Generate example.html
    example_html = f"""<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{theme_name.replace('_', ' ').title()} - Gemtexter Theme</title>
    <link rel="stylesheet" href="style.css" />
</head>
<body>
    <div class="header">
        <h1>{theme_name.replace('_', ' ').title()}</h1>
        <p>A {layout.replace('_', ' ')} layout with {colors['palette_type'].replace('_', ' ')} colors</p>
    </div>

    <div class="content">
        <h1>Welcome to {theme_name.replace('_', ' ').title()}</h1>
        <p>This theme features a carefully crafted {layout.replace('_', ' ')} layout with a {'dark' if colors['is_dark'] else 'light'} {colors['palette_type'].replace('_', ' ')} color scheme. The typography combines {fonts['heading'][2]} fonts for headings with {fonts['body'][2]} for body text.</p>

        <h2>Typography Showcase</h2>
        <p>The {fonts['body'][0].replace('_', ' ')} font family provides excellent readability for body text, while {fonts['heading'][0].replace('_', ' ')} adds character to headings. Code blocks use {fonts['code'][0].replace('_', ' ')} for clarity.</p>

        <h2>Color Palette</h2>
        <p>Primary: <span style="color: {colors['primary']}; font-weight: bold;">{colors['primary']}</span> | 
           Secondary: <span style="color: {colors['secondary']}; font-weight: bold;">{colors['secondary']}</span> | 
           Accent: <span style="color: {colors['accent']}; font-weight: bold;">{colors['accent']}</span></p>

        <h3>Interactive Elements</h3>
        <p>Links like <a href="#">this example</a> and longer <a href="#" class="textlink">text links that demonstrate the theme's navigation style</a> use the secondary color.</p>

        <div class="quote">
            "Design is not just what it looks like and feels like. Design is how it works." — Steve Jobs
        </div>

        <h3>Code Examples</h3>
        <p>Inline code like <code>theme.generate()</code> and larger blocks:</p>
        <pre>// Theme configuration
const theme = {{
    name: "{theme_name}",
    layout: "{layout}",
    colors: {{
        primary: "{colors['primary']}",
        secondary: "{colors['secondary']}",
        accent: "{colors['accent']}"
    }},
    fonts: {{
        heading: "{fonts['heading'][0]}",
        body: "{fonts['body'][0]}",
        code: "{fonts['code'][0]}"
    }}
}};</pre>

        <h2>Content Structure</h2>
        <ul>
            <li>Clean, readable typography with {font_sizes['base']}px base font size</li>
            <li>Heading scale ratio of {font_sizes['h1']}x for visual hierarchy</li>
            <li>Line height of {font_sizes['line_height']} for comfortable reading</li>
            <li>{layout.replace('_', ' ').title()} layout optimized for content flow</li>
            <li>{'Dark' if colors['is_dark'] else 'Light'} theme with {colors['palette_type'].replace('_', ' ')} color harmony</li>
        </ul>

        <h2>Font Licensing</h2>
        <p>All fonts used in this theme are properly licensed:</p>
        <ul>
            <li>{fonts['heading'][0]}: {fonts['heading'][1]} License</li>
            <li>{fonts['body'][0]}: {fonts['body'][1]} License</li>
            <li>{fonts['code'][0]}: {fonts['code'][1]} License</li>
        </ul>

        <h3>Final Thoughts</h3>
        <p>Every element of this theme has been carefully designed to create a harmonious reading experience. The {layout.replace('_', ' ')} layout ensures content is presented in an engaging way, while the color scheme provides the perfect backdrop for your words to shine.</p>

        <p>Whether you're writing technical documentation, creative prose, or anything in between, this theme adapts to showcase your content beautifully.</p>
    </div>
</body>
</html>"""
    
    with open(theme_dir / "example.html", "w") as f:
        f.write(example_html)
    
    # Generate LICENSE file
    license_content = f"""Theme: {theme_name}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Layout: {layout}
Color Scheme: {colors['palette_type']} ({'Dark' if colors['is_dark'] else 'Light'})

Font Licenses:
==============
Heading Font: {fonts['heading'][0]}
License: {fonts['heading'][1]}
Category: {fonts['heading'][2]}

Body Font: {fonts['body'][0]}
License: {fonts['body'][1]}
Category: {fonts['body'][2]}

Code Font: {fonts['code'][0]}
License: {fonts['code'][1]}
Category: {fonts['code'][2]}

All fonts are free for personal use.
"""
    
    with open(theme_dir / "LICENSE", "w") as f:
        f.write(license_content)
    
    return theme_name

def generate_screenshot(theme_name):
    """Generate a screenshot preview of the theme"""
    theme_dir = Path(f"/home/paul/git/gemtexter/extras/html/themes/{theme_name}")
    
    # Create a simple preview image using PIL
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to load theme colors from style.css
    with open(theme_dir / "style.css", "r") as f:
        css_content = f.read()
        
    # Extract colors from CSS
    import re
    bg_match = re.search(r'--color-bg:\s*([#\w]+);', css_content)
    primary_match = re.search(r'--color-primary:\s*([#\w]+);', css_content)
    
    if bg_match:
        try:
            bg_color = bg_match.group(1)
            img = Image.new('RGB', (400, 300), color=bg_color)
            draw = ImageDraw.Draw(img)
        except:
            pass
    
    # Add theme name
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 24)
    except:
        font = None
    
    text_color = 'black' if bg_match and bg_match.group(1).startswith('#f') else 'white'
    draw.text((20, 20), theme_name.replace('_', ' ').title(), fill=text_color, font=font)
    
    # Add some preview elements
    draw.rectangle((20, 60, 380, 62), fill=text_color)
    draw.text((20, 80), "Preview of theme layout", fill=text_color)
    
    # Save screenshot
    img.save(theme_dir.parent / "screenshots" / f"{theme_name}.png")

def main():
    """Generate 50 unique themes"""
    print("Generating 50 random themes...")
    
    themes = []
    used_names = set()
    
    # Ensure screenshots directory exists
    screenshots_dir = Path("/home/paul/git/gemtexter/extras/html/themes/screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    
    while len(themes) < 50:
        # Generate unique theme name
        theme_name = f"{random.choice(ADJECTIVES)}_{random.choice(NOUNS)}"
        if theme_name in used_names:
            continue
        used_names.add(theme_name)
        
        # Random font combination
        fonts = random.choice(FONT_COMBINATIONS)
        
        # Random color palette
        colors = generate_color_palette()
        
        # Random layout
        layout = random.choice(LAYOUTS)
        
        # Random font sizes
        font_sizes = generate_font_sizes()
        
        # Create theme
        try:
            created_theme = create_theme(theme_name, fonts, colors, layout, font_sizes)
            themes.append({
                'name': created_theme,
                'layout': layout,
                'colors': colors,
                'fonts': fonts
            })
            print(f"Created theme {len(themes)}/50: {created_theme}")
            
            # Generate screenshot
            generate_screenshot(created_theme)
        except Exception as e:
            print(f"Error creating theme {theme_name}: {e}")
    
    # Save theme metadata
    with open("/home/paul/git/gemtexter/extras/html/themes/themes_metadata.json", "w") as f:
        json.dump(themes, f, indent=2)
    
    print(f"\nSuccessfully created {len(themes)} themes!")
    return themes

if __name__ == "__main__":
    main()