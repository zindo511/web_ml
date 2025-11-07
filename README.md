# Website Bất Động Sản với Machine Learning

## Tính năng

- **Xác thực người dùng**: Đăng ký, đăng nhập với mật khẩu được mã hóa
- **Người mua**: Xem danh sách nhà, xem chi tiết nhà với nhiều ảnh, thanh toán, xem lịch sử đơn hàng
- **Người bán**: Thêm/sửa/xóa nhà, upload nhiều ảnh, xem danh sách nhà đang bán
- **Machine Learning**: Dự đoán giá nhà tự động bằng mô hình Random Forest
- **Thanh toán**: Hỗ trợ nhiều phương thức thanh toán, lưu thông tin đơn hàng đầy đủ

## Cài đặt

1. **Tạo môi trường ảo**:
```bash
python -m venv .venv
.venv\Scripts\activate
```

2. **Cài đặt thư viện**:
```bash
python -m pip install -r requirements.txt
```

3. **Chạy ứng dụng**:
```bash
python run.py
```

4. **Truy cập**: http://localhost:5000

**Tài khoản demo**:
- Người mua: `buyer1` / `buyer123`
- Người bán: `seller1` / `seller123`
