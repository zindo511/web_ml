from flask import Blueprint, render_template, request, session, redirect, url_for, flash
import sqlite3
import datetime
import os
from flask import current_app
from app.utils import load_model, predict_price, save_upload_file, FEATURE_NAMES

seller_bp = Blueprint('seller', __name__, url_prefix='/seller')

# Hệ số chuyển đổi từ m² sang ft²
M2_TO_FT2 = 10.764


@seller_bp.route('/')
def seller_home():
    if 'username' not in session or session.get('user_type') != 'seller':
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect(current_app.config['DB_PATH'])
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute('''SELECT id,
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
                   WHERE seller_username = ?
                   ORDER BY created_at DESC''',
                (session['username'],))
    houses = cur.fetchall()
    conn.close()

    return render_template('seller.html', my_houses=houses, username=session['username'])


@seller_bp.route('/add', methods=['POST'])
def seller_add_house():
    if 'username' not in session or session.get('user_type') != 'seller':
        return redirect(url_for('auth.login'))

    try:
        # Lấy giá trị từ form (đơn vị m²) và chuyển sang ft² (làm tròn)
        lot_area = round(float(request.form['lot_area']) * M2_TO_FT2)
        gr_liv_area = round(float(request.form['gr_liv_area']) * M2_TO_FT2)
        total_bsmt_sf = round(float(request.form['total_bsmt_sf']) * M2_TO_FT2)

        year_built = int(request.form['year_built'])
        year_remod_add = int(request.form['year_remod_add'])
        full_bath = int(request.form['full_bath'])
        bedroom_abv_gr = int(request.form['bedroom_abv_gr'])
        overall_qual = int(request.form['overall_qual'])
        overall_cond = int(request.form['overall_cond'])
        garage_cars = int(request.form['garage_cars'])

        seller_price = float(request.form.get('seller_price'))
        description = request.form.get('description', '').strip()

        model = load_model()
        features = [
            lot_area, gr_liv_area, total_bsmt_sf,
            year_built, year_remod_add,
            full_bath, bedroom_abv_gr,
            overall_qual, overall_cond,
            garage_cars
        ]
        predicted_price = predict_price(model, features)

        main_image = request.files.get('image')
        image_path = save_upload_file(main_image) if main_image else None

        if not image_path:
            flash('Ảnh chính là bắt buộc', 'danger')
            return redirect(url_for('seller.seller_home'))

        conn = sqlite3.connect(current_app.config['DB_PATH'])
        cur = conn.cursor()

        sql_query = '''INSERT INTO houses (seller_username, lot_area, gr_liv_area, total_bsmt_sf, \
                                           year_built, year_remod_add, full_bath, bedroom_abv_gr, \
                                           overall_qual, overall_cond, garage_cars, \
                                           seller_price, predicted_price, image_path, description, created_at) \
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

        params = (
            session['username'], lot_area, gr_liv_area, total_bsmt_sf,
            year_built, year_remod_add, full_bath, bedroom_abv_gr,
            overall_qual, overall_cond, garage_cars,
            seller_price, predicted_price, image_path, description,
            datetime.datetime.utcnow().isoformat()
        )

        cur.execute(sql_query, params)
        house_id = cur.lastrowid

        # Xử lý ảnh phụ
        additional_images = request.files.getlist('images')
        for img in additional_images:
            img_path = save_upload_file(img)
            if img_path:
                cur.execute('INSERT INTO house_images (house_id, image_path) VALUES (?, ?)',
                            (house_id, img_path))

        conn.commit()
        conn.close()
        flash('Đăng nhà thành công!', 'success')

    except Exception as e:
        print(f"Error adding house: {e}")
        flash(f'Lỗi khi đăng nhà: {e}', 'danger')

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
            cur.execute('DELETE FROM house_images WHERE house_id=?', (house_id,))
            cur.execute('DELETE FROM houses WHERE id=?', (house_id,))
            conn.commit()
            flash('Xóa nhà thành công.', 'success')
        else:
            flash('Không thể xóa nhà này.', 'danger')

        conn.close()
    except Exception as e:
        print(f"Error deleting house: {e}")
        flash(f'Lỗi khi xóa nhà: {e}', 'danger')

    return redirect(url_for('seller.seller_home'))


@seller_bp.route('/edit/<int:house_id>', methods=['GET', 'POST'])
def seller_edit_house(house_id):
    if 'username' not in session or session.get('user_type') != 'seller':
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect(current_app.config['DB_PATH'])
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute('SELECT * FROM houses WHERE id=?', (house_id,))
    house = cur.fetchone()

    if not house or house['seller_username'] != session['username'] or house['status'] != 'available':
        conn.close()
        flash('Bạn không có quyền sửa nhà này hoặc nhà đã bán.', 'danger')
        return redirect(url_for('seller.seller_home'))

    if request.method == 'POST':
        try:
            # Lấy giá trị từ form (đơn vị m²) và chuyển sang ft² (làm tròn)
            lot_area = round(float(request.form['lot_area']) * M2_TO_FT2)
            gr_liv_area = round(float(request.form['gr_liv_area']) * M2_TO_FT2)
            total_bsmt_sf = round(float(request.form['total_bsmt_sf']) * M2_TO_FT2)

            year_built = int(request.form['year_built'])
            year_remod_add = int(request.form['year_remod_add'])
            full_bath = int(request.form['full_bath'])
            bedroom_abv_gr = int(request.form['bedroom_abv_gr'])
            overall_qual = int(request.form['overall_qual'])
            overall_cond = int(request.form['overall_cond'])
            garage_cars = int(request.form['garage_cars'])

            seller_price = float(request.form.get('seller_price'))
            description = request.form.get('description', '').strip()

            # Dự đoán lại giá
            model = load_model()
            features = [
                lot_area, gr_liv_area, total_bsmt_sf,
                year_built, year_remod_add,
                full_bath, bedroom_abv_gr,
                overall_qual, overall_cond,
                garage_cars
            ]
            predicted_price = predict_price(model, features)

            # Xử lý ảnh nếu có ảnh mới
            file = request.files.get('image')
            if file and file.filename:
                image_path = save_upload_file(file)
                cur.execute('UPDATE houses SET image_path=? WHERE id=?', (image_path, house_id))

            sql_query = '''UPDATE houses \
                           SET lot_area=?, \
                               gr_liv_area=?, \
                               total_bsmt_sf=?, \
                               year_built=?, \
                               year_remod_add=?, \
                               full_bath=?, \
                               bedroom_abv_gr=?, \
                               overall_qual=?, \
                               overall_cond=?, \
                               garage_cars=?, \
                               seller_price=?, \
                               predicted_price=?, \
                               description=?
                           WHERE id = ?'''
            params = (
                lot_area, gr_liv_area, total_bsmt_sf,
                year_built, year_remod_add, full_bath,
                bedroom_abv_gr, overall_qual, overall_cond,
                garage_cars, seller_price, predicted_price,
                description, house_id
            )

            cur.execute(sql_query, params)
            conn.commit()
            conn.close()
            flash('Cập nhật nhà thành công!', 'success')
            return redirect(url_for('seller.seller_home'))

        except Exception as e:
            print(f"Error updating house: {e}")
            conn.close()
            flash(f'Lỗi khi cập nhật: {e}', 'danger')
            return render_template('seller_edit.html', house=house, username=session['username'])

    conn.close()
    return render_template('seller_edit.html', house=house, username=session['username'])