import uuid

def generate_order_id() -> str:
    """Generate unique order ID format: ORD4F7B2A1E"""
    return f"ORD{uuid.uuid4().hex[:8].upper()}"