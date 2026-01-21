"""
Amazon Fresh (India) scraper for grocery prices.
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


def scrape_amazon_fresh(product_name: str) -> Optional[Dict]:
    """
    Scrape Amazon Fresh (India) for product prices.
    
    Args:
        product_name: Name of the product to search
        
    Returns:
        Dictionary with price information or None if not found
    """
    try:
        # Amazon Fresh search URL
        search_url = f"https://www.amazon.in/s?k={product_name.replace(' ', '+')}&rh=n%3A4859498011"
        
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find first product result
        product_card = soup.find('div', {'data-component-type': 's-search-result'})
        
        if not product_card:
            return None
        
        # Extract price
        price_element = (
            product_card.find('span', class_='a-price-whole') or
            product_card.find('span', class_='a-price') or
            product_card.find('span', class_='a-offscreen')
        )
        
        if not price_element:
            return None
        
        price_text = price_element.get_text(strip=True)
        # Extract numeric price
        price = float(re.sub(r'[^\d.]', '', price_text))
        
        # Extract product link
        link_element = product_card.find('a', class_='a-link-normal', href=True)
        product_link = link_element['href'] if link_element else None
        
        if product_link and not product_link.startswith('http'):
            product_link = f"https://www.amazon.in{product_link}"
        
        # Check stock status (Amazon usually shows availability)
        stock_element = product_card.find('span', class_='a-color-state')
        in_stock = 'out of stock' not in (stock_element.get_text().lower() if stock_element else '')
        
        # Ensure we always return a real URL
        final_link = product_link if product_link and product_link.startswith('http') else search_url
        
        return {
            'store': 'Amazon Fresh',
            'price': round(price, 2),
            'currency': 'INR',
            'link': final_link,
            'in_stock': in_stock
        }
        
    except Exception as e:
        print(f"Error scraping Amazon Fresh: {str(e)}")
        return None


def fetch_amazonfresh_prices(product_name: str) -> List[Dict]:
    """Fetch prices from Amazon Fresh."""
    result = scrape_amazon_fresh(product_name)
    return [result] if result else []

