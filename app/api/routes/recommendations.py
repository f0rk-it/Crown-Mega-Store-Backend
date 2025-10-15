from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
from app.services.recommendation_service import RecommendationService
from app.api.deps import get_current_active_user
from app.schemas.product import ProductResponse

router = APIRouter()


class ActivityTrack(BaseModel):
    product_id: str
    activity_type: str
    

@router.get("/for-you", response_model=List[ProductResponse])
async def get_personalized_recommendations(
    current_user: dict = Depends(get_current_active_user),
    limit: int = Query(8, ge=1, le=20)
):
    """
    Get personalized product recommendations for current user
    Based on their browsing and purchase history
    """
    recommendations = RecommendationService.get_user_recommendations(
        current_user['sub'],
        limit
    )
    
    return recommendations

@router.get("/similar/{product_id}", response_model=List[ProductResponse])
async def get_similar_products(
    product_id: str,
    limit: int = Query(6, ge=1, le=12)
):
    """
    Get products similar to a specific product
    Based on category, price range, and ratings
    """
    similar = RecommendationService.get_similar_products(product_id, limit)
    
    return similar

@router.get("/trending", response_model=List[ProductResponse])
async def get_trending_products(limit: int = Query(8, ge=1, le=20)):
    """
    Get currently trending products
    Based on recent user activity
    """
    trending = RecommendationService.get_trending_products(set(), days=7)
    
    return trending[:limit]

@router.get("/popular", response_model=List[ProductResponse])
async def get_popular_products(limit: int = Query(8, ge=1, le=20)):
    """
    Get most popular products overall
    Based on order count and ratings
    """
    popular = RecommendationService.get_popular_products(limit)
    
    return popular

@router.post("/track")
async def track_user_activity(
    activity: ActivityTrack,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Track user activity for improving recommendations
    Call this when user views a product, adds to cart, or makes purchase
    """
    success = await RecommendationService.track_activity(
        current_user['sub'],
        activity.product_id,
        activity.activity_type
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to track activity"
        )
    
    return {
        "success": True,
        "message": "Activity tracked successfully"
    }