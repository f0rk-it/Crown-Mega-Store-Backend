-- Create product_images table for multiple images support
CREATE TABLE IF NOT EXISTS product_images (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  image_url TEXT NOT NULL,
  alt_text TEXT,
  display_order INTEGER DEFAULT 0,
  is_primary BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_product_images_product_id ON product_images(product_id);
CREATE INDEX idx_product_images_primary ON product_images(product_id, is_primary);
CREATE INDEX idx_product_images_order ON product_images(product_id, display_order);

-- Enable RLS (Row Level Security)
ALTER TABLE product_images ENABLE ROW LEVEL SECURITY;

-- Create policies for product_images
-- Allow read access to everyone
CREATE POLICY "Allow read access to product_images" ON product_images
  FOR SELECT USING (true);

-- Allow insert/update/delete for authenticated users (you can modify this based on your auth strategy)
CREATE POLICY "Allow insert product_images for authenticated users" ON product_images
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow update product_images for authenticated users" ON product_images
  FOR UPDATE USING (true);

CREATE POLICY "Allow delete product_images for authenticated users" ON product_images
  FOR DELETE USING (true);

-- Create function to automatically update updated_at
CREATE OR REPLACE FUNCTION update_product_images_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for auto-updating updated_at
CREATE TRIGGER update_product_images_updated_at
  BEFORE UPDATE ON product_images
  FOR EACH ROW EXECUTE PROCEDURE update_product_images_updated_at();