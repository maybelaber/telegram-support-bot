# Telegram Support Bot

A feature-rich Telegram bot built with Python, aiogram 3.x, PostgreSQL, and SQLAlchemy.

## Features

### User Features
- **User Registration**: `/start` command registers users in the database
- **Support Tickets**: Create support tickets using FSM
- **Help Command**: Get information about available commands

### Admin Features
- **Admin Panel**: `/admin` command shows admin options
- **Broadcast Messages**: `/broadcast` to send messages to all users
- **Statistics**: `/stats` to view bot usage statistics

## Quick Start

1. **Get your bot token** from [@BotFather](https://t.me/botfather)
2. **Get your Telegram ID** from [@userinfobot](https://t.me/userinfobot)
3. **Edit `.env`** file with your token and ID
4. **Run:**
   ```bash
   docker-compose up -d
   ```
5. **Check logs:**
   ```bash
   docker-compose logs -f bot
   ```

## Project Structure

```
telegram_bot/
├── bot/
│   ├── handlers/       # Command handlers
│   ├── keyboards/      # Reply keyboards
│   ├── middlewares/    # Database middleware
│   └── states/         # FSM states
├── database/           # Database models
├── main.py            # Main application
├── config.py          # Configuration
└── docker-compose.yml # Docker setup
```

## Commands

### User Commands
- `/start` - Register and start using the bot
- `/help` - Show help information
- `/ticket` - Create a new support ticket

### Admin Commands
- `/admin` - Show admin panel
- `/broadcast` - Broadcast a message to all users
- `/stats` - View bot statistics

## Technology Stack

- Python 3.11+
- aiogram 3.x
- PostgreSQL
- SQLAlchemy 2.0
- Docker & Docker Compose

## License

This project is provided as-is for educational purposes.
