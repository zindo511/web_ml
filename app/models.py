import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app


def get_db_connection():
    conn = sqlite3.connect(current_app.config['DB_PATH'])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    from .config import Config
    conn = sqlite3.connect(Config.DB_PATH)
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS users
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       username
                       TEXT
                       UNIQUE,
                       password
                       TEXT,
                       user_type
                       TEXT
                   )''')

    # ====================================================================
    # PHIÊN BẢN ĐÚNG CỦA BẢNG 'HOUSES' VỚI 10 ĐẶC TRƯNG
    # ====================================================================
    cur.execute('''CREATE TABLE IF NOT EXISTS houses
    (
        id
        INTEGER
        PRIMARY
        KEY
        AUTOINCREMENT,
        seller_username
        TEXT,

        -- 10 Đặc trưng của mô hình --
        lot_area
        REAL,
        year_built
        INTEGER,
        gr_liv_area
        REAL,
        full_bath
        INTEGER,
        bedroom_abv_gr
        INTEGER,
        total_bsmt_sf
        REAL,    -- MỚI
        year_remod_add
        INTEGER, -- MỚI
        overall_qual
        INTEGER, -- MỚI
        overall_cond
        INTEGER, -- MỚI
        garage_cars
        INTEGER, -- MỚI

        -- Các thông tin khác --
        seller_price
        REAL,
        predicted_price
        REAL,
        image_path
        TEXT,
        description
        TEXT,
        status
        TEXT
        DEFAULT
        'available',
        created_at
        TEXT,
        FOREIGN
        KEY
                   (
        seller_username
                   ) REFERENCES users
                   (
                       username
                   ))''')

    cur.execute('''CREATE TABLE IF NOT EXISTS house_images
    (
        id
        INTEGER
        PRIMARY
        KEY
        AUTOINCREMENT,
        house_id
        INTEGER,
        image_path
        TEXT,
        FOREIGN
        KEY
                   (
        house_id
                   ) REFERENCES houses
                   (
                       id
                   ) ON DELETE CASCADE)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS orders
    (
        id
        INTEGER
        PRIMARY
        KEY
        AUTOINCREMENT,
        house_id
        INTEGER,
        buyer_username
        TEXT,
        order_date
        TEXT,
        payment_status
        TEXT
        DEFAULT
        'pending',
        payment_method
        TEXT,
        full_name
        TEXT,
        phone
        TEXT,
        address
        TEXT,
        total_amount
        REAL,
        FOREIGN
        KEY
                   (
        house_id
                   ) REFERENCES houses
                   (
                       id
                   ),
        FOREIGN KEY
                   (
                       buyer_username
                   ) REFERENCES users
                   (
                       username
                   ))''')

    # Tạo user mẫu nếu chưa có
    cur.execute("SELECT * FROM users WHERE username='buyer1'")
    if not cur.fetchone():
        buyer_hash = generate_password_hash('buyer123')
        seller_hash = generate_password_hash('seller123')
        cur.execute("INSERT INTO users (username, password, user_type) VALUES ('buyer1', ?, 'buyer')", (buyer_hash,))
        cur.execute("INSERT INTO users (username, password, user_type) VALUES ('seller1', ?, 'seller')", (seller_hash,))

    conn.commit()
    conn.close()


def create_user(username, password, user_type):
    conn = sqlite3.connect(current_app.config['DB_PATH'])
    cur = conn.cursor()

    password_hash = generate_password_hash(password)

    try:
        cur.execute('INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)',
                    (username, password_hash, user_type))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def verify_user(username, password, user_type):
    conn = sqlite3.connect(current_app.config['DB_PATH'])
    cur = conn.cursor()

    cur.execute('SELECT * FROM users WHERE username=? AND user_type=?',
                (username, user_type))
    user = cur.fetchone()
    conn.close()

    if user and check_password_hash(user[2], password):
        return True
    return False


def user_exists(username):
    conn = sqlite3.connect(current_app.config['DB_PATH'])
    cur = conn.cursor()

    cur.execute('SELECT username FROM users WHERE username=?', (username,))
    result = cur.fetchone()
    conn.close()

    return result is not None