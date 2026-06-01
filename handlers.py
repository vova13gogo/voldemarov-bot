import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import markov
import settings
from keyboards import main_menu, settings_menu, confirm_reset, back_to_menu, back_to_settings

router = Router()

# ─── Тексты ───────────────────────────────────────────────────────────────────

def text_main_menu() -> str:
    status = "✅ активен" if settings.is_enabled() else "❌ отключён"
    return (
        "🤖 <b>Voldemarov Bot</b>\n\n"
        f"Статус: {status}\n"
        "Я учусь на сообщениях чата и иногда отвечаю сам.\n\n"
        "Выбери действие:"
    )

def text_stats() -> str:
    return (
        "📊 <b>Статистика</b>\n\n"
        f"📝 Пар слов в базе: <b>{markov.word_count()}</b>\n"
        f"📚 Обучено сообщений: <b>{markov.messages_trained()}</b>\n"
        f"🎯 Шанс ответа: <b>{settings.get_chance()}%</b>\n"
        f"💬 Ответы: <b>{'включены' if settings.is_enabled() else 'выключены'}</b>\n"
        f"📖 Обучение: <b>{'включено' if settings.is_learning() else 'выключено'}</b>"
    )

def text_help() -> str:
    return (
        "❓ <b>Помощь</b>\n\n"
        "Я — бот на основе цепей Маркова. Читаю сообщения в чате, "
        "учусь на них и иногда генерирую ответы.\n\n"
        "<b>Команды:</b>\n"
        "/start — главное меню\n"
        "/stats — статистика\n"
        "/settings — настройки\n"
        "/generate — сгенерировать фразу\n"
        "/setchance 25 — установить шанс ответа\n\n"
        "<b>Как это работает:</b>\n"
        "Бот запоминает пары слов и учится предсказывать следующее слово. "
        "Чем больше сообщений — тем лучше и связнее генерация.\n\n"
        "<b>Совет:</b> добавь бота в групповой чат — там он быстрее обучится."
    )

def text_settings() -> str:
    return (
        "⚙️ <b>Настройки</b>\n\n"
        f"🎯 Шанс ответа: <b>{settings.get_chance()}%</b>\n"
        f"💬 Ответы: <b>{'включены' if settings.is_enabled() else 'выключены'}</b>\n"
        f"📚 Обучение: <b>{'включено' if settings.is_learning() else 'выключено'}</b>"
    )

def generate_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔄 Ещё", callback_data="generate"),
        InlineKeyboardButton(text="◀️ В меню", callback_data="main_menu"),
    ]])

# ─── Команды ──────────────────────────────────────────────────────────────────

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(text_main_menu(), reply_markup=main_menu(), parse_mode="HTML")

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(text_help(), reply_markup=back_to_menu(), parse_mode="HTML")

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    await message.answer(text_stats(), reply_markup=back_to_menu(), parse_mode="HTML")

@router.message(Command("settings"))
async def cmd_settings(message: Message):
    await message.answer(
        text_settings(),
        reply_markup=settings_menu(settings.get_chance(), settings.is_enabled(), settings.is_learning()),
        parse_mode="HTML"
    )

@router.message(Command("generate"))
async def cmd_generate(message: Message):
    response = markov.generate()
    if response:
        await message.answer(f"🎲 <i>{response}</i>", parse_mode="HTML", reply_markup=generate_keyboard())
    else:
        await message.answer(
            "📚 Базы пока недостаточно для генерации.\n"
            "Напиши несколько сообщений чтобы я обучился.",
            reply_markup=back_to_menu()
        )

@router.message(Command("setchance"))
async def cmd_setchance(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer(
            "⚠️ Укажи значение от 0 до 100.\nПример: <code>/setchance 25</code>",
            parse_mode="HTML"
        )
        return
    if not args[1].isdigit():
        await message.answer("⚠️ Значение должно быть числом от 0 до 100.")
        return
    value = int(args[1])
    if not 0 <= value <= 100:
        await message.answer("⚠️ Значение должно быть от 0 до 100.")
        return
    await settings.set_chance(value)
    await message.answer(
        f"✅ Шанс ответа установлен: <b>{value}%</b>",
        reply_markup=back_to_settings(),
        parse_mode="HTML"
    )

# ─── Обычные сообщения ────────────────────────────────────────────────────────

@router.message(F.text)
async def handle_message(message: Message):
    text = message.text.strip()
    if text.startswith("/"):
        return

    if settings.is_learning():
        trained = markov.train(text)
        # Учимся и на тексте на который отвечают
        if message.reply_to_message and message.reply_to_message.text:
            markov.train(message.reply_to_message.text)
        if trained and markov.messages_trained() % 30 == 0:
            await markov.flush()

    if settings.is_enabled() and random.randint(1, 100) <= settings.get_chance():
        # Передаём текст как seed для контекстной генерации
        response = markov.generate(seed=text)
        if response:
            await message.reply(f"<i>{response}</i>", parse_mode="HTML")

# ─── Инлайн кнопки ────────────────────────────────────────────────────────────

@router.callback_query(F.data == "main_menu")
async def cb_main_menu(call: CallbackQuery):
    await call.answer()
    try:
        await call.message.edit_text(text_main_menu(), reply_markup=main_menu(), parse_mode="HTML")
    except Exception:
        pass

@router.callback_query(F.data == "stats")
async def cb_stats(call: CallbackQuery):
    await call.answer()
    try:
        await call.message.edit_text(text_stats(), reply_markup=back_to_menu(), parse_mode="HTML")
    except Exception:
        pass

@router.callback_query(F.data == "help")
async def cb_help(call: CallbackQuery):
    await call.answer()
    try:
        await call.message.edit_text(text_help(), reply_markup=back_to_menu(), parse_mode="HTML")
    except Exception:
        pass

@router.callback_query(F.data == "settings")
async def cb_settings(call: CallbackQuery):
    await call.answer()
    try:
        await call.message.edit_text(
            text_settings(),
            reply_markup=settings_menu(settings.get_chance(), settings.is_enabled(), settings.is_learning()),
            parse_mode="HTML"
        )
    except Exception:
        pass

@router.callback_query(F.data == "generate")
async def cb_generate(call: CallbackQuery):
    await call.answer()
    response = markov.generate()
    try:
        if response:
            await call.message.edit_text(
                f"🎲 <i>{response}</i>\n\n<i>Нажми ещё раз чтобы сгенерировать снова</i>",
                reply_markup=generate_keyboard(),
                parse_mode="HTML"
            )
        else:
            await call.message.edit_text(
                "📚 Базы пока недостаточно для генерации.\nНапиши несколько сообщений чтобы я обучился.",
                reply_markup=back_to_menu()
            )
    except Exception:
        pass

@router.callback_query(F.data == "toggle_replies")
async def cb_toggle_replies(call: CallbackQuery):
    await call.answer()
    await settings.set_enabled(not settings.is_enabled())
    try:
        await call.message.edit_text(
            text_settings(),
            reply_markup=settings_menu(settings.get_chance(), settings.is_enabled(), settings.is_learning()),
            parse_mode="HTML"
        )
    except Exception:
        pass

@router.callback_query(F.data == "toggle_learning")
async def cb_toggle_learning(call: CallbackQuery):
    await call.answer()
    await settings.set_learning(not settings.is_learning())
    try:
        await call.message.edit_text(
            text_settings(),
            reply_markup=settings_menu(settings.get_chance(), settings.is_enabled(), settings.is_learning()),
            parse_mode="HTML"
        )
    except Exception:
        pass

@router.callback_query(F.data == "chance_up")
async def cb_chance_up(call: CallbackQuery):
    await call.answer()
    await settings.set_chance(min(100, settings.get_chance() + 5))
    try:
        await call.message.edit_text(
            text_settings(),
            reply_markup=settings_menu(settings.get_chance(), settings.is_enabled(), settings.is_learning()),
            parse_mode="HTML"
        )
    except Exception:
        pass

@router.callback_query(F.data == "chance_down")
async def cb_chance_down(call: CallbackQuery):
    await call.answer()
    await settings.set_chance(max(0, settings.get_chance() - 5))
    try:
        await call.message.edit_text(
            text_settings(),
            reply_markup=settings_menu(settings.get_chance(), settings.is_enabled(), settings.is_learning()),
            parse_mode="HTML"
        )
    except Exception:
        pass

@router.callback_query(F.data == "chance_info")
async def cb_chance_info(call: CallbackQuery):
    await call.answer(
        f"Текущий шанс: {settings.get_chance()}%\n"
        "Используй ➕ и ➖ для изменения (шаг 5%)\n"
        "Или команду /setchance 25",
        show_alert=True
    )

@router.callback_query(F.data == "reset_confirm")
async def cb_reset_confirm(call: CallbackQuery):
    await call.answer()
    try:
        await call.message.edit_text(
            "⚠️ <b>Сброс базы</b>\n\n"
            "Это удалит все накопленные данные и бот начнёт обучение заново.\n"
            "Действие необратимо. Продолжить?",
            reply_markup=confirm_reset(),
            parse_mode="HTML"
        )
    except Exception:
        pass

@router.callback_query(F.data == "reset_yes")
async def cb_reset_yes(call: CallbackQuery):
    await call.answer()
    await markov.reset()
    try:
        await call.message.edit_text(
            "✅ База сброшена. Бот начнёт обучение заново.",
            reply_markup=back_to_menu()
        )
    except Exception:
        pass
