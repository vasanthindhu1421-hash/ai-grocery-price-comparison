"""
Script to seed categories and sample products into the database.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, Category, Product
from utils import normalize_product_name

def seed_categories():
    """Seed categories and sample products."""
    app = create_app()
    
    with app.app_context():
        # Check if categories already exist
        if Category.query.count() > 0:
            print("Categories already exist. Skipping seeding.")
            return
        
        # Create categories
        categories_data = [
            {
                'name': 'Dairy',
                'image_url': 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&h=300&fit=crop'
            },
            {
                'name': 'Grains',
                'image_url': 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400&h=300&fit=crop'
            },
            {
                'name': 'Oils',
                'image_url': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400&h=300&fit=crop'
            },
            {
                'name': 'Pulses',
                'image_url': 'https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=400&h=300&fit=crop'
            },
            {
                'name': 'Vegetables',
                'image_url': 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=400&h=300&fit=crop'
            }
        ]
        
        for cat_data in categories_data:
            category = Category(name=cat_data['name'], image_url=cat_data['image_url'])
            db.session.add(category)
        
        db.session.commit()
        print("Categories seeded successfully")
        
        # Seed sample products
        products_data = [
            {'name': 'Milk', 'category': 'Dairy'},
            {'name': 'Curd', 'category': 'Dairy'},
            {'name': 'Butter', 'category': 'Dairy'},
            {'name': 'Ghee', 'category': 'Dairy'},
            {'name': 'Rice', 'category': 'Grains'},
            {'name': 'Wheat', 'category': 'Grains'},
            {'name': 'Atta', 'category': 'Grains'},
            {'name': 'Sunflower Oil', 'category': 'Oils'},
            {'name': 'Groundnut Oil', 'category': 'Oils'},
            {'name': 'Toor Dal', 'category': 'Pulses'},
            {'name': 'Moong Dal', 'category': 'Pulses'},
            {'name': 'Chana Dal', 'category': 'Pulses'},
            {'name': 'Onion', 'category': 'Vegetables'},
            {'name': 'Tomato', 'category': 'Vegetables'},
            {'name': 'Potato', 'category': 'Vegetables'},
        ]
        
        for prod_data in products_data:
            category = Category.query.filter_by(name=prod_data['category']).first()
            if category:
                normalized_name = normalize_product_name(prod_data['name'])
                # Check if product already exists
                existing = Product.query.filter_by(normalized_name=normalized_name).first()
                if not existing:
                    product = Product(
                        name=prod_data['name'],
                        normalized_name=normalized_name,
                        category_id=category.id,
                        category=prod_data['category']
                    )
                    db.session.add(product)
        
        db.session.commit()
        print("Sample products seeded successfully")
        print("Seeding completed!")

if __name__ == '__main__':
    seed_categories()

