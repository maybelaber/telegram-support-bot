from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from bot.keyboards.keyboards import get_cancel_keyboard, get_main_menu_keyboard

router = Router()


class BroadcastStates(StatesGroup):
    waiting_for_message = State()


def is_admin(user_id: int, admin_ids: list[int]) -> bool:
    """Check if user is an admin"""
    return user_id in admin_ids


@router.message(Command("admin"))
async def cmd_admin(message: Message, admin_ids: list[int]):
    """Show admin panel"""
    if not is_admin(message.from_user.id, admin_ids):
        await message.answer("❌ You don't have permission to access the admin panel.")
        return
    
    admin_text = (
        "🔐 <b>Admin Panel</b>\n\n"
        "<b>Available Commands:</b>\n"
        "/broadcast - Send a message to all users\n"
        "/stats - View bot statistics\n"
    )
    await message.answer(admin_text, parse_mode="HTML")


@router.message(Command("broadcast"))
async def start_broadcast(message: Message, state: FSMContext, admin_ids: list[int]):
    """Start broadcast message process"""
    if not is_admin(message.from_user.id, admin_ids):
        await message.answer("❌ You don't have permission to broadcast messages.")
        return
    
    await state.set_state(BroadcastStates.waiting_for_message)
    await message.answer(
        "📢 <b>Broadcast Message</b>\n\n"
        "Send me the message you want to broadcast to all users.\n\n"
        "You can send:\n"
        "• Text messages\n"
        "• Photos with captions\n"
        "• Videos with captions\n\n"
        "Use /cancel to cancel the broadcast.",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )


@router.message(BroadcastStates.waiting_for_message, Command("cancel"))
@router.message(BroadcastStates.waiting_for_message, F.text == "❌ Cancel")
async def cancel_broadcast(message: Message, state: FSMContext):
    """Cancel broadcast"""
    await state.clear()
    await message.answer(
        "❌ Broadcast cancelled.",
        reply_markup=get_main_menu_keyboard()
    )


@router.message(BroadcastStates.waiting_for_message)
async def process_broadcast(message: Message, state: FSMContext, session: AsyncSession, admin_ids: list[int]):
    """Process and send broadcast message"""
    if not is_admin(message.from_user.id, admin_ids):
        await state.clear()
        await message.answer("❌ You don't have permission to broadcast messages.")
        return
    
    # Get all active users
    result = await session.execute(
        select(User).where(User.is_active == True)
    )
    users = result.scalars().all()
    
    if not users:
        await state.clear()
        await message.answer("❌ No active users found.")
        return
    
    # Send confirmation
    await message.answer(
        f"📢 Broadcasting to {len(users)} users...\n"
        "Please wait..."
    )
    
    # Broadcast message
    success_count = 0
    fail_count = 0
    
    for user in users:
        try:
            if message.text:
                await message.bot.send_message(
                    chat_id=user.telegram_id,
                    text=f"📢 <b>Broadcast Message</b>\n\n{message.text}",
                    parse_mode="HTML"
                )
            elif message.photo:
                await message.bot.send_photo(
                    chat_id=user.telegram_id,
                    photo=message.photo[-1].file_id,
                    caption=f"📢 <b>Broadcast Message</b>\n\n{message.caption or ''}",
                    parse_mode="HTML"
                )
            elif message.video:
                await message.bot.send_video(
                    chat_id=user.telegram_id,
                    video=message.video.file_id,
                    caption=f"📢 <b>Broadcast Message</b>\n\n{message.caption or ''}",
                    parse_mode="HTML"
                )
            success_count += 1
        except Exception as e:
            fail_count += 1
            # If user blocked the bot, deactivate them
            if "blocked" in str(e).lower():
                user.is_active = False
    
    await session.commit()
    await state.clear()
    
    # Send report
    report = (
        "✅ <b>Broadcast completed!</b>\n\n"
        f"📊 <b>Statistics:</b>\n"
        f"✅ Sent successfully: {success_count}\n"
        f"❌ Failed: {fail_count}\n"
        f"👥 Total users: {len(users)}"
    )
    await message.answer(report, parse_mode="HTML", reply_markup=get_main_menu_keyboard())


@router.message(Command("stats"))
async def cmd_stats(message: Message, session: AsyncSession, admin_ids: list[int]):
    """Show bot statistics"""
    if not is_admin(message.from_user.id, admin_ids):
        await message.answer("❌ You don't have permission to view statistics.")
        return
    
    # Get user count
    result = await session.execute(select(User))
    total_users = len(result.scalars().all())
    
    # Get active user count
    result = await session.execute(select(User).where(User.is_active == True))
    active_users = len(result.scalars().all())
    
    # Get ticket count
    from database.models import SupportTicket
    result = await session.execute(select(SupportTicket))
    total_tickets = len(result.scalars().all())
    
    stats_text = (
        "📊 <b>Bot Statistics</b>\n\n"
        f"👥 Total users: {total_users}\n"
        f"✅ Active users: {active_users}\n"
        f"📝 Total tickets: {total_tickets}\n"
    )
    await message.answer(stats_text, parse_mode="HTML")
