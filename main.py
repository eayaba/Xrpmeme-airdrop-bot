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

# Configuration
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_GROUP_ID = -1001234567890  # Your group ID
ADMIN_ID = 123456789  # Your Telegram user ID
TWITTER_USERNAME = "captxrpm"
PLAY_STORE_LINK = "https://play.google.com/store/apps/details?id=com.xrpm"
APP_STORE_LINK = "https://apps.apple.com/us/app/xrpm/id6739287517"

# Database simulation
user_db = {}
referral_codes = {}

def generate_referral_code():
    while True:
        code = 'XRPM-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if code not in referral_codes:
            return code

async def notify_referrer(referrer_id, referred_name):
    try:
        user_data = user_db[referrer_id]
        reward = min(user_data['referrals'], 3)  # Max 3 XRP
        
        await application.bot.send_message(
            chat_id=referrer_id,
            text=f"🎉 New referral! {referred_name} joined!\n"
                 f"Total referrals: {user_data['referrals']}/3\n"
                 f"Your bonus: {reward} XRP\n\n"
                 f"Share your code: `{user_data['referral_code']}`",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Failed to notify referrer: {str(e)}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id
    
    # Initialize new user
    if user_id not in user_db:
        referral_code = context.args[0] if context.args else None
        if referral_code and referral_code in referral_codes:
            referrer_id = referral_codes[referral_code]
            user_db[referrer_id]['referrals'] = min(user_db[referrer_id]['referrals'] + 1, 3)
            await notify_referrer(referrer_id, user.full_name)
        
        user_db[user_id] = {
            'name': user.full_name,
            'username': user.username,
            'steps': {
                'joined_group': False,
                'followed_twitter': False,
                'downloaded_app': False,
                'has_xrp': False
            },
            'referrals': 0,
            'referral_code': generate_referral_code(),
            'wallet_address': None,
            'joined_at': datetime.now(pytz.utc)
        }
        referral_codes[user_db[user_id]['referral_code']] = user_id
    
    user_data = user_db[user_id]
    
    # Create task buttons
    keyboard = [
        [InlineKeyboardButton("1️⃣ Join Telegram Group", url=f"https://t.me/+WbrfygqR3JoyMWM0")],
        [InlineKeyboardButton("2️⃣ Follow on Twitter", url=f"https://x.com/{TWITTER_USERNAME}")],
        [
            InlineKeyboardButton("📱 Android Download", url=PLAY_STORE_LINK),
            InlineKeyboardButton("🍏 iOS Download", url=APP_STORE_LINK)
        ],
        [InlineKeyboardButton("4️⃣ Verify XRP Balance", callback_data='verify_xrp')],
        [InlineKeyboardButton("5️⃣ Refer Friends", callback_data='referral_info')],
        [InlineKeyboardButton("✅ Verify All Tasks", callback_data='verify_all')]
    ]
    
    message = (
        "🚀 *XPM MEME Airdrop* 🚀\n\n"
        "*Complete these steps:*\n"
        f"1️⃣ Join Group {'✅' if user_data['steps']['joined_group'] else '❌'}\n"
        f"2️⃣ Follow Twitter {'✅' if user_data['steps']['followed_twitter'] else '❌'}\n"
        f"3️⃣ Download App {'✅' if user_data['steps']['downloaded_app'] else '❌'}\n"
        f"4️⃣ Own 1 XRP {'✅' if user_data['steps']['has_xrp'] else '❌'}\n"
        f"5️⃣ Refer 3 Friends ({user_data['referrals']}/3) {'✅' if user_data['referrals'] >= 3 else '❌'}\n\n"
        "*Referral Rewards:*\n"
        "1 friend = 1 XRP\n"
        "2 friends = 2 XRP\n"
        "3 friends = 3 XRP\n\n"
        f"Your code: `{user_data['referral_code']}`"
    )
    
    await update.message.reply_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )

async def verify_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(TELEGRAM_GROUP_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            user_db[user_id]['steps']['joined_group'] = True
            await update.callback_query.answer("✅ Group membership verified!")
        else:
            await update.callback_query.answer("❌ Please join the group first")
    except Exception as e:
        logger.error(f"Group check error: {str(e)}")
        await update.callback_query.answer("Verification failed, try again")

async def verify_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_db[user_id]['steps']['downloaded_app'] = True
    await update.callback_query.answer("✅ App download verified!")
    await start(update, context)

async def referral_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = user_db[user_id]
    
    keyboard = [
        [InlineKeyboardButton("📤 Share My Code", 
         url=f"https://t.me/share/url?url=Join%20XPM%20Airdrop&text=Use%20my%20code%20{user_data['referral_code']}%20to%20get%20bonus%20XRP!")],
        [InlineKeyboardButton("🔙 Back to Tasks", callback_data='back_to_start')]
    ]
    
    await update.callback_query.edit_message_text(
        f"*Your Referral Program*\n\n"
        f"🔢 Your code: `{user_data['referral_code']}`\n"
        f"👥 Referrals: {user_data['referrals']}/3\n"
        f"💰 Current bonus: {min(user_data['referrals'], 3)} XRP\n\n"
        "*How it works:*\n"
        "1. Share your code with friends\n"
        "2. They must use it when starting the bot\n"
        "3. You get 1 XRP per referral (max 3 XRP)",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    wallet = update.message.text.strip()
    
    if wallet.startswith('r') and len(wallet) >= 25:
        user_db[user_id]['wallet_address'] = wallet
        base_reward = 10
        referral_bonus = min(user_db[user_id]['referrals'], 3)
        total = base_reward + referral_bonus
        
        await update.message.reply_text(
            f"🎊 *Airdrop Registered!* 🎊\n\n"
            f"🔹 Base reward: 10 XRP\n"
            f"🔹 Referral bonus: {referral_bonus} XRP\n"
            f"💎 *Total: {total} XRP*\n\n"
            f"Will be sent to:\n`{wallet}`\n\n"
            "Thank you for participating!",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Admin notification
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"New airdrop claim:\n"
                 f"User: {user_db[user_id]['name']}\n"
                 f"Wallet: {wallet}\n"
                 f"Total: {total} XRP\n"
                 f"Code: {user_db[user_id]['referral_code']}"
        )
    else:
        await update.message.reply_text("Invalid XRP address. Must start with 'r' and be 25+ characters.")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(verify_group, pattern='verify_group'))
    application.add_handler(CallbackQueryHandler(verify_download, pattern='verify_download'))
    application.add_handler(CallbackQueryHandler(referral_info, pattern='referral_info'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet))
    
    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
