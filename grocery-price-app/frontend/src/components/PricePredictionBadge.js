import React from 'react';
import './PricePredictionBadge.css';

/**
 * PricePredictionBadge component displays AI price prediction.
 */
const PricePredictionBadge = ({ prediction, onClose }) => {
  if (!prediction) return null;

  const { prediction: predData } = prediction;
  if (!predData) return null;

  const getTrendIcon = (trend) => {
    if (trend === 'increasing') return '📈';
    if (trend === 'decreasing') return '📉';
    return '➡️';
  };

  const getTrendColor = (trend) => {
    if (trend === 'increasing') return '#dc3545';
    if (trend === 'decreasing') return '#28a745';
    return '#666';
  };

  return (
    <div className="prediction-modal-overlay" onClick={onClose}>
      <div className="prediction-modal" onClick={(e) => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>×</button>
        
        <div className="prediction-header">
          <h2>🤖 AI Price Prediction</h2>
          <p className="product-name">{prediction.product_name}</p>
        </div>

        <div className="prediction-content">
          {predData.error ? (
            <div className="error-message">
              <p>{predData.error}</p>
              {predData.available_records !== undefined && (
                <p>Available records: {predData.available_records}</p>
              )}
            </div>
          ) : (
            <>
              <div className="current-price-section">
                <span className="label">Current Price:</span>
                <span className="value">₹{predData.current_price}</span>
              </div>

              <div className="predicted-prices">
                <div className="prediction-item">
                  <span className="label">Predicted (1 day):</span>
                  <span 
                    className="value"
                    style={{ color: getTrendColor(predData.trend) }}
                  >
                    ₹{predData.predicted_price_1_day}
                    <span className="trend-icon">{getTrendIcon(predData.trend)}</span>
                  </span>
                </div>
                <div className="prediction-item">
                  <span className="label">Predicted (7 days):</span>
                  <span 
                    className="value"
                    style={{ color: getTrendColor(predData.trend) }}
                  >
                    ₹{predData.predicted_price_7_days}
                  </span>
                </div>
              </div>

              <div className="trend-section">
                <div className="trend-info">
                  <span className="label">Trend:</span>
                  <span 
                    className="trend-value"
                    style={{ color: getTrendColor(predData.trend) }}
                  >
                    {predData.trend.toUpperCase()}
                  </span>
                </div>
                <div className="confidence">
                  <span className="label">Confidence:</span>
                  <span className="value">{predData.confidence}%</span>
                </div>
              </div>

              {predData.explanation && (
                <div className="explanation">
                  <strong>📊 Analysis:</strong>
                  <p>{predData.explanation}</p>
                </div>
              )}

              <div className="recommendation">
                <strong>💡 Recommendation:</strong>
                <p>{predData.recommendation}</p>
              </div>

              {predData.historical_data_points && (
                <div className="data-info">
                  <small>Based on {predData.historical_data_points} historical price points</small>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default PricePredictionBadge;

