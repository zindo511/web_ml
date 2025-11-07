from flask import Blueprint, render_template, request, session, redirect, url_for
from app.models import create_user, verify_user, user_exists

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    if 'username' in session:
        if session.get('user_type') == 'buyer':
            return redirect(url_for('buyer.buyer_home'))
        elif session.get('user_type') == 'seller':
            return redirect(url_for('seller.seller_home'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    success = None
    
    if request.args.get('success') == 'registered':
        success = 'Đăng ký thành công! Vui lòng đăng nhập.'
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user_type = request.form.get('user_type')
        
        if verify_user(username, password, user_type):
            session['username'] = username
            session['user_type'] = user_type
            if user_type == 'buyer':
                return redirect(url_for('buyer.buyer_home'))
            else:
                return redirect(url_for('seller.seller_home'))
        else:
            error = 'Tên đăng nhập, mật khẩu hoặc loại tài khoản không đúng!'
    
    return render_template('login.html', error=error, success=success)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user_type = request.form.get('user_type', '').strip()
        
        if len(username) < 3:
            error = 'Tên đăng nhập phải có ít nhất 3 ký tự!'
        elif len(password) < 6:
            error = 'Mật khẩu phải có ít nhất 6 ký tự!'
        elif user_type not in ['buyer', 'seller']:
            error = 'Loại tài khoản không hợp lệ!'
        elif user_exists(username):
            error = 'Tên đăng nhập đã tồn tại. Vui lòng chọn tên khác!'
        else:
            if create_user(username, password, user_type):
                return redirect(url_for('auth.login', success='registered'))
            else:
                error = 'Đã xảy ra lỗi khi tạo tài khoản. Vui lòng thử lại!'
    
    return render_template('signup.html', error=error)

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
