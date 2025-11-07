from flask import Blueprint, render_template, request, session, redirect, url_for
import sqlite3
import datetime
import os
from flask import current_app
from app.utils import load_model, predict_price, save_upload_file

seller_bp = Blueprint('seller', __name__, url_prefix='/seller')

@seller_bp.route('/')
def seller_home():
    if 'username' not in session or session.get('user_type') != 'seller':
        return redirect(url_for('auth.login'))
    
    conn = sqlite3.connect(current_app.config['DB_PATH'])
    cur = conn.cursor()
    cur.execute('''SELECT id, lot_area, year_built, gr_liv_area, full_bath, 
                   bedroom_abv_gr, kitchen_abv_gr, seller_price, predicted_price, 
                   image_path, status, created_at 
                   FROM houses WHERE seller_username=? ORDER BY created_at DESC''',
                (session['username'],))
    houses = cur.fetchall()
    conn.close()
    
    my_houses = []
    for h in houses:
        my_houses.append({
            'id': h[0],
            'lot_area': h[1],
            'year_built': h[2],
            'gr_liv_area': h[3],
            'full_bath': h[4],
            'bedroom_abv_gr': h[5],
            'kitchen_abv_gr': h[6],
            'seller_price': h[7],
            'predicted_price': h[8],
            'image_path': h[9],
            'status': h[10],
            'created_at': h[11]
        })
    
    return render_template('seller.html', my_houses=my_houses, username=session['username'])

@seller_bp.route('/add', methods=['POST'])
def seller_add_house():
    if 'username' not in session or session.get('user_type') != 'seller':
        return redirect(url_for('auth.login'))
    
    try:
        lot_area = float(request.form.get('lot_area'))
        year_built = int(request.form.get('year_built'))
        gr_liv_area = float(request.form.get('gr_liv_area'))
        full_bath = int(request.form.get('full_bath'))
        bedroom_abv_gr = int(request.form.get('bedroom_abv_gr'))
        kitchen_abv_gr = int(request.form.get('kitchen_abv_gr'))
        seller_price = float(request.form.get('seller_price'))
        description = request.form.get('description', '').strip()
        
        model = load_model()
        features = [lot_area, year_built, gr_liv_area, full_bath, bedroom_abv_gr, kitchen_abv_gr]
        predicted_price = predict_price(model, features)
        
        main_image = request.files.get('image')
        image_path = save_upload_file(main_image) if main_image else None
        
        conn = sqlite3.connect(current_app.config['DB_PATH'])
        cur = conn.cursor()
        cur.execute('''INSERT INTO houses (seller_username, lot_area, year_built, gr_liv_area,
                       full_bath, bedroom_abv_gr, kitchen_abv_gr, seller_price, predicted_price,
                       image_path, description, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (session['username'], lot_area, year_built, gr_liv_area, full_bath,
                    bedroom_abv_gr, kitchen_abv_gr, seller_price, predicted_price,
                    image_path, description, datetime.datetime.utcnow().isoformat()))
        
        house_id = cur.lastrowid
        
        additional_images = request.files.getlist('images')
        for img in additional_images:
            img_path = save_upload_file(img)
            if img_path:
                cur.execute('INSERT INTO house_images (house_id, image_path) VALUES (?, ?)',
                           (house_id, img_path))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Error adding house: {e}")
    
    return redirect(url_for('seller.seller_home'))

@seller_bp.route('/delete/<int:house_id>', methods=['POST'])
def seller_delete_house(house_id):
    if 'username' not in session or session.get('user_type') != 'seller':
        return redirect(url_for('auth.login'))
    
    try:
        conn = sqlite3.connect(current_app.config['DB_PATH'])
        cur = conn.cursor()
        
        cur.execute('SELECT seller_username, status, image_path FROM houses WHERE id=?', (house_id,))
        house = cur.fetchone()
        
        if house and house[0] == session['username'] and house[1] == 'available':
            if house[2]:
                image_file = os.path.join(current_app.config['BASE_DIR'], 'static', house[2])
                if os.path.exists(image_file):
                    os.remove(image_file)
            
            cur.execute('SELECT image_path FROM house_images WHERE house_id=?', (house_id,))
            for row in cur.fetchall():
                if row[0]:
                    img_file = os.path.join(current_app.config['BASE_DIR'], 'static', row[0])
                    if os.path.exists(img_file):
                        os.remove(img_file)
            
            cur.execute('DELETE FROM houses WHERE id=?', (house_id,))
            conn.commit()
        
        conn.close()
    except Exception as e:
        print(f"Error deleting house: {e}")
    
    return redirect(url_for('seller.seller_home'))

@seller_bp.route('/edit/<int:house_id>', methods=['GET', 'POST'])
def seller_edit_house(house_id):
    if 'username' not in session or session.get('user_type') != 'seller':
        return redirect(url_for('auth.login'))
    
    conn = sqlite3.connect(current_app.config['DB_PATH'])
    cur = conn.cursor()
    
    if request.method == 'POST':
        try:
            cur.execute('SELECT seller_username, status FROM houses WHERE id=?', (house_id,))
            house = cur.fetchone()
            
            if not house or house[0] != session['username'] or house[1] != 'available':
                conn.close()
                return redirect(url_for('seller.seller_home'))
            
            lot_area = float(request.form.get('lot_area'))
            year_built = int(request.form.get('year_built'))
            gr_liv_area = float(request.form.get('gr_liv_area'))
            full_bath = int(request.form.get('full_bath'))
            bedroom_abv_gr = int(request.form.get('bedroom_abv_gr'))
            kitchen_abv_gr = int(request.form.get('kitchen_abv_gr'))
            seller_price = float(request.form.get('seller_price'))
            
            model = load_model()
            features = [lot_area, year_built, gr_liv_area, full_bath, bedroom_abv_gr, kitchen_abv_gr]
            predicted_price = predict_price(model, features)
            
            file = request.files.get('image')
            if file and file.filename:
                cur.execute('SELECT image_path FROM houses WHERE id=?', (house_id,))
                old_image = cur.fetchone()[0]
                if old_image:
                    old_file = os.path.join(current_app.config['BASE_DIR'], 'static', old_image)
                    if os.path.exists(old_file):
                        os.remove(old_file)
                
                image_path = save_upload_file(file)
                
                cur.execute('''UPDATE houses SET lot_area=?, year_built=?, gr_liv_area=?,
                               full_bath=?, bedroom_abv_gr=?, kitchen_abv_gr=?, seller_price=?,
                               predicted_price=?, image_path=? WHERE id=?''',
                           (lot_area, year_built, gr_liv_area, full_bath, bedroom_abv_gr,
                            kitchen_abv_gr, seller_price, predicted_price, image_path, house_id))
            else:
                cur.execute('''UPDATE houses SET lot_area=?, year_built=?, gr_liv_area=?,
                               full_bath=?, bedroom_abv_gr=?, kitchen_abv_gr=?, seller_price=?,
                               predicted_price=? WHERE id=?''',
                           (lot_area, year_built, gr_liv_area, full_bath, bedroom_abv_gr,
                            kitchen_abv_gr, seller_price, predicted_price, house_id))
            
            conn.commit()
            conn.close()
            return redirect(url_for('seller.seller_home'))
            
        except Exception as e:
            print(f"Error updating house: {e}")
            conn.close()
            return redirect(url_for('seller.seller_home'))
    
    cur.execute('''SELECT id, lot_area, year_built, gr_liv_area, full_bath,
                   bedroom_abv_gr, kitchen_abv_gr, seller_price, predicted_price,
                   image_path, seller_username, status FROM houses WHERE id=?''', (house_id,))
    house = cur.fetchone()
    conn.close()
    
    if not house or house[10] != session['username'] or house[11] != 'available':
        return redirect(url_for('seller.seller_home'))
    
    house_data = {
        'id': house[0],
        'lot_area': house[1],
        'year_built': house[2],
        'gr_liv_area': house[3],
        'full_bath': house[4],
        'bedroom_abv_gr': house[5],
        'kitchen_abv_gr': house[6],
        'seller_price': house[7],
        'predicted_price': house[8],
        'image_path': house[9]
    }
    
    return render_template('seller_edit.html', house=house_data, username=session['username'])
