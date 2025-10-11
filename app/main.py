from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import auth, products, orders, cart, recommendations, admin
from datetime import datetime

app = FastAPI(
    title=settings.APP_NAME,
    description='E-commerce API for Crown Mega Store',
    version='1.0.0'
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, 'http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Include router
app.include_router(auth.router, prefix='/api/auth', tags=['Authentication'])
app.include_router(products.router, prefix='/api/products', tags=['Products'])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(cart.router, prefix="/api/cart", tags=["Cart"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


@app.get('/')
async def root():
    return {
        'message': 'Welcome to Crown Mega Store API',
        'version': '1.0.0',
        'docs': '/docs'
    }

@app.get('/api/health')
async def health_check():
    return {
        'status': 'healthy',
        'environment': settings.ENVIRONMENT,
        'timestamp': datetime.utcnow().isoformat()
    }