"""
Migration script to move existing product images from image_url field 
to the new product_images table while maintaining backward compatibility.

Run this after creating the product_images table in Supabase.
"""

from app.core.database import get_db
from datetime import datetime
import uuid

def migrate_existing_images():
    """Migrate existing product images to the new product_images table"""
    db = get_db()
    
    print("Starting migration of existing product images...")
    
    # Get all products with image_url
    result = db.table('products').select('id, image_url, name, created_at, updated_at').execute()
    products = result.data
    
    migrated_count = 0
    skipped_count = 0
    
    for product in products:
        if product.get('image_url') and product['image_url'].strip():
            # Check if image already exists in product_images table
            existing_images = db.table('product_images').select('id').eq('product_id', product['id']).execute()
            
            if not existing_images.data:  # Only migrate if no images exist yet
                # Create image record
                image_data = {
                    'product_id': product['id'],
                    'image_url': product['image_url'],
                    'alt_text': product.get('name', ''),
                    'display_order': 0,
                    'is_primary': True,
                    'created_at': product.get('created_at', datetime.utcnow().isoformat()),
                    'updated_at': product.get('updated_at', datetime.utcnow().isoformat())
                }
                
                try:
                    db.table('product_images').insert(image_data).execute()
                    migrated_count += 1
                    print(f"✓ Migrated image for product {product['id']}")
                except Exception as e:
                    print(f"✗ Error migrating product {product['id']}: {e}")
            else:
                skipped_count += 1
                print(f"- Skipped product {product['id']} (already has images)")
        else:
            skipped_count += 1
            print(f"- Skipped product {product['id']} (no image_url)")
    
    print(f"\nMigration completed!")
    print(f"Images migrated: {migrated_count}")
    print(f"Products skipped: {skipped_count}")
    print(f"Total products processed: {len(products)}")

def verify_migration():
    """Verify that migration was successful"""
    db = get_db()
    
    # Count products with image_url
    products_with_url = db.table('products').select('id, image_url').execute()
    products_with_images = [p for p in products_with_url.data if p.get('image_url') and p['image_url'].strip()]
    
    # Count product_images records
    image_records = db.table('product_images').select('id, product_id').execute()
    
    print(f"\nMigration Verification:")
    print(f"Products with image_url: {len(products_with_images)}")
    print(f"Product image records: {len(image_records.data)}")
    
    # Check for products that have image_url but no records in product_images
    image_product_ids = {img['product_id'] for img in image_records.data}
    missing_migrations = [
        p for p in products_with_images 
        if p['id'] not in image_product_ids
    ]
    
    if missing_migrations:
        print(f"⚠️  Found {len(missing_migrations)} products with image_url but no image records:")
        for product in missing_migrations[:5]:  # Show first 5
            print(f"   - Product ID: {product['id']}")
    else:
        print("✓ All products with image_url have corresponding image records")

if __name__ == "__main__":
    migrate_existing_images()
    verify_migration()