"""
Camoufox browser wrapper for handling browser initialization and management.
Uses AsyncCamoufox for browser automation with Tor proxy support.
"""

import logging
import os
from typing import Optional

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
    logger.info(f"Creating AsyncCamoufox with headless={headless}, tor_proxy={tor_proxy}")
    
    # Set up environment variables for Xvfb
    display_num = "99"
    os.environ["DISPLAY"] = f":{display_num}"
    
    # Create configuration with explicit virtual display
    return AsyncCamoufox(
        headless=False,  # Don't use headless mode since we're using Xvfb
        proxy="socks5://127.0.0.1:9050" if tor_proxy else None,
        os="linux",  # Use Linux for server environment
        browser="firefox",
        strict_fingerprinting=False,
        humanize=False,
        block_webrtc=True,
        disable_coop=False,
        enable_cache=True,
        block_images=True,  # Block images to reduce bandwidth
        virtual_display=f":{display_num}",  # Explicitly set virtual display
        debug=True
    )
