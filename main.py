import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ContextTypes
)
import logging
from datetime import datetime
import pytz

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_TOKEN = "7916344131:AAGfmZstsfIeqLGXVjqtEOYm_lftHHhwTWc"  # Your token here
TELEGRAM_GROUP_LINK = "https://t.me/+WbrfygqR3JoyMWM0"
TWITTER_LINK = "https://x.com/captxrpm?s=11&t=RfuaoDpfagPLK3Y2aHujLw"
APP_DOWNLOAD_LINK = "https://xrpscan.com/tx/65F070CAFE3F1B07CDD7F8ABADD64211B02ED46F5E8C22982426E35FCB7321CB"

# In-memory storage
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user = update.effective_user
        user_id = user.id
        
        if user_id not in user_data:
            user_data[user_id] = {
                'completed_tasks': False,
                'wallet_address': None,
                'referral_code': f"XRPM{user_id}",
                'started_at': datetime.now(pytz.utc)
            }
        
        welcome_message = (
            "🌟 *Welcome to the XPM MEME Airdrop Bot!* 🌟\n\n"
            "Complete these simple tasks to qualify for 10 XRP:\n\n"
            "1. Join our Telegram: [Join Here]({})\n"
            "2. Follow us on Twitter (X): [Follow Here]({})\n"
            "3. Download XRPM App: [Download Here]({})\n"
            "4. Own at least 1 XRPM\n"
            "5. Refer friends (up to 3) - Your code: *{}*\n\n"
            "Click the button below when done!"
        ).format(
            TELEGRAM_GROUP_LINK,
            TWITTER_LINK,
            APP_DOWNLOAD_LINK,
            user_data[user_id]['referral_code']
        )
        
        keyboard = [
            [InlineKeyboardButton("✅ I've completed all tasks", callback_data='complete')],
            [InlineKeyboardButton("📲 Share Referral Link", callback_data='share')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=reply_markup,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Error in start handler: {str(e)}")
        if update and update.effective_message:
            await update.effective_message.reply_text("Sorry, something went wrong. Please try again.")

async def handle_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_id = update.effective_user.id
        wallet_address = update.message.text.strip()
        
        if wallet_address.startswith('r') and len(wallet_address) >= 25:
            user_data[user_id]['wallet_address'] = wallet_address
            
            if user_data[user_id]['completed_tasks']:
                await update.message.reply_text(
                    "🎉 *Congratulations!* 🎉\n\n"
                    "10 XRP will be sent to:\n"
                    f"`{wallet_address}`\n\n"
                    "Thanks for participating!",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("Please complete the tasks first!")
        else:
            await update.message.reply_text("Invalid XRP address. Must start with 'r' and be at least 25 characters long.")
    except Exception as e:
        logger.error(f"Error in wallet handler: {str(e)}")
        if update and update.effective_message:
            await update.effective_message.reply_text("Failed to process your wallet address. Please try again.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        query = update.callback_query
        await query.answer()
        
        if query.data == 'complete':
            user_data[query.from_user.id]['completed_tasks'] = True
            await query.edit_message_text("Tasks marked complete! Now send your XRP wallet address.")
        elif query.data == 'share':
            await query.edit_message_text(
                f"Share your referral code: {user_data[query.from_user.id]['referral_code']}\n\n"
                "Have your friends use this code when they join!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='back')]])
            )
        elif query.data == 'back':
            await start(update, context)
    except Exception as e:
        logger.error(f"Error in button handler: {str(e)}")
        if update and update.callback_query:
            await update.callback_query.message.reply_text("Sorry, something went wrong. Please try again.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a message to the user."""
    logger.error("Exception while handling update:", exc_info=context.error)
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "An unexpected error occurred. The developer has been notified. Please try again later."
        )

def main() -> None:
    try:
        logger.info("Starting XPM MEME Airdrop Bot...")
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Register handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet))
        application.add_handler(CallbackQueryHandler(button_handler))
        
        # Register error handler
        application.add_error_handler(error_handler)
        
        logger.info("Bot is now running...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.critical(f"Failed to start bot: {str(e)}")

if __name__ == '__main__':
    main()
