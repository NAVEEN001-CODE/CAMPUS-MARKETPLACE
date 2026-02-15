-- =====================================================
-- Campus Marketplace Database Schema
-- =====================================================

CREATE DATABASE IF NOT EXISTS campus_marketplace;
USE campus_marketplace;

-- ---------------------------------------------------
-- Users Table
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    department VARCHAR(100),
    role ENUM('student', 'staff') DEFAULT 'student',
    profile_image VARCHAR(255) DEFAULT 'default_avatar.png',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ---------------------------------------------------
-- Product Categories
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    icon VARCHAR(50) DEFAULT 'bi-tag'
);

INSERT IGNORE INTO categories (name, icon) VALUES
    ('Books', 'bi-book'),
    ('Electronics', 'bi-laptop'),
    ('Clothing', 'bi-bag'),
    ('Furniture', 'bi-house'),
    ('Sports', 'bi-trophy'),
    ('Stationery', 'bi-pencil'),
    ('Accessories', 'bi-watch'),
    ('Other', 'bi-three-dots');

-- ---------------------------------------------------
-- Products Table
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    seller_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category_id INT,
    item_condition ENUM('New', 'Like New', 'Used', 'Heavily Used') DEFAULT 'Used',
    status ENUM('available', 'sold', 'removed') DEFAULT 'available',
    image_filename VARCHAR(255),
    views_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- ---------------------------------------------------
-- AI Image Analysis Results (Core AI Feature)
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS product_ai_analysis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL UNIQUE,
    blur_score FLOAT DEFAULT 0.0,
    is_blurry BOOLEAN DEFAULT FALSE,
    condition_label VARCHAR(30) DEFAULT 'Unknown',
    condition_confidence FLOAT DEFAULT 0.0,
    feedback_text TEXT,
    trust_score INT DEFAULT 0,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- ---------------------------------------------------
-- Messages (Buyer-Seller Communication)
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    product_id INT,
    message_text TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
);

-- ---------------------------------------------------
-- Indexes for Performance
-- ---------------------------------------------------
CREATE INDEX idx_products_seller ON products(seller_id);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_messages_receiver ON messages(receiver_id);
CREATE INDEX idx_ai_product ON product_ai_analysis(product_id);
