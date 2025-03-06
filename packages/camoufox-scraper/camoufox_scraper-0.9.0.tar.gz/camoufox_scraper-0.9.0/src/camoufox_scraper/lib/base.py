"""Base abstract class for all video scrapers."""

import abc
import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from camoufox_scraper.lib.utils.camoufox_handler import get_client

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("freepornvideos-scraper")


class BaseScraper(abc.ABC):
    """Abstract base class for video scrapers."""
    
    def __init__(self, tor_proxy: bool = False):
        """
        Initialize the scraper.
        
        Args:
            tor_proxy: Whether to use Tor proxy
        """
        self.browser = None
        self.browser_initialized = False
        self.failed_urls = set()
        self.output_urls = []
        self.tor_proxy = tor_proxy
        self.concurrency = 1  # Default concurrency
    
    async def initialize_browser(self, tor_proxy: bool = None) -> None:
        """
        Initialize the browser instance.
        
        Args:
            tor_proxy: Whether to use Tor proxy (overrides constructor value if provided)
        """
        # Use parameters passed to this method, or fall back to values stored from constructor
        use_tor_proxy = tor_proxy if tor_proxy is not None else self.tor_proxy
        
        logger.info(f"Initializing browser (tor_proxy={use_tor_proxy})")
        try:
            self.client = await get_client(tor_proxy=use_tor_proxy)
            self.browser = await self.client.__aenter__()
            if not self.browser:
                raise RuntimeError("Browser initialization failed: returned None")
            self.browser_initialized = True
            logger.info("Browser initialized")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise RuntimeError(f"Browser initialization failed: {e}")
    
    async def close_browser(self) -> None:
        """Close the browser instance."""
        if self.browser_initialized and self.client:
            logger.info("Closing browser")
            await self.client.__aexit__(None, None, None)
            self.browser_initialized = False
            logger.info("Browser closed")
    
    def add_failed_url(self, url: str) -> None:
        """
        Add a URL to the failed list.
        
        Args:
            url: The URL that failed
        """
        self.failed_urls.add(url)
        logger.warning(f"Added to failed URLs: {url}")
    
    @abc.abstractmethod
    async def _extract_video_url_async(self, page_url: str) -> Optional[str]:
        """
        Asynchronously extract video URL from the given page.
        This method should be implemented by subclasses to handle site-specific extraction.
        
        Args:
            page_url: URL of the video page to scrape
            
        Returns:
            The direct video URL or None if not found
        """
        pass
    
    async def _run_async(self, urls: List[str]) -> None:
        """
        Process URLs asynchronously with proper concurrency.
        
        Args:
            urls: List of URLs to process
        """
        try:
            # Initialize browser if not already initialized
            if not self.browser_initialized:
                await self.initialize_browser()
            
            logger.info(f"Processing URLs with concurrency: {self.concurrency}")
            
            # Process URLs in batches based on concurrency
            for i in range(0, len(urls), self.concurrency):
                batch = urls[i:i + self.concurrency]
                logger.info(f"Processing batch of {len(batch)} URLs ({i+1}-{i+len(batch)} of {len(urls)})")
                
                # Create tasks for concurrent processing
                tasks = [self._extract_video_url_async(url) for url in batch]
                
                # Run tasks concurrently and gather results
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for url, result in zip(batch, results):
                    if isinstance(result, Exception):
                        logger.error(f"Error processing {url}: {result}")
                        self.add_failed_url(url)
                    elif result:
                        self.output_urls.append(result)
                        
        except Exception as e:
            logger.error(f"Error in _run_async: {e}")
    
    def run(self, input_file: str, output_file: str) -> Dict[str, Any]:
        """
        Run the scraper on a list of URLs from a file.
        
        Args:
            input_file: Path to file containing URLs to scrape
            output_file: Path to file where results will be saved
            
        Returns:
            Dictionary with the results
        """
        results = {
            "success": False,
            "processed": 0,
            "extracted": 0,
            "failed": 0,
            "output_file": output_file,
            "failed_file": None
        }
        
        # Read input URLs
        try:
            with open(input_file, "r") as f:
                urls = [line.strip() for line in f if line.strip()]
            
            if not urls:
                logger.error(f"No URLs found in {input_file}")
                return results
                
            logger.info(f"Loaded {len(urls)} URLs from {input_file}")
            results["processed"] = len(urls)
            
            # Set up browser and process URLs in a single event loop
            try:
                # Run the whole processing in a single asyncio event loop
                asyncio.run(self._run_async(urls))
                
                # Get the results
                extracted_urls = self.output_urls
                results["extracted"] = len(extracted_urls)
                
                # Save results
                with open(output_file, "w") as f:
                    for url in extracted_urls:
                        f.write(f"{url}\n")
                
                logger.info(f"Processed {len(urls)} URLs, successfully extracted {len(extracted_urls)}")
                logger.info(f"Results saved to {output_file}")
                
                # Save failed URLs
                if self.failed_urls:
                    failed_file = f"{Path(output_file).stem}_failed.txt"
                    with open(failed_file, "w") as f:
                        for url in self.failed_urls:
                            f.write(f"{url}\n")
                    logger.info(f"Failed URLs ({len(self.failed_urls)}) saved to {failed_file}")
                    results["failed"] = len(self.failed_urls)
                    results["failed_file"] = failed_file
                
                results["success"] = True
                return results
            except Exception as e:
                logger.error(f"Error processing URLs: {str(e)}")
                results["error"] = str(e)
                return results
                
        except Exception as e:
            logger.error(f"Error running scraper: {str(e)}")
            results["error"] = str(e)
            return results
    
    def process_urls(self, urls: List[str]) -> List[str]:
        """
        Process a list of URLs to extract video links.
        
        Args:
            urls: List of URLs to process
            
        Returns:
            List of extracted video URLs
        """
        # Reset output URLs
        self.output_urls = []
        
        # Run in a single event loop
        asyncio.run(self._run_async(urls))
        
        # Return the results
        return self.output_urls
