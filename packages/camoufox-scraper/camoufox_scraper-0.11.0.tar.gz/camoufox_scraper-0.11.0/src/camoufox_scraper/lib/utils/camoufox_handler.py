"""
Camoufox browser wrapper for handling browser initialization and management.
Uses AsyncCamoufox for browser automation with Tor proxy support.
"""

import logging
import os
import random
from typing import Optional

from camoufox import AsyncCamoufox

logger = logging.getLogger("freepornvideos-scraper")

# Track used display numbers to avoid conflicts
_used_display_numbers = set()

async def get_client( 
    tor_proxy: Optional[bool] = False,
    display_num: Optional[int] = None,
):
    """
    Get a Camoufox browser instance with anti-fingerprinting capabilities.
    
    Args:
        tor_proxy: Whether to route traffic through Tor proxy
        display_num: Specific display number to use (if None, one will be assigned)
    
    Returns:
        AsyncCamoufox: Browser instance with anti-fingerprinting enabled
    """
    global _used_display_numbers
    
    # Generate a unique display number if not provided
    if display_num is None:
        # Start from 100 to avoid conflicts with system displays
        while True:
            display_num = random.randint(100, 999)
            if display_num not in _used_display_numbers:
                _used_display_numbers.add(display_num)
                break
    
    display_id = f":{display_num}"
    logger.info(f"Creating AsyncCamoufox with tor_proxy={tor_proxy}, display={display_id}")
    
    # Set up environment variables for Xvfb
    os.environ["DISPLAY"] = display_id
    
    # Create configuration with explicit virtual display
    return AsyncCamoufox(
        headless=False,  # Don't use headless mode since we're using Xvfb
        proxy="socks5://127.0.0.1:9050" if tor_proxy else None,
        os=["macos", "windows", "linux"],
        humanize=False,
        disable_coop=False,
        enable_cache=True,
        virtual_display=display_id,  # Explicitly set virtual display
    )

def release_display(display_num: int):
    """
    Release a display number so it can be reused.
    
    Args:
        display_num: The display number to release
    """
    global _used_display_numbers
    if display_num in _used_display_numbers:
        _used_display_numbers.remove(display_num)
