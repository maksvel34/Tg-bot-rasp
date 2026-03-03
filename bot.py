import asyncio
import random
from datetime import datetime, time, timedelta, date
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# ======================
# ⚙ НАСТРОЙКИ
# ======================

TOKEN = "8628918090:AAEha-U3peBJFurJq9-nhrNliz0j-T1VxDw"
ADMIN_ID = [1071264428, 7237228038]

EVEN_WEEK_START = date(2026, 2, 9)

NO_CLASSES_PHRASES = [
    "Сегодня пар больше нет 😎",
    "Можно отдыхать 💤",
    "Свободен 🎉",
    "Бро ватафа какие пары",
    "Этот пепе может спать спокойно",
    "Ебать, справа пожалуста остановитесь",
    "бля ты бездарь типо",
    "Врямя есть иди готовь две в сырном",
    "Сіз қаншықсыз очпочмак сізге жете алмайсыз",
    "Ебель камэ иди домой",
    "Мама разрешила не идти",
    "В гостях заебись а ты пошел нахуй",
    "На сегодня отсосал все хуи",
]

# ======================
# 📚 РАСПИСАНИЕ
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

subscribers = set()

# ======================
# 🤖 ИНИЦИАЛИЗАЦИЯ
# ======================

bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ======================
# 🔘 КНОПКИ СНИЗУ
# ======================

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📌 Какая сейчас пара?")],
        [KeyboardButton(text="📖 Расписание сегодня")],
        [KeyboardButton(text="📅 Расписание завтра")],
        [KeyboardButton(text="🔔 Подписаться на уведомления")]
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

# ======================
# 📅 РАСПИСАНИЕ
# ======================

def get_schedule(target_date=None):
    if not target_date:
        target_date = datetime.now().date()

    week_type = get_week_type()
    day_name = target_date.strftime("%A")

    base = schedule.get(week_type, {}).get(day_name, [])
    temp = temporary_changes.get(str(target_date), [])

    return temp if temp else base

# ======================
# 📊 ТЕКУЩАЯ ПАРА
# ======================

def get_current_class():
    now = datetime.now()
    lessons = get_schedule()

    if not lessons:
        return None, None

    for lesson in lessons:
        start_dt = datetime.combine(now.date(), lesson["start"])
        end_dt = datetime.combine(now.date(), lesson["end"])

        if start_dt <= now <= end_dt:
            return "ongoing", lesson

        if now < start_dt:
            minutes = int((start_dt - now).total_seconds() // 60)
            return minutes, lesson

    return None, None

# ======================
# 🚀 СТАРТ
# ======================

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Готов батрачить", reply_markup=main_keyboard)

# ======================
# 📌 ТЕКУЩАЯ ПАРА
# ======================

@dp.message(F.text == "📌 Какая сейчас пара?")
async def current_class(message: Message):
    status, lesson = get_current_class()

    if status == "ongoing":
        text = f"🟢 Сейчас идёт:\n<b>{lesson['name']}</b>\nКабинет: {lesson['room']}\nПреподаватель: {lesson['teacher']}"
    elif isinstance(status, int):
        text = f"⏳ До начала {lesson['name']} осталось {status} минут\nКабинет: {lesson['room']}\nПреподаватель: {lesson['teacher']}"
    else:
        text = random.choice(NO_CLASSES_PHRASES)

    await message.answer(text)

# ======================
# 📖 СЕГОДНЯ
# ======================

@dp.message(F.text == "📖 Расписание сегодня")
async def today_schedule(message: Message):
    lessons = get_schedule()

    if not lessons:
        await message.answer(random.choice(NO_CLASSES_PHRASES))
        return

    text = "<b>📖 Сегодня:</b>\n\n"
    for lesson in lessons:
        text += f"{lesson['start']} - {lesson['end']}\n{lesson['name']} | {lesson['room']} | {lesson['teacher']}\n\n"

    await message.answer(text)

# ======================
# 📅 ЗАВТРА
# ======================

@dp.message(F.text == "📅 Расписание завтра")
async def tomorrow_schedule(message: Message):
    tomorrow = datetime.now().date() + timedelta(days=1)
    lessons = get_schedule(tomorrow)

    if not lessons:
        await message.answer(random.choice(NO_CLASSES_PHRASES))
        return

    text = "<b>📅 Завтра:</b>\n\n"
    for lesson in lessons:
        text += f"{lesson['start']} - {lesson['end']}\n{lesson['name']} | {lesson['room']} | {lesson['teacher']}\n\n"

    await message.answer(text)

# ======================
# 🔔 ПОДПИСКА
# ======================

@dp.message(F.text == "🔔 Подписаться на уведомления")
async def subscribe(message: Message):
    subscribers.add(message.from_user.id)
    await message.answer("✅ Ты подписан на уведомления")

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

            if 0 < diff <= 300:
                for user in subscribers:
                    await bot.send_message(
                        user,
                        f"🔔 Через 5 минут начнётся {lesson['name']} в кабинете {lesson['room']}"
                    )
        await asyncio.sleep(60)

# ======================
# 🔄 АВТОСБРОС
# ======================

async def reset_changes():
    while True:
        now = datetime.now()
        if now.hour == 0 and now.minute == 0:
            temporary_changes.clear()
        await asyncio.sleep(60)

# ======================
# ▶ ЗАПУСК
# ======================

async def main():
    asyncio.create_task(notifier())
    asyncio.create_task(reset_changes())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
