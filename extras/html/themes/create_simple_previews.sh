#!/bin/bash

# Create simple preview images for themes using ImageMagick if available
# Falls back to creating placeholder files if ImageMagick is not installed

THEMES_DIR="/home/paul/git/gemtexter/extras/html/themes"
SCREENSHOTS_DIR="$THEMES_DIR/screenshots"

# Create screenshots directory if it doesn't exist
mkdir -p "$SCREENSHOTS_DIR"

# Check if ImageMagick is available
if command -v convert &> /dev/null; then
    echo "ImageMagick found, creating preview images..."
    
    # Generate preview for each theme
    for theme_dir in "$THEMES_DIR"/*; do
        if [ -d "$theme_dir" ] && [ "$theme_dir" != "$SCREENSHOTS_DIR" ]; then
            theme_name=$(basename "$theme_dir")
            
            # Skip non-theme directories
            if [[ "$theme_name" == "screenshots" ]] || [[ "$theme_name" == *".py" ]] || [[ "$theme_name" == *".sh" ]] || [[ "$theme_name" == *".html" ]]; then
                continue
            fi
            
            echo "Creating preview for $theme_name..."
            
            # Create a simple preview image with theme name
            convert -size 400x300 \
                -background '#f0f0f0' \
                -fill '#333333' \
                -gravity center \
                -pointsize 24 \
                -font Arial \
                label:"$theme_name\n\nTheme Preview" \
                "$SCREENSHOTS_DIR/${theme_name}.png"
        fi
    done
    
    echo "Preview images created!"
else
    echo "ImageMagick not found. Creating placeholder files..."
    
    # Create placeholder files
    for theme_dir in "$THEMES_DIR"/*; do
        if [ -d "$theme_dir" ] && [ "$theme_dir" != "$SCREENSHOTS_DIR" ]; then
            theme_name=$(basename "$theme_dir")
            
            # Skip non-theme directories
            if [[ "$theme_name" == "screenshots" ]] || [[ "$theme_name" == *".py" ]] || [[ "$theme_name" == *".sh" ]] || [[ "$theme_name" == *".html" ]]; then
                continue
            fi
            
            # Create an empty placeholder file
            touch "$SCREENSHOTS_DIR/${theme_name}.png"
        fi
    done
    
    echo "Placeholder files created. To generate actual previews, install ImageMagick:"
    echo "  sudo apt install imagemagick  # Debian/Ubuntu"
    echo "  sudo dnf install ImageMagick  # Fedora"
    echo "  brew install imagemagick      # macOS"
fi

echo "Done! Preview files are in $SCREENSHOTS_DIR"