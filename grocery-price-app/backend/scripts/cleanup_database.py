"""
Database cleanup script to remove duplicate prices and normalize data.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, Price, Product
from datetime import datetime, timedelta
from sqlalchemy import func

def cleanup_duplicates():
    """Remove duplicate price entries."""
    app = create_app()
    
    with app.app_context():
        print("Starting database cleanup...")
        
        # Find duplicates: same product_id, store_name, and price within same day
        duplicates = db.session.query(
            Price.product_id,
            Price.store_name,
            func.date(Price.recorded_at).label('date'),
            Price.price,
            func.count(Price.id).label('count')
        ).group_by(
            Price.product_id,
            Price.store_name,
            func.date(Price.recorded_at),
            Price.price
        ).having(func.count(Price.id) > 1).all()
        
        print(f"Found {len(duplicates)} duplicate groups")
        
        removed = 0
        for dup in duplicates:
            # Keep the first one, remove others
            prices_to_remove = Price.query.filter_by(
                product_id=dup.product_id,
                store_name=dup.store_name,
                price=dup.price
            ).filter(
                func.date(Price.recorded_at) == dup.date
            ).order_by(Price.recorded_at).offset(1).all()
            
            for price in prices_to_remove:
                db.session.delete(price)
                removed += 1
        
        # Normalize product names
        products = Product.query.all()
        normalized_count = 0
        for product in products:
            from utils import normalize_product_name
            normalized = normalize_product_name(product.name)
            if product.normalized_name != normalized:
                product.normalized_name = normalized
                normalized_count += 1
        
        db.session.commit()
        
        print(f"Removed {removed} duplicate price entries")
        print(f"Normalized {normalized_count} product names")
        print("Database cleanup completed!")

if __name__ == '__main__':
    cleanup_duplicates()

