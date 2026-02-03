from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from bot.keyboards.keyboards import get_main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    """Handle /start command and register user"""
    user = message.from_user
    
    # Check if user already exists
    result = await session.execute(
        select(User).where(User.telegram_id == user.id)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        await message.answer(
            f"Welcome back, {user.first_name}! 👋\n\n"
            "I'm here to help you with support tickets.",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        # Create new user
        new_user = User(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        session.add(new_user)
        await session.commit()
        
        await message.answer(
            f"Hello, {user.first_name}! 👋\n\n"
            "Welcome to the Support Bot!\n"
            "You've been successfully registered.\n\n"
            "Use the menu below to create a support ticket or get help.",
            reply_markup=get_main_menu_keyboard()
        )


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Help")
async def cmd_help(message: Message):
    """Handle /help command"""
    help_text = (
        "🤖 <b>Support Bot Help</b>\n\n"
        "<b>Available Commands:</b>\n"
        "/start - Register and start the bot\n"
        "/help - Show this help message\n"
        "/ticket - Create a new support ticket\n\n"
        "<b>Features:</b>\n"
        "📝 Create support tickets\n"
        "💬 Provide detailed descriptions\n"
        "📧 Add your contact information\n\n"
        "Use the menu buttons for easy navigation!"
    )
    await message.answer(help_text, parse_mode="HTML", reply_markup=get_main_menu_keyboard())
