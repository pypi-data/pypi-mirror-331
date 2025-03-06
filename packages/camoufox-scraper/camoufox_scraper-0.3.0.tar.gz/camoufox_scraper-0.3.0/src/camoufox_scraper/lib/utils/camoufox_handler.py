"""
Camoufox browser wrapper for handling browser initialization and management.
Uses AsyncCamoufox for browser automation with Tor proxy support.
"""

import logging
from typing import List, Optional

from camoufox import AsyncCamoufox

logger = logging.getLogger("freepornvideos-scraper")

async def get_client(
    headless: Optional[bool] = True, 
    tor_proxy: Optional[bool] = False,
):
    """
    Get a Camoufox browser instance with anti-fingerprinting capabilities.
    
    Args:
        headless: Whether to run browser in headless mode
        tor_proxy: Whether to route traffic through Tor proxy
    
    Returns:
        AsyncCamoufox: Browser instance with anti-fingerprinting enabled
    """
    # Use a more flexible OS configuration
    os_options: List[str] = ["windows", "macos", "linux"]
    
    try:
        logger.info(f"Creating AsyncCamoufox with headless={headless}, tor_proxy={tor_proxy}")
        return AsyncCamoufox(
            headless=True if headless else False,
            proxy="socks5://127.0.0.1:9050" if tor_proxy else None,
            os=os_options,
            humanize=True,
            block_images=False,
            block_webrtc=True,
            disable_coop=False,
            enable_cache=True,
            # Add more relaxed fingerprinting settings
            strict_fingerprinting=False
        )
    except Exception as e:
        logger.error(f"Error creating AsyncCamoufox: {e}")
        
        # Fallback with minimal settings if the first attempt fails
        logger.info("Trying fallback configuration with minimal settings")
        return AsyncCamoufox(
            headless=True if headless else False,
            proxy="socks5://127.0.0.1:9050" if tor_proxy else None,
            os="linux",  # Just use linux as fallback
            humanize=False,  # Disable humanize
            block_images=True,  # Block images to reduce bandwidth
            strict_fingerprinting=False,  # Disable strict fingerprinting
            enable_cache=True
        )
