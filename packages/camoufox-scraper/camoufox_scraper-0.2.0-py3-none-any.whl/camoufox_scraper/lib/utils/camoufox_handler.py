"""
Camoufox browser wrapper for handling browser initialization and management.
Uses AsyncCamoufox for browser automation with Tor proxy support.
"""

from typing import Optional

from camoufox import AsyncCamoufox


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
    return AsyncCamoufox(
        headless=True if headless else False,
        proxy="socks5://127.0.0.1:9050" if tor_proxy else None,
        os=["linux"],
        humanize=True,
)
