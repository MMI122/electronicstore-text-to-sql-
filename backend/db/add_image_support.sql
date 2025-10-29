-- Add image support to products table
ALTER TABLE products 
ADD COLUMN image_url VARCHAR(500) DEFAULT NULL AFTER description,
ADD COLUMN image_alt_text VARCHAR(200) DEFAULT NULL AFTER image_url;

-- Add index for image_url for better performance
CREATE INDEX idx_products_image_url ON products(image_url);

-- Update existing products with placeholder images (optional)
UPDATE products 
SET image_url = 'https://via.placeholder.com/300x300?text=Product+Image',
    image_alt_text = CONCAT(product_name, ' - Product Image')
WHERE image_url IS NULL;
