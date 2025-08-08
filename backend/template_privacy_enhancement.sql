-- Enhanced Template Privacy and Organization System
-- This enhances the existing warehouse_template table

-- Step 1: Add new columns to warehouse_template table
ALTER TABLE warehouse_template 
ADD COLUMN IF NOT EXISTS visibility VARCHAR(20) DEFAULT 'PRIVATE',
ADD COLUMN IF NOT EXISTS company_id VARCHAR(100),
ADD COLUMN IF NOT EXISTS industry_category VARCHAR(50),
ADD COLUMN IF NOT EXISTS template_category VARCHAR(50) DEFAULT 'CUSTOM',
ADD COLUMN IF NOT EXISTS featured BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS rating DECIMAL(2,1) DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS downloads_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS tags TEXT; -- JSON array of tags

-- Step 2: Update existing is_public templates to new visibility system
UPDATE warehouse_template 
SET visibility = 'PUBLIC' 
WHERE is_public = TRUE;

UPDATE warehouse_template 
SET visibility = 'PRIVATE' 
WHERE is_public = FALSE;

-- Step 3: Create template categories lookup
CREATE TABLE IF NOT EXISTS template_categories (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    icon_name VARCHAR(50),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

-- Insert default categories
INSERT INTO template_categories (category_name, display_name, description, sort_order) VALUES 
('MANUFACTURING', 'Manufacturing', 'Templates for manufacturing warehouses', 1),
('RETAIL', 'Retail Distribution', 'Templates for retail distribution centers', 2),
('FOOD_BEVERAGE', 'Food & Beverage', 'Cold chain and food storage templates', 3),
('PHARMA', 'Pharmaceutical', 'Controlled environment and compliance templates', 4),
('AUTOMOTIVE', 'Automotive', 'Parts and assembly warehouse templates', 5),
('ECOMMERCE', 'E-commerce', 'Fulfillment center templates', 6),
('CUSTOM', 'Custom', 'User-created custom templates', 7),
('FEATURED', 'Featured', 'Curated premium templates', 8);

-- Step 4: Create company organizations table (if not exists)
CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    organization_name VARCHAR(150) NOT NULL,
    organization_code VARCHAR(50) UNIQUE NOT NULL,
    industry VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Step 5: Add organization reference to users (if not exists)
ALTER TABLE "user" 
ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id);

-- Step 6: Create template sharing permissions
CREATE TABLE IF NOT EXISTS template_permissions (
    id SERIAL PRIMARY KEY,
    template_id INTEGER REFERENCES warehouse_template(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES "user"(id),
    organization_id INTEGER REFERENCES organizations(id),
    permission_type VARCHAR(20) DEFAULT 'VIEW', -- VIEW, USE, EDIT
    granted_by INTEGER REFERENCES "user"(id),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 7: Create template reviews/ratings
CREATE TABLE IF NOT EXISTS template_reviews (
    id SERIAL PRIMARY KEY,
    template_id INTEGER REFERENCES warehouse_template(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES "user"(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 8: Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_template_visibility ON warehouse_template(visibility);
CREATE INDEX IF NOT EXISTS idx_template_company ON warehouse_template(company_id);
CREATE INDEX IF NOT EXISTS idx_template_category ON warehouse_template(template_category);
CREATE INDEX IF NOT EXISTS idx_template_featured ON warehouse_template(featured);
CREATE INDEX IF NOT EXISTS idx_template_permissions_template ON template_permissions(template_id);
CREATE INDEX IF NOT EXISTS idx_template_permissions_user ON template_permissions(user_id);

-- Step 9: Create useful views
CREATE OR REPLACE VIEW template_access_view AS
SELECT 
    t.*,
    u.username as creator_username,
    o.organization_name as creator_organization,
    tc.display_name as category_display_name,
    COALESCE(AVG(tr.rating), 0) as avg_rating,
    COUNT(tr.id) as review_count
FROM warehouse_template t
LEFT JOIN "user" u ON t.created_by = u.id
LEFT JOIN organizations o ON u.organization_id = o.id
LEFT JOIN template_categories tc ON t.template_category = tc.category_name
LEFT JOIN template_reviews tr ON t.id = tr.template_id
WHERE t.is_active = TRUE
GROUP BY t.id, u.username, o.organization_name, tc.display_name;