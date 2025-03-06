"""
Camoufox browser wrapper for handling browser initialization and management.
Uses AsyncCamoufox for browser automation with Tor proxy support.
"""

import logging
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
    
    # Use 'virtual' for headless mode on servers without a display
    headless_mode = 'virtual' if headless else False
    
    return AsyncCamoufox(
        headless=headless_mode,
        proxy="socks5://127.0.0.1:9050" if tor_proxy else None,
        os=["linux"],  # Simplify to just Linux for server environment
        humanize=True,
        block_webrtc=True,
        disable_coop=False,
        enable_cache=True,
        # Add debug flag to help with troubleshooting
        debug=True
    )
