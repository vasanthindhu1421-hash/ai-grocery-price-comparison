import React from 'react';
import { useNavigate } from 'react-router-dom';
import './PriceComparisonList.css';

/**
 * PriceComparisonList component displays prices from multiple stores.
 */
const PriceComparisonList = ({ prices, productName, productId, onPredictionClick }) => {
  const navigate = useNavigate();

  if (!prices || prices.length === 0) {
    return (
      <div className="no-results">
        <p>No prices found for this product.</p>
      </div>
    );
  }

  const handleProductClick = () => {
    if (productId) {
      navigate(`/product/${productId}`);
    }
  };

  // Remove duplicates by store name and filter invalid prices
  const uniquePrices = [];
  const seenStores = new Set();
  
  for (const price of prices) {
    if (!price) continue;
    const store = price.store || price.store_name;
    const priceValue = parseFloat(price.price);
    
    if (store && !seenStores.has(store) && !isNaN(priceValue) && priceValue > 0) {
      seenStores.add(store);
      uniquePrices.push({
        ...price,
        price: priceValue,
        store: store,
        store_name: store
      });
    }
  }
  
  // Sort by price ascending
  uniquePrices.sort((a, b) => a.price - b.price);
  
  // Find the lowest and highest prices
  const lowestPrice = uniquePrices.length > 0 ? uniquePrices[0].price : null;
  const highestPrice = uniquePrices.length > 0 ? uniquePrices[uniquePrices.length - 1].price : null;

  return (
    <div className="price-comparison-container">
      <div className="comparison-header">
        <h2>Price Comparison for "{productName}"</h2>
        {lowestPrice !== null && highestPrice !== null && (
          <div className="price-range">
            <span className="lowest">Lowest: ₹{lowestPrice.toFixed(2)}</span>
            <span className="highest">Highest: ₹{highestPrice.toFixed(2)}</span>
          </div>
        )}
      </div>

      <div className="price-list">
        {uniquePrices.map((price, index) => {
          const store = price.store || price.store_name;
          const productUrl = price.link || price.product_url || '';
          const isLowest = price.price === lowestPrice;
          
          return (
            <div
              key={`${store}-${index}`}
              className={`price-card ${isLowest ? 'best-price' : ''}`}
            >
              <div className="store-info">
                <h3 className="store-name">{store}</h3>
                {isLowest && (
                  <span className="best-badge">Best Price</span>
                )}
              </div>
              <div className="price-info">
                <span className="price-amount">₹{price.price.toFixed(2)}</span>
                <span className="currency">{price.currency || 'INR'}</span>
              </div>
              <div className="stock-info">
                {price.in_stock ? (
                  <span className="in-stock">✓ In Stock</span>
                ) : (
                  <span className="out-of-stock">✗ Out of Stock</span>
                )}
              </div>
              {productUrl && (
                <a
                  href={productUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="store-link"
                >
                  View on {store} →
                </a>
              )}
            </div>
          );
        })}
      </div>

      <div className="action-buttons">
        {productId && (
          <button className="details-button" onClick={handleProductClick}>
            View Product Details
          </button>
        )}
        <button className="predict-button" onClick={onPredictionClick}>
          🤖 Get Price Prediction
        </button>
      </div>
    </div>
  );
};

export default PriceComparisonList;

