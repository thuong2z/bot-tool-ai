import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import TOKEN, ADMIN_ID, REF_REWARD, CODE_PRICES, REQUIRED_CHANNELS
from database import init_db, add_user, update_balance, get_balance
from tasks import daily_checkin
from withdraw import withdraw_code
from admin import admin_stats, add_code

bot = telebot.TeleBot(TOKEN)
init_db()

# ==============================
# MENU CHÍNH
# ==============================
def main_menu():
    menu = ReplyKeyboardMarkup(resize_keyboard=True)
    menu.add(KeyboardButton("💰 Tài khoản"), KeyboardButton("♻️ Mời bạn"))
    menu.add(KeyboardButton("🔑 Rút Code"), KeyboardButton("📖 ĐIỂM DANH"))
    menu.add(KeyboardButton("🏆 Bảng xếp hạng"), KeyboardButton("📊 Thống Kê User"))
    return menu

# ==============================
# KIỂM TRA THAM GIA KÊNH
# ==============================
def check_join(user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# ==============================
# START
# ==============================
@bot.message_handler(commands=['start'])
def start_cmd(msg):
    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.first_name

    # Nếu chưa tham gia kênh => Bắt buộc join
    if not check_join(user_id):
        markup = InlineKeyboardMarkup()
        for channel in REQUIRED_CHANNELS:
            markup.add(InlineKeyboardButton(f"✅ Tham gia {channel}", url=f"https://t.me/{channel.replace('@','')}"))
        markup.add(InlineKeyboardButton("🔄 Tôi đã tham gia", callback_data="check_join"))
        bot.send_message(user_id,
                         "🚨 *Bạn phải tham gia đủ các kênh bên dưới trước khi sử dụng bot!*",
                         parse_mode="Markdown",
                         reply_markup=markup)
        return

    # Lưu user vào DB
    add_user(user_id, username)

    # Check nếu có ref
    if " " in msg.text:
        ref_id = msg.text.split(" ")[1]
        if ref_id.isdigit() and int(ref_id) != user_id:
            update_balance(int(ref_id), REF_REWARD)
            bot.send_message(int(ref_id),
                             f"🎉 *Bạn vừa nhận {REF_REWARD} xu từ lời mời thành công!*",
                             parse_mode="Markdown")

    bot.send_message(user_id,
                     f"👋 *Chào {username}!*\n"
                     f"🎯 Chào mừng bạn đến với *Bot Rút Code*.\n\n"
                     f"✅ Hoàn thành nhiệm vụ, điểm danh, mời bạn bè để tích xu.\n"
                     f"🎁 Đổi xu lấy *Code Game* ngay!",
                     parse_mode="Markdown",
                     reply_markup=main_menu())

# ==============================
# XỬ LÝ NÚT CHÍNH
# ==============================
@bot.message_handler(func=lambda m: True)
def main_handler(msg):
    user_id = msg.from_user.id
    text = msg.text

    if text == "💰 Tài khoản":
        balance = get_balance(user_id)
        bot.send_message(user_id,
                         f"💳 *TÀI KHOẢN CỦA BẠN*\n"
                         f"━━━━━━━━━━━━━━\n"
                         f"💰 Số dư: *{balance} xu*\n"
                         f"🔗 Link ref: `https://t.me/{bot.get_me().username}?start={user_id}`\n"
                         f"━━━━━━━━━━━━━━",
                         parse_mode="Markdown")

    elif text == "♻️ Mời bạn":
        bot.send_message(user_id,
                         f"🔗 *Link mời bạn bè của bạn:*\n"
                         f"`https://t.me/{bot.get_me().username}?start={user_id}`\n\n"
                         f"👉 Nhận *{REF_REWARD} xu* mỗi khi bạn bè hoàn thành nhiệm vụ.",
                         parse_mode="Markdown")

    elif text == "📖 ĐIỂM DANH":
        if daily_checkin(user_id):
            bot.send_message(user_id,
                             f"✅ *Điểm danh thành công!*\n"
                             f"Bạn nhận được *{REF_REWARD} xu*.",
                             parse_mode="Markdown")
        else:
            bot.send_message(user_id,
                             "❌ *Hôm nay bạn đã điểm danh rồi.*\nQuay lại vào ngày mai nhé!",
                             parse_mode="Markdown")

    elif text == "🔑 Rút Code":
        show_code_menu(user_id)

    elif text == "📊 Thống Kê User" and user_id == ADMIN_ID:
        bot.send_message(user_id, admin_stats())

    elif text == "🏆 Bảng xếp hạng":
        bot.send_message(user_id, "⏳ *Tính năng đang phát triển...*", parse_mode="Markdown")

    else:
        bot.send_message(user_id, "❌ *Chức năng chưa hỗ trợ hoặc bạn không phải Admin.*", parse_mode="Markdown")

# ==============================
# MENU RÚT CODE
# ==============================
def show_code_menu(user_id):
    markup = InlineKeyboardMarkup()
    for game, price in CODE_PRICES.items():
        markup.add(InlineKeyboardButton(f"{game} – {price} xu", callback_data=f"code:{game}"))
    bot.send_message(user_id, "🎁 *Chọn loại code bạn muốn đổi:*", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("code:"))
def process_code(call):
    user_id = call.from_user.id
    game = call.data.split("code:")[1]
    code, msg = withdraw_code(user_id, game)
    if code:
        bot.send_message(user_id, f"✅ *{msg}*\n🎁 *Code của bạn:* `{code}`", parse_mode="Markdown")
    else:
        bot.send_message(user_id, f"❌ *{msg}*", parse_mode="Markdown")

# ==============================
# XỬ LÝ NÚT "🔄 Tôi đã tham gia"
# ==============================
@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def recheck_join(call):
    user_id = call.from_user.id
    if check_join(user_id):
        bot.send_message(user_id,
                         "✅ *Xác minh thành công!*\nBạn đã tham gia đầy đủ kênh.",
                         parse_mode="Markdown",
                         reply_markup=main_menu())
    else:
        bot.answer_callback_query(call.id, "❌ Bạn vẫn chưa tham gia đủ kênh!")

# ==============================
# ADMIN THÊM CODE
# ==============================
@bot.message_handler(commands=['addcode'])
def admin_add_code(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    try:
        new_codes = msg.text.split("\n")[1:]  # Các code nằm từ dòng thứ 2
        res = add_code(new_codes)
        bot.send_message(ADMIN_ID, res)
    except:
        bot.send_message(ADMIN_ID, "❌ Sai định dạng. Ví dụ:\n/addcode\nGame A:ABCD-1234\nGame B:XYZ-5555")

# ==============================
# CHẠY BOT
# ==============================
print("🤖 Bot đang chạy...")
bot.polling(none_stop=True)
