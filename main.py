# main.py
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from config import BOT_TOKEN, ADMIN_IDS, DATABASE_PATH, REFERRAL_ENABLED
from database import init_db, add_user, get_user, log_action, get_stats, toggle_referrals

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

init_db()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    user = get_user(user_id)
    if user:
        await message.reply(f"🎯 Welcome back, {first_name}!")
    else:
        referral_code = message.get_args()
        if referral_code and referral_code.startswith('ref_'):
            inviter_id = int(referral_code.split('_')[1])
            inviter = get_user(inviter_id)
            if inviter:
                inviter_referral_count = inviter[4] + 1
                conn = sqlite3.connect(DATABASE_PATH)
                c = conn.cursor()
                c.execute("UPDATE users SET referral_count = ? WHERE user_id = ?", (inviter_referral_count, inviter_id))
                conn.commit()
                conn.close()
                await bot.send_message(inviter_id, f"🎉 You invited {first_name}! Your referral count: {inviter_referral_count}.")
        add_user(user_id, first_name, message.from_user.last_name, referral_code)
        await message.reply(f"👋 Welcome {first_name}! Thanks for joining Tajammal Tools.")
    await show_main_menu(message)

@dp.message_handler(commands=['broadcast'])
async def broadcast(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    text = message.text[len('/broadcast '):]
    users = get_all_users()
    for user in users:
        await bot.send_message(user[0], text)

@dp.message_handler(commands=['stats'])
async def show_stats(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    total_users, active_users, referral_count = get_stats()
    await message.reply(f"Total Users: {total_users}\nActive Users: {active_users}\nReferral Count: {referral_count}")

@dp.message_handler(commands=['refer'])
async def toggle_referrals_command(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    state = message.text.split()[1].lower()
    if state == 'on':
        toggle_referrals(True)
        await message.reply("Referral system has been enabled.")
    elif state == 'off':
        toggle_referrals(False)
        await message.reply("Referral system has been disabled.")

@dp.message_handler(commands=['users'])
async def export_users(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    users = get_all_users()
    user_list = "\n".join([f"{user[0]}: {user[1]} {user[2]}" for user in users])
    await message.reply(user_list)

async def show_main_menu(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(InlineKeyboardButton("📸 Front Camera", callback_data="front_camera"))
    keyboard.add(InlineKeyboardButton("📸 Back Camera", callback_data="back_camera"))
    keyboard.add(InlineKeyboardButton("🎙 Voice", callback_data="voice"))
    keyboard.add(InlineKeyboardButton("📍 Location", callback_data="location"))
    keyboard.add(InlineKeyboardButton("🎥 Front Video", callback_data="front_video"))
    keyboard.add(InlineKeyboardButton("🎥 Back Video", callback_data="back_video"))
    keyboard.add(InlineKeyboardButton("🔗 URL Shortener", callback_data="url_shortener"))
    await message.reply("Choose an option:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data in ["front_camera", "back_camera", "voice", "location", "front_video", "back_video", "url_shortener"])
async def handle_action(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    action = callback_query.data
    log_action(user_id, action)
    if action == "front_camera":
        await callback_query.message.reply("Front Camera Action")
    elif action == "back_camera":
        await callback_query.message.reply("Back Camera Action")
    elif action == "voice":
        await callback_query.message.reply("Voice Action")
    elif action == "location":
        await callback_query.message.reply("Location Action")
    elif action == "front_video":
        await callback_query.message.reply("Front Video Action")
    elif action == "back_video":
        await callback_query.message.reply("Back Video Action")
    elif action == "url_shortener":
        await callback_query.message.reply("URL Shortener Action")
    await show_main_menu(callback_query.message)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)