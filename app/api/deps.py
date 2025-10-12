from fastapi import Depends, HTTPException, status
from app.core.security import get_current_user
from app.core.database import get_db

async def get_current_active_user(current_user=Depends(get_current_user)):
    """Get current authenticated user"""
    return current_user

async def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    """Verify user is admin"""
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Admin access required'
        )
    return current_user

def get_user_from_db(user_id: str):
    """Get full user details from the database"""
    db = get_db()
    result = db.table('users').select('*').eq('id', user_id).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    
    return result.data[0]