"""
Price prediction API routes.
"""
from flask import Blueprint, request, jsonify
from ml.price_predictor import predict_price_from_history
from models import Product, Price
from utils import token_required

predict_bp = Blueprint('predict', __name__, url_prefix='')


@predict_bp.route('/predict', methods=['POST'])
@token_required
def predict():
    """
    Predict future price trends for a product using real historical data.
    Requires authentication.
    
    Expected JSON:
    {
        "product_id": 1,  // optional, can use product_name instead
        "product_name": "milk",  // optional
        "store_name": "BigBasket"  // optional, predict for specific store
    }
    """
    try:
        data = request.get_json()
        
        product = None
        store_name = data.get('store_name') if data else None
        
        # Get product
        if data and 'product_id' in data:
            product = Product.query.get(data['product_id'])
        elif data and 'product_name' in data:
            from utils import normalize_product_name
            normalized_name = normalize_product_name(data['product_name'])
            product = Product.query.filter_by(normalized_name=normalized_name).first()
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Get historical prices from database
        price_query = Price.query.filter_by(product_id=product.id)
        if store_name:
            price_query = price_query.filter_by(store_name=store_name)
        
        # Use scraped_at if available, fallback to recorded_at for backward compatibility
        try:
            historical_prices = price_query.order_by(Price.scraped_at.asc()).all()
        except:
            # Fallback for old schema
            historical_prices = price_query.order_by(Price.recorded_at.asc()).all()
        
        if len(historical_prices) < 3:
            return jsonify({
                'product_id': product.id,
                'product_name': product.name,
                'error': 'Not enough historical data for prediction. Need at least 3 price records.',
                'available_records': len(historical_prices)
            }), 400
        
        # Get prediction using real historical data
        prediction = predict_price_from_history(historical_prices, store_name)
        
        return jsonify({
            'product_id': product.id,
            'product_name': product.name,
            'store_name': store_name,
            'prediction': prediction
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

