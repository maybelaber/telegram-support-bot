from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Main menu keyboard"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📝 Create Support Ticket"),
        KeyboardButton(text="ℹ️ Help")
    )
    return builder.as_markup(resize_keyboard=True)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Cancel keyboard"""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="❌ Cancel"))
    return builder.as_markup(resize_keyboard=True)


def get_skip_keyboard() -> ReplyKeyboardMarkup:
    """Skip keyboard for optional fields"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="⏭ Skip"),
        KeyboardButton(text="❌ Cancel")
    )
    return builder.as_markup(resize_keyboard=True)


# Remove keyboard
remove_keyboard = ReplyKeyboardRemove()
