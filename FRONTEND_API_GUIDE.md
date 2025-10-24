# Crown Mega Store - Frontend Developer API Guide

## Overview
This guide contains all API endpoints, database schema, required forms, and page specifications for the Crown Mega Store frontend development.

**Base URL**: `http://localhost:8000` (development)  
**API Base**: `/api`

---

## 🔐 Authentication System

### Google OAuth Implementation
**Required**: Implement Google OAuth signin button

#### API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/auth/google` | Authenticate with Google token | No |
| `GET` | `/api/auth/me` | Get current user info | Yes |
| `POST` | `/api/auth/logout` | Logout user | Yes |
| `GET` | `/api/auth/verify` | Verify token validity | Yes |

#### Request/Response Examples

**POST /api/auth/google**
```json
// Request
{
  "token": "google_oauth_token_here"
}

// Response
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "customer",
    "avatar_url": "https://...",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

#### Frontend Implementation Required
- **Google OAuth Integration**: Use Google Sign-In library
- **Token Storage**: Store JWT in localStorage/httpOnly cookies
- **Auto-redirect**: Redirect to dashboard/profile after login
- **Auth Guard**: Protect authenticated routes
- **Header Authorization**: Include `Authorization: Bearer <token>` in requests

---

## 🛍️ Product Catalog System

### Database Schema - Products Table
```sql
products {
  id: UUID (Primary Key)
  name: VARCHAR(255)
  description: TEXT
  price: DECIMAL(10,2)
  category: VARCHAR(100)
  image_url: VARCHAR(500)
  stock_quantity: INTEGER
  view_count: INTEGER (default: 0)
  order_count: INTEGER (default: 0)
  rating: DECIMAL(3,2) (default: 0.00)
  is_featured: BOOLEAN (default: false)
  is_new: BOOLEAN (default: false)
  created_at: TIMESTAMP
  updated_at: TIMESTAMP
}
```

### API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/products/` | Get all products with filters | No |
| `GET` | `/api/products/search` | Search products | No |
| `GET` | `/api/products/categories` | Get all categories | No |
| `GET` | `/api/products/{product_id}` | Get single product | No |
| `POST` | `/api/products/` | Create product | Admin Only |
| `PUT` | `/api/products/{product_id}` | Update product | Admin Only |
| `DELETE` | `/api/products/{product_id}` | Delete product | Admin Only |

### Query Parameters for GET /api/products/
- `category`: Filter by category (optional)
- `sort_by`: `balanced|popularity|price_low|price_high|newest|rating` (default: balanced)
- `limit`: Products per page (default: 50, max: 100)
- `page`: Page number (default: 1)

### Frontend Pages Required

#### 1. **Shop/Products Listing Page** (`/shop`)
**Components Needed**:
- Product grid/list view toggle
- Category filter sidebar
- Sort dropdown
- Pagination
- Search bar
- Loading states

**Data to Display**:
- Product image
- Product name
- Price
- Category
- Stock status
- "Add to Cart" button
- Quick view option

**Forms Required**: None (just filters)

#### 2. **Product Details Page** (`/product/{id}`)
**Components Needed**:
- Image gallery/carousel
- Product information panel
- Quantity selector
- Add to cart form
- Related products section
- Reviews section (if implemented)

**Data to Display**:
- All product fields
- Stock quantity
- Category
- Description
- Related products

**Forms Required**:
- Add to Cart form (quantity selector)

#### 3. **Search Results Page** (`/search`)
**API Call**: `GET /api/products/search?q={query}&limit=20`

---

## 🛒 Shopping Cart System

### Database Schema - Cart Tables
```sql
cart_items {
  id: UUID (Primary Key)
  user_id: UUID (Foreign Key to users)
  product_id: UUID (Foreign Key to products)
  quantity: INTEGER
  created_at: TIMESTAMP
  updated_at: TIMESTAMP
}

-- View: cart_details (joins cart_items with products)
cart_details {
  id: UUID
  user_id: UUID
  product_id: UUID
  product_name: VARCHAR
  price: DECIMAL
  quantity: INTEGER
  image_url: VARCHAR
  stock_quantity: INTEGER
  category: VARCHAR
  subtotal: DECIMAL (calculated)
  created_at: TIMESTAMP
  updated_at: TIMESTAMP
}
```

### API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/cart/` | Get user's cart | Yes |
| `POST` | `/api/cart/add` | Add item to cart | Yes |
| `PUT` | `/api/cart/update/{product_id}` | Update item quantity | Yes |
| `DELETE` | `/api/cart/remove/{product_id}` | Remove item from cart | Yes |
| `DELETE` | `/api/cart/clear` | Clear entire cart | Yes |
| `GET` | `/api/cart/count` | Get cart items count | Yes |
| `POST` | `/api/cart/sync` | Sync local cart with DB | Yes |

### Request/Response Examples

**POST /api/cart/add**
```json
// Request
{
  "product_id": "product-uuid",
  "quantity": 2
}

// Response
{
  "success": true,
  "message": "Item added to cart successfully",
  "action": "added",
  "item_id": "cart-item-uuid",
  "quantity": 2
}
```

**GET /api/cart/**
```json
// Response
{
  "items": [
    {
      "id": "cart-item-uuid",
      "product_id": "product-uuid",
      "product_name": "Product Name",
      "price": 29.99,
      "quantity": 2,
      "image_url": "https://...",
      "stock_quantity": 50,
      "category": "Electronics",
      "subtotal": 59.98,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 59.98,
  "item_count": 1
}
```

### Frontend Pages Required

#### 1. **Shopping Cart Page** (`/cart`)
**Components Needed**:
- Cart items list
- Quantity update controls
- Remove item buttons
- Cart summary
- Checkout button
- Empty cart state

**Forms Required**:
- Quantity update form (per item)
- Clear cart confirmation

#### 2. **Cart Sidebar/Dropdown** (Global Component)
**Components Needed**:
- Mini cart preview
- Item count badge
- Quick access to full cart

---

## 📦 Order Management System

### Database Schema - Orders Tables
```sql
orders {
  id: UUID (Primary Key)
  order_id: VARCHAR(20) (Unique, format: ORD4F7B2A1E)
  user_id: UUID (Foreign Key, nullable for guest orders)
  customer_name: VARCHAR(255)
  customer_email: VARCHAR(255)
  customer_phone: VARCHAR(20)
  delivery_address: TEXT (nullable)
  pickup_preference: BOOLEAN (default: false)
  order_notes: TEXT (nullable)
  payment_preference: VARCHAR(50) (default: 'bank_transfer')
  total: DECIMAL(10,2)
  status: VARCHAR(50) (pending|confirmed|payment_received|processing|shipped|delivered|cancelled)
  payment_confirmed: BOOLEAN (default: false)
  payment_amount: DECIMAL(10,2) (nullable)
  payment_method: VARCHAR(50) (nullable)
  created_at: TIMESTAMP
  updated_at: TIMESTAMP
}

order_items {
  id: UUID (Primary Key)
  order_id: UUID (Foreign Key to orders)
  product_id: UUID (Foreign Key to products)
  product_name: VARCHAR(255)
  quantity: INTEGER
  price: DECIMAL(10,2)
  created_at: TIMESTAMP
}

order_status_history {
  id: UUID (Primary Key)
  order_id: UUID (Foreign Key to orders)
  status: VARCHAR(50)
  updated_by: VARCHAR(100)
  notes: TEXT (nullable)
  created_at: TIMESTAMP
}
```

### API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/orders/checkout` | Create new order | Optional |
| `GET` | `/api/orders/{order_id}` | Get order details | No |
| `GET` | `/api/orders/user/my-orders` | Get user's orders | Yes |
| `POST` | `/api/orders/{order_id}/status` | Update order status | Admin Only |
| `POST` | `/api/orders/{order_id}/payment` | Record payment | Admin Only |
| `GET` | `/api/orders/` | Get all orders | Admin Only |
| `GET` | `/api/orders/stats/dashboard` | Order statistics | Admin Only |

### Order Status Flow
1. **pending** → Order created, awaiting confirmation
2. **confirmed** → Order confirmed by admin
3. **payment_received** → Payment confirmed
4. **processing** → Order being prepared
5. **shipped** → Order shipped
6. **delivered** → Order delivered
7. **cancelled** → Order cancelled

### Request/Response Examples

**POST /api/orders/checkout**
```json
// Request
{
  "items": [
    {
      "product_id": "product-uuid",
      "product_name": "Product Name",
      "quantity": 2,
      "price": 29.99
    }
  ],
  "customer_info": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+2348012345678",
    "delivery_address": "123 Main St, Lagos, Nigeria",
    "pickup_preference": false,
    "order_notes": "Please call before delivery",
    "payment_preference": "bank_transfer"
  }
}

// Response
{
  "success": true,
  "message": "Order created successfully! Check your email for confirmation.",
  "order_id": "ORD4F7B2A1E",
  "total": 59.98,
  "status": "pending"
}
```

### Frontend Pages Required

#### 1. **Checkout Page** (`/checkout`)
**Form Fields Required**:
```javascript
{
  // Customer Information
  name: string (required),
  email: string (required, email validation),
  phone: string (required, Nigerian phone format),
  
  // Delivery Options
  delivery_address: string (required if pickup_preference = false),
  pickup_preference: boolean (default: false),
  
  // Additional Information
  order_notes: string (optional),
  payment_preference: string (default: 'bank_transfer')
}
```

**Components Needed**:
- Order summary sidebar
- Customer information form
- Delivery options toggle
- Payment preference selection
- Terms and conditions checkbox
- Submit order button

**Validation Rules**:
- Nigerian phone format: `+234XXXXXXXXX` or `0XXXXXXXXX`
- Email validation
- Required fields validation
- Address required if not pickup

#### 2. **Order Confirmation Page** (`/order/{order_id}`)
**Data to Display**:
- Order ID and status
- Customer information
- Ordered items with quantities and prices
- Total amount
- Order timeline/status history
- Contact information for support

#### 3. **My Orders Page** (`/account/orders`) - Authenticated Users Only
**Components Needed**:
- Orders list with filters
- Order status badges
- Quick actions (view details, track order)
- Pagination for large order lists

**API Calls**:
- `GET /api/orders/user/my-orders?status={status}`

#### 4. **Order Tracking Page** (`/track/{order_id}`)
**Components Needed**:
- Order status timeline
- Estimated delivery date
- Tracking information (if available)
- Contact information

---

## 🤖 Recommendations System

### Database Schema - User Activities Table
```sql
user_activities {
  id: UUID (Primary Key)
  user_id: UUID (Foreign Key to users)
  product_id: UUID (Foreign Key to products)
  activity_type: VARCHAR(50) (view|purchase|add_to_cart)
  category: VARCHAR(100)
  created_at: TIMESTAMP
}
```

### API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/recommendations/for-you` | Personalized recommendations | Yes |
| `GET` | `/api/recommendations/similar/{product_id}` | Similar products | No |
| `GET` | `/api/recommendations/trending` | Trending products | No |
| `GET` | `/api/recommendations/popular` | Popular products | No |
| `POST` | `/api/recommendations/track` | Track user activity | Yes |

### Activity Tracking

**POST /api/recommendations/track**
```json
// Request
{
  "product_id": "product-uuid",
  "activity_type": "view" // or "purchase", "add_to_cart"
}
```

**When to Track**:
- `view`: When user visits product details page
- `add_to_cart`: When user adds item to cart
- `purchase`: When user completes order (handled automatically)

### Frontend Implementation

#### Recommendation Sections to Add

1. **Homepage**:
   - "For You" section (personalized)
   - "Trending Now" section
   - "Popular Products" section

2. **Product Details Page**:
   - "Similar Products" section
   - "You Might Also Like" section

3. **After Adding to Cart**:
   - "Frequently Bought Together" section

**API Calls Example**:
```javascript
// Get personalized recommendations (8 products)
GET /api/recommendations/for-you?limit=8

// Get similar products (6 products)
GET /api/recommendations/similar/{productId}?limit=6

// Track product view
POST /api/recommendations/track
{
  "product_id": "uuid",
  "activity_type": "view"
}
```

---

## 👨‍💼 Admin Dashboard System

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/orders/stats/dashboard` | Order statistics |
| `GET` | `/api/orders/` | All orders with pagination |
| `POST` | `/api/orders/{order_id}/status` | Update order status |
| `POST` | `/api/orders/{order_id}/payment` | Record payment |
| `POST` | `/api/products/` | Create product |
| `PUT` | `/api/products/{product_id}` | Update product |
| `DELETE` | `/api/products/{product_id}` | Delete product |

### Admin Dashboard Stats Response
```json
{
  "total_orders": 150,
  "total_revenue": 45000.00,
  "pending_orders": 12,
  "confirmed_orders": 8,
  "completed_orders": 125,
  "recent_orders_count": 15,
  "average_order_value": 300.00,
  "status_breakdown": {
    "pending": 12,
    "confirmed": 8,
    "processing": 5,
    "shipped": 3,
    "delivered": 125,
    "cancelled": 2
  },
  "payment_confirmed_count": 140
}
```

### Frontend Admin Pages Required

#### 1. **Admin Dashboard** (`/admin/dashboard`)
**Components Needed**:
- Statistics cards (revenue, orders, etc.)
- Recent orders table
- Status breakdown charts
- Quick actions panel

#### 2. **Orders Management** (`/admin/orders`)
**Components Needed**:
- Orders table with sorting/filtering
- Status update modal
- Payment recording modal
- Order details view
- Export functionality

**Forms Required**:
- Status update form
- Payment recording form

#### 3. **Products Management** (`/admin/products`)
**Components Needed**:
- Products table with CRUD operations
- Add/Edit product modal
- Image upload
- Category management
- Inventory tracking

**Product Form Fields**:
```javascript
{
  name: string (required),
  description: string (optional),
  price: number (required, min: 0.01),
  category: string (required),
  image_url: string (optional),
  stock_quantity: number (required, min: 0),
  is_featured: boolean (default: false),
  is_new: boolean (default: false)
}
```

---

## 🎨 Frontend Implementation Guidelines

### 1. **State Management Requirements**
- User authentication state
- Shopping cart state (sync with backend)
- Product filters and search state
- Loading states for all API calls

### 2. **Required Pages Summary**

| Page | Route | Auth Required | Key Features |
|------|-------|---------------|--------------|
| Homepage | `/` | No | Hero, featured products, recommendations |
| Products | `/shop` | No | Product grid, filters, search, pagination |
| Product Details | `/product/{id}` | No | Product info, add to cart, similar products |
| Search Results | `/search` | No | Search results with filters |
| Cart | `/cart` | Optional | Cart items, quantity controls, checkout |
| Checkout | `/checkout` | Optional | Customer form, order summary |
| Order Confirmation | `/order/{id}` | No | Order details, next steps |
| My Orders | `/account/orders` | Yes | Order history, status tracking |
| Profile | `/account/profile` | Yes | User information, settings |
| Admin Dashboard | `/admin/dashboard` | Admin | Statistics, quick overview |
| Admin Orders | `/admin/orders` | Admin | Order management |
| Admin Products | `/admin/products` | Admin | Product CRUD operations |

### 3. **Form Validation Requirements**

#### Customer Information Form (Checkout)
```javascript
const validationRules = {
  name: {
    required: true,
    minLength: 2,
    pattern: /^[a-zA-Z\s]+$/
  },
  email: {
    required: true,
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  },
  phone: {
    required: true,
    pattern: /^(\+?234|0)?[789]\d{9}$/ // Nigerian phone format
  },
  delivery_address: {
    required: !pickup_preference,
    minLength: 10
  }
}
```

#### Product Form (Admin)
```javascript
const productValidation = {
  name: { required: true, minLength: 3, maxLength: 255 },
  price: { required: true, min: 0.01, type: 'number' },
  category: { required: true },
  stock_quantity: { required: true, min: 0, type: 'integer' },
  description: { maxLength: 1000 },
  image_url: { pattern: /^https?:\/\/.+/ }
}
```

### 4. **Error Handling**
- Display user-friendly error messages
- Handle network errors gracefully
- Show loading states during API calls
- Implement retry mechanisms for failed requests

### 5. **SEO and Performance**
- Implement meta tags for product pages
- Use lazy loading for product images
- Implement proper pagination
- Cache frequently accessed data

### 6. **Mobile Responsiveness**
- Responsive product grid
- Mobile-friendly navigation
- Touch-friendly buttons and forms
- Optimized mobile checkout flow

---

## 🔧 Environment Configuration

### Frontend Environment Variables Needed
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id
REACT_APP_BUSINESS_WHATSAPP=+2348012345678
REACT_APP_BUSINESS_PHONE=+2341234567
REACT_APP_BUSINESS_EMAIL=orders@crownmegastore.com
```

---

## 📧 Email Notifications (Automatic)

The backend automatically sends emails for:
- Order confirmation (to customer and business)
- Order status updates
- Payment confirmations
- Welcome emails for new users

**Frontend**: No email handling required - all handled by backend.

---

## 🚀 Getting Started Checklist

### Phase 1: Core Functionality
- [ ] Set up Google OAuth authentication
- [ ] Implement product listing and search
- [ ] Build product details page
- [ ] Create shopping cart functionality
- [ ] Implement checkout process

### Phase 2: User Features
- [ ] Add user dashboard/profile
- [ ] Implement order tracking
- [ ] Add recommendations sections
- [ ] Build responsive design

### Phase 3: Admin Features
- [ ] Create admin dashboard
- [ ] Implement order management
- [ ] Build product management
- [ ] Add analytics and reporting

### Phase 4: Enhancement
- [ ] Add performance optimizations
- [ ] Implement advanced filtering
- [ ] Add wishlist functionality
- [ ] Mobile app considerations

---

## ⚡ Quick Start API Testing

Use these endpoints to test basic functionality:

```bash
# Get all products
curl http://localhost:8000/api/products/

# Search products
curl "http://localhost:8000/api/products/search?q=phone"

# Get categories
curl http://localhost:8000/api/products/categories

# Health check
curl http://localhost:8000/api/health
```

---

## 📞 Support & Contact

**Backend Developer**: For API issues and questions  
**Business Email**: orders@crownmegastore.com  
**WhatsApp**: +2348012345678  

**API Documentation**: Available at `http://localhost:8000/docs` when server is running.