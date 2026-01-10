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
    def get_product_images(product_id: str):
        """Get all images for a product"""
        db = get_db()
        result = db.table('product_images').select('*').eq('product_id', product_id).order('display_order').execute()
        return result.data
    
    @staticmethod
    def add_product_images(product_id: str, images: List[dict]):
        """Add multiple images to a product"""
        db = get_db()
        
        # Prepare image data
        image_data = []
        for i, img in enumerate(images):
            image_record = {
                'product_id': product_id,
                'image_url': img['image_url'],
                'alt_text': img.get('alt_text'),
                'display_order': img.get('display_order', i),
                'is_primary': img.get('is_primary', i == 0),  # First image is primary by default
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            image_data.append(image_record)
        
        if image_data:
            result = db.table('product_images').insert(image_data).execute()
            return result.data
        return []
    
    @staticmethod
    def update_product_images(product_id: str, images: List[dict]):
        """Update product images (replace existing)"""
        db = get_db()
        
        # Delete existing images
        db.table('product_images').delete().eq('product_id', product_id).execute()
        
        # Add new images
        return ProductService.add_product_images(product_id, images)
    
    @staticmethod
    def get_products_with_images(products: List[dict]) -> List[dict]:
        """Enrich products with their images"""
        db = get_db()
        
        if not products:
            return products
        
        # Get all product IDs
        product_ids = [p['id'] for p in products]
        
        # Get all images for these products in one query
        images_result = db.table('product_images').select('*').in_('product_id', product_ids).order('display_order').execute()
        images_by_product = {}
        
        for img in images_result.data:
            if img['product_id'] not in images_by_product:
                images_by_product[img['product_id']] = []
            images_by_product[img['product_id']].append(img)
        
        # Enrich products with images
        for product in products:
            product['images'] = images_by_product.get(product['id'], [])
            
            # For backward compatibility: if no images but has image_url, create image entry
            if not product['images'] and product.get('image_url'):
                product['images'] = [{
                    'id': None,
                    'product_id': product['id'],
                    'image_url': product['image_url'],
                    'alt_text': product.get('name', ''),
                    'display_order': 0,
                    'is_primary': True,
                    'created_at': product.get('created_at'),
                    'updated_at': product.get('updated_at')
                }]
        
        return products
    
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
        
        # Add images to products
        products = ProductService.get_products_with_images(products)
        
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
        """Get single product by ID with images"""
        db = get_db()
        result = db.table('products').select('*').eq('id', product_id).execute()
        
        if not result.data:
            return None
        
        product = result.data[0]
        
        # Add images
        products_with_images = ProductService.get_products_with_images([product])
        return products_with_images[0] if products_with_images else product
    
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
        
        # Add images to filtered products
        filtered = ProductService.get_products_with_images(filtered)
        
        return filtered[:limit]
    
    @staticmethod
    def get_categories():
        """Get all unique product categories"""
        db = get_db()
        result = db.table('products').select('category').execute()
        
        categories = list(set(p['category'] for p in result.data))
        return sorted(categories)