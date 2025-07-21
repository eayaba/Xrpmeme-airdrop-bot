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

# Bot Token (Replace with your actual token)
TELEGRAM_TOKEN = "7916344131:AAGfmZstsfIeqLGXVjqtEOYm_lftHHhwTWc"

# App Configuration
TELEGRAM_GROUP_LINK = "https://t.me/+WbrfygqR3JoyMWM0"
TWITTER_LINK = "https://x.com/captxrpm"
PLAY_STORE_LINK = "https://play.google.com/store/apps/details?id=com.xrpm"
APP_STORE_LINK = "https://apps.apple.com/us/app/xrpm/id6739287517"
REFERRAL_PROGRAM_LINK = "https://myapp.xrpmemes.net?address=r48gmURH893SZXen7kYvy8NG4jeVncG1r7&rac=544783484"

# In-memory storage
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
        referral_codes[user_data[user_id]['referral_code']] = user_id
    
    # Create buttons - Added social media buttons here
    keyboard = [
        [InlineKeyboardButton("📢 Join Telegram Group", url=TELEGRAM_GROUP_LINK)],
        [InlineKeyboardButton("🐦 Follow on Twitter/X", url=TWITTER_LINK)],
        [
            InlineKeyboardButton("#3 📱 Android", url=PLAY_STORE_LINK),
            InlineKeyboardButton("#3 🍏 iPhone", url=APP_STORE_LINK)
        ],
        [InlineKeyboardButton("🔗 Activate Referral Program", url=REFERRAL_PROGRAM_LINK)],
        [InlineKeyboardButton("✅ Verify All Tasks", callback_data='verify')]
    ]
    
    await update.message.reply_text(
        "🌟 *XPMMEMEs Airdrop Bot* 🌟\n\n"
        "*Do this simple steps to be rewarded!*\n\n"
        "*Complete these steps:*\n"
        "1️⃣ Join our Telegram group\n"
        "2️⃣ Follow us on Twitter/X\n"
        "3️⃣ Download XRPM app and Send a Mininmum of 1 XRP to activate your new wallet\n"
        "4️⃣ Add XRPM to your token list/trustline\n"
        "5️⃣ Activate Referral Program\n"
        "6️⃣ Refer friends for reward by sharing your referral link\n\n"
        "*Reward tier*\n"
        "1 Friend   = 1 XRP + 100 XRPM\n"
        "2 Friends = 2 XRP + 200 XRPM\n"
        "3 Friends = 3 XRP + 300 XRPM\n\n"
        f"Your referral code: `{user_data[user_id]['referral_code']}`",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'verify':
        await query.edit_message_text(
            text="Please contact @captxrpm to verify your completed tasks.\n\n"
                 "Send them a message with:\n"
                 "1. Screenshot of your Telegram group membership\n"
                 "2. Screenshot of your Twitter follow\n"
                 "3. Screenshot of your app download\n"
                 "4. Your XRP wallet address\n"
                 "5. Your referral code\n\n"
                 "Once verified, you'll receive your rewards!",
            parse_mode=ParseMode.MARKDOWN
        )

async def handle_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    wallet_address = update.message.text.strip()
    
    if wallet_address.startswith('r') and len(wallet_address) >= 25:
        user_data[user_id]['wallet_address'] = wallet_address
        reward = 10 + min(user_data[user_id]['referrals'], 3)
        xrpm_reward = min(user_data[user_id]['referrals'], 3) * 100
        
        await update.message.reply_text(
            f"🎉 *Success!* �\n\n"
            f"*{reward} XRP* and *{xrpm_reward} XRPM* will be sent to:\n"
            f"`{wallet_address}`\n\n"
            f"Breakdown:\n"
            f"- Base reward: 10 XRP\n"
            f"- Referral bonus: {min(user_data[user_id]['referrals'], 3)} XRP\n"
            f"- XRPM referral bonus: {xrpm_reward} XRPM",
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
        application.add_handler(CallbackQueryHandler(handle_callback_query))
        
        logger.info("Bot is running...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")

if __name__ == '__main__':
    main()
