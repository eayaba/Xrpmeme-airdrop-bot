import os
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ContextTypes
)
from telegram.constants import ParseMode
import logging
from datetime import datetime
import pytz

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- SECURITY WARNING ---
# Never commit this to version control or share publicly
# For production, use environment variables instead
TELEGRAM_TOKEN = "7916344131:AAGfmZstsfIeqLGXVjqtEOYm_lftHHhwTWc"  # REPLACE WITH YOUR ACTUAL TOKEN

# App Configuration
TELEGRAM_GROUP_LINK = "https://t.me/+WbrfygqR3JoyMWM0"
TWITTER_LINK = "https://x.com/captxrpm"
PLAY_STORE_LINK = "https://play.google.com/store/apps/details?id=com.xrpm"
APP_STORE_LINK = "https://apps.apple.com/us/app/xrpm/id6739287517"

# In-memory storage (replace with database in production)
user_data = {}
referral_codes = {}

def generate_referral_code():
    while True:
        code = 'XRPM-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if code not in referral_codes:
            return code

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id
    
    if user_id not in user_data:
        # Check for referral code
        if context.args and context.args[0] in referral_codes:
            referrer_id = referral_codes[context.args[0]]
            user_data[referrer_id]['referrals'] += 1
            await context.bot.send_message(
                chat_id=referrer_id,
                text=f"🎉 New referral! {user.full_name} used your code!\n"
                     f"Total referrals: {user_data[referrer_id]['referrals']}/3"
            )
        
        # Create new user
        user_data[user_id] = {
            'completed_tasks': {
                'join_telegram': False,
                'follow_twitter': False,
                'download_app': False,
                'own_xrp': False
            },
            'referrals': 0,
            'wallet_address': None,
            'referral_code': generate_referral_code()
        }
        referral_codes[user_data[user_id]['referral_code'] = user_id
    
    # Create buttons
    keyboard = [
        [
            InlineKeyboardButton("📱 Android", url=PLAY_STORE_LINK),
            InlineKeyboardButton("🍏 iPhone", url=APP_STORE_LINK)
        ],
        [InlineKeyboardButton("✅ Verify All Tasks", callback_data='verify')]
    ]
    
    await update.message.reply_text(
        "🌟 *XPM MEME Airdrop Bot* 🌟\n\n"
        "*Complete these steps:*\n"
        "1️⃣ Join Telegram Group\n"
        "2️⃣ Follow on Twitter\n"
        "3️⃣ Download XRPM App\n"
        "4️⃣ Own 1+ XRP\n"
        "5️⃣ Refer Friends (1 XRP per referral, max 3 XRP)\n\n"
        f"Your code: `{user_data[user_id]['referral_code']}`",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    wallet_address = update.message.text.strip()
    
    if wallet_address.startswith('r') and len(wallet_address) >= 25:
        user_data[user_id]['wallet_address'] = wallet_address
        reward = 10 + min(user_data[user_id]['referrals'], 3)
        
        await update.message.reply_text(
            f"🎉 *Success!* 🎉\n\n"
            f"*{reward} XRP* will be sent to:\n"
            f"`{wallet_address}`\n\n"
            f"Breakdown:\n"
            f"- Base reward: 10 XRP\n"
            f"- Referral bonus: {min(user_data[user_id]['referrals'], 3)} XRP",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text("Invalid XRP address. Must start with 'r' and be 25+ characters.")

def main() -> None:
    try:
        logger.info("Starting bot...")
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet))
        
        logger.info("Bot is running...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")

if __name__ == '__main__':
    main()
