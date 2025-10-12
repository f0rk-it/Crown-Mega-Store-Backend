from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import GoogleAuthRequest, LoginResponse, UserResponse
from app.services.auth_service import AuthService
from app.api.deps import get_current_active_user, get_user_from_db

router = APIRouter()

@router.post('/google', response_model=LoginResponse)
async def google_auth(auth_request: GoogleAuthRequest):
    """Authenticate user with Google OAuth token
       Frontend should send the Google OAuth token after user signs in with Google.
    """
    try:
        # Verify Google token and get user info
        user_data = await AuthService.verify_google_token(auth_request.token)
        
        # Get or create user in database
        user = await AuthService.get_or_create_user(user_data)
        
        # Create session and return JWT token
        session = await AuthService.create_user_session(user)
        
        return session
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )

@router.get('/me', response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    """Get current authenticated users info"""
    user = get_user_from_db(current_user['id'])
    return user

@router.post('/logout')
async def logout(current_user: dict = Depends(get_current_active_user)):
    """Logout user (frontend should delete the token)"""
    return {
        'success': True,
        'message': 'Logged out successfully'
    }
    
@router.get('/verify')
async def verify_token(current_user: dict = Depends(get_current_active_user)):
    """Verify if the token is valid"""
    return {
        'valid': True,
        'user_id': current_user['sub'],
        'email': current_user['email'],
        'role': current_user['role']
    }