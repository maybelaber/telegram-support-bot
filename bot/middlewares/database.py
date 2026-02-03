from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class DatabaseMiddleware(BaseMiddleware):
    """Middleware to inject database session into handlers"""
    
    def __init__(self, session_maker):
        super().__init__()
        self.session_maker = session_maker
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with self.session_maker() as session:
            data['session'] = session
            return await handler(event, data)


class AdminMiddleware(BaseMiddleware):
    """Middleware to inject admin IDs into handlers"""
    
    def __init__(self, admin_ids: list[int]):
        super().__init__()
        self.admin_ids = admin_ids
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        data['admin_ids'] = self.admin_ids
        return await handler(event, data)
