from supabase import create_client, Client
from app.core.config import settings


class Database:
    _instance: Client = None
    
    @classmethod
    def get_client(cls) -> Client:
        if cls._instance is None:
            cls._instance = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
        return cls._instance
    
    @classmethod
    def get_admin_client(cls) -> Client:
        """Get client with service role key for admin operations"""
        return create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )


def get_db() -> Client:
    return Database.get_client()