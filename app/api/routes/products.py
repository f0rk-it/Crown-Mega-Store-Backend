from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import Optional, List
from app.schemas.product import ProductResponse, ProductCreate, ProductUpdate, ProductImageCreate, ProductImageResponse
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
    """Get single product by ID with images"""
    product = ProductService.get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )
    
    # Increment view count
    ProductService.increment_view_count(product_id)
    
    return product

@router.post('/', response_model=ProductResponse, dependencies=[Depends(get_current_admin_user)])
async def create_product(product: ProductCreate):
    """Create new product with optional multiple images (Admin only)"""
    from app.core.database import get_db
    db = get_db()
    
    # Separate images from product data
    images = product.images if product.images else []
    product_data = product.model_dump(exclude={'images'})
    product_data['created_at'] = datetime.utcnow().isoformat()
    product_data['updated_at'] = datetime.utcnow().isoformat()
    
    # Create the product
    result = db.table('products').insert(product_data).execute()
    created_product = result.data[0]
    
    # Add images if provided
    if images:
        image_data = []
        for img in images:
            image_record = img.model_dump()
            ProductService.add_product_images(created_product['id'], [image_record])
    
    # Return product with images
    return ProductService.get_product_by_id(created_product['id'])

@router.put('/{product_id}', response_model=ProductResponse, dependencies=[Depends(get_current_admin_user)])
async def update_product(product_id: str, product_update: ProductUpdate):
    """Update product with optional image updates (Admin only)"""
    from app.core.database import get_db
    db = get_db()
    
    # Check if product exists
    existing = ProductService.get_product_by_id(product_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )
    
    # Separate images from update data
    images = product_update.images
    update_data = {k: v for k, v in product_update.model_dump(exclude={'images'}).items() if v is not None}
    update_data['updated_at'] = datetime.utcnow().isoformat()
    
    # Update product data
    if update_data:
        result = db.table('products').update(update_data).eq('id', product_id).execute()
    
    # Update images if provided
    if images is not None:  # Allow empty list to clear images
        if images:
            image_data = [img.model_dump() for img in images]
            ProductService.update_product_images(product_id, image_data)
        else:
            # Clear all images if empty list provided
            db.table('product_images').delete().eq('product_id', product_id).execute()
    
    # Return updated product with images
    return ProductService.get_product_by_id(product_id)

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
    
    # Delete product images first (due to foreign key constraint)
    db.table('product_images').delete().eq('product_id', product_id).execute()
    
    # Delete product
    db.table('products').delete().eq('id', product_id).execute()
    
    return {
        'success': True,
        'message': 'Product deleted successfully'
    }

# Additional endpoints for managing product images
@router.get('/{product_id}/images', response_model=List[ProductImageResponse], dependencies=[Depends(get_current_admin_user)])
async def get_product_images(product_id: str):
    """Get all images for a specific product (Admin only)"""
    # Check if product exists
    existing = ProductService.get_product_by_id(product_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )
    
    images = ProductService.get_product_images(product_id)
    return images

@router.post('/{product_id}/images', response_model=List[ProductImageResponse], dependencies=[Depends(get_current_admin_user)])
async def add_product_images(product_id: str, images: List[ProductImageCreate]):
    """Add new images to a product (Admin only)"""
    # Check if product exists
    existing = ProductService.get_product_by_id(product_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )
    
    image_data = [img.model_dump() for img in images]
    created_images = ProductService.add_product_images(product_id, image_data)
    return created_images

@router.put('/{product_id}/images', response_model=List[ProductImageResponse], dependencies=[Depends(get_current_admin_user)])
async def replace_product_images(product_id: str, images: List[ProductImageCreate]):
    """Replace all images for a product (Admin only)"""
    # Check if product exists
    existing = ProductService.get_product_by_id(product_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )
    
    image_data = [img.model_dump() for img in images]
    updated_images = ProductService.update_product_images(product_id, image_data)
    return updated_images

@router.delete('/{product_id}/images', dependencies=[Depends(get_current_admin_user)])
async def delete_all_product_images(product_id: str):
    """Delete all images for a product (Admin only)"""
    from app.core.database import get_db
    db = get_db()
    
    # Check if product exists
    existing = ProductService.get_product_by_id(product_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )
    
    db.table('product_images').delete().eq('product_id', product_id).execute()
    
    return {
        'success': True,
        'message': 'All product images deleted successfully'
    }
    