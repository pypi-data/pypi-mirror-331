# FreePornVideos.xxx Scraper

A Python tool for scraping video URLs from FreePornVideos.xxx with anti-bot protection using Camoufox.

## Features

- Uses Camoufox for anti-fingerprinting and bot detection avoidance
- Modular architecture for easy maintenance and extension
- Typer-based CLI with rich error handling and progress indicators
- Extracts direct video URLs (preferring 720p quality when available)
- Follows redirects to get the final video URL
- Saves results to an output file
- Tracks and logs failed URLs

## Installation

This project uses [Rye](https://rye-up.com/) for dependency management.

```bash
# Clone the repository
git clone https://github.com/yourusername/freepornvideos-scraper.git
cd freepornvideos-scraper

# Install dependencies with Rye
rye sync
```

## Usage

### Command Line Interface

The script provides a Typer-based CLI with various options:

```bash
# Basic usage (will prompt for input file)
python -m freepornvideos_scraper

# Specify input and output files
python -m freepornvideos_scraper --input urls.txt --output results.txt

# Short form options
python -m freepornvideos_scraper -i urls.txt -o results.txt

# Run in headless mode (no browser UI)
python -m freepornvideos_scraper -i urls.txt --headless

# Route traffic through Tor (requires Tor running on port 9050)
python -m freepornvideos_scraper -i urls.txt --tor
```

### Input File Format

Create a text file with one FreePornVideos.xxx URL per line:

```
https://www.freepornvideos.xxx/videos/xxxxx/video-title-1/
https://www.freepornvideos.xxx/videos/yyyyy/video-title-2/
https://www.freepornvideos.xxx/videos/zzzzz/video-title-3/
```

### How It Works

The script will:

1. Load the URLs from the input file
2. Visit each URL with Camoufox browser
3. Click the play button on each page to load the video
4. Extract the direct video URL (preferring 720p quality)
5. Follow redirects to get the final video URL
6. Save the results to the specified output file
7. Create a separate file for any failed URLs

## Project Structure

The project has a modular architecture:

```
src/freepornvideos_scraper/
├── __init__.py
├── __main__.py          # Package entry point
├── scraper.py           # Main Typer CLI implementation
├── test_import.py       # Test utility
└── lib/                 # Core components
    ├── __init__.py
    ├── base.py          # Abstract base scraper class
    ├── scrapers/        # Site-specific scrapers
    │   ├── __init__.py
    │   └── freevideos.py # FreePornVideos implementation
    └── utils/           # Utility classes
        ├── __init__.py
        ├── camoufox_handler.py # Camoufox browser wrapper
        └── spoofing_config.py  # Anti-fingerprinting settings
```

## Requirements

- Python 3.8+
- camoufox (for browser automation with anti-fingerprinting)
- prompt-toolkit (for path completion in the CLI)
- requests (for following redirects)
- typer (for CLI interface)

## License

GPL-3.0
