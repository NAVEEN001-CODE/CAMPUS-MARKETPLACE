"""
Add admin role to users table and create default admin account.
"""
import pymysql
from werkzeug.security import generate_password_hash

conn = pymysql.connect(host='localhost', user='root', password='',
                       database='campus_marketplace', charset='utf8mb4')
cur = conn.cursor()

# Alter role ENUM to include 'admin'
try:
    cur.execute("""
        ALTER TABLE users 
        MODIFY COLUMN role ENUM('student', 'staff', 'admin') DEFAULT 'student'
    """)
    print("✅ Added 'admin' to role ENUM")
except Exception as e:
    print(f"Role ENUM update: {e}")

# Create default admin account
admin_email = "admin@campus.edu"
cur.execute("SELECT id FROM users WHERE email = %s", (admin_email,))
if not cur.fetchone():
    admin_hash = generate_password_hash("Admin@123")
    cur.execute("""
        INSERT INTO users (full_name, email, password_hash, phone, department, role)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, ("System Admin", admin_email, admin_hash, "0000000000", "Administration", "admin"))
    print("✅ Default admin created: admin@campus.edu / Admin@123")
else:
    # Update existing account to admin role
    cur.execute("UPDATE users SET role = 'admin' WHERE email = %s", (admin_email,))
    print("✅ Admin account already exists, ensured admin role")

conn.commit()
cur.close()
conn.close()
print("✅ Admin setup complete!")
