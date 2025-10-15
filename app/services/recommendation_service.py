from typing import List, Optional, Dict
from collections import Counter, defaultdict
from app.core.database import get_db
from datetime import datetime, timedelta


class RecommendationService:
    
    @staticmethod
    def get_user_recommendations(user_id: str, limit: int = 8) -> List[Dict]:
        """
        Generate personalized product recommendations for a user
        Based on their view/purchase history and similar users
        """
        db = get_db()
        
        # Get user's activity history
        user_activities = db.table('user_activities').select('*').eq('user_id', user_id).execute()
        
        if not user_activities.data:
            # New user - return popular products
            return RecommendationService.get_popular_products(limit)
        
        activities = user_activities.data
        
        # Extract preferences
        viewed_products = [a['product_id'] for a in activities if a['activity_type'] == 'view']
        purchased_products = [a['product_id'] for a in activities if a['activity_type'] == 'purchase']
        preferred_categories = [a['category'] for a in activities]
        
        # Get category preferences
        category_scores = Counter(preferred_categories)
        top_categories = [cat for cat, _ in category_scores.most_common(3)]
        
        recommedations = []
        seen_ids = set(viewed_products)
        
        # 1. Content-based: Similar categories (40% of recommendations)
        for category in top_categories:
            category_products = db.table('products').select('*').eq('category', category).execute()
            
            for product in category_products.data:
                if product['id'] not in seen_ids and product['stock_quantity'] > 0:
                    recommedations.append(product)
                    seen_ids.add(product['id'])
                    if len(recommedations) >= limit * 0.4:
                        break
                
            if len(recommedations) >= limit * 0.4:
                break
        
        # 2. Collaborative: Similar users (30% of recommendations)
        similar_user_products = RecommendationService.get_collaborative_recommendations(user_id, purchased_products, seen_ids)
        recommedations.extend(similar_user_products[:int(limit * 0.3)])
        
        # 3. Trending products (30% of recommendations)
        trending = RecommendationService.get_trending_products(seen_ids)
        recommedations.extend(trending[:int(limit * 0.3)])
        
        # Score and sort all recommendations
        scored = []
        for product in recommedations[:limit]:
            score = RecommendationService.calculate_recommendation_score(product, activities)
            scored.append((product, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [product for product, score in scored[:limit]]
    
    @staticmethod
    def get_collaborative_recommendations(user_id: str, user_purchases: List[str], exclude_ids: set) -> List[dict]:
        """Find products that similar users purchased"""
        db = get_db()
        
        if not user_purchases:
            return []
        
        # Get all purchase activities
        all_purchases = db.table('user_activities').select('*').eq('activity_type', 'purchase').execute()
        
        # Group by user
        user_purchase_map = defaultdict(set)
        for activity in all_purchases.data:
            if activity['user_id'] != user_id:
                user_purchase_map[activity['user_id']].add(activity['product_id'])
        
        # Find similar users (Jaccard similarity)
        user_purchase_set = set(user_purchases)
        similar_products = Counter()
        
        for other_user_id, other_purchases in user_purchase_map.items():
            intersection = len(user_purchase_set & other_purchases)
            union = len(user_purchase_set | other_purchases)
            
            if union > 0:
                similarity = intersection / union
                
                if similarity > 0.2: # At least 20% similarity
                    # Add their purchases to recommendations
                    for product_id in other_purchases:
                        if product_id not in exclude_ids:
                            similar_products[product_id] += similarity
        
        # Get product details for top recommendations
        recommendations = []
        for product_id, score in similar_products.most_common(10):
            product_result = db.table('products').select('*').eq('id', product_id).execute()
            if product_result.data and product_result.data[0]['stock_quantity'] > 0:
                recommendations.append(product_result.data[0])
        
        return recommendations
    
    @staticmethod
    def get_trending_products(exclude_ids: set, days: int = 7) -> List[dict]:
        """Get products with high recent activity"""
        db = get_db()
        
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        # Get recent activities
        recent_activities = db.table('user_activities').select('*').gte('created_at', cutoff_date).execute()
        
        # Count activity by product
        product_scores = Counter()
        for activity in recent_activities.data:
            if activity['product_id'] not in exclude_ids:
                weight = 3 if activity['activity_type'] == 'purchase' else 1
                product_scores[activity['product_id']] += weight
        
        # Get product details
        trending = []
        for product_id, score in product_scores.most_common(20):
            product_result = db.table('products').select('*').eq('id', product_id).execute()
            if product_result.data and product_result.data[0]['stock_quantity'] > 0:
                trending.append(product_result.data[0])
        
        return trending
    
    @staticmethod
    def get_popular_products(limit: int = 8) -> List[dict]:
        """Get most popular products overall"""
        db = get_db()
        
        # Get all prodcuts
        all_products = db.table('products').select('*').gt('stock_quantity', 0).execute()
        
        # Sort by order count and rating
        products = sorted(
            all_products.data,
            key=lambda p: (p.get('order_count', 0) * 0.7 + float(p.get('rating', 0)) * 10),
            reverse=True
        )
        
        return products[:limit]
    
    @staticmethod
    def calculate_recommendation_score(product: dict, user_activities: List[dict]) -> float:
        """Calculate how well a product mathces user preferences"""
        score = 0.0
        
        # Base quality score
        score += float(product.get('rating', 0)) * 10
        score += min(product.get('order_count', 0), 50)
        
        # Category preference
        user_categories = [a['category'] for a in user_activities]
        if user_categories:
            category_frequency = user_categories.count(product['category']) / len(user_categories)
            score += category_frequency * 30
        
        # Price preference
        purchased_activities = [a for a in user_activities if a['activity_type'] == 'purchase']
        if purchased_activities:
            db = get_db()
            purchased_prices = []
            
            for acitivity in purchased_activities:
                product_result = db.table('products').select('price').eq('id', acitivity['product_id']).execute()
                if product_result.data:
                    purchased_prices.append(float(product_result.data[0]['price']))
            
            if purchased_prices:
                avg_price = sum(purchased_prices) / len(purchased_prices)
            price_diff = abs(float(product['price']) - avg_price) / avg_price
            score += max(0, 20 - (price_diff * 20))
        
        # Stock availability bonus
        if product['stock_quantity'] > 0:
            score += 10
            
        # Featured/new bonus
        if product.get('is_new'):
            score += 15
        if product.get('is_featured'):
            score += 10
            
        return score
    
    @staticmethod
    def get_similar_products(product_id: str, limit: int = 6) -> List[dict]:
        """Get products similar to a specific product"""
        db = get_db()
        
        # Get the source product
        product_result = db.table('products').select('*').eq('id', product_id).execute()
        
        if not product_result.data:
            return []
        
        source_product = product_result.data[0]
        
        # Get products in same category
        similar_products = db.table('products').select('*').eq('category', source_product['category']).execute()
        
        recommendations = []
        for product in similar_products.data:
            if product['id'] != product_id and product['stock_quantity'] > 0:
                # Calculate similarity score
                price_diff = abs(float(product['price']) - float(source_product['price']))
                price_similarity = max(0, 100 - (price_diff / float(source_product['price']) * 100))
                
                rating_similarity = abs(float(product.get('rating', 0)) - float(source_product.get('rating', 0)))
                
                score = price_similarity + (100 - rating_similarity * 20) + product.get('order_count', 0)
                
                recommendations.append((product, score))
        
        # Sort by similarity score
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return [product for product, score in recommendations[:limit]]
    
    @staticmethod
    async def track_activity(user_id: str, product_id: str, activity_type: str):
        """Track user activity for recommendations"""
        db = get_db()
        
        # Get product category
        product_result = db.table('products').select('category').eq('id', product_id).execute()
        
        if not product_result.data:
            return False
        
        category = product_result.data[0]['category']
        
        # Save activity
        activity_data = {
            'user_id': user_id,
            'product_id': product_id,
            'activity_type': activity_type,
            'category': category,
            'created_at': datetime.utcnow().isoformat()
        }
        
        db.table('user_activities').insert(activity_data).execute()
        
        return True