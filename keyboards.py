from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand

def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings"),
        ],
        [
            InlineKeyboardButton(text="🎲 Сгенерировать", callback_data="generate"),
            InlineKeyboardButton(text="❓ Помощь", callback_data="help"),
        ],
    ])

def settings_menu(chance: int, enabled: bool, learning: bool) -> InlineKeyboardMarkup:
    status = "✅ Вкл" if enabled else "❌ Выкл"
    learn_status = "✅ Вкл" if learning else "❌ Выкл"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💬 Ответы: {status}", callback_data="toggle_replies")],
        [InlineKeyboardButton(text=f"📚 Обучение: {learn_status}", callback_data="toggle_learning")],
        [
            InlineKeyboardButton(text="➖", callback_data="chance_down"),
            InlineKeyboardButton(text=f"🎯 Шанс: {chance}%", callback_data="chance_info"),
            InlineKeyboardButton(text="➕", callback_data="chance_up"),
        ],
        [InlineKeyboardButton(text="🗑 Сбросить базу", callback_data="reset_confirm")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")],
    ])

def confirm_reset() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, сбросить", callback_data="reset_yes"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="settings"),
        ]
    ])

def back_to_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ В меню", callback_data="main_menu")]
    ])

def back_to_settings() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ К настройкам", callback_data="settings")]
    ])

BOT_COMMANDS = [
    BotCommand(command="start", description="Главное меню"),
    BotCommand(command="help", description="Помощь"),
    BotCommand(command="stats", description="Статистика"),
    BotCommand(command="settings", description="Настройки"),
    BotCommand(command="generate", description="Сгенерировать фразу"),
    BotCommand(command="setchance", description="Установить шанс ответа (0-100)"),
]
