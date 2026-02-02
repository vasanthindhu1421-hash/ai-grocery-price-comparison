import React from 'react';
import './CategoryGrid.css';

/**
 * CategoryGrid component displays product categories in a grid layout.
 */
const CategoryGrid = ({ categories, onCategoryClick }) => {
  if (!categories || categories.length === 0) {
    return null;
  }

  const getCategoryIcon = (categoryName) => {
    const icons = {
      'Dairy': '🥛',
      'Grains': '🌾',
      'Oils': '🛢️',
      'Pulses': '🫘',
      'Vegetables': '🥬'
    };
    return icons[categoryName] || '🛒';
  };

  return (
    <div className="category-grid-container">
      <h2 className="category-grid-title">Browse by Category</h2>
      <div className="category-grid">
        {categories.map((category) => (
          <div
            key={category.id}
            className="category-card"
            onClick={() => onCategoryClick(category)}
          >
            <div className="category-image-container">
              {category.image_url ? (
                <img
                  src={category.image_url}
                  alt={category.name}
                  className="category-image"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'block';
                  }}
                />
              ) : null}
              <div className="category-icon" style={{ display: category.image_url ? 'none' : 'block' }}>
                {getCategoryIcon(category.name)}
              </div>
            </div>
            <h3 className="category-name">{category.name}</h3>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CategoryGrid;

