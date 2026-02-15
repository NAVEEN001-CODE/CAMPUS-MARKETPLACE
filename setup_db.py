"""
Database Setup Script
Run this once to create the campus_marketplace database and tables.
"""
import pymysql

# Connection config (no database specified yet - we create it)
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    port=3306,
    charset='utf8mb4'
)

cursor = conn.cursor()

# Create database
cursor.execute("CREATE DATABASE IF NOT EXISTS campus_marketplace")
cursor.execute("USE campus_marketplace")

# Create tables
cursor.execute("""
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
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    icon VARCHAR(50) DEFAULT 'bi-tag'
)
""")

# Insert categories
categories = [
    ('Books', 'bi-book'),
    ('Electronics', 'bi-laptop'),
    ('Clothing', 'bi-bag'),
    ('Furniture', 'bi-house'),
    ('Sports', 'bi-trophy'),
    ('Stationery', 'bi-pencil'),
    ('Accessories', 'bi-watch'),
    ('Other', 'bi-three-dots'),
]
for name, icon in categories:
    try:
        cursor.execute("INSERT INTO categories (name, icon) VALUES (%s, %s)", (name, icon))
    except pymysql.err.IntegrityError:
        pass  # Already exists

cursor.execute("""
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
)
""")

cursor.execute("""
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
)
""")

cursor.execute("""
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
)
""")

conn.commit()
print("✅ Database 'campus_marketplace' created successfully!")
print("✅ All tables created: users, categories, products, product_ai_analysis, messages")
print("✅ 8 categories inserted")

cursor.close()
conn.close()
