from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.api.deps import get_current_active_user

router = APIRouter()


class CartItemAdd(BaseModel):
    product_id: str
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemResponse(BaseModel):
    id: str
    product_id: str
    product_name: str
    price: float
    quantity: int
    image_url: Optional[str]
    stock_quantity: int
    category: str
    subtotal: float
    created_at: datetime
    updated_at: datetime


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total: float
    item_count: int
    

@router.get("/", response_model=CartResponse)
async def get_cart(current_user: dict = Depends(get_current_active_user)):
    """
    Get current user's cart with all items and product details
    """
    user_id = current_user['sub']
    db = get_db()
    
    try:
        # Use the cart_details view for easy access to all data
        cart_result = db.table('cart_details').select('*').eq('user_id', user_id).execute()
        
        if not cart_result.data:
            return CartResponse(items=[], total=0.0, item_count=0)
        
        # Build cart items response
        cart_items = []
        total = 0.0
        
        for item in cart_result.data:
            subtotal = float(item['price']) * item['quantity']
            total += subtotal
            
            cart_items.append(CartItemResponse(
                id=item['id'],
                product_id=item['product_id'],
                product_name=item['product_name'],
                price=float(item['price']),
                quantity=item['quantity'],
                image_url=item.get('image_url'),
                stock_quantity=item['stock_quantity'],
                category=item['category'],
                subtotal=subtotal,
                created_at=item['created_at'],
                updated_at=item['updated_at']
            ))
        
        return CartResponse(
            items=cart_items,
            total=round(total, 2),
            item_count=len(cart_items)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching cart: {str(e)}"
        )

@router.post("/add")
async def add_to_cart(
    item: CartItemAdd,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Add item to cart or update quantity if already exists
    """
    user_id = current_user['sub']
    db = get_db()
    
    try:
        # Verify product exists and has stock
        product_result = db.table('products').select('*').eq('id', item.product_id).execute()
        
        if not product_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        product = product_result.data[0]
        
        # Check if product has enough stock
        if product['stock_quantity'] < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {product['stock_quantity']} units available in stock"
            )
        
        # Check if item already exists in cart
        existing_cart_item = db.table('cart_items').select('*').eq('user_id', user_id).eq('product_id', item.product_id).execute()
        
        if existing_cart_item.data:
            # Item exists - update quantity
            current_item = existing_cart_item.data[0]
            new_quantity = current_item['quantity'] + item.quantity
            
            # Check if new quantity exceeds stock
            if new_quantity > product['stock_quantity']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot add {item.quantity} more. Only {product['stock_quantity']} units available total"
                )
            
            # Update quantity
            updated = db.table('cart_items').update({
                'quantity': new_quantity,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', current_item['id']).execute()
            
            return {
                "success": True,
                "message": "Cart updated successfully",
                "action": "updated",
                "item_id": current_item['id'],
                "new_quantity": new_quantity
            }
        else:
            # New item - insert into cart
            cart_item_data = {
                'user_id': user_id,
                'product_id': item.product_id,
                'quantity': item.quantity,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            created = db.table('cart_items').insert(cart_item_data).execute()
            
            return {
                "success": True,
                "message": "Item added to cart successfully",
                "action": "added",
                "item_id": created.data[0]['id'],
                "quantity": item.quantity
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding to cart: {str(e)}"
        )

@router.put("/update/{product_id}")
async def update_cart_item(
    product_id: str,
    update: CartItemUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Update quantity of an item in the cart
    """
    user_id = current_user['sub']
    db = get_db()
    
    try:
        if update.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be greater than 0. Use delete endpoint to remove item."
            )
        
        # Check if item exists in user's cart
        cart_item_result = db.table('cart_items').select('*').eq('user_id', user_id).eq('product_id', product_id).execute()
        
        if not cart_item_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found in cart"
            )
        
        cart_item = cart_item_result.data[0]
        
        # Check product stock
        product_result = db.table('products').select('stock_quantity').eq('id', product_id).execute()
        
        if not product_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        product = product_result.data[0]
        
        if update.quantity > product['stock_quantity']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {product['stock_quantity']} units available in stock"
            )
        
        # Update quantity
        updated = db.table('cart_items').update({
            'quantity': update.quantity,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', cart_item['id']).execute()
        
        return {
            "success": True,
            "message": "Cart item updated successfully",
            "item_id": cart_item['id'],
            "new_quantity": update.quantity
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating cart: {str(e)}"
        )

@router.delete("/remove/{product_id}")
async def remove_from_cart(
    product_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Remove an item from the cart
    """
    user_id = current_user['sub']
    db = get_db()
    
    try:
        # Check if item exists in cart
        cart_item_result = db.table('cart_items').select('id').eq('user_id', user_id).eq('product_id', product_id).execute()
        
        if not cart_item_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found in cart"
            )
        
        cart_item_id = cart_item_result.data[0]['id']
        
        # Delete the item
        db.table('cart_items').delete().eq('id', cart_item_id).execute()
        
        return {
            "success": True,
            "message": "Item removed from cart successfully",
            "removed_item_id": cart_item_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing from cart: {str(e)}"
        )

@router.delete("/clear")
async def clear_cart(current_user: dict = Depends(get_current_active_user)):
    """
    Clear all items from the cart
    """
    user_id = current_user['sub']
    db = get_db()
    
    try:
        # Get count before deleting
        cart_items = db.table('cart_items').select('id').eq('user_id', user_id).execute()
        items_count = len(cart_items.data)
        
        # Delete all items for this user
        db.table('cart_items').delete().eq('user_id', user_id).execute()
        
        return {
            "success": True,
            "message": "Cart cleared successfully",
            "items_removed": items_count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing cart: {str(e)}"
        )

@router.get("/count")
async def get_cart_count(current_user: dict = Depends(get_current_active_user)):
    """
    Get the number of items in the cart (useful for navbar badge)
    """
    user_id = current_user['sub']
    db = get_db()
    
    try:
        cart_items = db.table('cart_items').select('id').eq('user_id', user_id).execute()
        
        return {
            "count": len(cart_items.data)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching cart count: {str(e)}"
        )
        
@router.post("/sync")
async def sync_cart(
    items: List[CartItemAdd],
    current_user: dict = Depends(get_current_active_user)
):
    """
    Sync cart items (useful when user logs in and had items in local storage)
    Merges local cart with database cart
    """
    user_id = current_user['sub']
    db = get_db()
    
    try:
        synced_count = 0
        errors = []
        
        for item in items:
            try:
                # Check if product exists and has stock
                product_result = db.table('products').select('stock_quantity').eq('id', item.product_id).execute()
                
                if not product_result.data:
                    errors.append({
                        "product_id": item.product_id,
                        "error": "Product not found"
                    })
                    continue
                
                product = product_result.data[0]
                
                # Check existing cart item
                existing = db.table('cart_items').select('*').eq('user_id', user_id).eq('product_id', item.product_id).execute()
                
                if existing.data:
                    # Update quantity (take maximum of both)
                    new_quantity = max(existing.data[0]['quantity'], item.quantity)
                    
                    if new_quantity <= product['stock_quantity']:
                        db.table('cart_items').update({
                            'quantity': new_quantity,
                            'updated_at': datetime.utcnow().isoformat()
                        }).eq('id', existing.data[0]['id']).execute()
                        synced_count += 1
                else:
                    # Add new item
                    if item.quantity <= product['stock_quantity']:
                        db.table('cart_items').insert({
                            'user_id': user_id,
                            'product_id': item.product_id,
                            'quantity': item.quantity,
                            'created_at': datetime.utcnow().isoformat(),
                            'updated_at': datetime.utcnow().isoformat()
                        }).execute()
                        synced_count += 1
                        
            except Exception as e:
                errors.append({
                    "product_id": item.product_id,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "message": "Cart synced successfully",
            "synced_count": synced_count,
            "errors": errors if errors else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing cart: {str(e)}"
        )