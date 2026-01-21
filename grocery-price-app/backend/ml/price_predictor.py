"""
Price prediction module using linear regression.
Predicts future price trends based on real historical data from database.
"""
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from typing import Dict, List
from models import Price


def predict_price_from_history(historical_prices: List[Price], store_name: str = None) -> Dict:
    """
    Predict future price using real historical data from database.
    
    Args:
        historical_prices: List of Price objects from database
        store_name: Optional store name for context
        
    Returns:
        Dictionary with predicted price and trend information
    """
    if len(historical_prices) < 3:
        return {
            'error': 'Not enough historical data for prediction. Need at least 3 price records.',
            'available_records': len(historical_prices)
        }
    
    # Extract prices and timestamps (use scraped_at if available, fallback to recorded_at)
    prices = [float(price.price) for price in historical_prices]
    timestamps = []
    for price in historical_prices:
        # Try scraped_at first, fallback to recorded_at
        if hasattr(price, 'scraped_at') and price.scraped_at:
            timestamps.append(price.scraped_at)
        elif hasattr(price, 'recorded_at') and price.recorded_at:
            timestamps.append(price.recorded_at)
        else:
            from datetime import datetime
            timestamps.append(datetime.utcnow())
    
    # Convert timestamps to days since first record
    first_timestamp = timestamps[0]
    days_since_start = [(ts - first_timestamp).total_seconds() / 86400 for ts in timestamps]
    
    # Prepare data for regression
    X = np.array([[day] for day in days_since_start])
    y = np.array(prices)
    
    # Train linear regression model
    model = LinearRegression()
    model.fit(X, y)
    
    # Get current price (latest)
    current_price = float(prices[-1])
    
    # Predict next 7 days
    future_days = 7
    last_day = days_since_start[-1]
    future_X = np.array([[last_day + i] for i in range(1, future_days + 1)])
    predictions = model.predict(future_X)
    
    # Calculate trend
    trend = model.coef_[0]
    trend_direction = "increasing" if trend > 0 else "decreasing" if trend < 0 else "stable"
    
    # Get prediction for next day
    next_day_price = round(float(predictions[0]), 2)
    
    # Calculate confidence (based on R² score)
    score = model.score(X, y)
    confidence = round(max(0, min(100, score * 100)), 1)
    
    # Calculate moving average for better trend detection
    window_size = min(7, len(prices))
    recent_prices = prices[-window_size:]
    moving_avg = np.mean(recent_prices)
    
    # Calculate price variance for explanation
    price_variance = np.var(prices)
    price_std = np.std(prices)
    
    # Use moving average to improve prediction
    if len(prices) >= 7:
        # Weighted prediction: 70% regression, 30% moving average
        next_day_price = round(0.7 * next_day_price + 0.3 * moving_avg, 2)
    
    # Generate explanation
    explanation = _generate_explanation(trend, current_price, next_day_price, price_std, store_name, len(historical_prices))
    
    return {
        'current_price': round(current_price, 2),
        'predicted_price_1_day': next_day_price,
        'predicted_price_7_days': round(float(predictions[-1]), 2),
        'trend': trend_direction,
        'trend_magnitude': round(abs(trend), 4),
        'confidence': confidence,
        'price_variance': round(price_variance, 2),
        'moving_average': round(moving_avg, 2),
        'explanation': explanation,
        'recommendation': _get_recommendation(trend, current_price, next_day_price),
        'historical_data_points': len(historical_prices)
    }


def _generate_explanation(trend: float, current_price: float, predicted_price: float, 
                         price_std: float, store_name: str = None, data_points: int = 0) -> str:
    """
    Generate explanation for price prediction.
    
    Args:
        trend: Price trend coefficient
        current_price: Current price
        predicted_price: Predicted future price
        price_std: Standard deviation of historical prices
        store_name: Store name for context
        data_points: Number of historical data points
        
    Returns:
        Explanation string
    """
    price_change = predicted_price - current_price
    percent_change = (price_change / current_price) * 100
    
    store_context = f" at {store_name}" if store_name else ""
    
    if abs(percent_change) < 1:
        return f"Price is expected to remain stable{store_context}. Historical data shows low volatility (₹{price_std:.2f} standard deviation) based on {data_points} price records."
    elif percent_change > 0:
        return f"Price is expected to increase by ₹{abs(price_change):.2f} ({abs(percent_change):.1f}%){store_context}. This trend is based on {data_points} historical price points with a standard deviation of ₹{price_std:.2f}."
    else:
        return f"Price is expected to decrease by ₹{abs(price_change):.2f} ({abs(percent_change):.1f}%){store_context}. Historical data shows moderate volatility (₹{price_std:.2f} standard deviation) from {data_points} price records."


def _get_recommendation(trend: float, current_price: float, predicted_price: float) -> str:
    """
    Generate a recommendation based on price prediction.
    
    Args:
        trend: Price trend coefficient
        current_price: Current price
        predicted_price: Predicted future price
        
    Returns:
        Recommendation string
    """
    price_change = predicted_price - current_price
    percent_change = (price_change / current_price) * 100
    
    if percent_change < -5:
        return "Buy now - price expected to increase significantly"
    elif percent_change > 5:
        return "Wait - price expected to decrease significantly"
    elif percent_change < -2:
        return "Good time to buy - price may increase soon"
    elif percent_change > 2:
        return "Consider waiting - price may decrease"
    else:
        return "Price stable - buy when convenient"

