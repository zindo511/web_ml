from flask import Blueprint, render_template, session, redirect, url_for, abort
import sqlite3
from flask import current_app


buyer_bp = Blueprint('buyer', __name__, url_prefix='/buyer')
house_bp = Blueprint('house', __name__, url_prefix='/house')


@buyer_bp.route('/')
def buyer_home():
    if 'username' not in session or session.get('user_type') != 'buyer':
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect(current_app.config['DB_PATH'])
    conn.row_factory = sqlite3.Row  # Dùng Row factory
    cur = conn.cursor()


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

    # Lấy dữ liệu đơn hàng cùng thông tin nhà
    cur.execute('''
        SELECT o.id as order_id,
               o.order_date,
               o.payment_status,
               o.total_amount,
               o.payment_method,
               o.full_name,
               o.phone,
               o.address,
               h.id as house_id,
               h.seller_username as house_seller_username,
               h.lot_area as house_lot_area,
               h.year_built as house_year_built,
               h.gr_liv_area as house_gr_liv_area,
               h.full_bath as house_full_bath,
               h.bedroom_abv_gr as house_bedroom_abv_gr,
               h.garage_cars as house_garage_cars,
               h.overall_qual as house_overall_qual,
               h.overall_cond as house_overall_cond,
               h.seller_price as house_seller_price,
               h.predicted_price as house_predicted_price,
               h.image_path as house_image_path
        FROM orders o
        JOIN houses h ON o.house_id = h.id
        WHERE o.buyer_username = ?
        ORDER BY o.order_date DESC
    ''', (session['username'],))

    rows = cur.fetchall()
    conn.close()

    # Chuyển Row thành list dict tương thích với template
    orders = []
    for row in rows:
        orders.append({
            'id': row['order_id'],
            'order_date': row['order_date'],
            'payment_status': row['payment_status'],
            'total_amount': row['total_amount'],
            'payment_method': row['payment_method'],
            'full_name': row['full_name'],
            'phone': row['phone'],
            'address': row['address'],
            'house_id': row['house_id'],
            'house_image_path': row['house_image_path'],
            'house_seller_username': row['house_seller_username'],
            'house_lot_area': row['house_lot_area'],
            'house_year_built': row['house_year_built'],
            'house_gr_liv_area': row['house_gr_liv_area'],
            'house_full_bath': row['house_full_bath'],
            'house_bedroom_abv_gr': row['house_bedroom_abv_gr'],
            'house_garage_cars': row['house_garage_cars'],
            'house_overall_qual': row['house_overall_qual'],
            'house_overall_cond': row['house_overall_cond'],
            'house_seller_price': row['house_seller_price'],
            'house_predicted_price': row['house_predicted_price'],
        })

    return render_template('buyer_orders.html', orders=orders, username=session['username'])
