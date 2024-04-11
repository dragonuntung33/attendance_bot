import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from datetime import datetime, timedelta

# Token bot Telegram Anda
TOKEN = "7183965478:AAHbF5-7jqGm0PgBFxr9FmqvQi5kyDgl6Fo"

# Batas waktu untuk setiap aktivitas dalam menit
ACTIVITY_TIME_LIMIT = {
    "ijin toilet": 20,
    "ijin merokok": 10,
    "istirahat": 60,
    "ijin market": 15,
}

# Waktu masuk kerja yang diharapkan
EXPECTED_START_TIME = datetime.strptime("09:00", "%H:%M")

# Fungsi untuk menghitung waktu keterlambatan
def calculate_late_time(actual_time):
    late_time = actual_time - EXPECTED_START_TIME
    late_minutes = late_time.total_seconds() // 60
    return int(late_minutes)

# Fungsi untuk mengirim pesan ke grup
def send_message(bot, chat_id, text, reply_markup=None):
    bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

# Fungsi untuk menghitung durasi waktu
def calculate_duration(start_time):
    end_time = datetime.now()
    duration = end_time - start_time
    return int(duration.total_seconds() // 60)

# Fungsi untuk mengatur pesan balasan berdasarkan waktu keterlambatan
def set_response_message(late_minutes):
    if late_minutes <= 0:
        return "OK 🟢"
    elif late_minutes <= 10:
        return f"Peringatan 🟡\nKeterlambatan: {late_minutes} menit"
    else:
        return f"Terlambat dengan denda 1000 🔴"

# Fungsi untuk menangani tombol yang ditekan
def button_click(update, context):
    query = update.callback_query
    data = query.data

    # Ambil informasi tombol yang ditekan
    activity, action = data.split("_")
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    user_id = query.from_user.id

    # Cek apakah user sudah menekan tombol masuk sebelumnya
    if user_id not in context.user_data:
        send_message(context.bot, chat_id, "Anda harus menekan tombol Masuk Kerja terlebih dahulu.")
        return

    # Cek apakah user sedang dalam aktivitas lain
    if "activity" in context.user_data[user_id]:
        send_message(context.bot, chat_id, "Anda sedang dalam aktivitas lain. Harap selesaikan aktivitas tersebut terlebih dahulu.")
        return

    # Memulai aktivitas
    if action == "start":
        context.user_data[user_id]["activity"] = activity
        context.user_data[user_id]["start_time"] = datetime.now()
        send_message(context.bot, chat_id, f"Anda telah memulai aktivitas {activity}.")
    # Mengakhiri aktivitas
    elif action == "back":
        start_time = context.user_data[user_id]["start_time"]
        duration = calculate_duration(start_time)
        response_message = f"Anda telah menyelesaikan aktivitas {activity} dengan durasi {duration} menit."
        
        # Check keterlambatan untuk aktivitas Masuk Kerja
        if activity == "masuk_kerja":
            late_minutes = calculate_late_time(start_time)
            response_message += "\n" + set_response_message(late_minutes)

        send_message(context.bot, chat_id, response_message)

        # Reset data aktivitas
        del context.user_data[user_id]["activity"]
        del context.user_data[user_id]["start_time"]

# Fungsi untuk memeriksa apakah sudah saatnya untuk mereset data kehadiran
def check_reset(context):
    now = datetime.now()
    if now.hour == 0 and now.minute == 0:
        context.user_data.clear()

def main():
    updater = Updater(token=7183965478:AAHbF5-7jqGm0PgBFxr9FmqvQi5kyDgl6Fo, use_context=True)
    dispatcher = updater.dispatcher

    # Menambahkan handler untuk tombol
    buttons = [
        InlineKeyboardButton("Masuk Kerja", callback_data="masuk_kerja_start"),
        InlineKeyboardButton("Ijin Toilet", callback_data="ijin_toilet_start"),
        InlineKeyboardButton("Ijin Rokok", callback_data="ijin_rokok_start"),
        InlineKeyboardButton("Ijin Market", callback_data="ijin_market_start"),
        InlineKeyboardButton("Istirahat", callback_data="istirahat_start"),
        InlineKeyboardButton("Pulang", callback_data="pulang_start"),
        InlineKeyboardButton("Back", callback_data="back")
    ]
    keyboard = [buttons[:3], buttons[3:6], [buttons[6]]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    dispatcher.add_handler(CallbackQueryHandler(button_click))

    # Menambahkan handler untuk periksa reset
    dispatcher.job_queue.run_repeating(check_reset, interval=60, first=0)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()