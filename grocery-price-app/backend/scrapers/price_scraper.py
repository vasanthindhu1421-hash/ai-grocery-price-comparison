"""
Price scraper module for Indian grocery stores.
Aggregates prices from multiple real Indian grocery platforms.
"""
import time
import random
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import individual store scrapers
from scrapers.bigbasket_scraper import fetch_bigbasket_prices
from scrapers.zepto_scraper import fetch_zepto_prices
from scrapers.instamart_scraper import fetch_instamart_prices
from scrapers.jiomart_scraper import fetch_jiomart_prices
from scrapers.amazonfresh_scraper import fetch_amazonfresh_prices


# User agent rotation for better scraping success
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]


def fetch_prices(product_name: str) -> List[Dict]:
    """
    Fetch prices for a product from multiple Indian grocery stores.
    Uses parallel scraping for better performance.
    Handles errors gracefully and returns empty list on failure.
    
    Args:
        product_name: Name of the product to search for
        
    Returns:
        List of dictionaries containing store, price, and link information
    """
    if not product_name or not product_name.strip():
        return []
    
    prices_data = []
    
    # Define all scrapers (ONLY Indian stores)
    scrapers = [
        ('BigBasket', fetch_bigbasket_prices),
        ('Zepto', fetch_zepto_prices),
        ('Swiggy Instamart', fetch_instamart_prices),
        ('JioMart', fetch_jiomart_prices),
        ('Amazon Fresh', fetch_amazonfresh_prices),
    ]
    
    # Use ThreadPoolExecutor for parallel scraping
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_store = {
            executor.submit(scraper_func, product_name): store_name
            for store_name, scraper_func in scrapers
        }
        
        for future in as_completed(future_to_store):
            store_name = future_to_store[future]
            try:
                results = future.result(timeout=15)  # 15 second timeout per store
                if results:
                    prices_data.extend(results)
            except Exception as e:
                print(f"Error fetching prices from {store_name}: {str(e)}")
                # Continue with other stores even if one fails
                continue
    
    # Remove duplicates by store name
    unique_prices = {}
    for price_info in prices_data:
        store = price_info.get('store', '')
        if store and store not in unique_prices:
            unique_prices[store] = price_info
    
    prices_data = list(unique_prices.values())
    
    # Sort by price (lowest first)
    prices_data.sort(key=lambda x: x.get('price', float('inf')))
    
    return prices_data

