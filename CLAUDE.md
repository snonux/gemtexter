# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Gemtexter is a static site generator and blog engine written in GNU Bash that converts Gemini Gemtext format into multiple output formats (HTML, Markdown, Atom feeds). It's intentionally written in Bash to explore the maintainability of larger Bash scripts.

## Development Commands

### Core Commands
- `./gemtexter --generate [filter]` - Generate all output formats (optional regex filter)
- `./gemtexter --template` - Process template files only
- `./gemtexter --feed` - Generate Atom feeds and Gemfeeds only
- `./gemtexter --html-theme` - Process HTML theme files
- `./gemtexter --draft` - Generate draft content

### Testing and Verification
- `./gemtexter --test` - Run ShellCheck and unit tests
- `./gemtexter --verify` - Verify Atom feed syntax with XMLLint

### Git Integration
- `./gemtexter --git-add` - Add all changes to Git
- `./gemtexter --git-sync` - Sync with remote repositories
- `./gemtexter --publish` - Full workflow: generate → verify → git add → git sync

### Publishing Blog Posts
1. Create new file: `$CONTENT_BASE_DIR/gemtext/gemfeed/YYYY-MM-DD-title.gmi`
2. First level 1 title (`# Title`) becomes the displayed link name
3. Gemtexter adds `> Published at TIMESTAMP` automatically
4. Run `./gemtexter --generate` to update all indices and feeds

## Architecture

### Module Structure
The codebase is organized into library modules in `lib/`:
- `generate.source.sh` - Core conversion logic (Gemtext → HTML/Markdown)
- `atomfeed.source.sh` - Atom feed generation
- `gemfeed.source.sh` - Gemini feed management
- `html.source.sh` - HTML-specific generation
- `md.source.sh` - Markdown-specific generation
- `template.source.sh` - Template processing engine
- `git.source.sh` - Git integration
- `log.source.sh` - Logging utilities
- `assert.source.sh` - Testing utilities

### Content Structure
```
$CONTENT_BASE_DIR/
├── gemtext/    # Source Gemtext files (edit these)
├── html/       # Generated HTML output
├── md/         # Generated Markdown output
└── cache/      # Temporary feed generation cache
```

### Configuration
Main configuration file: `gemtexter.conf`
- Can be overridden by `~/.config/gemtexter.conf`
- Or via `CONFIG_FILE_PATH` environment variable

Key variables:
- `DOMAIN` - Site domain
- `CONTENT_BASE_DIR` - Base directory for content (default: ../foo.zone-content)
- `HTML_THEME_DIR` - HTML theme directory
- `ATOM_MAX_ENTRIES` - Feed entry limit
- `PRE_GENERATE_HOOK`, `POST_PUBLISH_HOOK` - Custom hooks

### Templating System
- Template files: `.gmi.tpl` extension
- Single-line templates: `<< command`
- Multi-line templates: `<<< ... >>>`
- Built-in functions:
  - `<< template::inline::index keyword1 keyword2` - Generate index of matching posts
  - `<< template::inline::rindex keyword1 keyword2` - Reverse sorted index
  - `<< template::inline::toc` - Generate table of contents

## Key Implementation Details

### File Generation Flow
1. Source files are read from `gemtext/` directory
2. Templates (`.gmi.tpl`) are processed first
3. Gemtext is converted to target formats using sed-based transformations
4. Special handling for:
   - Code blocks with syntax highlighting (requires GNU Source Highlight)
   - Image files (copied directly)
   - Atom feed generation for blog posts
   - Git integration for version control

### Blog Post Detection
- Files matching `gemfeed/YYYY-MM-DD-*.gmi` are treated as blog posts
- Automatically added to indices and Atom feeds
- Timestamp management via `> Published at` line

### HTML Generation Specifics
- XHTML Transitional 1.0 output
- Theme support via `HTML_THEME_DIR`
- Mastodon verification support via `MASTODON_URI`
- Source code highlighting with configurable CSS themes
- Special files preserved: `.domains`, `robots.txt`

### Markdown Generation Specifics
- GitHub/Codeberg Pages compatible
- Preserves `_config.yml` and `CNAME` files
- Links adjusted for web viewing

## Testing Approach
- Static analysis with ShellCheck
- Unit test functions in library modules
- Atom feed validation with XMLLint
- Run all tests: `./gemtexter --test`