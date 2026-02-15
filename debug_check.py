"""Test admin module routes."""
import urllib.request
import urllib.parse
import http.cookiejar

BASE = "http://127.0.0.1:5000"
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def post(path, data):
    encoded = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=encoded, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        resp = opener.open(req)
        return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")

def get(path):
    try:
        resp = opener.open(f"{BASE}{path}")
        return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")

print("=" * 60)
print("  ADMIN MODULE TEST")
print("=" * 60)

# 1. Admin Login
print("\n1️⃣  Admin Login...")
status, html = post("/login", {"email": "admin@campus.edu", "password": "Admin@123"})
print(f"   Login status: {status}")
print(f"   Redirected to admin: {'admin' in html.lower() or status == 200}")

# 2. Admin Dashboard
print("\n2️⃣  Admin Dashboard...")
status, html = get("/admin/")
print(f"   Status: {status}")
print(f"   Has stats: {'Total Users' in html}")
print(f"   Has nav links: {'User Management' in html or 'Users' in html}")
print(f"   Has recent: {'Recent' in html}")

# 3. User Management
print("\n3️⃣  User Management...")
status, html = get("/admin/users")
print(f"   Status: {status}")
print(f"   Has table: {'Full Name' in html}")
print(f"   Has actions: {'Delete' in html or 'bi-trash' in html}")

# 4. Product Management
print("\n4️⃣  Product Management...")
status, html = get("/admin/products")
print(f"   Status: {status}")
print(f"   Has table: {'Title' in html or 'Product' in html}")
print(f"   Has filters: {'Status' in html}")

# 5. Category Management
print("\n5️⃣  Category Management...")
status, html = get("/admin/categories")
print(f"   Status: {status}")
print(f"   Has form: {'Add New Category' in html}")
print(f"   Has existing: {'Books' in html}")

# 6. AI Analytics
print("\n6️⃣  AI Analytics...")
status, html = get("/admin/ai_analytics")
print(f"   Status: {status}")
print(f"   Has stats: {'Total Analyzed' in html}")
print(f"   Has table: {'Blur Score' in html or 'Trust Score' in html}")

# 7. Non-admin cannot access
print("\n7️⃣  Access Control Test...")
# Logout first
get("/logout")
# Login as regular user
post("/login", {"email": "rahul@campus.edu", "password": "Test1234"})
status, html = get("/admin/")
blocked = "Access denied" in html or "Admin" not in html or status != 200
print(f"   Non-admin blocked: {'✅' if blocked else '❌'}")

print("\n" + "=" * 60)
print("  ADMIN MODULE TEST COMPLETE!")
print("=" * 60)
print(f"\n🔐 Admin login: admin@campus.edu / Admin@123")
print(f"📊 Admin dashboard: http://localhost:5000/admin/")
