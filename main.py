import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import load_config
from database import Database
from bot.handlers import basic, support, admin
from bot.middlewares.database import DatabaseMiddleware, AdminMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main function to start the bot"""
    # Load configuration
    config = load_config()
    logger.info("Configuration loaded")
    
    # Initialize database
    db = Database(config.db.url)
    
    # Wait for database to be ready
    max_retries = 5
    retry_delay = 5
    for attempt in range(max_retries):
        try:
            await db.create_tables()
            logger.info("Database tables created")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database connection failed (attempt {attempt + 1}/{max_retries}): {e}")
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Failed to connect to database after {max_retries} attempts")
                raise
    
    # Initialize bot and dispatcher
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Initialize storage for FSM
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Register middlewares
    dp.message.middleware(DatabaseMiddleware(db.session_maker))
    dp.message.middleware(AdminMiddleware(config.bot.admin_ids))
    
    # Register routers
    dp.include_router(basic.router)
    dp.include_router(support.router)
    dp.include_router(admin.router)
    
    # Start bot
    logger.info("Starting bot...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot stopped due to error: {e}")
