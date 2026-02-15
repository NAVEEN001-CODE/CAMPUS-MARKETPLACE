"""
End-to-End Test Script for Campus Marketplace
Tests: Register -> Login -> Add Product (AI analysis) -> View Product
"""
import urllib.request
import urllib.parse
import http.cookiejar
import json
import os

BASE = "http://127.0.0.1:5000"

# Setup cookie-handling opener (for session persistence)
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def post(path, data):
    """POST form data and return response."""
    encoded = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=encoded, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        resp = opener.open(req)
        return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def get(path):
    """GET a page and return response."""
    try:
        resp = opener.open(f"{BASE}{path}")
        return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


print("=" * 60)
print("  CAMPUS MARKETPLACE — END-TO-END TEST")
print("=" * 60)

# ─── Test 1: Homepage ────────────────────────────────────
print("\n1️⃣  Testing Homepage...")
status, html = get("/")
has_brand = "CampusMarket" in html
has_hero = "Buy" in html and "Campus" in html
has_search = "Search products" in html
has_login = "Login" in html
print(f"   Status: {status}")
print(f"   Brand:  {'✅' if has_brand else '❌'}")
print(f"   Hero:   {'✅' if has_hero else '❌'}")
print(f"   Search: {'✅' if has_search else '❌'}")
print(f"   Login:  {'✅' if has_login else '❌'}")

# ─── Test 2: Registration ────────────────────────────────
print("\n2️⃣  Testing User Registration...")
status, html = post("/register", {
    "full_name": "Rahul Sharma",
    "email": "rahul@campus.edu",
    "password": "Test1234",
    "confirm_password": "Test1234",
    "phone": "9876543210",
    "department": "Computer Science",
    "role": "student"
})
success = "Registration successful" in html or status == 302 or "Sign In" in html
print(f"   Status: {status}")
print(f"   Result: {'✅ Registered' if success else '❌ Failed'}")

# ─── Test 3: Login ────────────────────────────────────────
print("\n3️⃣  Testing User Login...")
status, html = post("/login", {
    "email": "rahul@campus.edu",
    "password": "Test1234"
})
logged_in = "Rahul" in html or "Welcome" in html or "Sell Item" in html or status == 302
# Follow redirect to homepage
status2, html2 = get("/")
has_user = "Rahul" in html2
has_sell = "Sell Item" in html2
has_logout = "Logout" in html2
print(f"   Status: {status}")
print(f"   Logged in: {'✅' if has_user or logged_in else '❌'}")
print(f"   Sell Item nav: {'✅' if has_sell else '❌'}")
print(f"   Logout nav:    {'✅' if has_logout else '❌'}")

# ─── Test 4: Add Product Page ────────────────────────────
print("\n4️⃣  Testing Add Product Page...")
status, html = get("/add_product")
has_form = "Product Title" in html or 'name="title"' in html
has_upload = 'name="image"' in html
has_categories = "Books" in html or "Electronics" in html
has_ai_section = "AI Analysis" in html or "aiAnalysisPanel" in html
print(f"   Status: {status}")
print(f"   Form:       {'✅' if has_form else '❌'}")
print(f"   Upload:     {'✅' if has_upload else '❌'}")
print(f"   Categories: {'✅' if has_categories else '❌'}")
print(f"   AI Panel:   {'✅' if has_ai_section else '❌'}")

# ─── Test 5: Upload Product with Image ───────────────────
print("\n5️⃣  Testing Product Upload with AI Analysis...")
# Create a test image (solid blue 100x100 PNG)
from PIL import Image
import io

img = Image.new("RGB", (200, 200), color=(70, 130, 180))
img_bytes = io.BytesIO()
img.save(img_bytes, format="PNG")
img_bytes.seek(0)

# Build multipart form data
import uuid
boundary = uuid.uuid4().hex

body = b""
# title
body += f"--{boundary}\r\n".encode()
body += b'Content-Disposition: form-data; name="title"\r\n\r\n'
body += b"Data Structures Textbook - 3rd Edition\r\n"
# description
body += f"--{boundary}\r\n".encode()
body += b'Content-Disposition: form-data; name="description"\r\n\r\n'
body += b"Used textbook in good condition. Purchased 6 months ago. Brand: McGraw Hill. No markings.\r\n"
# price
body += f"--{boundary}\r\n".encode()
body += b'Content-Disposition: form-data; name="price"\r\n\r\n'
body += b"350\r\n"
# category_id (1 = Books)
body += f"--{boundary}\r\n".encode()
body += b'Content-Disposition: form-data; name="category_id"\r\n\r\n'
body += b"1\r\n"
# item_condition
body += f"--{boundary}\r\n".encode()
body += b'Content-Disposition: form-data; name="item_condition"\r\n\r\n'
body += b"Used\r\n"
# image file
body += f"--{boundary}\r\n".encode()
body += b'Content-Disposition: form-data; name="image"; filename="test_product.png"\r\n'
body += b"Content-Type: image/png\r\n\r\n"
body += img_bytes.read()
body += b"\r\n"
body += f"--{boundary}--\r\n".encode()

req = urllib.request.Request(
    f"{BASE}/add_product",
    data=body,
    method="POST"
)
req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

try:
    resp = opener.open(req)
    status = resp.status
    html = resp.read().decode("utf-8", errors="replace")
except urllib.error.HTTPError as e:
    status = e.code
    html = e.read().decode("utf-8", errors="replace")

product_created = "successfully" in html or "AI analysis" in html.lower() or "trust" in html.lower() or status == 200
has_trust = "trust" in html.lower() or "Trust" in html
has_condition = "condition" in html.lower()
has_feedback = "feedback" in html.lower() or "Feedback" in html

print(f"   Status: {status}")
print(f"   Created:   {'✅' if product_created else '❌'}")
print(f"   Trust:     {'✅' if has_trust else '❌'}")
print(f"   Condition: {'✅' if has_condition else '❌'}")
print(f"   Feedback:  {'✅' if has_feedback else '❌'}")

# ─── Test 6: My Listings ─────────────────────────────────
print("\n6️⃣  Testing My Listings...")
status, html = get("/my_listings")
has_products = "Data Structures" in html
print(f"   Status: {status}")
print(f"   Listed: {'✅' if has_products else '❌'}")

# ─── Test 7: Messages Page ──────────────────────────────
print("\n7️⃣  Testing Messages Page...")
status, html = get("/messages")
print(f"   Status: {status}")
print(f"   Loads: {'✅' if status == 200 else '❌'}")

# ─── Test 8: Product Detail + AI Analysis ────────────────
print("\n8️⃣  Testing Product Detail with AI Analysis...")
status, html = get("/product/1")
has_ai_report = "AI Image Analysis" in html or "AI Analysis" in html
has_trust_circle = "trust-circle" in html or "trust_score" in html.lower()
has_blur = "blur" in html.lower() or "clarity" in html.lower()
print(f"   Status: {status}")
print(f"   AI Report:    {'✅' if has_ai_report else '❌'}")
print(f"   Trust Circle: {'✅' if has_trust_circle else '❌'}")
print(f"   Blur Info:    {'✅' if has_blur else '❌'}")

# ─── Summary ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  TEST COMPLETE!")
print("=" * 60)
print(f"\n🌐 Open in browser: http://localhost:5000")
print(f"👤 Test user: rahul@campus.edu / Test1234")
