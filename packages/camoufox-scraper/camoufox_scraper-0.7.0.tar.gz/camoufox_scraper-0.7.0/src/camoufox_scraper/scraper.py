"""FreePornVideos.xxx Scraper main entry point."""

import logging
import os
import time
from enum import Enum
from pathlib import Path
from typing import Optional

import typer
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter

from camoufox_scraper.lib.factory import ScraperFactory

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("freepornvideos-scraper")

# Create Typer app
app = typer.Typer(
    help="Video Scraper - Extract direct video URLs from various adult websites",
    add_completion=False
)


class ScraperName(str, Enum):
    """Supported scraper types."""
    FREEVIDEOS = "freevideos"


def get_input_file_path() -> str:
    """
    Prompt the user to enter a path to the input file with URL completion.
    
    Returns:
        Selected file path
    """
    # Get the current working directory to use as default path
    current_dir = os.getcwd()
    file_completer = PathCompleter(get_paths=lambda: [current_dir])
    
    while True:
        try:
            file_path = prompt(
                "Enter path to file containing URLs: ",
                completer=file_completer
            )
            
            path = Path(file_path)
            if not path.exists():
                logger.error(f"File does not exist: {file_path}")
                continue
                
            if not path.is_file():
                logger.error(f"Not a file: {file_path}")
                continue
                
            return file_path
            
        except KeyboardInterrupt:
            logger.info("Operation cancelled")
            raise
        except Exception as e:
            logger.error(f"Error: {e}")


@app.command()
def scrape(
    scraper_name: ScraperName = typer.Argument(
        ScraperName.FREEVIDEOS, 
        help="Name of the scraper to use"
    ),
    input_file: Optional[str] = typer.Option(
        None, "--input", "-i", 
        help="Path to file containing URLs (one per line)"
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", 
        help="Path to save extracted URLs"
    ),
    tor: bool = typer.Option(
        False, "--tor", 
        help="Route traffic through Tor proxy"
    ),
    concurrency: int = typer.Option(
        1, "--concurrency", "-c",
        help="Number of URLs to process concurrently (default: 1)"
    ),
) -> None:
    """
    Scrape video URLs from adult websites.
    
    This will process each URL in the input file, visit the page,
    play the video, and extract the direct video URL.
    """
    try:
        logger.info(f"Starting scraper: {scraper_name}")
        
        # Get the input file path if not provided
        if not input_file:
            input_file = get_input_file_path()
        else:
            # Validate input file
            path = Path(input_file)
            if not path.exists() or not path.is_file():
                logger.error(f"Invalid input file: {input_file}")
                raise typer.Exit(code=1)
        
        logger.info(f"Using input file: {input_file}")
        
        # Get output file path if not provided
        if not output_file:
            output_file = os.path.join(
                os.path.dirname(input_file),
                f"extracted_urls_{int(time.time())}.txt"
            )
        
        logger.info(f"Output will be saved to: {output_file}")
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        # Create and run the scraper
        try:
            # Validate concurrency
            if concurrency < 1:
                logger.warning(f"Invalid concurrency value: {concurrency}, using 1 instead")
                concurrency = 1
            
            scraper = ScraperFactory.create_scraper(
                scraper_name=scraper_name, 
                headless=False, 
                tor_proxy=tor
            )
            
            # Set concurrency
            scraper.concurrency = concurrency
            logger.info(f"Using concurrency: {concurrency}")
            
            logger.info("Initializing browser")
            
            # Just run the scraper directly - it handles its own browser initialization
            results = scraper.run(input_file, output_file)
            
            # Display summary
            if results["success"]:
                typer.echo(typer.style("\n✅ Scraping completed successfully", fg=typer.colors.GREEN, bold=True))
                typer.echo(f"   Processed URLs: {results['processed']}")
                typer.echo(f"   Extracted URLs: {results['extracted']}")
                typer.echo(f"   Failed URLs: {results['failed']}")
                typer.echo(f"   Output file: {results['output_file']}")
                if results["failed_file"]:
                    typer.echo(f"   Failed URLs file: {results['failed_file']}")
            else:
                typer.echo(typer.style("\n❌ Scraping failed", fg=typer.colors.RED, bold=True))
                if "error" in results and results["error"]:
                    typer.echo(typer.style(f"   Error: {results['error']}", fg=typer.colors.RED))
        except RuntimeError as e:
            logger.error(f"Runtime error: {str(e)}")
            typer.echo(typer.style(f"\n❌ Runtime error: {str(e)}", fg=typer.colors.RED, bold=True))
            raise typer.Exit(code=1)
        except TimeoutError as e:
            logger.error(f"Timeout error: {str(e)}")
            typer.echo(typer.style(f"\n❌ Timeout error: {str(e)}", fg=typer.colors.RED, bold=True))
            typer.echo("\nTips to fix this issue:")
            typer.echo("1. Check your internet connection")
            typer.echo("2. Make sure Tor service is running if using the --tor option")
            typer.echo("3. Try again later as the site might be temporarily blocking requests")
            raise typer.Exit(code=1)
    except KeyboardInterrupt:
        logger.info("Scraper stopped by user")
        typer.echo(typer.style("\n⚠️ Scraper stopped by user", fg=typer.colors.YELLOW, bold=True))
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}")
        typer.echo(typer.style(f"\n❌ Error: {str(e)}", fg=typer.colors.RED, bold=True))
        raise typer.Exit(code=1)


@app.command()
def list_scrapers():
    """List all available scrapers."""
    scrapers = ScraperFactory.get_available_scrapers()
    typer.echo("Available scrapers:")
    for scraper in scrapers:
        typer.echo(f"  - {scraper}")


def main():
    """Main entry point for the scraper."""
    app()


if __name__ == "__main__":
    app() 
