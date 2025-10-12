from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import Optional
from app.schemas.product import ProductResponse, ProductCreate, ProductUpdate
from app.services.product_service import ProductService
from app.api.deps import get_current_active_user, get_current_admin_user
from datetime import datetime

router = APIRouter()

@router.get('/', response_model=dict)
async def get_products(
    category: Optional[str] = None,
    sort_by: str = Query('balanced', description='balanced, popularity, price_low, price_high, newest, rating'),
    limit: int = Query(50, ge=1, le=100),
    page: int = Query(1, ge=1)
):
    """
    Get all products with filtering and sorting
    
    - **category**: Filter by product category (optional)
    - **sort_by**: Sorting strategy (default: balanced)
    - **limit**: Number of products per page
    - **page**: Page number
    """
    offset = (page - 1) * limit
    result = ProductService.get_all_products(category, sort_by, limit, offset)
    return result

@router.get('/search')
async def search_products(
    q: str = Query(..., min_length=2, description='Search term'),
    limit: int = Query(20, ge=1, le=50)
):
    """Search products by name or description"""
    products = ProductService.search_products(q, limit)
    return {
        'products': products,
        'count': len(products),
        'search_item': q
    }

@router.get('/categories')
async def get_categories():
    """Get all available product categories"""
    categories = ProductService.get_categories()
    return {
        'categories': categories,
        'count': len(categories)
    }

@router.get('/{product_id}', response_model=ProductResponse)
async def get_product(product_id: str):
    """Get single product by ID"""
    product = ProductService.get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )
    
    # Increment view count
    ProductService.increment_view_count(product_id)
    
    return product

@router.post('/', response_model=ProductCreate, dependencies=[Depends(get_current_admin_user)])
async def create_product(product: ProductCreate):
    """Create new product (Admin only)"""
    from app.core.database import get_db
    db = get_db()
    
    product_data = product.model_dump()
    product_data['created_at'] = datetime.utcnow().isoformat()
    product_data['updated_at'] = datetime.utcnow().isoformat()
    
    result = db.table('products').insert(product_data).execute()
    
    return result.data[0]

@router.put('/{product_id}', response_model=ProductResponse, dependencies=[Depends(get_current_admin_user)])
async def update_product(product_id: str, product_update: ProductUpdate):
    """Update product (Admin only)"""
    from app.core.database import get_db
    db = get_db()
    
    # Check if product exists
    existing = ProductService.get_product_by_id(product_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )
    
    # Update only provides fields
    update_data = {k: v for k, v in product_update.model_dump().items() if v is not None}
    update_data['updated_at'] = datetime.utcnow().isoformat()
    
    result = db.table('products').update(update_data).eq('id', product_id).execute()
    
    return result.data[0]

@router.delete('/{product_id}', dependencies=[Depends(get_current_admin_user)])
async def delete_product(product_id: str):
    """Delete product (Admin only)"""
    from app.core.database import get_db
    db = get_db()
    
    # Check if product exists
    existing = ProductService.get_product_by_id(product_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )
    
    db.table('products').delete().eq('id', product_id).execute()
    
    return {
        'success': True,
        'message': 'Product deleted successfully'
    }
    