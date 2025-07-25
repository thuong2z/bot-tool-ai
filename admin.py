from database import total_users
from withdraw import read_codes, save_codes

def admin_stats():
    return f"👥 Tổng user: {total_users()}\n📦 Code còn lại: {len(read_codes())}"

def add_code(new_codes):
    codes = read_codes()
    codes.extend(new_codes)
    save_codes(codes)
    return f"✅ Đã thêm {len(new_codes)} code mới.\nTổng hiện có: {len(codes)}"