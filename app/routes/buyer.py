from flask import Blueprint, render_template, session, redirect, url_for
import sqlite3
from flask import current_app

buyer_bp = Blueprint('buyer', __name__, url_prefix='/buyer')

@buyer_bp.route('/')
def buyer_home():
    if 'username' not in session or session.get('user_type') != 'buyer':
        return redirect(url_for('auth.login'))
    
    conn = sqlite3.connect(current_app.config['DB_PATH'])
    cur = conn.cursor()
    cur.execute('''SELECT id, seller_username, lot_area, year_built, gr_liv_area, 
                   full_bath, bedroom_abv_gr, kitchen_abv_gr, seller_price, 
                   predicted_price, image_path, created_at 
                   FROM houses WHERE status='available' ORDER BY created_at DESC''')
    houses = cur.fetchall()
    conn.close()
    
    houses_list = []
    for h in houses:
        houses_list.append({
            'id': h[0],
            'seller_username': h[1],
            'lot_area': h[2],
            'year_built': h[3],
            'gr_liv_area': h[4],
            'full_bath': h[5],
            'bedroom_abv_gr': h[6],
            'kitchen_abv_gr': h[7],
            'seller_price': h[8],
            'predicted_price': h[9],
            'image_path': h[10],
            'created_at': h[11]
        })
    
    return render_template('buyer.html', houses=houses_list, username=session['username'])

@buyer_bp.route('/orders')
def buyer_orders():
    if 'username' not in session or session.get('user_type') != 'buyer':
        return redirect(url_for('auth.login'))
    
    conn = sqlite3.connect(current_app.config['DB_PATH'])
    cur = conn.cursor()
    
    cur.execute('''SELECT o.id, o.order_date, o.payment_method, o.payment_status, 
                   o.total_amount, o.full_name, o.phone, o.address,
                   h.id, h.seller_username, h.lot_area, h.year_built, h.gr_liv_area,
                   h.full_bath, h.bedroom_abv_gr, h.kitchen_abv_gr, h.seller_price,
                   h.predicted_price, h.image_path
                   FROM orders o
                   JOIN houses h ON o.house_id = h.id
                   WHERE o.buyer_username=?
                   ORDER BY o.order_date DESC''', (session['username'],))
    
    orders = cur.fetchall()
    conn.close()
    
    orders_list = []
    for o in orders:
        orders_list.append({
            'id': o[0],
            'order_date': o[1],
            'payment_method': o[2],
            'payment_status': o[3],
            'total_amount': o[4],
            'full_name': o[5],
            'phone': o[6],
            'address': o[7],
            'house': {
                'id': o[8],
                'seller_username': o[9],
                'lot_area': o[10],
                'year_built': o[11],
                'gr_liv_area': o[12],
                'full_bath': o[13],
                'bedroom_abv_gr': o[14],
                'kitchen_abv_gr': o[15],
                'seller_price': o[16],
                'predicted_price': o[17],
                'image_path': o[18]
            }
        })
    
    return render_template('buyer_orders.html', orders=orders_list, username=session['username'])

from flask import Blueprint as BP
house_bp = BP('house', __name__)

@house_bp.route('/house/<int:house_id>')
def house_detail(house_id):
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    conn = sqlite3.connect(current_app.config['DB_PATH'])
    cur = conn.cursor()
    
    cur.execute('''SELECT id, seller_username, lot_area, year_built, gr_liv_area, 
                   full_bath, bedroom_abv_gr, kitchen_abv_gr, seller_price, 
                   predicted_price, image_path, description, status, created_at 
                   FROM houses WHERE id=?''', (house_id,))
    house = cur.fetchone()
    
    if not house:
        conn.close()
        return redirect(url_for('buyer.buyer_home'))
    
    cur.execute('SELECT image_path FROM house_images WHERE house_id=?', (house_id,))
    additional_images = [row[0] for row in cur.fetchall()]
    
    conn.close()
    
    house_data = {
        'id': house[0],
        'seller_username': house[1],
        'lot_area': house[2],
        'year_built': house[3],
        'gr_liv_area': house[4],
        'full_bath': house[5],
        'bedroom_abv_gr': house[6],
        'kitchen_abv_gr': house[7],
        'seller_price': house[8],
        'predicted_price': house[9],
        'image_path': house[10],
        'description': house[11],
        'status': house[12],
        'created_at': house[13],
        'additional_images': additional_images
    }
    
    return render_template('house_detail.html', house=house_data, username=session['username'])
