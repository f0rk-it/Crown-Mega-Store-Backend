from typing import Optional
from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token
from datetime import datetime


class AuthService:
    
    @staticmethod
    async def verify_google_token(token: str) -> dict:
        """Verify Google OAuth token and extract user info"""
        try:
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            
            # Token is valid, extract user info
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return {
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'name': idinfo.get('name', ''),
                'avatar_url': idinfo.get('picture', '')
            }
        
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google token: {str(e)}"
            )
    
    @staticmethod
    async def get_or_create_user(user_data: dict):
        """Get existing user or create a new one"""
        db = get_db()
        
        try:
            # Check if user exists by email
            result = db.table('users').select('*').eq('email', user_data['email']).execute()
            
            if result.data and len(result.data) > 0:
                # User exists, update their info
                user = result.data[0]
                
                # Update user data
                updated_user = db.table('users').update({
                    'name': user_data.get('name', user['name']),
                    'avatar_url': user_data.get('avatar_url', user.get('avatar_url')),
                    'google_id': user_data.get('google_id', user.get('google_id')),
                    'updated_at': datetime.utcnow().isoformat()
                }).eq('id', user['id']).execute()
                
                if updated_user.data and len(updated_user.data) > 0:
                    return updated_user.data[0]
                return user
            else:
                # Create new user
                new_user_data = {
                    'email': user_data['email'],
                    'name': user_data.get('name', 'User'),
                    'google_id': user_data.get('google_id', ''),
                    'avatar_url': user_data.get('avatar_url', ''),
                    'role': 'customer',
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                new_user = db.table('users').insert(new_user_data).execute()
                
                if new_user.data and len(new_user.data) > 0:
                    return new_user.data[0]
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail='Failed to create user'
                    )
                    
        except HTTPException:
            raise
        except Exception as e:
            print(f"Database error in get_or_create_user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database operation failed: {str(e)}"
            )
    
    @staticmethod
    async def create_user_session(user: dict) -> dict:
        """Create a JWT token for user session"""
        try:
            token_data = {
                'sub': user['id'],
                'email': user['email'],
                'role': user.get('role', 'customer')
            }
            
            access_token = create_access_token(token_data)
            
            return {
                'access_token': access_token,
                'token_type': 'bearer',
                'user': user
            }
        
        except Exception as e:
            print(f"Error creating session: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create session: {str(e)}"
            )