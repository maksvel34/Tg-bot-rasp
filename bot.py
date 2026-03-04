import asyncio
import json
import os
import random
from datetime import datetime, time, timedelta, date

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiohttp import web

# ======================
# ⚙ НАСТРОЙКИ
# ======================

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

ADMIN_ID = [1071264428, 7237228038]
EVEN_WEEK_START = date(2026, 2, 9)

# ======================
# 💾 ПОДПИСЧИКИ
# ======================

SUBSCRIBERS_FILE = "subscribers.json"

def load_subscribers():
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_subscribers():
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(list(subscribers), f)

subscribers = load_subscribers()
notified_today = set()

# ======================
# 📚 РАСПИСАНИЕ (оставь своё)
# ======================

schedule = {
        "even": {
            "Monday": [
                {"start": time(9, 50), "end": time(11, 20), "name": "ЛК Высшая математика", "room": "309А",
                 "teacher": "доц. Вронский Б.М."},
                {"start": time(11, 30), "end": time(13, 00), "name": "ЛК История России", "room": "211А",
                 "teacher": "доц. Манаев А.Ю."},
                {"start": time(13, 20), "end": time(14, 50), "name": "ПЗ Математическая логика и теория алгоритмов",
                 "room": "306В", "teacher": "ст.пр. Степанова Е.И."},
                {"start": time(15, 00), "end": time(16, 30), "name": "ЛК Человек и право",
                 "room": "309А", "teacher": "Шевченко В.И."},
            ],
            "Tuesday": [
                {"start": time(9, 50), "end": time(11, 20), "name": "ЛК Цифровые технологии в профессиональной сфере", "room": "309А",
                 "teacher": "доц. Филиппов Д.М."},
                {"start": time(11, 30), "end": time(13, 00), "name": "ПЗ Цифровые технологии в профессиональной сфере", "room": "8А",
                 "teacher": "доц. Филиппов Д.М."},
                {"start": time(13, 20), "end": time(14, 50), "name": "ПЗ Физическая культура",
                 "room": "спортзал ТА", "teacher": "Ковальчук Елена Сергеевна"},
                {"start": time(15, 00), "end": time(16, 30), "name": "ПЗ История России",
                 "room": "201В", "teacher": "Маргасов В.С."},
            ],
            "Wednesday": [
                {"start": time(9, 50), "end": time(11, 20), "name": "1 подгруппа - нет пары | 2 подгруппа - ПЗ Теория и технологии программирования на языках высокого уровня", "room": "119А",
                 "teacher": "Енина А.А."},
                {"start": time(11, 30), "end": time(13, 00), "name": "ЛК Теория и технологии программирования на языках высокого уровня", "room": "18А",
                 "teacher": "Степанов А.В"},
                {"start": time(13, 20), "end": time(14, 50), "name": "ПЗ Иностранный язык",
                 "room": "531Б", "teacher": "Ермоленко О.В."},
            ],
            "Thursday": [
                {"start": time(8, 00), "end": time(9, 30), "name": "ПЗ Высшая математика", "room": "302В",
                 "teacher": "доц. Вронский Б.М."},
                {"start": time(9, 50), "end": time(11, 20), "name": "ПЗ Основы российской государственности", "room": "411В",
                 "teacher": "Валуев Д.Г."},
                {"start": time(11, 30), "end": time(13, 00), "name": "ЛК Экономическая культура и финансовая грамотность",
                 "room": "411В", "teacher": "Друзин Р.В."},
                {"start": time(13, 20), "end": time(14, 50), "name": "ПЗ Экономическая культура и финансовая грамотность",
                 "room": "411В", "teacher": "Друзин Р.В."},
            ],
            "Friday": [
                {"start": time(8, 00), "end": time(9, 30),
                 "name": "1 подгруппа - ПЗ Теория и технологии программирования на языках высокого уровня | 2 подгруппа - нет пары", "room": "119А",
                 "teacher": "Енина А.А."},
                {"start": time(9, 50), "end": time(11, 20),
                 "name": "ЛК Математическая логика и теория алгоритмов", "room": "302В",
                 "teacher": "Степанова Е.И."},
                {"start": time(11, 30), "end": time(13, 00), "name": "ЛК Метрология, стандартизация и сертификация",
                 "room": "301В", "teacher": "куратор группы Дементьев М.Ю."},
                {"start": time(13, 20), "end": time(14, 50), "name": "ПЗ Метрология, стандартизация и сертификация",
                 "room": "301В", "teacher": "куратор группы Дементьев М.Ю."},
            ],
        },
        "odd": {
            "Monday": [
                {"start": time(9, 50), "end": time(11, 20), "name": "ЛК Высшая математика", "room": "309А",
                 "teacher": "доц. Вронский Б.М."},
                {"start": time(11, 30), "end": time(13, 00), "name": "ЛК История России", "room": "211А",
                 "teacher": "доц. Манаев А.Ю."},
                {"start": time(13, 20), "end": time(14, 50), "name": "ПЗ Математическая логика и теория алгоритмов",
                 "room": "306В", "teacher": "ст.пр. Степанова Е.И."},
            ],
            "Tuesday": [
                {"start": time(9, 50), "end": time(11, 20), "name": "ЛК Цифровые технологии в профессиональной сфере", "room": "309А",
                 "teacher": "доц. Филиппов Д.М."},
                {"start": time(11, 30), "end": time(13, 00), "name": "ПЗ Цифровые технологии в профессиональной сфере", "room": "8А",
                 "teacher": "доц. Филиппов Д.М."},
                {"start": time(13, 20), "end": time(14, 50), "name": "ПЗ Физическая культура",
                 "room": "спортзал ТА", "teacher": "Ковальчук Елена Сергеевна"},
                {"start": time(15, 00), "end": time(16, 30), "name": "ПЗ История России",
                 "room": "201В", "teacher": "Маргасов В.С."},
            ],
            "Wednesday": [
                {"start": time(8, 00), "end": time(9, 30), "name": "1 подгруппа - нет пары | 2 подгруппа - ПЗ Теория и технологии программирования на языках высокого уровня", "room": "119А",
                 "teacher": "Енина А.А."},
                {"start": time(9, 50), "end": time(11, 20), "name": "ЛК Теория и технологии программирования на языках высокого уровня", "room": "18А",
                 "teacher": "Степанов А.В"},
                {"start": time(11, 30), "end": time(13, 00), "name": "ЛК Основы российской государственности",
                 "room": "309В", "teacher": "Валуев Д.Г."},
                {"start": time(13, 20), "end": time(14, 50), "name": "ПЗ Иностранный язык",
                 "room": "531Б", "teacher": "Ермоленко О.В."},
                {"start": time(15, 00), "end": time(16, 30), "name": "ПЗ Человек и право",
                 "room": "301В", "teacher": "Шевченко В.И."},
            ],
            "Thursday": [
                {"start": time(8, 00), "end": time(9, 30), "name": "ПЗ Высшая математика", "room": "309А",
                 "teacher": "доц. Вронский Б.М."},
                {"start": time(9, 50), "end": time(11, 20), "name": "ПЗ Основы российской государственности", "room": "304А",
                 "teacher": "Валуев Д.Г."},

            ],
            "Friday": [
                {"start": time(8, 00), "end": time(9, 30), "name": "1 подгруппа - ПЗ Теория и технологии программирования на языках высокого уровня | 2 подгруппа - нет пары", "room": "119А",
                 "teacher": "Енина А.А."},
                {"start": time(9, 50), "end": time(11, 20), "name": "ЛК Математическая логика и теория алгоритмов", "room": "401В",
                 "teacher": "Степанова Е.И."},
                {"start": time(13, 20), "end": time(14, 50), "name": "ЛК Материаловедение",
                 "room": "ул.Генерала Васильева,32а (завод СЭЛМА)", "teacher": "Скиданчук А.Г."},
                {"start": time(15, 00), "end": time(16, 30), "name": "ПЗ Материаловедение",
                 "room": "ул.Генерала Васильева,32а (завод СЭЛМА)", "teacher": "Скиданчук А.Г."},
            ],
    }
    }

temporary_changes = {}

# ======================
# 🤖 ИНИЦИАЛИЗАЦИЯ
# ======================

bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ======================
# 🔘 КНОПКИ
# ======================

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📌 Какая сейчас пара?")],
        [KeyboardButton(text="📖 Расписание сегодня")],
        [KeyboardButton(text="📅 Расписание завтра")],
        [KeyboardButton(text="🔔 Подписаться")],
        [KeyboardButton(text="❌ Отписаться")]
    ],
    resize_keyboard=True
)

# ======================
# 🔢 НЕДЕЛЯ
# ======================

def get_week_type():
    today = date.today()
    delta = (today - EVEN_WEEK_START).days
    weeks = delta // 7
    return "even" if weeks % 2 == 0 else "odd"

def get_schedule(target_date=None):
    if not target_date:
        target_date = datetime.now().date()

    week_type = get_week_type()
    day_name = target_date.strftime("%A")

    return schedule.get(week_type, {}).get(day_name, [])

# ======================
# 🚀 СТАРТ
# ======================

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Бот запущен 🚀", reply_markup=main_keyboard)

# ======================
# 🔔 ПОДПИСКА
# ======================

@dp.message(F.text == "🔔 Подписаться")
async def subscribe(message: Message):
    user_id = message.from_user.id
    subscribers.add(user_id)
    save_subscribers()
    await message.answer("✅ Подписка активирована")

@dp.message(F.text == "❌ Отписаться")
async def unsubscribe(message: Message):
    user_id = message.from_user.id
    subscribers.discard(user_id)
    save_subscribers()
    await message.answer("❌ Ты отписался")

# ======================
# ⏰ УВЕДОМЛЕНИЯ
# ======================

async def notifier():
    while True:
        now = datetime.now()
        lessons = get_schedule()

        for lesson in lessons:
            start_dt = datetime.combine(now.date(), lesson["start"])
            diff = (start_dt - now).total_seconds()

            lesson_id = f"{now.date()}_{lesson['start']}"

            if 0 < diff <= 600 and lesson_id not in notified_today:
                for user in subscribers:
                    try:
                        await bot.send_message(
                            user,
                            f"🔔 Через 10 минут начнётся {lesson['name']}"
                        )
                    except:
                        pass

                notified_today.add(lesson_id)

        await asyncio.sleep(30)

# ======================
# 🌐 WEBHOOK
# ======================

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)
    asyncio.create_task(notifier())

async def on_shutdown(app):
    await bot.delete_webhook()

def main():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, dp.webhook_handler())
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    port = int(os.getenv("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()