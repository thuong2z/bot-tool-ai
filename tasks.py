from datetime import date
from database import get_checkin, set_checkin, update_balance
from config import DAILY_REWARD

def daily_checkin(user_id):
    today = str(date.today())
    last = get_checkin(user_id)
    if last != today:
        update_balance(user_id, DAILY_REWARD)
        set_checkin(user_id, today)
        return True
    return False