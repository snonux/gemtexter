#!/usr/bin/env python3

import os
import re
from pathlib import Path

def hex_to_rgba(hex_color):
    """Convert hex color with alpha to rgba format"""
    if len(hex_color) == 9:  # #RRGGBBAA
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        a = int(hex_color[7:9], 16) / 255
        return f"rgba({r}, {g}, {b}, {a:.2f})"
    elif len(hex_color) == 5:  # #RGBA
        r = int(hex_color[1] * 2, 16)
        g = int(hex_color[2] * 2, 16)
        b = int(hex_color[3] * 2, 16)
        a = int(hex_color[4] * 2, 16) / 255
        return f"rgba({r}, {g}, {b}, {a:.2f})"
    return hex_color

def fix_css_file(css_path):
    """Fix CSS validation issues in a single file"""
    with open(css_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Fix hex colors with alpha channel (8 digits or 4 digits)
    # Match #RRGGBBAA or #RGBA patterns
    hex_alpha_pattern = r'#([0-9a-fA-F]{8}|[0-9a-fA-F]{4})\b'
    
    def replace_hex_alpha(match):
        return hex_to_rgba(match.group(0))
    
    content = re.sub(hex_alpha_pattern, replace_hex_alpha, content)
    
    # Fix color + percentage opacity patterns like {colors['text']}0A
    opacity_pattern = r'\{[^}]+\}([0-9A-Fa-f]{2})\b'
    content = re.sub(opacity_pattern, lambda m: f"rgba(0, 0, 0, {int(m.group(1), 16) / 255:.2f})", content)
    
    # Fix vendor prefixes - ensure they're properly formatted
    content = re.sub(r'-webkit-font-smoothing:\s*antialiased;', '-webkit-font-smoothing: antialiased;', content)
    content = re.sub(r'-moz-osx-font-smoothing:\s*grayscale;', '-moz-osx-font-smoothing: grayscale;', content)
    
    # Fix word-wrap (deprecated) to overflow-wrap
    content = re.sub(r'word-wrap:\s*break-word;', 'overflow-wrap: break-word;', content)
    
    # Fix any background-clip issues
    content = re.sub(r'-webkit-background-clip:\s*text;', '-webkit-background-clip: text;', content)
    content = re.sub(r'background-clip:\s*text;', '', content)  # Remove non-webkit background-clip: text
    
    # Fix -webkit-text-fill-color
    content = re.sub(r'-webkit-text-fill-color:\s*transparent;', '-webkit-text-fill-color: transparent;', content)
    
    # Ensure proper CSS comments
    content = re.sub(r'/\*([^*]|\*[^/])*\*/', lambda m: m.group(0), content)
    
    # Fix @import statements if they exist
    content = re.sub(r'@import\s+url\([\'"]([^\'")]+)[\'"]\)([^;]*);', r'@import url("\1")\2;', content)
    
    # Fix any remaining color notations that might be invalid
    # Look for patterns like #0f01 and convert to rgba
    short_alpha_pattern = r'#([0-9a-fA-F]{3})([0-9a-fA-F]{1})\b'
    
    def replace_short_alpha(match):
        rgb = match.group(1)
        alpha = match.group(2)
        r = int(rgb[0] * 2, 16)
        g = int(rgb[1] * 2, 16)
        b = int(rgb[2] * 2, 16)
        a = int(alpha * 2, 16) / 255
        return f"rgba({r}, {g}, {b}, {a:.2f})"
    
    content = re.sub(short_alpha_pattern, replace_short_alpha, content)
    
    # Ensure all font-family declarations have proper fallbacks
    content = re.sub(r'font-family:\s*([\'"]?)text\1,\s*sans-serif;', 'font-family: text, sans-serif;', content)
    content = re.sub(r'font-family:\s*([\'"]?)heading\1,\s*serif;', 'font-family: heading, serif;', content)
    content = re.sub(r'font-family:\s*([\'"]?)code\1,\s*monospace;', 'font-family: code, monospace;', content)
    content = re.sub(r'font-family:\s*([\'"]?)handnotes\1,\s*cursive;', 'font-family: handnotes, cursive;', content)
    
    # Fix any clip-path issues
    content = re.sub(r'clip-path:\s*polygon\(([^)]+)\);', lambda m: f'clip-path: polygon({m.group(1)});', content)
    
    # Fix multi-line background declarations
    # Find patterns where background or background-image spans multiple lines
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Check if this line contains background/background-image without semicolon
        if ('background:' in line or 'background-image:' in line) and not line.strip().endswith(';'):
            # Collect all lines until we find a semicolon
            combined_line = line
            i += 1
            while i < len(lines) and not lines[i-1].strip().endswith(';'):
                combined_line += ' ' + lines[i].strip()
                i += 1
            fixed_lines.append(combined_line)
        else:
            fixed_lines.append(line)
            i += 1
    
    content = '\n'.join(fixed_lines)
    
    # Fix specific SVG data URLs in background-image
    content = re.sub(r'background-image:\s*url\(\'data:image/svg\+xml;utf8,([^\']+)\'\)\s*,', 
                     r"background-image: url('data:image/svg+xml;utf8,\1'),", content)
    
    # Fix text-shadow and box-shadow declarations spanning multiple lines
    content = re.sub(r'text-shadow:\s*\n\s*', 'text-shadow: ', content)
    content = re.sub(r'box-shadow:\s*\n\s*', 'box-shadow: ', content)
    
    # Write back only if changes were made
    if content != original_content:
        with open(css_path, 'w') as f:
            f.write(content)
        return True
    return False

def fix_all_themes():
    """Fix CSS validation issues in all theme files"""
    themes_dir = Path("/home/paul/git/gemtexter/extras/html/themes")
    fixed_count = 0
    
    # Get all theme directories
    theme_dirs = [d for d in themes_dir.iterdir() if d.is_dir() and d.name not in ['screenshots', '.git']]
    
    print(f"Fixing CSS validation issues in {len(theme_dirs)} themes...")
    
    for theme_dir in theme_dirs:
        css_file = theme_dir / "style.css"
        if css_file.exists():
            if fix_css_file(css_file):
                fixed_count += 1
                print(f"Fixed: {theme_dir.name}")
            else:
                print(f"No fixes needed: {theme_dir.name}")
        
        # Also check for override CSS files
        for override_css in theme_dir.glob("*-override.css"):
            if fix_css_file(override_css):
                print(f"Fixed override: {override_css.name}")
    
    print(f"\nFixed {fixed_count} theme CSS files")
    
    # Also fix the main theme CSS files if they exist
    main_themes = ["default", "simple", "business", "future", "retrosimple"]
    for theme_name in main_themes:
        theme_css = themes_dir / theme_name / "style.css"
        if theme_css.exists():
            if fix_css_file(theme_css):
                print(f"Fixed main theme: {theme_name}")

def validate_css_syntax(css_path):
    """Basic CSS syntax validation"""
    with open(css_path, 'r') as f:
        content = f.read()
    
    issues = []
    
    # Check for unclosed brackets
    open_braces = content.count('{')
    close_braces = content.count('}')
    if open_braces != close_braces:
        issues.append(f"Mismatched braces: {open_braces} open, {close_braces} close")
    
    # Check for missing semicolons (basic check)
    lines = content.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if line and not line.startswith('/*') and not line.endswith(('{', '}', ';', '*/')):
            if ':' in line and not line.startswith('@'):
                issues.append(f"Line {i+1}: Missing semicolon? '{line}'")
    
    return issues

if __name__ == "__main__":
    fix_all_themes()
    
    # Optional: Run basic validation
    print("\nRunning basic CSS validation...")
    themes_dir = Path("/home/paul/git/gemtexter/extras/html/themes")
    theme_dirs = [d for d in themes_dir.iterdir() if d.is_dir() and d.name not in ['screenshots', '.git']]
    
    for theme_dir in theme_dirs:
        css_file = theme_dir / "style.css"
        if css_file.exists():
            issues = validate_css_syntax(css_file)
            if issues:
                print(f"\n{theme_dir.name}:")
                for issue in issues:
                    print(f"  - {issue}")