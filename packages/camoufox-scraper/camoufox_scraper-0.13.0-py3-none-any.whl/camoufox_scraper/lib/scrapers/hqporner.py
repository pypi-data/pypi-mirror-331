"""HQPorner site-specific scraper implementation."""

import logging
from typing import Optional

from camoufox_scraper.lib.base import BaseScraper
from camoufox_scraper.lib.utils.camoufox_handler import get_client

logger = logging.getLogger("freepornvideos-scraper")


class HQPornerScraper(BaseScraper):
    """HQPorner specific scraper implementation."""
    
    async def _extract_video_url_async(self, page_url: str) -> Optional[str]:
        """
        Asynchronously extract video URL from the given HQPorner page.
        
        Args:
            page_url: URL of the video page to scrape
            
        Returns:
            The extracted video URL or None if not found
        """
        browser = None
        client = None
        page = None
        
        try:
            logger.info(f"Processing HQPorner URL: {page_url}")
            
            # Create a new browser instance for this task
            try:
                client = await get_client(tor_proxy=self.tor_proxy)
                browser = await client.__aenter__()
                if not browser:
                    raise RuntimeError("Browser initialization failed: returned None")
            except Exception as e:
                logger.error(f"Failed to initialize browser for URL {page_url}: {e}")
                self.add_failed_url(page_url)
                return None
            
            # Create a new page
            try:
                page = await browser.new_page()
                if not page:
                    raise RuntimeError("Browser.new_page() returned None")
            except Exception as e:
                logger.error(f"Failed to create new page: {e}")
                self.add_failed_url(page_url)
                return None
            
            # Navigate to the page
            try:
                response = await page.goto(page_url)
                if not response:
                    logger.error(f"Failed to load page: {page_url}")
                    self.add_failed_url(page_url)
                    return None
            except Exception as e:
                logger.error(f"Failed to navigate to page: {e}")
                self.add_failed_url(page_url)
                return None
                
            # Wait for content to load
            logger.info("Waiting for page to load completely")
            await page.wait_for_load_state("networkidle", timeout=30000)
            
            # Extract video sources from the page
            logger.info("Extracting video sources")
            video_sources = await page.evaluate("""() => {
                // Find all video source elements
                const sources = Array.from(document.querySelectorAll('video source'));
                
                // If no sources found, check the video element itself
                if (!sources || sources.length === 0) {
                    const video = document.querySelector('video');
                    if (video && video.src) {
                        return [{
                            url: video.src,
                            quality: 'default'
                        }];
                    }
                    return [];
                }
                
                // Extract sources with quality information
                return sources.map(source => {
                    let quality = 'unknown';
                    if (source.getAttribute('title')) {
                        quality = source.getAttribute('title');
                    }
                    
                    let url = source.src || source.getAttribute('src');
                    // Ensure URL is absolute
                    if (url && url.startsWith('//')) {
                        url = 'https:' + url;
                    }
                    
                    return {
                        url: url,
                        quality: quality
                    };
                }).filter(source => source.url && source.url.includes('.mp4'));
            }""")
            
            if not video_sources:
                logger.warning("No video sources found, trying alternative extraction method")
                
                # Try to extract from the video element directly
                video_url = await page.evaluate(r"""() => {
                    const video = document.querySelector('video');
                    if (video && video.src) {
                        return video.src;
                    }
                    
                    // Look for video URL pattern in page source
                    const pageSource = document.documentElement.outerHTML;
                    const matches = pageSource.match(/src=["']([^"']+\.mp4)["']/g);
                    if (matches && matches.length > 0) {
                        // Extract URL from the match
                        const urlMatch = matches[0].match(/src=["']([^"']+)["']/);
                        if (urlMatch && urlMatch[1]) {
                            let url = urlMatch[1];
                            if (url.startsWith('//')) {
                                url = 'https:' + url;
                            }
                            return url;
                        }
                    }
                    
                    return null;
                }""")
                
                if video_url:
                    logger.info(f"Found video URL using alternative method: {video_url}")
                    return video_url
                
                logger.warning("No video sources found after alternative extraction")
                self.add_failed_url(page_url)
                return None
            
            logger.info(f"Found {len(video_sources)} video sources")
            
            # Find the highest quality source (prefer 720p)
            preferred_source = None
            
            # First try to find 720p
            for source in video_sources:
                if "720p" in source["quality"] or "720" == source["quality"]:
                    preferred_source = source
                    logger.info(f"Found 720p source: {source['url']}")
                    break
            
            # If 720p not found, try to find 1080p
            if not preferred_source:
                for source in video_sources:
                    if "1080p" in source["quality"] or "1080" == source["quality"]:
                        preferred_source = source
                        logger.info(f"Found 1080p source: {source['url']}")
                        break
            
            # If neither 720p nor 1080p found, use the first source
            if not preferred_source and video_sources:
                preferred_source = video_sources[0]
                logger.info(f"Using default source: {preferred_source['url']}")
            
            if not preferred_source:
                logger.warning("No usable video source found")
                self.add_failed_url(page_url)
                return None
            
            # Get the source URL
            video_url = preferred_source["url"]
            
            # Ensure URL is absolute
            if video_url.startswith('//'):
                video_url = 'https:' + video_url
                
            logger.info(f"Selected video source: {preferred_source['quality']} - {video_url}")
            
            return video_url
                
        except Exception as e:
            logger.error(f"Error extracting URL from {page_url}: {e}")
            self.add_failed_url(page_url)
            return None
        finally:
            # Always close the page and browser
            if page:
                try:
                    await page.close()
                except Exception as e:
                    logger.warning(f"Error closing page: {e}")
            
            # Close the browser instance
            if client and browser:
                try:
                    await client.__aexit__(None, None, None)
                except Exception as e:
                    logger.warning(f"Error closing browser: {e}")
