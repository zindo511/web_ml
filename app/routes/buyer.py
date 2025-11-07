from flask import Blueprint, render_template, session, redirect, url_for, abort
import sqlite3
from flask import current_app

# ==========================================================
# ĐỔI TÊN BLUEPRINT ĐỂ TRÁNH TRÙNG LẶP VỚI house_bp
# ==========================================================
buyer_bp = Blueprint('buyer', __name__, url_prefix='/buyer')
house_bp = Blueprint('house', __name__, url_prefix='/house')


@buyer_bp.route('/')
def buyer_home():
    if 'username' not in session or session.get('user_type') != 'buyer':
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect(current_app.config['DB_PATH'])
    conn.row_factory = sqlite3.Row  # Dùng Row factory
    cur = conn.cursor()

    # ==========================================================
    # SỬA SELECT: Lấy 10 đặc trưng, xóa kitchen_abv_gr
    # ==========================================================
    cur.execute('''SELECT id,
                          seller_username,
                          lot_area,
                          gr_liv_area,
                          total_bsmt_sf,
                          year_built,
                          year_remod_add,
                          full_bath,
                          bedroom_abv_gr,
                          overall_qual,
                          overall_cond,
                          garage_cars,
                          seller_price,
                          predicted_price,
                          image_path,
                          status,
                          created_at
                   FROM houses
                   WHERE status = 'available'
                   ORDER BY created_at DESC''',
                )
    houses = cur.fetchall()
    conn.close()

    return render_template('buyer.html', houses=houses, username=session['username'])


@house_bp.route('/<int:house_id>')
def house_detail(house_id):
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect(current_app.config['DB_PATH'])
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # ==========================================================
    # SỬA SELECT: Lấy 10 đặc trưng, xóa kitchen_abv_gr
    # ==========================================================
    cur.execute('''SELECT h.id,
                          h.seller_username,
                          h.lot_area,
                          h.gr_liv_area,
                          h.total_bsmt_sf,
                          h.year_built,
                          h.year_remod_add,
                          h.full_bath,
                          h.bedroom_abv_gr,
                          h.overall_qual,
                          h.overall_cond,
                          h.garage_cars,
                          h.seller_price,
                          h.predicted_price,
                          h.image_path,
                          h.description,
                          h.status,
                          h.created_at,
                          u.username as seller_name
                   FROM houses h
                            JOIN users u ON h.seller_username = u.username
                   WHERE h.id = ?
                     AND h.status = 'available' ''', (house_id,))
    house = cur.fetchone()

    if not house:
        conn.close()
        abort(404)  # Không tìm thấy nhà

    # Lấy các ảnh phụ
    cur.execute('SELECT image_path FROM house_images WHERE house_id=?', (house_id,))
    images = cur.fetchall()

    conn.close()
    return render_template('house_detail.html', house=house, images=images, username=session['username'])


@buyer_bp.route('/orders')
def buyer_orders():
    if 'username' not in session or session.get('user_type') != 'buyer':
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect(current_app.config['DB_PATH'])
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute('''SELECT o.id,
                          o.order_date,
                          o.payment_status,
                          o.total_amount,
                          h.id as house_id,
                          h.image_path
                   FROM orders o
                            JOIN houses h ON o.house_id = h.id
                   WHERE o.buyer_username = ?
                   ORDER BY o.order_date DESC''',
                (session['username'],))
    orders = cur.fetchall()
    conn.close()

    return render_template('buyer_orders.html', orders=orders, username=session['username'])