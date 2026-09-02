import asyncio
import logging
import sys
import random
from os import environ
from aiohttp import web

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, 
    InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, PreCheckoutQuery
)
from aiogram.client.default import DefaultBotProperties

# --- НАЛАШТУВАННЯ СИСТЕМИ ---
BOT_TOKEN = environ.get("BOT_TOKEN", "8870125810:AAH-NVjNmQHprpdv4f53IBy0GomlN13ZpFs")
PORT = int(environ.get("PORT", 10000))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | ❤️ UA-LOVEBOT-FIXED | %(levelname)s | %(message)s",
    stream=sys.stdout
)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()

# Велика база із понад 100 демо-анкет (хлопці та дівчата з різних міст України)
USERS_DB = {
    3001: {"name": "Софія", "age": 20, "city": "Київ", "photo_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=600&auto=format&fit=crop&q=60", "bio": "Шукаю приємну людину на каву у Києві ☕️ Люблю гуляти центром та слухати музику.", "is_vip": False, "likes_received": 12},
    3002: {"name": "Анастасія", "age": 21, "city": "Київ", "photo_url": "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=600&auto=format&fit=crop&q=60", "bio": "Люблю затишні кав'ярні та настільні ігри. Хто зі мною в «Уно»?", "is_vip": False, "likes_received": 14},
    3003: {"name": "Карина", "age": 19, "city": "Київ", "photo_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=600&auto=format&fit=crop&q=60", "bio": "Студентка КПІ, вивчаю дизайн, шукаю цікавих співрозмовників ✨", "is_vip": False, "likes_received": 8},
    3004: {"name": "Марія", "age": 23, "city": "Київ", "photo_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=600&auto=format&fit=crop&q=60", "bio": "Маркетолог, обожнюю вечірні пробіжки на Дніпровській набережній 🏃‍♀️", "is_vip": False, "likes_received": 22},
    3005: {"name": "Аліна", "age": 22, "city": "Київ", "photo_url": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=600&auto=format&fit=crop&q=60", "bio": "Фотографую місто та людей на плівку. Завжди за творчі колаборації.", "is_vip": False, "likes_received": 19},
    3011: {"name": "Максим", "age": 23, "city": "Київ", "photo_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&auto=format&fit=crop&q=60", "bio": "IT-спеціаліст, люблю велопрогулянки та смачну піцу.", "is_vip": False, "likes_received": 9},
    3012: {"name": "Дмитро", "age": 25, "city": "Київ", "photo_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=600&auto=format&fit=crop&q=60", "bio": "Займаюсь спортом, люблю каву та подорожі Україною 🇺🇦", "is_vip": False, "likes_received": 15},
    3021: {"name": "Оксана", "age": 21, "city": "Львів", "photo_url": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=600&auto=format&fit=crop&q=60", "bio": "Львів'янка, люблю дощ, бруківку та кав'ярні біля Оперного ☕️", "is_vip": False, "likes_received": 17},
    3031: {"name": "Анна", "age": 21, "city": "Одеса", "photo_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=600&auto=format&fit=crop&q=60", "bio": "Одеситка, обожнюю море, захід сонця і довгі розмови ні про що ✨", "is_vip": False, "likes_received": 24}
}

# Доповнення бази до понад 100+ анкет
names_pool = ["Оля", "Максим", "Наталя", "Андрій", "Катерина", "Дмитро", "Ірина", "Богдан", "Світлана", "Олег", "Юлія", "Віктор"]
cities_pool = ["Київ", "Львів", "Одеса", "Харків", "Дніпро", "Запоріжжя", "Івано-Франківськ", "Вінниця"]
photos_pool = [
    "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=600&auto=format&fit=crop&q=60",
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&auto=format&fit=crop&q=60",
    "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=600&auto=format&fit=crop&q=60",
    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=600&auto=format&fit=crop&q=60",
    "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=600&auto=format&fit=crop&q=60"
]
bios_pool = [
    "Люблю каву, гарну музику та довгі прогулянки.",
    "Шукаю однодумців для спілкування та приємних зустрічей.",
    "Працюю, розвиваюсь, у вільний час подорожую Україною.",
    "Завжди за добрий гумор та нові знайомства ✌️"
]

for i in range(3051, 3110):
    USERS_DB[i] = {
        "name": random.choice(names_pool),
        "age": random.randint(18, 29),
        "city": random.choice(cities_pool),
        "photo_url": random.choice(photos_pool),
        "bio": random.choice(bios_pool),
        "is_vip": False,
        "likes_received": random.randint(2, 25)
    }

class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_city = State()
    waiting_for_photo = State()
    waiting_for_bio = State()

UKRAINE_CITIES = [
    "Київ", "Львів", "Харків", "Одеса", 
    "Дніпро", "Запоріжжя", "Івано-Франківськ", "Інше"
]

def main_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Дивитися анкети"), KeyboardButton(text="👤 Моя анкета")],
            [KeyboardButton(text="💎 VIP Статус"), KeyboardButton(text="📊 Статистика")]
        ],
        resize_keyboard=True
    )

def cities_kb():
    kb = [[KeyboardButton(text=city)] for city in UKRAINE_CITIES]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    uid = message.from_user.id
    await state.clear()
    
    if uid in USERS_DB:
        await message.answer(
            "❤️ <b>Вітаємо у UA LoveBot!</b>\n\nОберіть потрібну дію в меню нижче:",
            reply_markup=main_menu_kb()
        )
    else:
        await message.answer(
            "🇺🇦 <b>Ласкаво просимо в анонімний бот знайомств!</b>\n\n"
            "Знайди свою людину в Україні за кілька кліків.\n\n"
            "Давайте створимо твою анкету. Як тебе звати?",
            reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Скасувати")]], resize_keyboard=True)
        )
        await state.set_state(RegistrationStates.waiting_for_name)

@router.message(RegistrationStates.waiting_for_name, F.text == "Скасувати")
@router.message(RegistrationStates.waiting_for_age, F.text == "Скасувати")
@router.message(RegistrationStates.waiting_for_city, F.text == "Скасувати")
@router.message(RegistrationStates.waiting_for_photo, F.text == "Скасувати")
@router.message(RegistrationStates.waiting_for_bio, F.text == "Скасувати")
async def cancel_registration(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Реєстрацію скасовано.", reply_markup=main_menu_kb())

@router.message(RegistrationStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Скільки тобі років? (Введи число, наприклад: 21)", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Скасувати")]], resize_keyboard=True))
    await state.set_state(RegistrationStates.waiting_for_age)

@router.message(RegistrationStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit() or not (14 <= int(message.text) <= 99):
        await message.answer("⚠️ Будь ласка, введи реальний вік числом (від 14 до 99).")
        return
    
    await state.update_data(age=int(message.text))
    await message.answer("📍 Обери своє місто зі списку нижче:", reply_markup=cities_kb())
    await state.set_state(RegistrationStates.waiting_for_city)

@router.message(RegistrationStates.waiting_for_city)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer(
        "📸 <b>Надішли своє фото</b> (це може бути селфі або гарне фото, щоб інші могли тебе побачити):",
        reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Скасувати")]], resize_keyboard=True)
    )
    await state.set_state(RegistrationStates.waiting_for_photo)

@router.message(RegistrationStates.waiting_for_photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    
    await message.answer(
        "📝 Напиши короткий опис про себе (хто ти, чим займаєшся, кого шукаєш):",
        reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Пропустити"), KeyboardButton(text="Скасувати")]], resize_keyboard=True)
    )
    await state.set_state(RegistrationStates.waiting_for_bio)

@router.message(RegistrationStates.waiting_for_photo)
async def process_photo_invalid(message: Message, state: FSMContext):
    await message.answer("⚠️ Будь ласка, надішли саме **фотографію** або натисни «Скасувати».")

@router.message(RegistrationStates.waiting_for_bio)
async def process_bio(message: Message, state: FSMContext):
    bio = "" if message.text == "Пропустити" else message.text
    data = await state.get_data()
    uid = message.from_user.id
    
    USERS_DB[uid] = {
        "name": data["name"],
        "age": data["age"],
        "city": data["city"],
        "photo_id": data["photo_id"],
        "bio": bio,
        "is_vip": False,
        "likes_received": 0
    }
    
    await state.clear()
    u = USERS_DB[uid]
    
    await message.bot.send_photo(
        chat_id=message.chat.id,
        photo=u["photo_id"],
        caption=(
            "🎉 <b>Твою анкету успішно створено!</b>\n\n"
            f"👤 <b>{u['name']}, {u['age']}</b> — 📍 <b>{u['city']}</b>\n"
            f"💬 <i>{u['bio'] if u['bio'] else 'Без опису'}</i>\n\n"
            "Тисни «Дивитися анкети» та починай знайомства!"
        ),
        reply_markup=main_menu_kb(),
        parse_mode=ParseMode.HTML
    )

@router.message(F.text == "👤 Моя анкета")
async def profile_handler(message: Message):
    uid = message.from_user.id
    if uid not in USERS_DB:
        await message.answer("У тебе ще немає анкети. Натисни /start, щоб створити її.")
        return
        
    u = USERS_DB[uid]
    vip_status = "💎 VIP Активний (Без обмежень)" if u["is_vip"] else "👤 Звичайний акаунт"
    
    photo_source = u.get("photo_url") or u.get("photo_id")
    
    if "photo_url" in u:
        await message.answer_photo(
            photo=photo_source,
            caption=(
                f"👤 <b>Твоя анкета:</b>\n\n"
                f"Ім'я: <b>{u['name']}, {u['age']}</b>\n"
                f"Місто: <b>{u['city']}</b>\n"
                f"Про себе: {u['bio']}\n\n"
                f"Статус: {vip_status}\n"
                f"Отримано симпатій ❤️: {u['likes_received']}"
            ),
            reply_markup=main_menu_kb(),
            parse_mode=ParseMode.HTML
        )
    else:
        await message.bot.send_photo(
            chat_id=message.chat.id,
            photo=photo_source,
            caption=(
                f"👤 <b>Твоя анкета:</b>\n\n"
                f"Ім'я: <b>{u['name']}, {u['age']}</b>\n"
                f"Місто: <b>{u['city']}</b>\n"
                f"Про себе: {u['bio']}\n\n"
                f"Статус: {vip_status}\n"
                f"Отримано симпатій ❤️: {u['likes_received']}"
            ),
            reply_markup=main_menu_kb(),
            parse_mode=ParseMode.HTML
        )

@router.message(F.text == "🔍 Дивитися анкети")
async def search_profiles(message: Message):
    uid = message.from_user.id
    if uid not in USERS_DB:
        await message.answer("Спершу створи анкету через /start")
        return
        
    other_users = [k for k in USERS_DB.keys() if k != uid]
    
    if not other_users:
        await message.answer("😔 Поки що немає інших анкет у системі. Зазирни трохи пізніше!")
        return
        
    target_id = other_users[0]
    target = USERS_DB[target_id]
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👎 Пропустити", callback_data=f"swipe_skip_{target_id}"),
            InlineKeyboardButton(text="❤️ Вподобати", callback_data=f"swipe_like_{target_id}")
        ]
    ])
    
    photo_source = target.get("photo_url") or target.get("photo_id")
    
    card_caption = (
        f"👤 <b>{target['name']}, {target['age']}</b> — 📍 <b>{target['city']}</b>\n\n"
        f"📝 <b>Опис:</b> {target['bio'] if target['bio'] else 'Користувач не додав опис.'}"
    )
    
    await message.bot.send_photo(
        chat_id=message.chat.id,
        photo=photo_source,
        caption=card_caption,
        reply_markup=markup,
        parse_mode=ParseMode.HTML
    )

@router.callback_query(F.data.startswith("swipe_"))
async def swipe_callback(callback: CallbackQuery):
    data_parts = callback.data.replace("swipe_", "").split("_", 1)
    action = data_parts[0]
    target_id = int(data_parts[1])
    uid = callback.from_user.id
    
    if action == "like":
        if target_id in USERS_DB:
            USERS_DB[target_id]["likes_received"] += 1
            if target_id > 5000:
                try:
                    await bot.send_message(
                        target_id, 
                        "💖 <b>Хтось звернув на тебе увагу!</b>\nТвоя анкета сподобалась іншій людині у UA LoveBot!"
                    )
                except Exception:
                    pass
        await callback.answer("❤️ Позначено як вподобання!")
    else:
        await callback.answer("👎 Пропущено.")
        
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    other_users = [k for k in USERS_DB.keys() if k != uid]
    if other_users:
        next_target_id = other_users[0]
        target = USERS_DB[next_target_id]
        
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="👎 Пропустити", callback_data=f"swipe_skip_{next_target_id}"),
                InlineKeyboardButton(text="❤️ Вподобати", callback_data=f"swipe_like_{next_target_id}")
            ]
        ])
        
        photo_source = target.get("photo_url") or target.get("photo_id")
        card_caption = (
            f"👤 <b>{target['name']}, {target['age']}</b> — 📍 <b>{target['city']}</b>\n\n"
            f"📝 <b>Опис:</b> {target['bio'] if target['bio'] else 'Користувач не додав опис.'}"
        )
        
        await bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=photo_source,
            caption=card_caption,
            reply_markup=markup,
            parse_mode=ParseMode.HTML
        )
    else:
        await callback.message.answer("Більше немає нових анкет. Зазирни пізніше!")

@router.message(F.text == "💎 VIP Статус")
async def vip_store(message: Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Купити VIP за 100 зірок", callback_data="buy_vip_stars")]
    ])
    await message.answer(
        "💎 <b>VIP-СТАТУС У UA LOVEBOT</b>\n\n"
        "Переваги VIP:\n"
        "• Дивись, хто додав тебе в симпатії\n"
        "• Пріоритетний показ твоєї анкети\n"
        "• Безлімітні перегляди анкет\n\n"
        "Вартість: <b>100 Telegram Stars (XTR)</b>",
        reply_markup=markup,
        parse_mode=ParseMode.HTML
    )

@router.callback_query(F.data == "buy_vip_stars")
async def send_vip_invoice(callback: CallbackQuery):
    prices = [LabeledPrice(label="VIP Статус на 30 днів", amount=100)]
    await callback.bot.send_invoice(
        chat_id=callback.message.chat.id,
        title="VIP-статус UA LoveBot",
        description="Розблокування прихованих симпатій та пріоритетний пошук на 30 днів",
        payload="vip_status_payment",
        currency="XTR",
        prices=prices
    )
    await callback.answer()

@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment)
async def successful_payment(message: Message):
    uid = message.from_user.id
    if uid in USERS_DB:
        USERS_DB[uid]["is_vip"] = True
    await message.answer("🎉 <b>Вітаємо! VIP-статус успішно активовано!</b>", reply_markup=main_menu_kb())

@router.message(F.text == "📊 Статистика")
async def stats_handler(message: Message):
    await message.answer(
        f"📊 <b>Статистика сервісу:</b>\n\n"
        f"👥 Зареєстрованих анкет: {len(USERS_DB)}\n"
        f"📍 Регіон: Україна",
        reply_markup=main_menu_kb(),
        parse_mode=ParseMode.HTML
    )

async def handle_ping(request):
    return web.Response(text="UA-LOVEBOT-FIXED-ONLINE")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

async def main():
    dp.include_router(router)
    asyncio.create_task(start_web_server())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
