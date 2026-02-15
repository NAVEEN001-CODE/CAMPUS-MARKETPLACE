"""
Campus Marketplace — Main Flask Application
A secure, campus-exclusive platform for buying and selling used/unused items.
Enhanced with AI-based image analysis and trust scoring.
"""

import os
import uuid
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import pymysql
import pymysql.cursors

from config import Config
from ai_module import analyze_product_image
from ai_module.trust_scorer import get_trust_label

# ─── App Initialization ─────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Register Admin Blueprint
from admin_routes import admin_bp
app.register_blueprint(admin_bp)


# ─── Database Helper ─────────────────────────────────────────────────
def get_db():
    """Create and return a MySQL database connection."""
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB'],
        port=app.config['MYSQL_PORT'],
        cursorclass=pymysql.cursors.DictCursor,
        charset='utf8mb4'
    )


def query_db(query, args=(), one=False, commit=False):
    """Execute a database query and return results."""
    db = get_db()
    cur = db.cursor()
    cur.execute(query, args)
    if commit:
        db.commit()
        last_id = cur.lastrowid
        cur.close()
        db.close()
        return last_id
    results = cur.fetchone() if one else cur.fetchall()
    cur.close()
    db.close()
    return results


# ─── Auth Decorator ──────────────────────────────────────────────────
def login_required(f):
    """Decorator to protect routes that require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ─── File Upload Helper ─────────────────────────────────────────────
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def save_upload(file):
    """Save uploaded file with a unique name. Returns the filename."""
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filename
    return None


# ═══════════════════════════════════════════════════════════════════
#  ROUTES
# ═══════════════════════════════════════════════════════════════════

# ─── Homepage ────────────────────────────────────────────────────────
@app.route('/')
def index():
    """Homepage — Browse all available products with search and filters."""
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category', '', type=str)
    sort_by = request.args.get('sort', 'newest')

    query = """
        SELECT p.*, u.full_name AS seller_name, c.name AS category_name,
               c.icon AS category_icon,
               ai.trust_score, ai.condition_label
        FROM products p
        JOIN users u ON p.seller_id = u.id
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN product_ai_analysis ai ON ai.product_id = p.id
        WHERE p.status = 'available'
    """
    params = []

    if search:
        query += " AND (p.title LIKE %s OR p.description LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])

    if category_id:
        query += " AND p.category_id = %s"
        params.append(category_id)

    # Sorting
    sort_map = {
        'newest': 'p.created_at DESC',
        'oldest': 'p.created_at ASC',
        'price_low': 'p.price ASC',
        'price_high': 'p.price DESC',
        'trust': 'ai.trust_score DESC',
    }
    query += f" ORDER BY {sort_map.get(sort_by, 'p.created_at DESC')}"

    products = query_db(query, params)
    categories = query_db("SELECT * FROM categories ORDER BY name")

    return render_template('index.html',
                           products=products,
                           categories=categories,
                           search=search,
                           selected_category=category_id,
                           sort_by=sort_by,
                           get_trust_label=get_trust_label)


# ─── User Registration ──────────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        phone = request.form.get('phone', '').strip()
        department = request.form.get('department', '').strip()
        role = request.form.get('role', 'student')

        errors = []
        if not full_name:
            errors.append('Full name is required.')
        if not email or '@' not in email:
            errors.append('Valid email is required.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm:
            errors.append('Passwords do not match.')

        # Check if email already exists
        existing = query_db("SELECT id FROM users WHERE email = %s", (email,), one=True)
        if existing:
            errors.append('An account with this email already exists.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register.html')

        password_hash = generate_password_hash(password)
        query_db(
            """INSERT INTO users (full_name, email, password_hash, phone, department, role)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (full_name, email, password_hash, phone, department, role),
            commit=True
        )
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# ─── User Login ──────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = query_db(
            "SELECT * FROM users WHERE email = %s", (email,), one=True
        )

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['user_email'] = user['email']
            session['user_role'] = user['role']
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            # Redirect admin to admin dashboard
            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


# ─── Logout ──────────────────────────────────────────────────────────
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ─── Add Product (with AI Analysis) ─────────────────────────────────
@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    """Upload a new product listing. Triggers AI image analysis."""
    categories = query_db("SELECT * FROM categories ORDER BY name")

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', 0, type=float)
        category_id = request.form.get('category_id', None, type=int)
        item_condition = request.form.get('item_condition', 'Used')
        file = request.files.get('image')

        errors = []
        if not title:
            errors.append('Product title is required.')
        if price <= 0:
            errors.append('Price must be greater than zero.')
        if not file or file.filename == '':
            errors.append('Product image is required.')
        elif file and not allowed_file(file.filename):
            errors.append('Invalid image format. Use JPG, PNG, GIF, or WebP.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('add_product.html', categories=categories)

        # Save uploaded image
        filename = save_upload(file)
        if not filename:
            flash('Error saving image.', 'danger')
            return render_template('add_product.html', categories=categories)

        # Insert product into database
        product_id = query_db(
            """INSERT INTO products
               (seller_id, title, description, price, category_id, item_condition, image_filename)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (session['user_id'], title, description, price,
             category_id, item_condition, filename),
            commit=True
        )

        # ── AI IMAGE ANALYSIS ──
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            ai_result = analyze_product_image(image_path, description)

            # Store AI results in database
            query_db(
                """INSERT INTO product_ai_analysis
                   (product_id, blur_score, is_blurry, condition_label,
                    condition_confidence, feedback_text, trust_score)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (product_id,
                 ai_result['blur_score'],
                 ai_result['is_blurry'],
                 ai_result['condition_label'],
                 ai_result['condition_confidence'],
                 ai_result['feedback_text'],
                 ai_result['trust_score']),
                commit=True
            )
        except Exception as e:
            print(f"[AI Analysis Error] {e}")
            # Product is still saved even if AI fails

        flash('Product listed successfully! AI analysis complete.', 'success')
        return redirect(url_for('product_detail', product_id=product_id))

    return render_template('add_product.html', categories=categories)


# ─── Product Detail ──────────────────────────────────────────────────
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """View a single product with AI analysis feedback."""
    product = query_db(
        """SELECT p.*, u.full_name AS seller_name, u.email AS seller_email,
                  u.department AS seller_department, u.phone AS seller_phone,
                  c.name AS category_name, c.icon AS category_icon
           FROM products p
           JOIN users u ON p.seller_id = u.id
           LEFT JOIN categories c ON p.category_id = c.id
           WHERE p.id = %s""",
        (product_id,), one=True
    )

    if not product:
        abort(404)

    # Increment view count
    query_db("UPDATE products SET views_count = views_count + 1 WHERE id = %s",
             (product_id,), commit=True)

    # Get AI analysis
    ai_analysis = query_db(
        "SELECT * FROM product_ai_analysis WHERE product_id = %s",
        (product_id,), one=True
    )

    trust_info = None
    if ai_analysis:
        trust_info = get_trust_label(ai_analysis['trust_score'])

    return render_template('product_detail.html',
                           product=product,
                           ai_analysis=ai_analysis,
                           trust_info=trust_info)


# ─── My Listings ─────────────────────────────────────────────────────
@app.route('/my_listings')
@login_required
def my_listings():
    """View current user's product listings."""
    products = query_db(
        """SELECT p.*, c.name AS category_name,
                  ai.trust_score, ai.condition_label
           FROM products p
           LEFT JOIN categories c ON p.category_id = c.id
           LEFT JOIN product_ai_analysis ai ON ai.product_id = p.id
           WHERE p.seller_id = %s
           ORDER BY p.created_at DESC""",
        (session['user_id'],)
    )
    return render_template('my_listings.html',
                           products=products,
                           get_trust_label=get_trust_label)


# ─── Mark as Sold ────────────────────────────────────────────────────
@app.route('/product/<int:product_id>/sold', methods=['POST'])
@login_required
def mark_sold(product_id):
    product = query_db("SELECT * FROM products WHERE id = %s AND seller_id = %s",
                       (product_id, session['user_id']), one=True)
    if not product:
        abort(403)
    query_db("UPDATE products SET status = 'sold' WHERE id = %s",
             (product_id,), commit=True)
    flash('Product marked as sold!', 'success')
    return redirect(url_for('my_listings'))


# ─── Delete Product ──────────────────────────────────────────────────
@app.route('/product/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    product = query_db("SELECT * FROM products WHERE id = %s AND seller_id = %s",
                       (product_id, session['user_id']), one=True)
    if not product:
        abort(403)

    # Delete image file
    if product['image_filename']:
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], product['image_filename'])
        if os.path.exists(img_path):
            os.remove(img_path)

    query_db("DELETE FROM products WHERE id = %s", (product_id,), commit=True)
    flash('Product deleted.', 'info')
    return redirect(url_for('my_listings'))


# ─── Messages ────────────────────────────────────────────────────────
@app.route('/messages')
@login_required
def messages():
    """View all conversations for the current user."""
    conversations = query_db(
        """SELECT DISTINCT
               CASE WHEN m.sender_id = %s THEN m.receiver_id ELSE m.sender_id END AS other_user_id,
               u.full_name AS other_user_name,
               p.title AS product_title,
               p.id AS product_id,
               (SELECT message_text FROM messages
                WHERE (sender_id = m.sender_id AND receiver_id = m.receiver_id)
                   OR (sender_id = m.receiver_id AND receiver_id = m.sender_id)
                ORDER BY created_at DESC LIMIT 1) AS last_message,
               (SELECT created_at FROM messages
                WHERE (sender_id = m.sender_id AND receiver_id = m.receiver_id)
                   OR (sender_id = m.receiver_id AND receiver_id = m.sender_id)
                ORDER BY created_at DESC LIMIT 1) AS last_time
           FROM messages m
           JOIN users u ON u.id = CASE WHEN m.sender_id = %s THEN m.receiver_id ELSE m.sender_id END
           LEFT JOIN products p ON p.id = m.product_id
           WHERE m.sender_id = %s OR m.receiver_id = %s
           GROUP BY other_user_id, u.full_name, p.title, p.id
           ORDER BY last_time DESC""",
        (session['user_id'], session['user_id'],
         session['user_id'], session['user_id'])
    )
    return render_template('messages.html', conversations=conversations)


@app.route('/messages/<int:other_user_id>', methods=['GET', 'POST'])
@login_required
def chat(other_user_id):
    """Chat with another user."""
    product_id = request.args.get('product_id', None, type=int)

    if request.method == 'POST':
        message_text = request.form.get('message', '').strip()
        prod_id = request.form.get('product_id', None, type=int)
        if message_text:
            query_db(
                """INSERT INTO messages (sender_id, receiver_id, product_id, message_text)
                   VALUES (%s, %s, %s, %s)""",
                (session['user_id'], other_user_id, prod_id, message_text),
                commit=True
            )

    # Fetch all messages
    chat_messages = query_db(
        """SELECT m.*, u.full_name AS sender_name
           FROM messages m
           JOIN users u ON m.sender_id = u.id
           WHERE ((m.sender_id = %s AND m.receiver_id = %s)
               OR (m.sender_id = %s AND m.receiver_id = %s))
           ORDER BY m.created_at ASC""",
        (session['user_id'], other_user_id,
         other_user_id, session['user_id'])
    )

    # Mark as read
    query_db(
        """UPDATE messages SET is_read = TRUE
           WHERE sender_id = %s AND receiver_id = %s AND is_read = FALSE""",
        (other_user_id, session['user_id']),
        commit=True
    )

    other_user = query_db("SELECT * FROM users WHERE id = %s",
                          (other_user_id,), one=True)

    return render_template('chat.html',
                           messages=chat_messages,
                           other_user=other_user,
                           product_id=product_id)


# ─── AI Analysis API (AJAX Endpoint) ────────────────────────────────
@app.route('/api/analyze_image', methods=['POST'])
@login_required
def api_analyze_image():
    """
    AJAX endpoint: Analyze an uploaded image and return AI results as JSON.
    Used for live preview during product upload.
    """
    file = request.files.get('image')
    description = request.form.get('description', '')

    if not file or file.filename == '':
        return jsonify({'error': 'No image provided'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file format'}), 400

    # Save temporarily
    filename = save_upload(file)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        result = analyze_product_image(image_path, description)
        trust_info = get_trust_label(result['trust_score'])
        result['trust_label'] = trust_info['label']
        result['trust_color'] = trust_info['color']
        result['trust_icon'] = trust_info['icon']
        result['temp_filename'] = filename
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─── Error Handlers ─────────────────────────────────────────────────
@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html',
                           error_code=404,
                           error_message='Page not found'), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('base.html',
                           error_code=403,
                           error_message='Access denied'), 403


# ─── Run ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
