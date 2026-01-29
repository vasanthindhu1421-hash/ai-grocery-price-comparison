"""
Product-related API routes.
"""
from flask import Blueprint, request, jsonify
from models import db, Product, Price, SearchHistory
from scrapers.price_scraper import fetch_prices
from datetime import datetime
from utils import token_required
import re

product_bp = Blueprint('product', __name__, url_prefix='')


def normalize_product_name(name):
    """Normalize product name for consistent searching."""
    # Convert to lowercase, remove extra spaces, remove special chars
    normalized = re.sub(r'[^\w\s]', '', name.lower())
    normalized = ' '.join(normalized.split())
    return normalized


@product_bp.route('/search', methods=['POST'])
@token_required
def search():
    """
    Search for products and fetch prices from multiple stores.
    Requires authentication.
    
    Expected JSON:
    {
        "product_name": "milk"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'product_name' not in data:
            return jsonify({'error': 'Product name is required'}), 400
        
        product_name = data['product_name'].strip()
        if not product_name:
            return jsonify({'error': 'Product name cannot be empty'}), 400
        
        user = request.current_user
        
        # Normalize product name
        from utils import normalize_product_name
        normalized_name = normalize_product_name(product_name)
        
        # DB-first: try exact normalized match, then prefix/contains to avoid false 404s
        product = Product.query.filter_by(normalized_name=normalized_name).first()
        if not product:
            product = Product.query.filter(
                Product.normalized_name.like(f'{normalized_name}%')
            ).order_by(Product.created_at.asc()).first()
        if not product:
            product = Product.query.filter(
                Product.normalized_name.like(f'%{normalized_name}%')
            ).order_by(Product.created_at.asc()).first()
        
        if not product:
            product = Product(
                name=product_name,
                normalized_name=normalized_name,
                description=f"Price comparison for {product_name}",
                category="Grocery"
            )
            db.session.add(product)
            db.session.flush()  # Get product.id without committing
        
        # Try to fetch prices using scraper, fallback to cached data
        prices_data = []
        use_cached = False
        
        try:
            prices_data = fetch_prices(product_name)
        except Exception as e:
            print(f"Scraping error: {str(e)}")
            # Fallback to cached data from database
            use_cached = True
        
        # If scraping failed or returned no data, use cached prices
        if not prices_data or use_cached:
            try:
                # Try scraped_at first, fallback to recorded_at for backward compatibility
                cached_prices = Price.query.filter_by(product_id=product.id).order_by(
                    Price.scraped_at.desc()
                ).all()
            except:
                # Fallback for old schema
                cached_prices = Price.query.filter_by(product_id=product.id).order_by(
                    Price.recorded_at.desc()
                ).all()
            
            if cached_prices:
                # Group by store and get latest price per store
                store_prices = {}
                for cp in cached_prices:
                    if cp.store_name not in store_prices:
                        product_url = getattr(cp, 'product_url', None) or getattr(cp, 'link', '')
                        store_prices[cp.store_name] = {
                            'store': cp.store_name,
                            'price': float(cp.price),
                            'currency': cp.currency or 'INR',
                            'link': product_url,
                            'product_url': product_url,
                            'in_stock': cp.in_stock,
                            'cached': True
                        }
                
                prices_data = list(store_prices.values())
                use_cached = True
        
        if not prices_data:
            # Never return 404 if we have a matching product in DB; return empty prices gracefully
            return jsonify({
                'product': product.to_dict(),
                'prices': [],
                'warning': '⚠ Live data unavailable, showing last updated prices',
                'message': f'No cached prices yet for {product.name}. Try again later.'
            }), 200
        
        # Remove duplicates and sort by price
        unique_prices = {}
        for price_info in prices_data:
            store = price_info['store']
            if store not in unique_prices:
                unique_prices[store] = price_info
        
        prices_data = list(unique_prices.values())
        prices_data.sort(key=lambda x: x['price'])
        
        # Save search history
        search_history = SearchHistory(
            user_id=user.id,
            query=product_name,
            results_count=len(prices_data)
        )
        db.session.add(search_history)
        
        # Save prices to database (update if exists, insert if new)
        current_time = datetime.utcnow()
        seen_stores = set()  # Track stores to prevent duplicates
        
        for price_info in prices_data:
            store_name = price_info['store']
            
            # Skip if we've already processed this store (prevent duplicates)
            if store_name in seen_stores:
                continue
            seen_stores.add(store_name)
            
            # Check if price exists for this product+store (same day)
            try:
                existing_price = Price.query.filter_by(
                    product_id=product.id,
                    store_name=store_name
                ).filter(
                    Price.scraped_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                ).first()
            except:
                # Fallback for old schema
                existing_price = Price.query.filter_by(
                    product_id=product.id,
                    store_name=store_name
                ).filter(
                    Price.recorded_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                ).first()
            
            product_url = price_info.get('link') or price_info.get('product_url', '')
            
            if existing_price:
                # Update existing price
                existing_price.price = round(float(price_info['price']), 2)
                existing_price.currency = price_info.get('currency', 'INR')
                if hasattr(existing_price, 'product_url'):
                    existing_price.product_url = product_url
                elif hasattr(existing_price, 'link'):
                    existing_price.link = product_url
                existing_price.in_stock = price_info.get('in_stock', True)
                if hasattr(existing_price, 'scraped_at'):
                    existing_price.scraped_at = current_time
                elif hasattr(existing_price, 'recorded_at'):
                    existing_price.recorded_at = current_time
            else:
                # Insert new price (handle both old and new schema)
                price_data = {
                    'product_id': product.id,
                    'store_name': store_name,
                    'price': round(float(price_info['price']), 2),
                    'currency': price_info.get('currency', 'INR'),
                    'in_stock': price_info.get('in_stock', True),
                }
                
                # Use new schema fields if available
                if hasattr(Price, 'product_url'):
                    price_data['product_url'] = product_url
                if hasattr(Price, 'scraped_at'):
                    price_data['scraped_at'] = current_time
                else:
                    # Fallback for old schema
                    price_data['link'] = product_url
                    price_data['recorded_at'] = current_time
                
                price = Price(**price_data)
                db.session.add(price)
        
        db.session.commit()
        
        response_data = {
            'product': product.to_dict(),
            'prices': prices_data,
            'message': f'Found {len(prices_data)} prices for {product_name}'
        }
        
        if use_cached:
            response_data['warning'] = '⚠ Live data unavailable, showing last updated prices'
        
        return jsonify(response_data), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@product_bp.route('/product/<int:product_id>', methods=['GET'])
@token_required
def get_product(product_id):
    """
    Get product details by ID.
    Requires authentication.
    
    Args:
        product_id: ID of the product
    """
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify(product.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@product_bp.route('/search-history', methods=['GET'])
@token_required
def get_search_history():
    """Get user's search history. Requires authentication."""
    try:
        user = request.current_user
        history = SearchHistory.query.filter_by(user_id=user.id).order_by(
            SearchHistory.searched_at.desc()
        ).limit(50).all()
        
        return jsonify({
            'history': [h.to_dict() for h in history]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@product_bp.route('/products/suggest', methods=['GET'])
@token_required
def suggest_products():
    """
    Get product suggestions for autocomplete.
    Requires authentication.
    
    Query params:
        q: partial product name (min 2 characters)
    """
    try:
        query = request.args.get('q', '').strip()
        
        # 1-character suggestions are required (e.g., "m" -> "milk")
        if len(query) < 1:
            return jsonify({'suggestions': []}), 200
        
        # Search in normalized_name for better matching
        normalized_query = normalize_product_name(query)
        
        # Prefix match for true autocomplete behavior (m -> milk, mi -> milk)
        products = Product.query.filter(
            Product.normalized_name.like(f'{normalized_query}%')
        ).order_by(Product.name).limit(10).all()
        
        # Remove duplicates by name
        seen_names = set()
        suggestions = []
        for p in products:
            if p.name not in seen_names:
                seen_names.add(p.name)
                suggestions.append({'id': p.id, 'name': p.name})
        
        return jsonify({'suggestions': suggestions}), 200
        
    except Exception as e:
        # Return empty suggestions on error instead of crashing
        print(f"Error in suggest_products: {str(e)}")
        return jsonify({'suggestions': []}), 200

