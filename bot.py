import asyncio
import random
import json
import os
import hashlib
import re
from datetime import datetime, time, timedelta, date
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatType


# ======================
# ⚙ НАСТРОЙКИ
# ======================
TOKEN = "8628918090:AAE-WeIyeu8LVkIe5_LZDEbvfycleAzViB8"
# 🔧 Впишите сюда ID админов
ADMIN_ID = [1071264428,7237228038]
EVEN_WEEK_START = date(2026, 2, 9)
SUBSCRIBERS_FILE = "subscribers.json"

# ✅ Часовой пояс (0 = время сервера, 3 = Москва)
TIMEZONE_OFFSET_HOURS = 3

# ✅ ID ветки (None = работать везде, число = только в конкретной ветке)
ALLOWED_THREAD_ID = 5

# Список фраз
NO_CLASSES_PHRASES = [
    "Сегодня пар больше нет 😎", "Можно отдыхать 💤", "Свободен 🎉",
    "Бро ватафа какие пары", "Этот пепе может спать спокойно",
    "Время есть иди готовь две в сырном", "Сіз қаншықсыз очпочмак сізге жете алмайсыз",
    "Мама разрешила не идти", "Иди домой, пары закончились",
    "На сегодня всё, отдыхай", "Пар нет, наслаждайся жизнью",
    "Пар нет, а Скитейкин лох", "А сам чекнуть не можешь?", "Заходят как то два дракона в бар. Один спрашивает другого: Почему здесь так жарко? -Ебало завали.",
    "Не скажу", "У Вики спроси", "Напиши я гей, а я скину тебе сто рублей",
    "Извените а кто ваш любимый исполнитель?", "Я не ебу",
    "Меня крестил лично батюшка владимир",
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
            {"start": time(15, 00), "end": time(16, 30), "name": "ЛК Человек и право", "room": "309А",
             "teacher": "Шевченко В.И."},
        ],
        "Tuesday": [
            {"start": time(9, 50), "end": time(11, 20), "name": "ЛК Цифровые технологии в профессиональной сфере",
             "room": "309А", "teacher": "доц. Филиппов Д.М."},
            {"start": time(11, 30), "end": time(13, 00), "name": "ПЗ Цифровые технологии в профессиональной сфере",
             "room": "8А", "teacher": "доц. Филиппов Д.М."},
            {"start": time(13, 20), "end": time(14, 50), "name": "ПЗ Физическая культура", "room": "спортзал ТА",
             "teacher": "Ковальчук Елена Сергеевна"},
            {"start": time(15, 00), "end": time(16, 30), "name": "ПЗ История России", "room": "201В",
             "teacher": "Маргасов В.С."},
        ],
        "Wednesday": [
            {"start": time(9, 50), "end": time(11, 20),
             "name": "1 подгруппа - нет пары | 2 подгруппа - ПЗ Теория и технологии программирования", "room": "119А",
             "teacher": "Енина А.А."},
            {"start": time(11, 30), "end": time(13, 00), "name": "ЛК Теория и технологии программирования",
             "room": "18А", "teacher": "Степанов А.В"},
            {"start": time(13, 20), "end": time(14, 50), "name": "ПЗ Иностранный язык", "room": "531Б",
             "teacher": "Ермоленко О.В."},
        ],
        "Thursday": [
            {"start": time(8, 00), "end": time(9, 30), "name": "ПЗ Высшая математика", "room": "302В",
             "teacher": "доц. Вронский Б.М."},
            {"start": time(9, 50), "end": time(11, 20), "name": "ПЗ Основы российской государственности",
             "room": "411В", "teacher": "Валуев Д.Г."},
            {"start": time(11, 30), "end": time(13, 00), "name": "ЛК Экономическая культура и финансовая грамотность",
             "room": "411В", "teacher": "Друзин Р.В."},
            {"start": time(13, 20), "end": time(14, 50), "name": "ПЗ Экономическая культура и финансовая грамотность",
             "room": "411В", "teacher": "Друзин Р.В."},
        ],
        "Friday": [
            {"start": time(8, 00), "end": time(9, 30),
             "name": "1 подгруппа - ПЗ Теория и технологии программирования | 2 подгруппа - нет пары", "room": "119А",
             "teacher": "Енина А.А."},
            {"start": time(9, 50), "end": time(11, 20), "name": "ЛК Математическая логика и теория алгоритмов",
             "room": "302В", "teacher": "Степанова Е.И."},
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
            {"start": time(9, 50), "end": time(11, 20), "name": "ЛК Цифровые технологии в профессиональной сфере",
             "room": "309А", "teacher": "доц. Филиппов Д.М."},
            {"start": time(11, 30), "end": time(13, 00), "name": "ПЗ Цифровые технологии в профессиональной сфере",
             "room": "8А", "teacher": "доц. Филиппов Д.М."},
            {"start": time(13, 20), "end": time(14, 50), "name": "ПЗ Физическая культура", "room": "спортзал ТА",
             "teacher": "Ковальчук Елена Сергеевна"},
            {"start": time(15, 00), "end": time(16, 30), "name": "ПЗ История России", "room": "201В",
             "teacher": "Маргасов В.С."},
        ],
        "Wednesday": [
            {"start": time(8, 00), "end": time(9, 30),
             "name": "1 подгруппа - нет пары | 2 подгруппа - ПЗ Теория и технологии программирования", "room": "119А",
             "teacher": "Енина А.А."},
            {"start": time(9, 50), "end": time(11, 20), "name": "ЛК Теория и технологии программирования",
             "room": "18А", "teacher": "Степанов А.В"},
            {"start": time(11, 30), "end": time(13, 00), "name": "ЛК Основы российской государственности",
             "room": "309В", "teacher": "Валуев Д.Г."},
            {"start": time(13, 20), "end": time(14, 50), "name": "ПЗ Иностранный язык", "room": "531Б",
             "teacher": "Ермоленко О.В."},
            {"start": time(15, 00), "end": time(16, 30), "name": "ПЗ Человек и право", "room": "301В",
             "teacher": "Шевченко В.И."},
        ],
        "Thursday": [
            {"start": time(8, 00), "end": time(9, 30), "name": "ПЗ Высшая математика", "room": "309А",
             "teacher": "доц. Вронский Б.М."},
            {"start": time(9, 50), "end": time(11, 20), "name": "ПЗ Основы российской государственности",
             "room": "304А", "teacher": "Валуев Д.Г."},
        ],
        "Friday": [
            {"start": time(8, 00), "end": time(9, 30),
             "name": "1 подгруппа - ПЗ Теория и технологии программирования | 2 подгруппа - нет пары", "room": "119А",
             "teacher": "Енина А.А."},
            {"start": time(9, 50), "end": time(11, 20), "name": "ЛК Математическая логика и теория алгоритмов",
             "room": "401В", "teacher": "Степанова Е.И."},
            {"start": time(13, 20), "end": time(14, 50), "name": "ЛК Материаловедение",
             "room": "ул.Генерала Васильева,32а (завод СЭЛМА)", "teacher": "Скиданчук А.Г."},
            {"start": time(15, 00), "end": time(16, 30), "name": "ПЗ Материаловедение",
             "room": "ул.Генерала Васильева,32а (завод СЭЛМА)", "teacher": "Скиданчук А.Г."},
        ],
    }
}

# ======================
# 🔤 МАППИНГИ
# ======================
DAY_EN_TO_RU = {"Monday": "Понедельник", "Tuesday": "Вторник", "Wednesday": "Среда", "Thursday": "Четверг",
                "Friday": "Пятница"}
DAY_RU_TO_EN = {v: k for k, v in DAY_EN_TO_RU.items()}
SUBJECT_MAP = {}
temporary_changes = {}
subscribers = set()
notified_lessons = set()
admin_context = {}


# ======================
# 🗄️ ПЕРСИСТЕНТНОСТЬ
# ======================
def load_subscribers():
    if os.path.exists(SUBSCRIBERS_FILE):
        try:
            with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except:
            return set()
    return set()


def save_subscribers(subs):
    try:
        with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(subs), f, ensure_ascii=False, indent=2)
    except:
        pass


# ======================
# 🔤 ОЧИСТКА НАЗВАНИЙ
# ======================
def clean_subject_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r'^(ЛК|ПЗ|ЛБ)\s+', '', name)
    name = re.sub(r'^\d+\s+подгруппа\s*-\s*', '', name)
    name = re.sub(r'\|\s*\d+\s+подгруппа\s*-\s*.*$', '', name)
    name = re.sub(r'\s*-\s*нет пары.*$', '', name)
    return name.strip()


def generate_subject_id(name: str) -> str:
    clean = clean_subject_name(name)
    short = clean[:20].lower().replace(" ", "_")
    short = re.sub(r'[^a-zа-яё0-9_]', '', short)
    hash_part = hashlib.md5(clean.encode("utf-8")).hexdigest()[:8]
    result = f"subj_{short}_{hash_part}"
    return result[:64]


def init_subject_map():
    global SUBJECT_MAP
    SUBJECT_MAP = {}
    subjects = get_all_subjects()
    for subj in subjects:
        subj_id = generate_subject_id(subj)
        SUBJECT_MAP[subj_id] = subj
    return SUBJECT_MAP


# ======================
# 🤖 ИНИЦИАЛИЗАЦИЯ
# ======================
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


# ======================
# ✅ FIX #1: Время
# ======================
def get_local_now():
    if TIMEZONE_OFFSET_HOURS != 0:
        return datetime.now() + timedelta(hours=TIMEZONE_OFFSET_HOURS)
    return datetime.now()

def get_local_date():
    return get_local_now().date()


# ======================
# ✅ FIX #2: Ветки
# ======================
def is_allowed_thread(message: Message) -> bool:
    if ALLOWED_THREAD_ID is None:
        return True
    if message.is_topic_message and message.message_thread_id != ALLOWED_THREAD_ID:
        return False
    return True


# ======================
# ✅ FIX #4: 100% ПРОВЕРКА АДМИНКИ + ТИП ЧАТА
# ======================
def get_safe_keyboard(user_id: int, chat_type: str) -> ReplyKeyboardMarkup:
    """
    ГЕНЕРИРУЕТ КЛАВИАТУРУ ЗАНОВО КАЖДЫЙ РАЗ.
    Кнопка админа появляется ТОЛЬКО если:
    1. user_id в ADMIN_ID
    2. chat_type == 'private' (личный чат)
    """
    is_admin = user_id in ADMIN_ID
    is_private = chat_type == ChatType.PRIVATE

    # ✅ Кнопка управления видна только админу в ЛИЧНОМ чате
    show_admin_button = is_admin and is_private

    if show_admin_button:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="⚙️ Управление расписанием")],
                [KeyboardButton(text="📌 Какая сейчас пара?")],
                [KeyboardButton(text="📖 Расписание сегодня"), KeyboardButton(text="📅 Расписание завтра")],
                [KeyboardButton(text="🔔 Подписаться на уведомления"),
                 KeyboardButton(text="🔕 Отписаться от уведомлений")],
                [KeyboardButton(text="📚 Предметы")],
            ],
            resize_keyboard=True
        )
    else:
        # Обычная клавиатура для всех в группах и для обычных пользователей
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📌 Какая сейчас пара?")],
                [KeyboardButton(text="📖 Расписание сегодня"), KeyboardButton(text="📅 Расписание завтра")],
                [KeyboardButton(text="🔔 Подписаться на уведомления"),
                 KeyboardButton(text="🔕 Отписаться от уведомлений")],
                [KeyboardButton(text="📚 Предметы")],
            ],
            resize_keyboard=True
        )


# ======================
# 🔘 ОСТАЛЬНЫЕ КЛАВИАТУРЫ
# ======================
def get_week_select_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Чётная", callback_data="week_even"),
         InlineKeyboardButton(text="Нечётная", callback_data="week_odd")],
        [InlineKeyboardButton(text="🔙 В меню", callback_data="nav_main")]
    ])


def get_days_keyboard():
    days = [("Monday", "Понедельник"), ("Tuesday", "Вторник"), ("Wednesday", "Среда"), ("Thursday", "Четверг"),
            ("Friday", "Пятница")]
    keyboard = []
    for i in range(0, len(days), 2):
        row = [InlineKeyboardButton(text=days[i][1], callback_data=f"day_{days[i][0]}")]
        if i + 1 < len(days):
            row.append(InlineKeyboardButton(text=days[i + 1][1], callback_data=f"day_{days[i + 1][0]}"))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="nav_week")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_lessons_keyboard(lessons, week_type, day_name):
    keyboard = []
    for idx, lesson in enumerate(lessons):
        short_name = (lesson["name"][:25] + "..") if len(lesson["name"]) > 25 else lesson["name"]
        callback = f"lesson_{week_type}_{day_name}_{idx}"
        if len(callback.encode('utf-8')) > 64:
            callback = f"lsn_{week_type[:3]}_{day_name[:3]}_{idx}"
        callback = callback[:64]
        keyboard.append([InlineKeyboardButton(text=f"{short_name} ({lesson['start']})", callback_data=callback)])
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="nav_days")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_lesson_edit_keyboard(week_type, day_name, idx):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить название", callback_data=f"edit_name_{week_type}_{day_name}_{idx}")],
        [InlineKeyboardButton(text="🚪 Изменить кабинет", callback_data=f"edit_room_{week_type}_{day_name}_{idx}")],
        [InlineKeyboardButton(text="👨‍🏫 Изменить преподавателя",
                              callback_data=f"edit_teacher_{week_type}_{day_name}_{idx}")],
        [InlineKeyboardButton(text="⏰ Изменить время", callback_data=f"edit_time_{week_type}_{day_name}_{idx}")],
        [InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"del_{week_type}_{day_name}_{idx}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"nav_lessons_{week_type}_{day_name}")]
    ])


def get_subjects_keyboard(subjects):
    keyboard = []
    seen_clean_names = set()
    for subj in sorted(subjects):
        clean_name = clean_subject_name(subj)
        if clean_name in seen_clean_names:
            continue
        seen_clean_names.add(clean_name)
        subj_id = generate_subject_id(subj)
        short = (clean_name[:35] + "..") if len(clean_name) > 35 else clean_name
        keyboard.append([InlineKeyboardButton(text=short, callback_data=f"subj_{subj_id.replace('subj_', '')}")])
    keyboard.append([InlineKeyboardButton(text="🔙 В меню", callback_data="nav_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ======================
# 🔢 НЕДЕЛЯ И РАСПИСАНИЕ
# ======================
def get_week_type(target_date=None):
    if target_date is None:
        target_date = get_local_date()  # ✅ Было: date.today()
    delta = (target_date - EVEN_WEEK_START).days
    weeks = delta // 7
    return "even" if weeks % 2 == 0 else "odd"


def get_schedule(target_date=None):
    if target_date is None:
        target_date = get_local_date()  # ✅ Было: date.today()
    week_type = get_week_type(target_date)
    day_name = target_date.strftime("%A")
    base = schedule.get(week_type, {}).get(day_name, [])
    temp = temporary_changes.get(str(target_date), [])
    return temp if temp else base


def get_all_subjects():
    subjects = set()
    for week in schedule.values():
        for day_lessons in week.values():
            for lesson in day_lessons:
                name = lesson["name"]
                if " | " in name:
                    parts = name.split(" | ")
                    for part in parts:
                        if "нет пары" not in part:
                            clean = clean_subject_name(part)
                            if clean: subjects.add(clean)
                elif "нет пары" not in name:
                    clean = clean_subject_name(name)
                    if clean: subjects.add(clean)
    return sorted(subjects)


def find_subject_occurrences(subject_name):
    result = []
    for week_type in ["even", "odd"]:
        for day_en, lessons in schedule[week_type].items():
            for lesson in lessons:
                name = lesson["name"]
                clean_name = clean_subject_name(name)
                if subject_name == clean_name or subject_name in clean_name:
                    day_ru = DAY_EN_TO_RU.get(day_en, day_en)
                    lesson_type = ""
                    if name.startswith("ЛК"):
                        lesson_type = "Лекция"
                    elif name.startswith("ПЗ"):
                        lesson_type = "Практика"
                    elif name.startswith("ЛБ"):
                        lesson_type = "Лабораторная"
                    result.append({"day": day_ru, "start": lesson["start"].strftime("%H:%M"),
                                   "end": lesson["end"].strftime("%H:%M"),
                                   "week": "чёт" if week_type == "even" else "нечёт", "room": lesson["room"],
                                   "teacher": lesson["teacher"], "type": lesson_type})
    return result


# ======================
# 📊 ТЕКУЩАЯ ПАРА
# ======================
def get_current_class():
    now = get_local_now()
    today = get_local_now()
    if now.hour < 3:
        return None, None
    lessons = get_schedule(today)
    if not lessons:
        return None, None
    last_lesson_end = None
    for lesson in lessons:
        end_dt = datetime.combine(today, lesson["end"])
        if last_lesson_end is None or end_dt > last_lesson_end:
            last_lesson_end = end_dt
    if last_lesson_end and now > last_lesson_end:
        return None, None
    for lesson in lessons:
        start_dt = datetime.combine(today, lesson["start"])
        end_dt = datetime.combine(today, lesson["end"])
        if start_dt <= now <= end_dt:
            return "ongoing", lesson
        if now < start_dt:
            minutes = int((start_dt - now).total_seconds() // 60)
            return minutes, lesson
    return None, None


# ======================
# 🎯 FSM
# ======================
class AdminEdit(StatesGroup):
    waiting_name = State()
    waiting_room = State()
    waiting_teacher = State()
    waiting_start_time = State()
    waiting_end_time = State()


# ======================
# 🚀 СТАРТ
# ======================
@dp.message(Command("start"))
async def start_handler(message: Message):
    if not is_allowed_thread(message):
        return
    # ✅ Генерируем клавиатуру с учётом типа чата и ID
    keyboard = get_safe_keyboard(message.from_user.id, message.chat.type)
    await message.answer("Готов батрачить ⚙️", reply_markup=keyboard)


# ======================
# 👥 ОБЫЧНЫЕ КНОПКИ
# ======================
@dp.message(F.text == "📌 Какая сейчас пара?")
async def current_class(message: Message):
    if not is_allowed_thread(message): return
    status, lesson = get_current_class()
    if status == "ongoing":
        text = f"🟢 Сейчас идёт:\n<b>{lesson['name']}</b>\n🚪 {lesson['room']}\n👨‍🏫 {lesson['teacher']}"
    elif isinstance(status, int):
        text = f"⏳ До {lesson['name']} осталось {status} мин\n🚪 {lesson['room']}\n👨‍🏫 {lesson['teacher']}"
    else:
        text = random.choice(NO_CLASSES_PHRASES)
    await message.answer(text)


@dp.message(F.text == "📖 Расписание сегодня")
async def today_schedule(message: Message):
    if not is_allowed_thread(message): return
    lessons = get_schedule(get_local_date())
    if not lessons:
        await message.answer(random.choice(NO_CLASSES_PHRASES));
        return
    text = "<b>📖 Сегодня:</b>\n\n"
    for lesson in lessons:
        text += f"⏰ {lesson['start'].strftime('%H:%M')}–{lesson['end'].strftime('%H:%M')}\n📚 {lesson['name']}\n🚪 {lesson['room']} | 👨‍🏫 {lesson['teacher']}\n\n"
    await message.answer(text)


@dp.message(F.text == "📅 Расписание завтра")
async def tomorrow_schedule(message: Message):
    if not is_allowed_thread(message):
        return
    tomorrow = get_local_date() + timedelta(days=1)  # ✅ Было: date.today()
    lessons = get_schedule(tomorrow)
    if not lessons:
        await message.answer(random.choice(NO_CLASSES_PHRASES));
        return
    text = "<b>📅 Завтра:</b>\n\n"
    for lesson in lessons:
        text += f"⏰ {lesson['start'].strftime('%H:%M')}–{lesson['end'].strftime('%H:%M')}\n📚 {lesson['name']}\n🚪 {lesson['room']} | 👨‍🏫 {lesson['teacher']}\n\n"
    await message.answer(text)


@dp.message(F.text == "🔔 Подписаться на уведомления")
async def subscribe(message: Message):
    if not is_allowed_thread(message): return
    if message.from_user.id not in subscribers:
        subscribers.add(message.from_user.id);
        save_subscribers(subscribers)
        await message.answer("✅ Вы подписаны на уведомления за 5 минут до пары!")
    else:
        await message.answer("ℹ️ Вы уже подписаны")


@dp.message(F.text == "🔕 Отписаться от уведомлений")
async def unsubscribe(message: Message):
    if not is_allowed_thread(message): return
    if message.from_user.id in subscribers:
        subscribers.remove(message.from_user.id);
        save_subscribers(subscribers)
        await message.answer("🔕 Вы отписаны от уведомлений")
    else:
        await message.answer("ℹ️ Вы не были подписаны")


@dp.message(F.text == "📚 Предметы")
async def show_subjects(message: Message):
    if not is_allowed_thread(message): return
    subjects = get_all_subjects()
    if not subjects:
        await message.answer("❌ Предметы не найдены");
        return
    await message.answer("📚 Выберите предмет:", reply_markup=get_subjects_keyboard(subjects))


# ======================
# ✅ FIX #4: CALLBACK С ПРОВЕРКОЙ ПРАВ
# ======================
@dp.callback_query(F.data.startswith("subj_"))
async def subject_info(callback: CallbackQuery):
    subj_id = callback.data.replace("subj_", "")
    full_id = f"subj_{subj_id}"
    subject = SUBJECT_MAP.get(full_id)
    if not subject:
        for key, val in SUBJECT_MAP.items():
            if key.endswith(subj_id) or subj_id in key:
                subject = val;
                break
    if not subject:
        await callback.answer("❌ Предмет не найден", show_alert=True);
        return
    occurrences = find_subject_occurrences(subject)
    if not occurrences:
        await callback.answer("❌ Пар не найдено", show_alert=True);
        return
    text = f"<b>{subject}</b>\n"
    for occ in occurrences:
        type_str = f"({occ['type']})" if occ['type'] else ""
        text += f"{occ['day']} {occ['start']}–{occ['end']} {type_str} ({occ['week']} нед.)\n🚪 {occ['room']} | 👨‍🏫 {occ['teacher']}\n"
    await callback.message.answer(text, reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔙 В меню", callback_data="nav_main")]]), parse_mode=ParseMode.HTML)
    await callback.answer()


@dp.callback_query(F.data == "nav_main")
async def back_to_main(callback: CallbackQuery):
    # ✅ 100% ПРОВЕРКА: Генерируем клавиатуру заново на основе ID и ТИПА ЧАТА
    keyboard = get_safe_keyboard(callback.from_user.id, callback.message.chat.type)
    await callback.message.delete()
    await callback.message.answer("Главное меню:", reply_markup=keyboard)
    await callback.answer()


@dp.callback_query(F.data == "nav_week")
async def back_week(callback: CallbackQuery):
    await callback.message.edit_text("🗓️ Какую неделю изменить?", reply_markup=get_week_select_keyboard())
    await callback.answer()


@dp.callback_query(F.data == "nav_days")
async def back_days(callback: CallbackQuery):
    await callback.message.edit_text("🗓️ Какую неделю изменить?", reply_markup=get_week_select_keyboard())
    await callback.answer()


@dp.callback_query(F.data.startswith("nav_lessons_"))
async def admin_back_lessons(callback: CallbackQuery):
    parts = callback.data.replace("nav_lessons_", "").split("_")
    if len(parts) >= 2:
        week_type = parts[0]
        day_name = "_".join(parts[1:]) if len(parts) > 2 else parts[1]
        day_en = DAY_RU_TO_EN.get(day_name, day_name)
        lessons = schedule.get(week_type, {}).get(day_en, [])
        await callback.message.edit_text(f"📚 {day_name} ({week_type}): выберите пару",
                                         reply_markup=get_lessons_keyboard(lessons, week_type, day_name))
        await callback.answer()


# ======================
# ⚙️ АДМИН: УПРАВЛЕНИЕ
# ======================
@dp.message(F.text == "⚙️ Управление расписанием")
async def admin_schedule_start(message: Message):
    if not is_allowed_thread(message): return
    # ✅ Тройная проверка: ветка + админ + личный чат
    if message.from_user.id not in ADMIN_ID:
        await message.answer("❌ Доступ запрещён. Вы не администратор.")
        return
    if message.chat.type != ChatType.PRIVATE:
        await message.answer("❌ Управление расписанием доступно только в личных сообщениях с ботом.")
        return
    await message.answer("🗓️ Какую неделю изменить?", reply_markup=get_week_select_keyboard())


@dp.callback_query(F.data.startswith("week_"))
async def admin_select_week(callback: CallbackQuery):
    # ✅ Проверка прав для кнопок админки
    if callback.from_user.id not in ADMIN_ID:
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    week_type = "even" if "even" in callback.data else "odd"
    admin_context[callback.from_user.id] = {"week_type": week_type}
    await callback.message.edit_text(f"🗓️ {week_type} неделя — выберите день:", reply_markup=get_days_keyboard())
    await callback.answer()


@dp.callback_query(F.data.startswith("day_"))
async def admin_select_day(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_ID:
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    day_en = callback.data.replace("day_", "")
    day_ru = DAY_EN_TO_RU.get(day_en, day_en)
    ctx = admin_context.get(callback.from_user.id, {})
    week_type = ctx.get("week_type", "even")
    lessons = schedule.get(week_type, {}).get(day_en, [])
    if not lessons:
        await callback.answer("❌ Нет пар в этот день", show_alert=True);
        return
    await callback.message.edit_text(f"📚 {day_ru} ({week_type}): выберите пару для редактирования",
                                     reply_markup=get_lessons_keyboard(lessons, week_type, day_ru))
    await callback.answer()


@dp.callback_query(F.data.startswith("lesson_"))
async def admin_select_lesson(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_ID:
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    parts = callback.data.split("_")
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True);
        return
    week_type = parts[1]
    day_name = parts[2]
    idx = int(parts[3])
    day_en = DAY_RU_TO_EN.get(day_name, day_name)
    lessons = schedule.get(week_type, {}).get(day_en, [])
    if idx >= len(lessons):
        await callback.answer("❌ Ошибка индекса", show_alert=True);
        return
    lesson = lessons[idx]
    text = f"<b>{lesson['name']}</b>\n⏰ {lesson['start'].strftime('%H:%M')}–{lesson['end'].strftime('%H:%M')}\n🚪 {lesson['room']}\n👨‍🏫 {lesson['teacher']}"
    admin_context[callback.from_user.id] = {"week_type": week_type, "day_name": day_name, "day_en": day_en, "idx": idx,
                                            "lesson": lesson.copy()}
    await callback.message.edit_text(text, reply_markup=get_lesson_edit_keyboard(week_type, day_name, idx))
    await callback.answer()


# ======================
# ✏️ РЕДАКТИРОВАНИЕ ПОЛЕЙ
# ======================
@dp.callback_query(F.data.startswith("edit_name_"))
async def edit_name_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_ID: return
    ctx = admin_context.get(callback.from_user.id, {})
    lesson = ctx.get("lesson", {})
    await callback.message.answer(
        f"📝 Введите новое название пары:\nТекущее: <b>{lesson.get('name', 'N/A')}</b>\nОтправьте /cancel для отмены",
        parse_mode=ParseMode.HTML)
    await state.set_state(AdminEdit.waiting_name)
    await callback.answer()


@dp.callback_query(F.data.startswith("edit_room_"))
async def edit_room_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_ID: return
    ctx = admin_context.get(callback.from_user.id, {})
    lesson = ctx.get("lesson", {})
    await callback.message.answer(
        f"🚪 Введите новый кабинет:\nТекущий: <b>{lesson.get('room', 'N/A')}</b>\nОтправьте /cancel для отмены",
        parse_mode=ParseMode.HTML)
    await state.set_state(AdminEdit.waiting_room)
    await callback.answer()


@dp.callback_query(F.data.startswith("edit_teacher_"))
async def edit_teacher_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_ID: return
    ctx = admin_context.get(callback.from_user.id, {})
    lesson = ctx.get("lesson", {})
    await callback.message.answer(
        f"👨‍🏫 Введите нового преподавателя:\nТекущий: <b>{lesson.get('teacher', 'N/A')}</b>\nОтправьте /cancel для отмены",
        parse_mode=ParseMode.HTML)
    await state.set_state(AdminEdit.waiting_teacher)
    await callback.answer()


@dp.callback_query(F.data.startswith("edit_time_"))
async def edit_time_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_ID: return
    ctx = admin_context.get(callback.from_user.id, {})
    lesson = ctx.get("lesson", {})
    await callback.message.answer(
        f"⏰ Введите новое время в формате ЧЧ:ММ-ЧЧ:ММ\nТекущее: <b>{lesson.get('start', '').strftime('%H:%M')}-{lesson.get('end', '').strftime('%H:%M')}</b>\nПример: 09:00-10:30\nОтправьте /cancel для отмены",
        parse_mode=ParseMode.HTML)
    await state.set_state(AdminEdit.waiting_start_time)
    await callback.answer()


# ======================
# 💾 СОХРАНЕНИЕ ИЗМЕНЕНИЙ
# ======================
@dp.message(AdminEdit.waiting_name)
async def save_name(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_ID: return
    if message.text == "/cancel":
        await state.clear();
        await message.answer("❌ Отменено");
        return
    ctx = admin_context.get(message.from_user.id, {})
    week_type = ctx.get("week_type");
    day_name = ctx.get("day_name");
    day_en = ctx.get("day_en");
    idx = ctx.get("idx")
    if not all([week_type, day_en, idx is not None]):
        await message.answer("❌ Ошибка контекста");
        await state.clear();
        return
    today = get_local_date();
    target_date = None
    for i in range(7):
        check_date = today + timedelta(days=i)
        if check_date.strftime("%A") == day_en and get_week_type(check_date) == week_type:
            target_date = check_date;
            break
    if not target_date:
        await message.answer("❌ Не найдена дата");
        await state.clear();
        return
    if str(target_date) not in temporary_changes:
        base = schedule.get(week_type, {}).get(day_en, [])
        temporary_changes[str(target_date)] = [l.copy() for l in base]
    if idx < len(temporary_changes[str(target_date)]):
        temporary_changes[str(target_date)][idx]["name"] = message.text
        await message.answer(f"✅ Название обновлено: <b>{message.text}</b>", parse_mode=ParseMode.HTML)
        admin_context[message.from_user.id]["lesson"]["name"] = message.text
    else:
        await message.answer("❌ Ошибка индекса")
    await state.clear()
    await message.answer("Выберите действие:", reply_markup=get_lesson_edit_keyboard(week_type, day_name, idx))


@dp.message(AdminEdit.waiting_room)
async def save_room(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_ID: return
    if message.text == "/cancel":
        await state.clear();
        await message.answer("❌ Отменено");
        return
    ctx = admin_context.get(message.from_user.id, {})
    week_type = ctx.get("week_type");
    day_name = ctx.get("day_name");
    day_en = ctx.get("day_en");
    idx = ctx.get("idx")
    if not all([week_type, day_en, idx is not None]):
        await message.answer("❌ Ошибка контекста");
        await state.clear();
        return
    today = get_local_date();
    target_date = None
    for i in range(7):
        check_date = today + timedelta(days=i)
        if check_date.strftime("%A") == day_en and get_week_type(check_date) == week_type:
            target_date = check_date;
            break
    if not target_date:
        await message.answer("❌ Не найдена дата");
        await state.clear();
        return
    if str(target_date) not in temporary_changes:
        base = schedule.get(week_type, {}).get(day_en, [])
        temporary_changes[str(target_date)] = [l.copy() for l in base]
    if idx < len(temporary_changes[str(target_date)]):
        temporary_changes[str(target_date)][idx]["room"] = message.text
        await message.answer(f"✅ Кабинет обновлён: <b>{message.text}</b>", parse_mode=ParseMode.HTML)
        admin_context[message.from_user.id]["lesson"]["room"] = message.text
    else:
        await message.answer("❌ Ошибка индекса")
    await state.clear()
    await message.answer("Выберите действие:", reply_markup=get_lesson_edit_keyboard(week_type, day_name, idx))


@dp.message(AdminEdit.waiting_teacher)
async def save_teacher(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_ID: return
    if message.text == "/cancel":
        await state.clear();
        await message.answer("❌ Отменено");
        return
    ctx = admin_context.get(message.from_user.id, {})
    week_type = ctx.get("week_type");
    day_name = ctx.get("day_name");
    day_en = ctx.get("day_en");
    idx = ctx.get("idx")
    if not all([week_type, day_en, idx is not None]):
        await message.answer("❌ Ошибка контекста");
        await state.clear();
        return
    today = get_local_date();
    target_date = None
    for i in range(7):
        check_date = today + timedelta(days=i)
        if check_date.strftime("%A") == day_en and get_week_type(check_date) == week_type:
            target_date = check_date;
            break
    if not target_date:
        await message.answer("❌ Не найдена дата");
        await state.clear();
        return
    if str(target_date) not in temporary_changes:
        base = schedule.get(week_type, {}).get(day_en, [])
        temporary_changes[str(target_date)] = [l.copy() for l in base]
    if idx < len(temporary_changes[str(target_date)]):
        temporary_changes[str(target_date)][idx]["teacher"] = message.text
        await message.answer(f"✅ Преподаватель обновлён: <b>{message.text}</b>", parse_mode=ParseMode.HTML)
        admin_context[message.from_user.id]["lesson"]["teacher"] = message.text
    else:
        await message.answer("❌ Ошибка индекса")
    await state.clear()
    await message.answer("Выберите действие:", reply_markup=get_lesson_edit_keyboard(week_type, day_name, idx))


@dp.message(AdminEdit.waiting_start_time)
async def save_time(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_ID: return
    if message.text == "/cancel":
        await state.clear();
        await message.answer("❌ Отменено");
        return
    match = re.match(r'(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})', message.text)
    if not match:
        await message.answer("❌ Неверный формат. Пример: 09:00-10:30");
        return
    start_h, start_m, end_h, end_m = map(int, match.groups())
    try:
        new_start = time(start_h, start_m);
        new_end = time(end_h, end_m)
    except:
        await message.answer("❌ Неверное время");
        return
    ctx = admin_context.get(message.from_user.id, {})
    week_type = ctx.get("week_type");
    day_name = ctx.get("day_name");
    day_en = ctx.get("day_en");
    idx = ctx.get("idx")
    if not all([week_type, day_en, idx is not None]):
        await message.answer("❌ Ошибка контекста");
        await state.clear();
        return
    today = get_local_date();
    target_date = None
    for i in range(7):
        check_date = today + timedelta(days=i)
        if check_date.strftime("%A") == day_en and get_week_type(check_date) == week_type:
            target_date = check_date;
            break
    if not target_date:
        await message.answer("❌ Не найдена дата");
        await state.clear();
        return
    if str(target_date) not in temporary_changes:
        base = schedule.get(week_type, {}).get(day_en, [])
        temporary_changes[str(target_date)] = [l.copy() for l in base]
    if idx < len(temporary_changes[str(target_date)]):
        temporary_changes[str(target_date)][idx]["start"] = new_start
        temporary_changes[str(target_date)][idx]["end"] = new_end
        await message.answer(f"✅ Время обновлено: <b>{new_start.strftime('%H:%M')}-{new_end.strftime('%H:%M')}</b>",
                             parse_mode=ParseMode.HTML)
        admin_context[message.from_user.id]["lesson"]["start"] = new_start
        admin_context[message.from_user.id]["lesson"]["end"] = new_end
    else:
        await message.answer("❌ Ошибка индекса")
    await state.clear()
    await message.answer("Выберите действие:", reply_markup=get_lesson_edit_keyboard(week_type, day_name, idx))


@dp.message(Command("cancel"))
async def cancel_edit(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Редактирование отменено")


# ======================
# 🗑️ УДАЛЕНИЕ
# ======================
@dp.callback_query(F.data.startswith("del_"))
async def admin_delete_lesson(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_ID:
        await callback.answer("❌ Доступ запрещён", show_alert=True);
        return
    parts = callback.data.split("_")
    if len(parts) < 4:
        await callback.answer("❌ Ошибка", show_alert=True);
        return
    week_type = parts[1];
    day_name = parts[2];
    idx = int(parts[3])
    day_en = DAY_RU_TO_EN.get(day_name, day_name)
    today = get_local_date();
    target_date = None
    for i in range(7):
        check_date = today + timedelta(days=i)
        if check_date.strftime("%A") == day_en and get_week_type(check_date) == week_type:
            target_date = check_date;
            break
    if not target_date:
        await callback.answer("❌ Не найдена дата", show_alert=True);
        return
    lessons = schedule.get(week_type, {}).get(day_en, [])
    if idx >= len(lessons):
        await callback.answer("❌ Ошибка", show_alert=True);
        return
    if str(target_date) not in temporary_changes:
        base = schedule.get(week_type, {}).get(day_en, [])
        temporary_changes[str(target_date)] = [l.copy() for l in base]
    if idx < len(temporary_changes[str(target_date)]):
        deleted = temporary_changes[str(target_date)].pop(idx)
        await callback.message.edit_text(
            f"🗑️ Удалено: {deleted['name']}\nИзменения сбросятся после окончания времени пары.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="nav_days")]]))
        await callback.answer()


# ======================
# ⏰ УВЕДОМЛЕНИЯ
# ======================
async def notifier():
    global notified_lessons
    while True:
        now = get_local_now()
        today = get_local_date()  # ✅ Было: date.today()
        lessons = get_schedule(today)
        for idx, lesson in enumerate(lessons):
            start_dt = datetime.combine(today, lesson["start"])
            diff = (start_dt - now).total_seconds()
            lesson_key = f"{today}_{idx}"
            if 0 < diff <= 300 and lesson_key not in notified_lessons:
                for user in subscribers:
                    try:
                        await bot.send_message(user,
                                               f"🔔 Через 5 мин: {lesson['name']}\n🚪 {lesson['room']}\n⏰ {lesson['start'].strftime('%H:%M')}")
                    except:
                        pass
                notified_lessons.add(lesson_key)
            elif diff < 0 and lesson_key in notified_lessons:
                notified_lessons.discard(lesson_key)
        await asyncio.sleep(60)


# ======================
# 🔄 АВТОСБРОС
# ======================
async def reset_changes():
    while True:
        now = get_local_now()
        today = get_local_date()  # ✅ Было: date.today()
        if now.hour == 0 and now.minute < 1:
            temporary_changes.clear();
            notified_lessons.clear()
        to_remove = []
        for date_str, lessons in list(temporary_changes.items()):
            try:
                change_date = date.fromisoformat(date_str)
                if change_date < today:
                    to_remove.append(date_str);
                    continue
                if change_date == today:
                    indices_to_remove = []
                    for idx, lesson in enumerate(lessons):
                        end_dt = datetime.combine(change_date, lesson["end"])
                        if now > end_dt: indices_to_remove.append(idx)
                    for idx in reversed(indices_to_remove):
                        if idx < len(temporary_changes[date_str]):
                            temporary_changes[date_str].pop(idx)
                    if not temporary_changes[date_str]:
                        to_remove.append(date_str)
            except Exception as e:
                to_remove.append(date_str)
        for key in to_remove:
            temporary_changes.pop(key, None)
        await asyncio.sleep(60)


# ======================
# ▶ ЗАПУСК
# ======================
async def main():
    global subscribers, SUBJECT_MAP
    subscribers = load_subscribers()
    SUBJECT_MAP = init_subject_map()
    asyncio.create_task(notifier())
    asyncio.create_task(reset_changes())
    await dp.start_polling(bot)


@dp.message(Command("time"))
async def debug_time(message: Message):
    if message.from_user.id not in ADMIN_ID:
        return

    server_now = datetime.now()
    bot_now = get_local_now()
    moscow_now = datetime.now() + timedelta(hours=3)  # Примерное МСК

    await message.answer(
        f"🖥 Время сервера: <code>{server_now.strftime('%H:%M:%S')}</code>\n"
        f"🤖 Время бота: <code>{bot_now.strftime('%H:%M:%S')}</code>\n"
        f"🇷🇺 Примерное МСК: <code>{moscow_now.strftime('%H:%M:%S')}</code>\n"
        f"⚙️ Текущий оффсет: <code>{TIMEZONE_OFFSET_HOURS}</code>",
        parse_mode=ParseMode.HTML
    )


@dp.message(Command("getid"))
async def get_thread_id(message: Message):
    # Проверка на админа (чтобы обычные юзеры не спамили)
    if message.from_user.id not in ADMIN_ID:
        return

    thread_id = message.message_thread_id if message.is_topic_message else "Нет (обычный чат)"
    chat_id = message.chat.id

    await message.answer(
        f"🆔 ID чата: <code>{chat_id}</code>\n"
        f"🧵 ID ветки: <code>{thread_id}</code>",
        parse_mode=ParseMode.HTML
    )
if __name__ == "__main__":

    asyncio.run(main())



