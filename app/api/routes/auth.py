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
        print(f"Received Google auth request")
        
        # Verify Google token and get user info
        print('Verifying Google token...')
        user_data = await AuthService.verify_google_token(auth_request.token)
        print(f"Token verified for user: {user_data.get('email')}")
        
        # Get or create user in database
        print('Getting or creating user...')
        user = await AuthService.get_or_create_user(user_data)
        print(f"User retrieved/created: {user.get('id')}")
        
        # Create session and return JWT token
        print('Creating session...')
        session = await AuthService.create_user_session(user)
        print('Session created successfully')
        
        return session
    
    except HTTPException as he:
        print(f"HTTPException: {he.detail}")
        raise
    except Exception as e:
        print(f"Unexpected error in google_auth: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )

@router.get('/me', response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    """Get current authenticated users info"""
    try:
        user = get_user_from_db(current_user['sub'])
        return user
    except Exception as e:
        print(f"Error getting current user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user info: {str(e)}"
        )

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