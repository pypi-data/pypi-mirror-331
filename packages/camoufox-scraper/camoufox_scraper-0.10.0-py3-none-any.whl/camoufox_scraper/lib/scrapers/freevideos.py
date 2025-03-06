"""FreePornVideos.xxx site-specific scraper implementation."""

import asyncio
import logging
import random
from typing import Optional

import requests

from camoufox_scraper.lib.base import BaseScraper
from camoufox_scraper.lib.utils.camoufox_handler import get_client

logger = logging.getLogger("freepornvideos-scraper")


class FreePornVideosScraper(BaseScraper):
    """FreePornVideos.xxx specific scraper implementation."""
    
    async def _extract_video_url_async(self, page_url: str) -> Optional[str]:
        """
        Asynchronously extract video URL from the given page.
        
        Args:
            page_url: URL of the video page to scrape
            
        Returns:
            The extracted video URL or None if not found
        """
        # Create a new browser instance for each concurrent task
        browser = None
        client = None
        page = None
        
        try:
            logger.info(f"Processing URL: {page_url}")
            
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
            
            # Create a new page with explicit error handling
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
            await page.wait_for_selector("div.player-wrap", timeout=30000)
            
            # CRITICAL: Click the "Play Video" button to load video source elements
            try:
                logger.info("Clicking Play Video button to load video sources")
                
                # Define the big play button selector
                big_play_button_selector = ".vjs-big-play-button"
                
                # Try to click the play button with retries
                max_retries = 3
                retry_delays = [2, 4, 6]  # Increasing timeouts in seconds
                
                for retry in range(max_retries):
                    try:
                        logger.info(f"Attempt {retry+1}/{max_retries} to click play button")
                        
                        # Try JavaScript click first (more reliable with overlays)
                        await page.evaluate(f"""() => {{
                            const button = document.querySelector('{big_play_button_selector}');
                            if (button) {{
                                button.click();
                                console.log('JS click on play button');
                                return true;
                            }}
                            return false;
                        }}""")
                        logger.info("Attempted JavaScript click on play button")
                        
                        # Wait for sources to load after clicking play
                        await asyncio.sleep(2)
                        
                        # Check if video sources are loaded
                        has_sources = await page.evaluate("""() => {
                            // Check for video sources
                            const videoElements = document.querySelectorAll('video source');
                            if (videoElements && videoElements.length > 0) {
                                return true;
                            }
                            
                            // Check for video with src attribute
                            const videoTags = document.querySelectorAll('video');
                            if (videoTags && videoTags.length > 0) {
                                for (const video of videoTags) {
                                    if (video.src && video.src.includes('.mp4')) {
                                        return true;
                                    }
                                }
                            }
                            
                            return false;
                        }""")
                        
                        if has_sources:
                            logger.info("Video sources successfully loaded after click")
                            break
                        else:
                            logger.warning(f"No video sources found after click attempt {retry+1}, will retry")
                            if retry < max_retries - 1:
                                await asyncio.sleep(retry_delays[retry])
                    except Exception as e:
                        logger.warning(f"Click attempt {retry+1} failed: {e}")
                        if retry < max_retries - 1:
                            await asyncio.sleep(retry_delays[retry])
                
            except Exception as e:
                logger.warning(f"Could not click play button after all retries: {e}, trying to extract sources anyway")
            
            # Scroll down to ensure the video player is in view
            await self._scroll_page(page)
            
            # Extract video URLs from the page
            logger.info("Extracting video sources")
            video_sources = await page.evaluate(r"""() => {
                // Find all video source elements
                const videoElements = document.querySelectorAll('video source');
                
                // If no direct sources found, try to find in javascript variables
                if (!videoElements || videoElements.length === 0) {
                    // Also check the video element itself for src attribute
                    const videoTags = document.querySelectorAll('video');
                    if (videoTags && videoTags.length > 0) {
                        for (const video of videoTags) {
                            if (video.src && video.src.includes('.mp4')) {
                                return [{url: video.src, quality: 'default'}];
                            }
                        }
                    }
                    
                    // Look for player configuration with sources
                    try {
                        // Common patterns in the page JavaScript
                        const scripts = document.querySelectorAll('script');
                        for (const script of scripts) {
                            const content = script.textContent || script.innerText;
                            if (content && content.includes('source:') && content.includes('.mp4')) {
                                const match = content.match(/source:\s*['"]([^'"]+)['"]/);
                                if (match && match[1]) {
                                    return [{url: match[1], quality: 'unknown'}];
                                }
                            }
                        }
                    } catch (e) {
                        console.error('Error extracting from JS:', e);
                    }
                    return []; // Return empty array if no sources found
                }
                
                // Collect sources from video elements
                const sources = [];
                videoElements.forEach(source => {
                    if (source.src && source.src.includes('.mp4')) {
                        let quality = 'unknown';
                        if (source.getAttribute('title')) {
                            quality = source.getAttribute('title');
                        } else if (source.getAttribute('label')) {
                            quality = source.getAttribute('label');
                        } else if (source.getAttribute('data-quality')) {
                            quality = source.getAttribute('data-quality');
                        }
                        sources.push({
                            url: source.src,
                            quality: quality
                        });
                    }
                });
                    
                return sources;
            }""")
            
            if not video_sources:
                logger.warning("No video sources found")
                self.add_failed_url(page_url)
                return None
            
            # Find the highest quality source (prefer 720p)
            logger.info(f"Found {len(video_sources)} video sources")
            preferred_source = None
            
            # First try to find 720p
            for source in video_sources:
                if source["quality"] == "720p":
                    preferred_source = source
                    break
            
            # If 720p not found, use the first source
            if not preferred_source and video_sources:
                preferred_source = video_sources[0]
            
            if not preferred_source:
                logger.warning("No usable video source found")
                self.add_failed_url(page_url)
                return None
            
            # Get the source URL
            video_url = preferred_source["url"]
            logger.info(f"Selected video source: {preferred_source['quality']} - {video_url}")
            
            # Ensure the URL ends with a slash if it's from freepornvideos.xxx
            if "freepornvideos.xxx/get_file" in video_url and not video_url.endswith('/'):
                video_url = video_url + '/'
                logger.info(f"Added trailing slash to URL: {video_url}")
            
            # Follow redirects to get the final URL
            try:
                logger.info("Following redirects to get final URL")
                response = requests.head(video_url, allow_redirects=True, timeout=10)
                final_url = response.url
                logger.info(f"Final URL after redirects: {final_url}")
                return final_url
            except Exception as e:
                logger.error(f"Error following redirects: {e}")
                # Return the original URL if we can't follow redirects
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
    
    async def _scroll_page(self, page) -> None:
        """
        Scroll a page to simulate human behavior and load lazy content.
        
        Args:
            page: The page to scroll
        """
        try:
            logger.info("Scrolling page to load lazy content")
            
            # Get page height
            height = await page.evaluate("document.body.scrollHeight")
            viewport_height = await page.evaluate("window.innerHeight")
            
            # Calculate number of steps based on page height
            steps = min(max(int(height / viewport_height), 3), 10)
            
            for i in range(steps):
                # Calculate scroll position
                position = (i + 1) * viewport_height
                
                # Scroll to position
                await page.evaluate(f"window.scrollTo(0, {position})")
                
                # Add some random pause between scrolls
                await asyncio.sleep(random.uniform(0.5, 1.5))
                
            # Scroll back to top for good measure
            await page.evaluate("window.scrollTo(0, 0)")
            logger.info("Page scrolling complete")
            
        except Exception as e:
            logger.error(f"Error scrolling page: {e}")
            # Don't let scrolling errors fail the whole process
