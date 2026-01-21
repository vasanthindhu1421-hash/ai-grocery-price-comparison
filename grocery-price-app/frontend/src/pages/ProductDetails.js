import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getProduct, getPricePrediction } from '../services/api';
import PricePredictionBadge from '../components/PricePredictionBadge';
import './ProductDetails.css';

/**
 * ProductDetails page component.
 */
const ProductDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const data = await getProduct(id);
        setProduct(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchProduct();
    }
  }, [id]);

  const handleGetPrediction = async () => {
    if (!product) return;

    setLoading(true);
    try {
      const predData = await getPricePrediction({
        product_id: product.id,
        product_name: product.name,
      });
      setPrediction(predData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !product) {
    return <div className="loading">Loading product details...</div>;
  }

  if (error) {
    return (
      <div className="error-container">
        <p>❌ {error}</p>
        <button onClick={() => navigate('/')}>Go Back Home</button>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="error-container">
        <p>Product not found</p>
        <button onClick={() => navigate('/')}>Go Back Home</button>
      </div>
    );
  }

  const prices = product.prices || [];
  const lowestPrice = prices.length > 0 ? Math.min(...prices.map(p => p.price)) : null;

  return (
    <div className="product-details-page">
      <button className="back-button" onClick={() => navigate('/')}>
        ← Back to Search
      </button>

      <div className="product-header">
        <h1>{product.name}</h1>
        {product.category && (
          <span className="category-badge">{product.category}</span>
        )}
      </div>

      {product.description && (
        <p className="product-description">{product.description}</p>
      )}

      {prices.length > 0 && (
        <div className="prices-section">
          <h2>Available Prices</h2>
          <div className="price-cards">
            {prices.map((price) => (
              <div
                key={price.id}
                className={`price-card ${price.price === lowestPrice ? 'best-price' : ''}`}
              >
                <div className="store-name">{price.store_name}</div>
                <div className="price">₹{price.price.toFixed(2)}</div>
                <div className="stock-status">
                  {price.in_stock ? '✓ In Stock' : '✗ Out of Stock'}
                </div>
                {price.link && (
                  <a
                    href={price.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="store-link"
                  >
                    Visit Store →
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="prediction-section">
        <button
          className="predict-button"
          onClick={handleGetPrediction}
          disabled={loading}
        >
          🤖 Get AI Price Prediction
        </button>
      </div>

      {prediction && (
        <PricePredictionBadge
          prediction={prediction}
          onClose={() => setPrediction(null)}
        />
      )}
    </div>
  );
};

export default ProductDetails;

