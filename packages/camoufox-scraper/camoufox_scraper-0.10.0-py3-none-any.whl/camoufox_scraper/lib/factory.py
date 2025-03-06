"""Factory for creating scrapers."""

from typing import Dict, Type

from camoufox_scraper.lib.base import BaseScraper
from camoufox_scraper.lib.scrapers.freevideos import FreePornVideosScraper


class ScraperFactory:
    """Factory class for creating scraper instances."""
    
    # Registry of available scrapers
    _scrapers: Dict[str, Type[BaseScraper]] = {
        "freevideos": FreePornVideosScraper,
    }
    
    @classmethod
    def get_available_scrapers(cls) -> list[str]:
        """
        Get a list of available scraper names.
        
        Returns:
            List of scraper names
        """
        return list(cls._scrapers.keys())
    
    @classmethod
    def create_scraper(cls, scraper_name: str, tor_proxy: bool = False) -> BaseScraper:
        """
        Create a scraper instance by name.
        
        Args:
            scraper_name: Name of the scraper to create
            tor_proxy: Whether to use Tor proxy
            
        Returns:
            Scraper instance
            
        Raises:
            ValueError: If scraper_name is not recognized
        """
        try:
            scraper_class = cls._scrapers[scraper_name.lower()]
            return scraper_class(tor_proxy=tor_proxy)
        except KeyError:
            available = ", ".join(cls.get_available_scrapers())
            raise ValueError(
                f"Unknown scraper: {scraper_name}. Available scrapers: {available}"
            ) 
