from typing import List, Optional
from app.core.database import get_db
from datetime import datetime, timedelta


class ProductService:
    
    @staticmethod
    def calculate_product_score(product: dict, strategy: str = 'balanced') -> float:
        """Calculate product ranking score"""
        if strategy == 'popularity':
            return (product.get('view_count', 0) * 0.3) + (product.get('order_count', 0) * 0.7)
        
        elif strategy == 'balanced':
            popularity = (product.get('view_count', 0) * 0.2) + (product.get('order_count', 0) * 0.4)
            rating_score = float(product.get('rating', 0)) * 20
            stock_score = min(product.get('stock_quantity', 0), 20)
            
            boost = 0
            if product.get('is_featured'):
                boost += 50
            if product.get('is_new'):
                boost += 30
            
            return popularity + rating_score + stock_score + boost
        return 0
    
    @staticmethod
    def get_all_products(
        category: Optional[str] = None,
        sort_by: str = 'balanced',
        limit: int = 50,
        offset: int = 0
    ):
        """Get products with filtering and sorting"""
        db = get_db()
        
        # Build query
        query = db.table('products').select('*')
        
        if category:
            query = query.eq('category', category)
        
        # Execute query
        result = query.execute()
        products = result.data
        
        # Apply sorting
        if sort_by == 'balanced':
            products.sort(key=lambda p: ProductService.calculate_product_score(p, 'balanced'), reverse=True)
        elif sort_by == 'popularity':
            products.sort(key=lambda p: ProductService.calculate_product_score(p, 'popularity'), reverse=True)
        elif sort_by == 'price_low':
            products.sort(key=lambda p: float(p['price']))
        elif sort_by == 'price_high':
            products.sort(key=lambda p: float(p['price']), reverse=True)
        elif sort_by == 'newest':
            products.sort(key=lambda p: p['created_at'], reverse=True)
        elif sort_by == 'rating':
            products.sort(key=lambda p: float(p.get('rating', 0)), reverse=True)
        
        # Apply pagination
        paginated_products = products[offset:offset + limit]
        
        return {
            'products': paginated_products,
            'total_count': len(products),
            'page': offset // limit + 1,
            'page_size': limit
        }
    
    @staticmethod
    def get_product_by_id(product_id: str):
        """Get single product by ID"""
        db = get_db()
        result = db.table('products').select('*').eq('id', product_id).execute()
        
        if not result.data:
            return None
        
        return result.data[0]
    
    @staticmethod
    def increment_view_count(product_id: str):
        """Increment product view count"""
        db = get_db()
        product = ProductService.get_product_by_id(product_id)
        
        if product:
            new_count = product.get('view_count', 0) + 1
            db.table('products').update({
                'view_count': new_count,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', product_id).execute()
        
    @staticmethod
    def search_products(search_term: str, limit: int = 20):
        """Search products by name or description"""
        db = get_db()
        
        result = db.table('products').select('*').execute()
        products = result.data
        
        # Filter by search term
        search_lower = search_term.lower()
        filtered = [
            p for p in products
            if search_lower in p['name'].lower() or (p.get('description') and search_lower in p['description'].lower())
        ]        
        
        return filtered[:limit]
    
    @staticmethod
    def get_categories():
        """Get all unique product categories"""
        db = get_db()
        result = db.table('products').select('category').execute()
        
        categories = list(set(p['category'] for p in result.data))
        return sorted(categories)