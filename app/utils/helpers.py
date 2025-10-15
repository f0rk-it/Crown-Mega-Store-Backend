from typing import Optional, Dict, Any
from datetime import datetime
import re

def format_price(price: float) -> str:
    """Format price a to 2 decimal places with currency symbol"""
    return f"₦{price:.2f}"

def format_datetime(dt: datetime) -> str:
    """Format datetime to readable string"""
    return dt.strftime("%B %d, %Y at %I:%M %p")

def validate_phone_number(phone: str) -> bool:
    """Validate NGN phone number format"""
    # Accepts: +2348012345678, 08012345678, 2348012345678
    pattern = r'^(\+?234|0)?[789]\d{9}$'
    return bool(re.match(pattern, phone))

def sanitize_string(text: str) -> str:
    """Remove potentially harmful characters from string"""
    return re.sub(r'[<>\"\'%;()&+]', '', text)

def calculate_discount_price(original_price: float, discount_percent: float) -> float:
    """Calculate discounted price"""
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount must be between 0 and 100")
    
    discount_amount = original_price * (discount_percent / 100)
    return original_price - discount_amount

def paginate_results(items: list, page: int, page_size: int) -> Dict[str, Any]:
    """Paginate a list of items"""
    total_items = len(items)
    total_pages = (total_items + page_size - 1) // page_size
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    return {
        'items': items[start_idx:end_idx],
        'page': page,
        'page_size': page_size,
        'total_items': total_items,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_prev': page > 1
    }

def generate_slug(text: str) -> str:
    """Generate URL-friendly slug from text"""
    # Convert to lowercase
    slug = text.lower()
    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)
    # Remove special characters
    slug = re.sub(r'[^\w\-]', '', slug)
    # Remove multiple hyphens
    slug = re.sub(r'\-+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    return slug

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)].strip() + suffix

def format_order_status(status: str) -> str:
    """Format order status for display"""
    status_map = {
        'pending': 'Pending',
        'confirmed': 'Confirmed',
        'payment_received': 'Payment Received',
        'processing': 'Processing',
        'shipped': 'Shipped',
        'delivered': 'Delivered',
        'cancelled': 'Cancelled'
    }
    
    return status_map.get(status, status.replace('_', ' ').title())

def calculate_delivery_estimate(days: int = 3) -> str:
    """Calculate estimated delivery date"""
    from datetime import timedelta
    
    delivery_date = datetime.utcnow() + timedelta(days=days)
    return delivery_date.strftime("%A, %B %d, %Y")

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    
    return f"{size_bytes:.2f} TB"