"""
Admin Module — Routes and Helpers
Provides admin dashboard, user management, product management, and category management.
"""

from functools import wraps
from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, session, abort, jsonify
)
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ─── Admin Auth Decorator ───────────────────────────────────────────
def admin_required(f):
    """Decorator to protect admin-only routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        if session.get('user_role') != 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# ─── Helpers (import from app) ──────────────────────────────────────
def get_query_db():
    """Get query_db from the app module."""
    from app import query_db
    return query_db


# ═══════════════════════════════════════════════════════════════════
#  ADMIN DASHBOARD
# ═══════════════════════════════════════════════════════════════════

@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard with platform statistics."""
    query_db = get_query_db()

    # Aggregate stats
    stats = {
        'total_users': query_db(
            "SELECT COUNT(*) AS cnt FROM users WHERE role != 'admin'", one=True
        )['cnt'],
        'total_products': query_db(
            "SELECT COUNT(*) AS cnt FROM products", one=True
        )['cnt'],
        'active_products': query_db(
            "SELECT COUNT(*) AS cnt FROM products WHERE status = 'available'", one=True
        )['cnt'],
        'sold_products': query_db(
            "SELECT COUNT(*) AS cnt FROM products WHERE status = 'sold'", one=True
        )['cnt'],
        'total_messages': query_db(
            "SELECT COUNT(*) AS cnt FROM messages", one=True
        )['cnt'],
        'total_categories': query_db(
            "SELECT COUNT(*) AS cnt FROM categories", one=True
        )['cnt'],
        'ai_analyzed': query_db(
            "SELECT COUNT(*) AS cnt FROM product_ai_analysis", one=True
        )['cnt'],
    }

    # Average trust score
    avg_trust = query_db(
        "SELECT AVG(trust_score) AS avg_score FROM product_ai_analysis", one=True
    )
    stats['avg_trust_score'] = round(avg_trust['avg_score'] or 0, 1)

    # Recent users (last 5)
    recent_users = query_db(
        "SELECT * FROM users WHERE role != 'admin' ORDER BY created_at DESC LIMIT 5"
    )

    # Recent products (last 5)
    recent_products = query_db("""
        SELECT p.*, u.full_name AS seller_name, ai.trust_score
        FROM products p
        JOIN users u ON p.seller_id = u.id
        LEFT JOIN product_ai_analysis ai ON ai.product_id = p.id
        ORDER BY p.created_at DESC LIMIT 5
    """)

    # Category distribution
    category_stats = query_db("""
        SELECT c.name, COUNT(p.id) AS product_count
        FROM categories c
        LEFT JOIN products p ON p.category_id = c.id
        GROUP BY c.id, c.name
        ORDER BY product_count DESC
    """)

    # Condition distribution from AI analysis
    condition_stats = query_db("""
        SELECT condition_label, COUNT(*) AS cnt
        FROM product_ai_analysis
        GROUP BY condition_label
    """)

    return render_template('admin/dashboard.html',
                           stats=stats,
                           recent_users=recent_users,
                           recent_products=recent_products,
                           category_stats=category_stats,
                           condition_stats=condition_stats)


# ═══════════════════════════════════════════════════════════════════
#  USER MANAGEMENT
# ═══════════════════════════════════════════════════════════════════

@admin_bp.route('/users')
@admin_required
def manage_users():
    """View and manage all users."""
    query_db = get_query_db()
    search = request.args.get('search', '').strip()
    role_filter = request.args.get('role', '')

    query = """
        SELECT u.*, 
               (SELECT COUNT(*) FROM products WHERE seller_id = u.id) AS product_count
        FROM users u
        WHERE u.role != 'admin'
    """
    params = []

    if search:
        query += " AND (u.full_name LIKE %s OR u.email LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])
    if role_filter:
        query += " AND u.role = %s"
        params.append(role_filter)

    query += " ORDER BY u.created_at DESC"

    users = query_db(query, params)
    return render_template('admin/users.html',
                           users=users, search=search, role_filter=role_filter)


@admin_bp.route('/users/<int:user_id>/toggle_status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Block or unblock a user by changing their role."""
    query_db = get_query_db()
    user = query_db("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
    if not user or user['role'] == 'admin':
        abort(404)

    new_role = request.form.get('new_role', 'student')
    query_db("UPDATE users SET role = %s WHERE id = %s", (new_role, user_id), commit=True)
    flash(f"User '{user['full_name']}' role updated to '{new_role}'.", 'success')
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user and all their data."""
    query_db = get_query_db()
    user = query_db("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
    if not user or user['role'] == 'admin':
        abort(404)

    # Delete user's product images
    products = query_db("SELECT image_filename FROM products WHERE seller_id = %s", (user_id,))
    from flask import current_app
    for p in products:
        if p['image_filename']:
            img_path = os.path.join(current_app.config['UPLOAD_FOLDER'], p['image_filename'])
            if os.path.exists(img_path):
                os.remove(img_path)

    query_db("DELETE FROM users WHERE id = %s", (user_id,), commit=True)
    flash(f"User '{user['full_name']}' has been deleted.", 'info')
    return redirect(url_for('admin.manage_users'))


# ═══════════════════════════════════════════════════════════════════
#  PRODUCT MANAGEMENT
# ═══════════════════════════════════════════════════════════════════

@admin_bp.route('/products')
@admin_required
def manage_products():
    """View and manage all products."""
    query_db = get_query_db()
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')

    query = """
        SELECT p.*, u.full_name AS seller_name, u.email AS seller_email,
               c.name AS category_name,
               ai.trust_score, ai.condition_label, ai.is_blurry
        FROM products p
        JOIN users u ON p.seller_id = u.id
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN product_ai_analysis ai ON ai.product_id = p.id
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (p.title LIKE %s OR p.description LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])
    if status_filter:
        query += " AND p.status = %s"
        params.append(status_filter)
    if category_filter:
        query += " AND p.category_id = %s"
        params.append(category_filter)

    query += " ORDER BY p.created_at DESC"

    products = query_db(query, params)
    categories = query_db("SELECT * FROM categories ORDER BY name")

    return render_template('admin/products.html',
                           products=products, categories=categories,
                           search=search, status_filter=status_filter,
                           category_filter=category_filter)


@admin_bp.route('/products/<int:product_id>/remove', methods=['POST'])
@admin_required
def remove_product(product_id):
    """Admin removes a product listing."""
    query_db = get_query_db()
    product = query_db("SELECT * FROM products WHERE id = %s", (product_id,), one=True)
    if not product:
        abort(404)

    # Delete image file
    if product['image_filename']:
        from flask import current_app
        img_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product['image_filename'])
        if os.path.exists(img_path):
            os.remove(img_path)

    query_db("DELETE FROM products WHERE id = %s", (product_id,), commit=True)
    flash(f"Product '{product['title']}' has been removed.", 'info')
    return redirect(url_for('admin.manage_products'))


@admin_bp.route('/products/<int:product_id>/toggle_status', methods=['POST'])
@admin_required
def toggle_product_status(product_id):
    """Toggle product status (available/removed)."""
    query_db = get_query_db()
    product = query_db("SELECT * FROM products WHERE id = %s", (product_id,), one=True)
    if not product:
        abort(404)

    new_status = 'removed' if product['status'] == 'available' else 'available'
    query_db("UPDATE products SET status = %s WHERE id = %s", (new_status, product_id), commit=True)
    flash(f"Product '{product['title']}' status changed to '{new_status}'.", 'success')
    return redirect(url_for('admin.manage_products'))


# ═══════════════════════════════════════════════════════════════════
#  CATEGORY MANAGEMENT
# ═══════════════════════════════════════════════════════════════════

@admin_bp.route('/categories')
@admin_required
def manage_categories():
    """View and manage categories."""
    query_db = get_query_db()
    categories = query_db("""
        SELECT c.*, COUNT(p.id) AS product_count
        FROM categories c
        LEFT JOIN products p ON p.category_id = c.id
        GROUP BY c.id, c.name, c.icon
        ORDER BY c.name
    """)
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/categories/add', methods=['POST'])
@admin_required
def add_category():
    """Add a new category."""
    query_db = get_query_db()
    name = request.form.get('name', '').strip()
    icon = request.form.get('icon', 'bi-tag').strip()

    if not name:
        flash('Category name is required.', 'danger')
        return redirect(url_for('admin.manage_categories'))

    existing = query_db("SELECT id FROM categories WHERE name = %s", (name,), one=True)
    if existing:
        flash('Category already exists.', 'warning')
        return redirect(url_for('admin.manage_categories'))

    query_db("INSERT INTO categories (name, icon) VALUES (%s, %s)", (name, icon), commit=True)
    flash(f"Category '{name}' added successfully.", 'success')
    return redirect(url_for('admin.manage_categories'))


@admin_bp.route('/categories/<int:category_id>/edit', methods=['POST'])
@admin_required
def edit_category(category_id):
    """Edit a category."""
    query_db = get_query_db()
    name = request.form.get('name', '').strip()
    icon = request.form.get('icon', 'bi-tag').strip()

    if not name:
        flash('Category name is required.', 'danger')
        return redirect(url_for('admin.manage_categories'))

    query_db("UPDATE categories SET name = %s, icon = %s WHERE id = %s",
             (name, icon, category_id), commit=True)
    flash(f"Category updated successfully.", 'success')
    return redirect(url_for('admin.manage_categories'))


@admin_bp.route('/categories/<int:category_id>/delete', methods=['POST'])
@admin_required
def delete_category(category_id):
    """Delete a category."""
    query_db = get_query_db()
    cat = query_db("SELECT * FROM categories WHERE id = %s", (category_id,), one=True)
    if not cat:
        abort(404)

    query_db("DELETE FROM categories WHERE id = %s", (category_id,), commit=True)
    flash(f"Category '{cat['name']}' deleted.", 'info')
    return redirect(url_for('admin.manage_categories'))


# ═══════════════════════════════════════════════════════════════════
#  AI ANALYTICS
# ═══════════════════════════════════════════════════════════════════

@admin_bp.route('/ai_analytics')
@admin_required
def ai_analytics():
    """View AI analysis statistics and reports."""
    query_db = get_query_db()

    # All analyzed products
    analyses = query_db("""
        SELECT ai.*, p.title AS product_title, p.image_filename, 
               u.full_name AS seller_name
        FROM product_ai_analysis ai
        JOIN products p ON ai.product_id = p.id
        JOIN users u ON p.seller_id = u.id
        ORDER BY ai.analyzed_at DESC
    """)

    # Stats
    total = len(analyses)
    blurry_count = sum(1 for a in analyses if a['is_blurry'])
    avg_trust = sum(a['trust_score'] for a in analyses) / total if total > 0 else 0

    condition_counts = {}
    for a in analyses:
        label = a['condition_label'] or 'Unknown'
        condition_counts[label] = condition_counts.get(label, 0) + 1

    ai_stats = {
        'total_analyzed': total,
        'blurry_count': blurry_count,
        'clear_count': total - blurry_count,
        'avg_trust_score': round(avg_trust, 1),
        'condition_counts': condition_counts,
    }

    return render_template('admin/ai_analytics.html',
                           analyses=analyses, ai_stats=ai_stats)
