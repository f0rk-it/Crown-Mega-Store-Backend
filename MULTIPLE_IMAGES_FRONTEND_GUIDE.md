# Frontend Integration Guide for Multiple Product Images

## Overview
This guide explains how to integrate the new multiple images feature into your frontend application.

## API Changes

### 1. Product Response Format
Products now include an `images` array:

```json
{
  "id": "product-id",
  "name": "Product Name",
  "price": 29.99,
  "image_url": "legacy-image.jpg",  // Still available for backward compatibility
  "images": [
    {
      "id": "image-id-1",
      "product_id": "product-id",
      "image_url": "https://example.com/image1.jpg",
      "alt_text": "Product front view",
      "display_order": 0,
      "is_primary": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": "image-id-2",
      "product_id": "product-id",
      "image_url": "https://example.com/image2.jpg",
      "alt_text": "Product side view",
      "display_order": 1,
      "is_primary": false,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 2. Creating Products with Multiple Images

**POST /products/**
```json
{
  "name": "Nike Air Max 270",
  "description": "Comfortable running shoes",
  "price": 129.99,
  "category": "shoes",
  "stock_quantity": 50,
  "is_featured": true,
  "images": [
    {
      "image_url": "https://example.com/nike-270-black.jpg",
      "alt_text": "Nike Air Max 270 - Black",
      "display_order": 0,
      "is_primary": true
    },
    {
      "image_url": "https://example.com/nike-270-white.jpg", 
      "alt_text": "Nike Air Max 270 - White",
      "display_order": 1,
      "is_primary": false
    }
  ]
}
```

### 3. Additional Image Management Endpoints

- `GET /products/{product_id}/images` - Get all images for a product
- `POST /products/{product_id}/images` - Add new images to a product
- `PUT /products/{product_id}/images` - Replace all images for a product
- `DELETE /products/{product_id}/images` - Delete all images for a product

## Frontend Components

### 1. Product Image Gallery Component

```jsx
// ProductImageGallery.jsx
import React, { useState } from 'react';

const ProductImageGallery = ({ product }) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  
  // Handle both new images array and legacy image_url
  const images = product.images?.length > 0 ? product.images : 
    product.image_url ? [{ image_url: product.image_url, alt_text: product.name }] : [];
  
  const currentImage = images[currentImageIndex];

  if (!images.length) {
    return <div className="no-image">No images available</div>;
  }

  return (
    <div className="product-gallery">
      {/* Main Image */}
      <div className="main-image">
        <img 
          src={currentImage.image_url} 
          alt={currentImage.alt_text || product.name}
          className="w-full h-96 object-cover"
        />
      </div>
      
      {/* Thumbnail Navigation */}
      {images.length > 1 && (
        <div className="thumbnails flex space-x-2 mt-4">
          {images.map((image, index) => (
            <button
              key={image.id || index}
              onClick={() => setCurrentImageIndex(index)}
              className={`thumbnail ${index === currentImageIndex ? 'active' : ''}`}
            >
              <img 
                src={image.image_url} 
                alt={image.alt_text || `${product.name} ${index + 1}`}
                className="w-16 h-16 object-cover border-2"
              />
            </button>
          ))}
        </div>
      )}
      
      {/* Navigation Arrows */}
      {images.length > 1 && (
        <div className="image-navigation">
          <button 
            onClick={() => setCurrentImageIndex((prev) => 
              prev === 0 ? images.length - 1 : prev - 1
            )}
            className="nav-button prev"
          >
            &#8249;
          </button>
          <button 
            onClick={() => setCurrentImageIndex((prev) => 
              prev === images.length - 1 ? 0 : prev + 1
            )}
            className="nav-button next"
          >
            &#8250;
          </button>
        </div>
      )}
    </div>
  );
};

export default ProductImageGallery;
```

### 2. Product Card Component (for listings)

```jsx
// ProductCard.jsx  
import React from 'react';

const ProductCard = ({ product }) => {
  // Get primary image or first available image
  const primaryImage = product.images?.find(img => img.is_primary) || 
                      product.images?.[0] || 
                      (product.image_url ? { image_url: product.image_url, alt_text: product.name } : null);

  return (
    <div className="product-card">
      {primaryImage ? (
        <img 
          src={primaryImage.image_url} 
          alt={primaryImage.alt_text || product.name}
          className="product-card-image"
        />
      ) : (
        <div className="no-image-placeholder">No Image</div>
      )}
      
      <div className="product-info">
        <h3>{product.name}</h3>
        <p>${product.price}</p>
        {product.images?.length > 1 && (
          <span className="image-count">+{product.images.length - 1} more</span>
        )}
      </div>
    </div>
  );
};

export default ProductCard;
```

### 3. Admin Product Form Component

```jsx
// AdminProductForm.jsx
import React, { useState } from 'react';

const AdminProductForm = ({ onSubmit, initialProduct = null }) => {
  const [product, setProduct] = useState(initialProduct || {
    name: '',
    description: '',
    price: '',
    category: '',
    stock_quantity: '',
    is_featured: false,
    is_new: false,
    images: []
  });

  const [newImage, setNewImage] = useState({
    image_url: '',
    alt_text: '',
    display_order: 0,
    is_primary: false
  });

  const addImage = () => {
    if (!newImage.image_url) return;
    
    setProduct(prev => ({
      ...prev,
      images: [...prev.images, { ...newImage, display_order: prev.images.length }]
    }));
    
    setNewImage({
      image_url: '',
      alt_text: '',
      display_order: 0,
      is_primary: false
    });
  };

  const removeImage = (index) => {
    setProduct(prev => ({
      ...prev,
      images: prev.images.filter((_, i) => i !== index)
    }));
  };

  const moveImage = (fromIndex, toIndex) => {
    setProduct(prev => {
      const newImages = [...prev.images];
      const [moved] = newImages.splice(fromIndex, 1);
      newImages.splice(toIndex, 0, moved);
      
      // Update display_order
      newImages.forEach((img, i) => {
        img.display_order = i;
      });
      
      return { ...prev, images: newImages };
    });
  };

  const setPrimaryImage = (index) => {
    setProduct(prev => ({
      ...prev,
      images: prev.images.map((img, i) => ({
        ...img,
        is_primary: i === index
      }))
    }));
  };

  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit(product); }}>
      {/* Basic product fields */}
      <div className="form-group">
        <label>Product Name</label>
        <input 
          type="text" 
          value={product.name}
          onChange={(e) => setProduct(prev => ({ ...prev, name: e.target.value }))}
          required
        />
      </div>
      
      <div className="form-group">
        <label>Price</label>
        <input 
          type="number" 
          step="0.01"
          value={product.price}
          onChange={(e) => setProduct(prev => ({ ...prev, price: parseFloat(e.target.value) }))}
          required
        />
      </div>

      {/* Images section */}
      <div className="form-group">
        <label>Product Images</label>
        
        {/* Current images */}
        <div className="current-images">
          {product.images.map((image, index) => (
            <div key={index} className="image-item flex items-center space-x-2 mb-2">
              <img 
                src={image.image_url} 
                alt={image.alt_text}
                className="w-16 h-16 object-cover"
              />
              <div className="flex-1">
                <input 
                  type="text" 
                  placeholder="Alt text"
                  value={image.alt_text}
                  onChange={(e) => {
                    const newImages = [...product.images];
                    newImages[index].alt_text = e.target.value;
                    setProduct(prev => ({ ...prev, images: newImages }));
                  }}
                />
              </div>
              <button 
                type="button" 
                onClick={() => setPrimaryImage(index)}
                className={image.is_primary ? 'primary-btn active' : 'primary-btn'}
              >
                Primary
              </button>
              <button type="button" onClick={() => removeImage(index)}>Remove</button>
            </div>
          ))}
        </div>

        {/* Add new image */}
        <div className="add-image-form">
          <input 
            type="url" 
            placeholder="Image URL"
            value={newImage.image_url}
            onChange={(e) => setNewImage(prev => ({ ...prev, image_url: e.target.value }))}
          />
          <input 
            type="text" 
            placeholder="Alt text"
            value={newImage.alt_text}
            onChange={(e) => setNewImage(prev => ({ ...prev, alt_text: e.target.value }))}
          />
          <button type="button" onClick={addImage}>Add Image</button>
        </div>
      </div>

      <button type="submit">Save Product</button>
    </form>
  );
};

export default AdminProductForm;
```

## Migration Strategy

1. **Deploy backend changes first**
2. **Run the database migration script**
3. **Update frontend gradually:**
   - Start by updating product display components to handle both old and new image formats
   - Update admin forms to support multiple images
   - Test thoroughly with existing products

## Backward Compatibility

The system maintains full backward compatibility:
- Existing products with `image_url` will still work
- API responses include both `image_url` (for legacy) and `images` array
- Frontend code can gradually migrate to use the new `images` array
- Legacy `image_url` field can eventually be removed after full migration