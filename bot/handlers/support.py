from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import SupportTicket
from bot.states.support import SupportTicketStates
from bot.keyboards.keyboards import (
    get_cancel_keyboard,
    get_skip_keyboard,
    get_main_menu_keyboard
)

router = Router()


@router.message(Command("ticket"))
@router.message(F.text == "📝 Create Support Ticket")
async def start_ticket_creation(message: Message, state: FSMContext):
    """Start the support ticket creation process"""
    await state.set_state(SupportTicketStates.waiting_for_subject)
    await message.answer(
        "📝 <b>Create Support Ticket</b>\n\n"
        "Please enter the subject of your ticket:",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )


@router.message(SupportTicketStates.waiting_for_subject, F.text == "❌ Cancel")
@router.message(SupportTicketStates.waiting_for_description, F.text == "❌ Cancel")
@router.message(SupportTicketStates.waiting_for_contact, F.text == "❌ Cancel")
async def cancel_ticket_creation(message: Message, state: FSMContext):
    """Cancel ticket creation"""
    await state.clear()
    await message.answer(
        "❌ Ticket creation cancelled.",
        reply_markup=get_main_menu_keyboard()
    )


@router.message(SupportTicketStates.waiting_for_subject)
async def process_subject(message: Message, state: FSMContext):
    """Process the ticket subject"""
    if not message.text:
        await message.answer("Please enter a valid subject.")
        return
    
    await state.update_data(subject=message.text)
    await state.set_state(SupportTicketStates.waiting_for_description)
    await message.answer(
        "📄 Please provide a detailed description of your issue:",
        reply_markup=get_cancel_keyboard()
    )


@router.message(SupportTicketStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    """Process the ticket description"""
    if not message.text:
        await message.answer("Please enter a valid description.")
        return
    
    await state.update_data(description=message.text)
    await state.set_state(SupportTicketStates.waiting_for_contact)
    await message.answer(
        "📧 Please provide your contact information (email or phone):\n\n"
        "You can also skip this step if you prefer.",
        reply_markup=get_skip_keyboard()
    )


@router.message(SupportTicketStates.waiting_for_contact, F.text == "⏭ Skip")
async def skip_contact_info(message: Message, state: FSMContext, session: AsyncSession):
    """Skip contact information and save ticket"""
    data = await state.get_data()
    
    # Create ticket in database
    ticket = SupportTicket(
        user_id=message.from_user.id,
        subject=data['subject'],
        description=data['description'],
        contact_info=None
    )
    session.add(ticket)
    await session.commit()
    
    await state.clear()
    await message.answer(
        "✅ <b>Support ticket created successfully!</b>\n\n"
        f"📌 Ticket ID: #{ticket.id}\n"
        f"📝 Subject: {ticket.subject}\n\n"
        "Our support team will review your ticket and get back to you soon.",
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard()
    )


@router.message(SupportTicketStates.waiting_for_contact)
async def process_contact_info(message: Message, state: FSMContext, session: AsyncSession):
    """Process contact information and save ticket"""
    if not message.text:
        await message.answer("Please enter valid contact information or skip.")
        return
    
    data = await state.get_data()
    
    # Create ticket in database
    ticket = SupportTicket(
        user_id=message.from_user.id,
        subject=data['subject'],
        description=data['description'],
        contact_info=message.text
    )
    session.add(ticket)
    await session.commit()
    
    await state.clear()
    await message.answer(
        "✅ <b>Support ticket created successfully!</b>\n\n"
        f"📌 Ticket ID: #{ticket.id}\n"
        f"📝 Subject: {ticket.subject}\n"
        f"📧 Contact: {ticket.contact_info}\n\n"
        "Our support team will review your ticket and get back to you soon.",
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard()
    )
