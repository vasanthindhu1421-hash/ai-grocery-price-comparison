"""
Zepto scraper for Indian grocery prices.
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-IN,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}


def scrape_zepto(product_name: str) -> Optional[Dict]:
    """
    Scrape Zepto for product prices.
    
    Args:
        product_name: Name of the product to search
        
    Returns:
        Dictionary with price information or None if not found
    """
    try:
        # Zepto search URL
        search_url = f"https://www.zeptonow.com/search?q={product_name.replace(' ', '%20')}"
        
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find first product result
        product_card = soup.find('div', class_='product-card') or soup.find('div', {'data-product-id': True})
        
        if not product_card:
            return None
        
        # Extract price
        price_element = (
            product_card.find('span', class_='price') or
            product_card.find('div', class_='product-price') or
            product_card.find('span', class_='selling-price')
        )
        
        if not price_element:
            return None
        
        price_text = price_element.get_text(strip=True)
        # Extract numeric price
        price = float(re.sub(r'[^\d.]', '', price_text))
        
        # Extract product link
        link_element = product_card.find('a', href=True)
        product_link = link_element['href'] if link_element else None
        
        if product_link and not product_link.startswith('http'):
            product_link = f"https://www.zeptonow.com{product_link}"
        
        # Check stock status
        stock_element = product_card.find('span', class_='out-of-stock')
        in_stock = stock_element is None
        
        # Ensure we always return a real URL
        final_link = product_link if product_link and product_link.startswith('http') else search_url
        
        return {
            'store': 'Zepto',
            'price': round(price, 2),
            'currency': 'INR',
            'link': final_link,
            'in_stock': in_stock
        }
        
    except Exception as e:
        print(f"Error scraping Zepto: {str(e)}")
        return None


def fetch_zepto_prices(product_name: str) -> List[Dict]:
    """Fetch prices from Zepto."""
    result = scrape_zepto(product_name)
    return [result] if result else []

