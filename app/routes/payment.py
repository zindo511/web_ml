from flask import Blueprint, render_template, request, session, redirect, url_for
import sqlite3
import datetime
from flask import current_app

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

@payment_bp.route('/<int:house_id>')
def payment(house_id):
    if 'username' not in session or session.get('user_type') != 'buyer':
        return redirect(url_for('auth.login'))
    
    conn = sqlite3.connect(current_app.config['DB_PATH'])
    cur = conn.cursor()
    cur.execute('''SELECT id, seller_username, lot_area, year_built, gr_liv_area,
                   full_bath, bedroom_abv_gr, kitchen_abv_gr, seller_price, 
                   predicted_price, image_path FROM houses WHERE id=? AND status='available' ''',
                (house_id,))
    house = cur.fetchone()
    conn.close()
    
    if not house:
        return redirect(url_for('buyer.buyer_home'))
    
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
        'image_path': house[10]
    }
    
    return render_template('payment.html', house=house_data, username=session['username'])

@payment_bp.route('/confirm/<int:house_id>', methods=['POST'])
def confirm_payment(house_id):
    if 'username' not in session or session.get('user_type') != 'buyer':
        return redirect(url_for('auth.login'))
    
    payment_method = request.form.get('payment_method', 'card')
    full_name = request.form.get('full_name', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    
    try:
        conn = sqlite3.connect(current_app.config['DB_PATH'])
        cur = conn.cursor()
        
        cur.execute('SELECT seller_price FROM houses WHERE id=? AND status="available"', (house_id,))
        house = cur.fetchone()
        
        if not house:
            conn.close()
            return redirect(url_for('buyer.buyer_home'))
        
        seller_price = house[0]
        total_amount = seller_price * 1.02  
        
        cur.execute('''INSERT INTO orders (house_id, buyer_username, order_date, payment_status,
                       payment_method, full_name, phone, address, total_amount)
                       VALUES (?, ?, ?, 'completed', ?, ?, ?, ?, ?)''',
                   (house_id, session['username'], datetime.datetime.utcnow().isoformat(),
                    payment_method, full_name, phone, address, total_amount))
        
        order_id = cur.lastrowid
        
        cur.execute('UPDATE houses SET status="sold" WHERE id=?', (house_id,))
        
        conn.commit()
        conn.close()
        
        return redirect(url_for('payment.payment_success', order_id=order_id))
        
    except Exception as e:
        print(f"Payment error: {e}")
        return redirect(url_for('buyer.buyer_home'))

@payment_bp.route('/success/<int:order_id>')
def payment_success(order_id):
    if 'username' not in session or session.get('user_type') != 'buyer':
        return redirect(url_for('auth.login'))
    
    conn = sqlite3.connect(current_app.config['DB_PATH'])
    cur = conn.cursor()
    
    cur.execute('''SELECT o.id, o.order_date, o.payment_method, o.full_name, o.phone, 
                   o.address, o.total_amount, o.payment_status,
                   h.id, h.seller_username, h.lot_area, h.year_built, h.gr_liv_area,
                   h.full_bath, h.bedroom_abv_gr, h.kitchen_abv_gr, h.seller_price,
                   h.predicted_price, h.image_path
                   FROM orders o
                   JOIN houses h ON o.house_id = h.id
                   WHERE o.id=? AND o.buyer_username=?''', (order_id, session['username']))
    
    order = cur.fetchone()
    conn.close()
    
    if not order:
        return redirect(url_for('buyer.buyer_home'))
    
    order_data = {
        'id': order[0],
        'order_date': order[1],
        'payment_method': order[2],
        'full_name': order[3],
        'phone': order[4],
        'address': order[5],
        'total_amount': order[6],
        'payment_status': order[7],
        'house': {
            'id': order[8],
            'seller_username': order[9],
            'lot_area': order[10],
            'year_built': order[11],
            'gr_liv_area': order[12],
            'full_bath': order[13],
            'bedroom_abv_gr': order[14],
            'kitchen_abv_gr': order[15],
            'seller_price': order[16],
            'predicted_price': order[17],
            'image_path': order[18]
        }
    }
    
    return render_template('payment_success.html', order=order_data, username=session['username'])
