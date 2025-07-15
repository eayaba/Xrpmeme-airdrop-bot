import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler
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
TELEGRAM_TOKEN = os.getenv('7916344131:AAGfmZstsfIeqLGXVjqtEOYm_lftHHhwTWc')
TELEGRAM_GROUP_LINK = "https://t.me/+WbrfygqR3JoyMWM0"
TWITTER_LINK = "https://x.com/captxrpm?s=11&t=RfuaoDpfagPLK3Y2aHujLw"
APP_DOWNLOAD_LINK = "https://xrpscan.com/tx/65F070CAFE3F1B07CDD7F8ABADD64211B02ED46F5E8C22982426E35FCB7321CB"
ADMIN_USER_ID = None  # Set your admin user ID for notifications

# In-memory storage (replace with a database in production)
user_data = {}

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    user_id = user.id
    
    if user_id not in user_data:
        user_data[user_id] = {
            'completed_tasks': {
                'join_telegram': False,
                'follow_twitter': False,
                'download_app': False,
                'own_xrpm': False
            },
            'referrals': [],
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
        "4. Own at least 1 XRPM (we'll trust you on this)\n"
        "5. Refer friends (up to 3) - Your code: *{}*\n\n"
        "After completing all tasks, send your XRP wallet address to claim your reward!"
    ).format(
        TELEGRAM_GROUP_LINK,
        TWITTER_LINK,
        APP_DOWNLOAD_LINK,
        user_data[user_id]['referral_code']
    )
    
    # Create inline keyboard for task completion
    keyboard = [
        [InlineKeyboardButton("✅ I've completed all tasks", callback_data='completed_tasks')],
        [InlineKeyboardButton("📲 Share Referral Link", callback_data='share_referral')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_markdown(
        welcome_message,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

def handle_wallet_submission(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    wallet_address = update.message.text.strip()
    
    # Basic XRP address validation (very simple check)
    if len(wallet_address) >= 25 and wallet_address.startswith('r'):
        user_data[user_id]['wallet_address'] = wallet_address
        
        # Check if all tasks are marked complete
        if all(user_data[user_id]['completed_tasks'].values()):
            # Success message
            congrats_message = (
                "🎉 *Congratulations!* 🎉\n\n"
                "You've qualified for the XPM MEME airdrop!\n\n"
                "10 XRP will be sent to your wallet:\n"
                "`{}`\n\n"
                "Thanks for participating! Hope you didn't cheat the system 😉"
            ).format(wallet_address)
            
            update.message.reply_markdown(congrats_message)
            
            # Notify admin (optional)
            if ADMIN_USER_ID:
                context.bot.send_message(
                    chat_id=ADMIN_USER_ID,
                    text=f"New airdrop claim:\nUser: @{update.effective_user.username}\nWallet: {wallet_address}"
                )
        else:
            update.message.reply_text(
                "You haven't completed all tasks yet! Please complete them first."
            )
    else:
        update.message.reply_text(
            "That doesn't look like a valid XRP wallet address. "
            "Please send a valid address starting with 'r'."
        )

def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    
    if query.data == 'completed_tasks':
        # Mark all tasks as complete (since we're not verifying)
        for task in user_data[user_id]['completed_tasks']:
            user_data[user_id]['completed_tasks'][task] = True
        
        query.answer()
        query.edit_message_text(
            text="Awesome! Now please send me your XRP wallet address to claim your 10 XRP reward.",
            reply_markup=None
        )
    
    elif query.data == 'share_referral':
        referral_message = (
            "Join the XPM MEME airdrop and get 10 XRP!\n\n"
            "Use my referral code: *{}*\n\n"
            "Start here: @{}"
        ).format(
            user_data[user_id]['referral_code'],
            context.bot.username
        )
        
        query.answer()
        query.edit_message_text(
            text=referral_message,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data='back_to_main')
            ]]),
            parse_mode='Markdown'
        )
    
    elif query.data == 'back_to_main':
        # Re-send the start message
        start(update, context)
        query.answer()

def error_handler(update: Update, context: CallbackContext) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    if update and update.effective_message:
        update.effective_message.reply_text(
            "An error occurred. Please try again later."
        )

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(TELEGRAM_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("referral", start))  # Same as start
    
    # Handle wallet submissions
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command,
        handle_wallet_submission
    ))
    
    # Handle button callbacks
    dispatcher.add_handler(CallbackQueryHandler(button_handler))
    
    # Register error handler
    dispatcher.add_error_handler(error_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
