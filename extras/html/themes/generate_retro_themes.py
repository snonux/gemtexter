#!/usr/bin/env python3

import os
import random
import colorsys
from pathlib import Path
import shutil
from datetime import datetime
import json

# Retro/Retro-futuristic theme names
RETRO_ADJECTIVES = [
    "neon", "cyber", "retro", "vintage", "classic", "terminal", "matrix",
    "synthwave", "vaporwave", "outrun", "arcade", "pixel", "digital",
    "analog", "chrome", "laser", "hologram", "circuit", "grid", "vector",
    "mainframe", "quantum", "atomic", "cosmic", "stellar", "binary",
    "monochrome", "phosphor", "cathode", "vacuum", "transistor", "silicon",
    "electric", "magnetic", "plasma", "photon", "neutron", "fusion",
    "console", "command", "system", "kernel", "daemon", "process"
]

RETRO_NOUNS = [
    "terminal", "console", "system", "grid", "wave", "pulse", "beam",
    "drive", "core", "matrix", "nexus", "portal", "gateway", "interface",
    "station", "deck", "hub", "node", "cluster", "array", "circuit",
    "module", "unit", "engine", "reactor", "chamber", "sphere", "cube",
    "prism", "crystal", "void", "dimension", "reality", "simulation",
    "cyberspace", "mainframe", "database", "network", "protocol", "stream",
    "buffer", "cache", "memory", "processor", "compiler", "runtime"
]

# Retro color palettes
RETRO_PALETTES = [
    # Classic terminal green
    {
        "name": "terminal_green",
        "background": "#000000",
        "text": "#00ff00",
        "primary": "#00ff00",
        "secondary": "#00cc00",
        "accent": "#00ff88",
        "glow": "#00ff0033"
    },
    # Amber CRT
    {
        "name": "amber_crt",
        "background": "#0a0400",
        "text": "#ffb000",
        "primary": "#ff9500",
        "secondary": "#ff7700",
        "accent": "#ffc500",
        "glow": "#ff950033"
    },
    # Synthwave purple/pink
    {
        "name": "synthwave",
        "background": "#0a0014",
        "text": "#ff00ff",
        "primary": "#ff00ff",
        "secondary": "#00ffff",
        "accent": "#ff00aa",
        "glow": "#ff00ff33"
    },
    # Retro blue CRT
    {
        "name": "blue_crt",
        "background": "#000014",
        "text": "#00ccff",
        "primary": "#0099ff",
        "secondary": "#00ddff",
        "accent": "#00ffff",
        "glow": "#00ccff33"
    },
    # Classic white on blue
    {
        "name": "dos_classic",
        "background": "#0000aa",
        "text": "#ffffff",
        "primary": "#ffff00",
        "secondary": "#00ffff",
        "accent": "#ff00ff",
        "glow": "#ffffff22"
    },
    # Matrix green
    {
        "name": "matrix",
        "background": "#000000",
        "text": "#00ff41",
        "primary": "#00ff41",
        "secondary": "#008f11",
        "accent": "#00ff00",
        "glow": "#00ff4133"
    },
    # Cyberpunk neon
    {
        "name": "cyberpunk",
        "background": "#0a0012",
        "text": "#e5ccff",
        "primary": "#ff0090",
        "secondary": "#00f0ff",
        "accent": "#ffee00",
        "glow": "#ff009033"
    },
    # Retro orange
    {
        "name": "retro_orange",
        "background": "#1a0f00",
        "text": "#ff6600",
        "primary": "#ff3300",
        "secondary": "#ff9900",
        "accent": "#ffcc00",
        "glow": "#ff660033"
    },
    # Phosphor white
    {
        "name": "phosphor",
        "background": "#000000",
        "text": "#e0e0e0",
        "primary": "#ffffff",
        "secondary": "#cccccc",
        "accent": "#aaaaaa",
        "glow": "#ffffff22"
    },
    # Vapor pink
    {
        "name": "vapor",
        "background": "#1a0014",
        "text": "#ff99cc",
        "primary": "#ff66cc",
        "secondary": "#cc99ff",
        "accent": "#ffccff",
        "glow": "#ff66cc33"
    }
]

# Font combinations for retro themes
RETRO_FONTS = [
    {"heading": "hack", "body": "hack", "code": "hack"},
    {"heading": "consola-mono", "body": "consola-mono", "code": "consola-mono"},
    {"heading": "intelone-mono", "body": "intelone-mono", "code": "intelone-mono"},
    {"heading": "hack", "body": "intelone-mono", "code": "consola-mono"},
    {"heading": "pixelon", "body": "hack", "code": "consola-mono"},
    {"heading": "repetition-scrolling", "body": "hack", "code": "hack"},
    {"heading": "zai-aeg-mignon-typewriter-1924", "body": "consola-mono", "code": "hack"},
    {"heading": "higher-jump", "body": "hack", "code": "intelone-mono"},
]

# Retro CSS effects and layouts
def generate_retro_css(theme_name, colors, fonts, effect_type):
    """Generate retro-themed CSS with various effects"""
    
    css = f"""/* Retro Theme: {theme_name} */
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
    --color-bg: {colors['background']};
    --color-text: {colors['text']};
    --color-primary: {colors['primary']};
    --color-secondary: {colors['secondary']};
    --color-accent: {colors['accent']};
    --color-glow: {colors['glow']};
}}

* {{
    box-sizing: border-box;
}}

html {{
    font-size: 16px;
    background-color: var(--color-bg);
    min-height: 100vh;
}}
"""

    # Add retro background effects
    if effect_type == "scanlines":
        css += """
html::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(255, 255, 255, 0.03) 2px,
        rgba(255, 255, 255, 0.03) 4px
    );
    pointer-events: none;
    z-index: 1;
}
"""
    elif effect_type == "grid":
        css += f"""
html {{
    background-image: 
        linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
    background-size: 20px 20px;
    background-position: -1px -1px;
}}
"""
    elif effect_type == "dots":
        css += f"""
html {{
    background-image: radial-gradient(circle, {colors['glow']} 1px, transparent 1px);
    background-size: 20px 20px;
}}
"""
    elif effect_type == "crt":
        css += """
@keyframes flicker {
    0% { opacity: 0.97; }
    100% { opacity: 1; }
}

html::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: repeating-linear-gradient(
        0deg,
        rgba(0, 0, 0, 0.15),
        rgba(0, 0, 0, 0.15) 1px,
        transparent 1px,
        transparent 2px
    );
    pointer-events: none;
    z-index: 1;
    animation: flicker 0.15s infinite;
}
"""

    # Body styles - single column, minimum 1200px
    css += f"""
body {{
    font-family: text, monospace;
    background-color: var(--color-bg);
    color: var(--color-text);
    line-height: 1.6;
    margin: 0 auto;
    padding: 2em;
    min-width: 1200px;
    max-width: 1400px;
    position: relative;
    overflow-x: auto;
}}

/* Retro glow effect */
body::before {{
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(ellipse at center, transparent 0%, var(--color-bg) 100%);
    pointer-events: none;
    z-index: 2;
}}

/* Content wrapper */
.content {{
    position: relative;
    z-index: 3;
    width: 100%;
    min-width: 1200px;
}}

/* Headers with retro styling */
h1, h2, h3 {{
    font-family: heading, monospace;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 1.5em 0 0.5em 0;
    position: relative;
}}

h1 {{
    font-size: 2.5em;
    color: var(--color-primary);
    text-shadow: 
        0 0 10px var(--color-glow),
        0 0 20px var(--color-glow),
        0 0 30px var(--color-glow);
    border-bottom: 2px solid var(--color-primary);
    padding-bottom: 0.5em;
}}
"""

    # Add terminal-specific styles
    if "terminal" in theme_name or effect_type == "terminal":
        css += """
h1::before {
    content: "$ ";
    color: var(--color-secondary);
}

h2 {
    font-size: 1.8em;
    color: var(--color-secondary);
}

h2::before {
    content: "> ";
    color: var(--color-accent);
}

h3 {
    font-size: 1.4em;
    color: var(--color-accent);
}

h3::before {
    content: "# ";
    color: var(--color-secondary);
}

/* Terminal cursor effect */
@keyframes blink {
    0%, 49% { opacity: 1; }
    50%, 100% { opacity: 0; }
}

h1::after {
    content: "_";
    animation: blink 1s infinite;
    color: var(--color-primary);
}
"""
    else:
        css += """
h2 {
    font-size: 1.8em;
    color: var(--color-secondary);
    text-shadow: 0 0 5px var(--color-glow);
}

h3 {
    font-size: 1.4em;
    color: var(--color-accent);
}
"""

    # Common styles
    css += f"""
/* Links with retro hover effects */
a {{
    font-family: code, monospace;
    color: var(--color-secondary);
    text-decoration: none;
    position: relative;
    transition: all 0.3s ease;
}}

a:hover {{
    color: var(--color-accent);
    text-shadow: 0 0 5px var(--color-glow);
}}

a::after {{
    content: "";
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 0;
    height: 2px;
    background: var(--color-accent);
    transition: width 0.3s ease;
}}

a:hover::after {{
    width: 100%;
}}

/* Text link styling */
.textlink {{
    font-family: text, monospace;
}}

/* Quotes with retro border */
.quote {{
    font-family: handnotes, monospace;
    border-left: 4px solid var(--color-accent);
    border-right: 4px solid var(--color-accent);
    padding: 1em 2em;
    margin: 2em 0;
    background-color: rgba(255, 255, 255, 0.02);
    font-style: italic;
    position: relative;
}}

.quote::before,
.quote::after {{
    content: '"';
    font-size: 3em;
    color: var(--color-accent);
    position: absolute;
    opacity: 0.3;
}}

.quote::before {{
    top: -0.2em;
    left: 0.1em;
}}

.quote::after {{
    bottom: -0.5em;
    right: 0.1em;
}}

/* Code blocks with terminal styling */
pre {{
    font-family: code, monospace;
    background-color: rgba(0, 0, 0, 0.5);
    border: 1px solid var(--color-primary);
    padding: 1.5em;
    overflow-x: auto;
    margin: 2em 0;
    box-shadow: 
        inset 0 0 20px rgba(0, 0, 0, 0.5),
        0 0 10px var(--color-glow);
    position: relative;
}}

pre::before {{
    content: "OUTPUT";
    position: absolute;
    top: -0.5em;
    left: 1em;
    background: var(--color-bg);
    padding: 0 0.5em;
    color: var(--color-primary);
    font-size: 0.8em;
    letter-spacing: 0.2em;
}}

code {{
    font-family: code, monospace;
    color: var(--color-accent);
}}

/* Lists with retro bullets */
ul {{
    list-style: none;
    padding-left: 2em;
}}

ul li::before {{
    content: "▸ ";
    color: var(--color-accent);
    font-weight: bold;
    margin-left: -1.5em;
    margin-right: 0.5em;
}}

/* Images */
img {{
    max-width: 100%;
    height: auto;
    filter: contrast(1.1) brightness(0.9);
    border: 2px solid var(--color-primary);
}}

/* Horizontal rules */
hr {{
    border: none;
    height: 2px;
    background: linear-gradient(90deg, 
        transparent 0%, 
        var(--color-primary) 20%, 
        var(--color-primary) 80%, 
        transparent 100%);
    margin: 3em 0;
    position: relative;
}}

hr::after {{
    content: "◆";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: var(--color-bg);
    color: var(--color-primary);
    padding: 0 1em;
    font-size: 1.5em;
}}

/* Paragraphs */
p {{
    margin: 1em 0;
    text-align: justify;
    hyphens: auto;
}}

/* Special retro effects */
@keyframes glitch {{
    0%, 100% {{ text-shadow: 0 0 5px var(--color-glow); }}
    25% {{ text-shadow: -2px 0 var(--color-accent), 2px 0 var(--color-secondary); }}
    50% {{ text-shadow: 2px 0 var(--color-accent), -2px 0 var(--color-secondary); }}
    75% {{ text-shadow: 0 0 10px var(--color-glow); }}
}}

h1:hover {{
    animation: glitch 0.3s infinite;
}}

/* Footer styling */
.footer {{
    margin-top: 4em;
    padding-top: 2em;
    border-top: 2px solid var(--color-primary);
    text-align: center;
    color: var(--color-secondary);
    font-size: 0.9em;
    letter-spacing: 0.1em;
}}
"""

    return css

def create_retro_theme(theme_name, palette, fonts, effect_type):
    """Create a complete retro theme"""
    theme_dir = Path(f"/home/paul/git/gemtexter/extras/html/themes/{theme_name}")
    theme_dir.mkdir(exist_ok=True)
    
    # Generate CSS
    css_content = generate_retro_css(theme_name, palette, fonts, effect_type)
    with open(theme_dir / "style.css", "w") as f:
        f.write(css_content)
    
    # Copy fonts
    font_map = {
        "heading": fonts["heading"],
        "text": fonts["body"],
        "code": fonts["code"],
        "handnotes": "hack"  # Default for quotes
    }
    
    for font_type, font_name in font_map.items():
        src_candidates = [
            f"/home/paul/git/gemtexter/extras/html/fonts/{font_name}/Hack-Regular.ttf",
            f"/home/paul/git/gemtexter/extras/html/fonts/{font_name}/ConsolaMono-Book.ttf",
            f"/home/paul/git/gemtexter/extras/html/fonts/{font_name}/intelone-mono-font-family-regular.ttf",
            f"/home/paul/git/gemtexter/extras/html/fonts/{font_name}/Pixelon.ttf",
            f"/home/paul/git/gemtexter/extras/html/fonts/{font_name}/repet___.ttf",
            f"/home/paul/git/gemtexter/extras/html/fonts/{font_name}/zai_AEGMignonTypewriter1924.ttf",
            f"/home/paul/git/gemtexter/extras/html/fonts/{font_name}/Higher Jump.ttf",
            f"/home/paul/git/gemtexter/extras/html/fonts/{font_name}/{font_name}.ttf"
        ]
        
        for src in src_candidates:
            if os.path.exists(src):
                dst = theme_dir / f"{font_type}.ttf"
                shutil.copy(src, dst)
                break
    
    # Create theme.conf
    theme_conf = f"""declare -xr HTML_HEADER=./extras/html/header.html.part
declare -xr HTML_FOOTER=./extras/html/footer.html.part
declare -xr HTML_CSS_STYLE=$HTML_THEME_DIR/style.css
declare -xr HTML_WEBFONT_HEADING=$HTML_THEME_DIR/heading.ttf
declare -xr HTML_WEBFONT_TEXT=$HTML_THEME_DIR/text.ttf
declare -xr HTML_WEBFONT_CODE=$HTML_THEME_DIR/code.ttf
declare -xr HTML_WEBFONT_HANDNOTES=$HTML_THEME_DIR/handnotes.ttf
declare -xr SOURCE_HIGHLIGHT_CSS=./extras/html/source-highlight-styles/neon.css
"""
    
    with open(theme_dir / "theme.conf", "w") as f:
        f.write(theme_conf)
    
    # Create example.html
    example_html = f"""<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{theme_name.replace('_', ' ').upper()} :: RETRO THEME</title>
    <link rel="stylesheet" href="style.css" />
</head>
<body>
    <div class="content">
        <h1>SYSTEM: {theme_name.replace('_', ' ').upper()}</h1>
        
        <p>Welcome to the {palette['name'].replace('_', ' ')} retro theme. This single-column layout features a minimum width of 1200px for optimal viewing on modern displays while maintaining that classic retro aesthetic.</p>
        
        <h2>INTERFACE ELEMENTS</h2>
        
        <p>This theme combines {"monospace fonts" if "terminal" in theme_name else "retro-futuristic typography"} with a carefully crafted color palette inspired by {"classic computer terminals" if "terminal" in effect_type else "retro computing aesthetics"}.</p>
        
        <h3>FEATURES</h3>
        
        <ul>
            <li>Single column layout optimized for readability</li>
            <li>Minimum 1200px width for modern displays</li>
            <li>{"CRT scanline effects" if effect_type == "scanlines" else "Retro visual effects"}</li>
            <li>Monospace typography throughout</li>
            <li>High contrast color scheme</li>
        </ul>
        
        <h2>CODE DISPLAY</h2>
        
        <p>Execute commands with style. Inline code like <code>theme --activate {theme_name}</code> stands out clearly.</p>
        
        <pre>// THEME CONFIGURATION
const retroTheme = {{
    name: "{theme_name}",
    style: "{palette['name']}",
    effect: "{effect_type}",
    width: "1200px",
    initialized: true
}};

console.log("Theme loaded successfully");</pre>
        
        <h3>NAVIGATION</h3>
        
        <p>Navigate through the system with <a href="#">hyperlinks</a> that glow on hover. Longer <a href="#" class="textlink">text-based navigation links demonstrate the retro hover effects</a>.</p>
        
        <div class="quote">
            "The future is already here — it's just not evenly distributed." Experience the aesthetics of retro computing with modern web standards.
        </div>
        
        <h2>VISUAL STYLE</h2>
        
        <p>The {effect_type} effect {"creates authentic scanlines reminiscent of CRT monitors" if effect_type == "scanlines" else "adds visual depth to the interface"}. Every element has been carefully styled to evoke the golden age of computing.</p>
        
        <hr />
        
        <h3>SYSTEM STATUS</h3>
        
        <ul>
            <li>Theme Engine: ACTIVE</li>
            <li>Visual Effects: ENABLED</li>
            <li>Glow Intensity: OPTIMAL</li>
            <li>Contrast Ratio: HIGH</li>
            <li>Readability: MAXIMUM</li>
        </ul>
        
        <p>This retro theme brings together the best of classic computing aesthetics with modern web technologies. The single-column layout ensures content remains focused and readable, while the 1200px minimum width takes advantage of contemporary display resolutions.</p>
        
        <div class="footer">
            SYSTEM THEME :: {theme_name.upper()} :: RETRO FUTURISTIC DESIGN
        </div>
    </div>
</body>
</html>"""
    
    with open(theme_dir / "example.html", "w") as f:
        f.write(example_html)
    
    # Create LICENSE
    license_content = f"""Theme: {theme_name}
Style: Retro/Retro-futuristic
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Color Palette: {palette['name']}
Effect Type: {effect_type}
Layout: Single Column (min-width: 1200px)

Font Licenses:
==============
All monospace fonts used are free for personal use.
- Hack: MIT License
- Consola Mono: SIL Open Font License
- Intel One Mono: Open Font License
- Other retro fonts: Free for personal use

This theme is designed for modern displays while maintaining
a classic retro computing aesthetic.
"""
    
    with open(theme_dir / "LICENSE", "w") as f:
        f.write(license_content)
    
    return theme_name

def main():
    print("Generating 50 retro/retro-futuristic themes...")
    
    # Clean up existing themes (except original ones)
    themes_dir = Path("/home/paul/git/gemtexter/extras/html/themes")
    original_themes = ["default", "simple", "business", "future", "retrosimple"]
    
    for theme_dir in themes_dir.iterdir():
        if theme_dir.is_dir() and theme_dir.name not in original_themes + ["screenshots"]:
            shutil.rmtree(theme_dir)
    
    # Generate 50 new retro themes
    themes = []
    effect_types = ["scanlines", "grid", "dots", "crt", "terminal", "none"]
    
    for i in range(50):
        # Generate unique name
        adj = random.choice(RETRO_ADJECTIVES)
        noun = random.choice(RETRO_NOUNS)
        theme_name = f"{adj}_{noun}"
        
        # Ensure uniqueness
        while theme_name in [t['name'] for t in themes]:
            adj = random.choice(RETRO_ADJECTIVES)
            noun = random.choice(RETRO_NOUNS)
            theme_name = f"{adj}_{noun}"
        
        # Select palette and fonts
        palette = random.choice(RETRO_PALETTES).copy()
        fonts = random.choice(RETRO_FONTS)
        effect_type = random.choice(effect_types)
        
        # Force terminal effect for terminal-themed names
        if "terminal" in theme_name or "console" in theme_name or "command" in theme_name:
            effect_type = "terminal"
        
        # Create theme
        created_name = create_retro_theme(theme_name, palette, fonts, effect_type)
        
        themes.append({
            'name': created_name,
            'palette': palette['name'],
            'effect': effect_type,
            'fonts': fonts
        })
        
        print(f"Created theme {i+1}/50: {created_name} ({palette['name']}, {effect_type})")
    
    # Save metadata
    with open(themes_dir / "retro_themes_metadata.json", "w") as f:
        json.dump(themes, f, indent=2)
    
    print("\nSuccessfully generated 50 retro themes!")
    print("All themes feature:")
    print("- Single column layout")
    print("- Minimum 1200px width")
    print("- Retro/retro-futuristic styling")
    print("- Various terminal and CRT effects")

if __name__ == "__main__":
    main()