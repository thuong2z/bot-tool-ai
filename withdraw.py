from database import get_balance, update_balance
from config import CODE_PRICES

def read_codes():
    with open("codes.txt", "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def save_codes(codes):
    with open("codes.txt", "w") as f:
        f.write("\n".join(codes))

def withdraw_code(user_id, game):
    balance = get_balance(user_id)
    price = CODE_PRICES.get(game, 0)
    if balance < price:
        return None, "Bạn không đủ xu để đổi code."
    codes = read_codes()
    for c in codes:
        if c.startswith(game):
            update_balance(user_id, -price)
            codes.remove(c)
            save_codes(codes)
            return c, "Đổi code thành công!"
    return None, "Hết code cho game này."