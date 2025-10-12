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
        
        # Check if user exists
        result = db.table('users').select().eq('email', user_data['email']).execute()
        
        if result.data:
            # User exists, update their info
            user = result.data[0]
            updated_user = db.table('users').update({
                'name': user_data['name'],
                'avatar_url': user_data['avatar_url'],
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', user['id']).execute()
        else:
            # Create a new user
            new_user = db.table('users').insert({
                'email': user_data['email'],
                'name': user_data['name'],
                'google_id': user_data['google_id'],
                'avatar_url': user_data['avatar_url'],
                'role': 'customer'
            }).execute()

            return new_user.data[0]
    
    @staticmethod
    async def create_user_session(user: dict) -> dict:
        """Create a JWT token for user session"""
        token_data = {
            'sub': user['id'],
            'email': user['email'],
            'role': user['role']
        }
        
        access_token = create_access_token(data=token_data)
        
        return {
            'access_token': access_token,
            'token_type': 'bearer',
            'user': user
        }