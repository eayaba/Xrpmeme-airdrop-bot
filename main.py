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
TELEGRAM_TOKEN = "7916344131:AAGfmZstsfIeqLGXVjqtEOYm_lftHHhwTWc"
TELEGRAM_GROUP_LINK = "https://t.me/+WbrfygqR3JoyMWM0"
TWITTER_LINK = "https://x.com/captxrpm?s=11&t=RfuaoDpfagPLK3Y2aHujLw"
PLAY_STORE_LINK = "https://play.google.com/store/apps/details?id=com.xrpm"
APP_STORE_LINK = "https://apps.apple.com/us/app/xrpm/id6739287517"

# In-memory storage (replace with database in production)
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user = update.effective_user
        user_id = user.id
        
        if user_id not in user_data:
            user_data[user_id] = {
                'steps_completed': {
                    'join_telegram': False,
                    'follow_twitter': False,
                    'download_app': False,
                    'own_xrp': False
                },
                'referrals': 0,
                'wallet_address': None,
                'referral_code': f"XRPM{user_id}",
                'started_at': datetime.now(pytz.utc)
            }
        
        # Step-by-step task buttons
        keyboard = [
            [InlineKeyboardButton("1️⃣ Join Telegram Group", url=TELEGRAM_GROUP_LINK)],
            [InlineKeyboardButton("2️⃣ Follow on X (Twitter)", url=TWITTER_LINK)],
            [InlineKeyboardButton("3️⃣ Download XRPM App", callback_data='download_app')],
            [InlineKeyboardButton("4️⃣ I own 1 XRP in my wallet", callback_data='own_xrp')],
            [InlineKeyboardButton("5️⃣ Refer Friends (0/3)", callback_data='referral_info')],
            [InlineKeyboardButton("✅ Verify Completion", callback_data='verify_tasks')]
        ]
        
        welcome_message = (
            "🌟 *XPM MEME Airdrop Bot* 🌟\n\n"
            "*Complete these steps to qualify:*\n\n"
            "1️⃣ Join our Telegram group\n"
            "2️⃣ Follow us on X (Twitter)\n"
            "3️⃣ Download XRPM app\n"
            "4️⃣ Own at least 1 XRP in your wallet\n"
            "5️⃣ Refer friends to earn extra XRP\n\n"
            "*Referral Rewards:*\n"
            "1 referral = 1 XRP\n"
            "2 referrals = 2 XRP\n"
            "3 referrals = 3 XRP\n\n"
            "Your referral code: `{}`"
        ).format(user_data[user_id]['referral_code'])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Error in start handler: {str(e)}")
        if update and update.effective_message:
            await update.effective_message.reply_text("Sorry, something went wrong. Please try again.")

async def download_app_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        query = update.callback_query
        await query.answer()
        
        keyboard = [
            [InlineKeyboardButton("Android (Play Store)", url=PLAY_STORE_LINK)],
            [InlineKeyboardButton("iOS (App Store)", url=APP_STORE_LINK)],
            [InlineKeyboardButton("🔙 Back", callback_data='back_to_main')]
        ]
        
        await query.edit_message_text(
            "📲 *Download XRPM App*\n\n"
            "Choose your platform:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error in download app handler: {str(e)}")

async def referral_info_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        
        keyboard = [
            [InlineKeyboardButton("📤 Share Referral Link", callback_data='share_referral')],
            [InlineKeyboardButton("🔙 Back", callback_data='back_to_main')]
        ]
        
        await query.edit_message_text(
            f"*Referral Program*\n\n"
            f"Your referrals: {user_data[user_id]['referrals']}/3\n"
            f"Your code: `{user_data[user_id]['referral_code']}`\n\n"
            "*Rewards:*\n"
            "1 referral = 1 XRP\n"
            "2 referrals = 2 XRP\n"
            "3 referrals = 3 XRP\n\n"
            "Share your code with friends!",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error in referral info handler: {str(e)}")

async def verify_tasks_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        
        if all(user_data[user_id]['steps_completed'].values()):
            await query.edit_message_text(
                "✅ *All tasks completed!*\n\n"
                "Now send me your XRP wallet address to claim your rewards.\n\n"
                f"Referral bonus: {user_data[user_id]['referrals']} XRP",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.edit_message_text(
                "❌ *Tasks Incomplete*\n\n"
                "Please complete all tasks before verification.",
                parse_mode=ParseMode.MARKDOWN
            )
    except Exception as e:
        logger.error(f"Error in verify tasks handler: {str(e)}")

async def handle_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_id = update.effective_user.id
        wallet_address = update.message.text.strip()
        
        if wallet_address.startswith('r') and len(wallet_address) >= 25:
            user_data[user_id]['wallet_address'] = wallet_address
            
            if all(user_data[user_id]['steps_completed'].values()):
                base_reward = 10
                referral_bonus = user_data[user_id]['referrals']
                total_reward = base_reward + referral_bonus
                
                await update.message.reply_text(
                    "🎉 *Congratulations!* 🎉\n\n"
                    f"*{total_reward} XRP* will be sent to:\n"
                    f"`{wallet_address}`\n\n"
                    f"Breakdown:\n"
                    f"- Base reward: 10 XRP\n"
                    f"- Referral bonus: {referral_bonus} XRP\n\n"
                    "Thanks for participating!",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text(
                    "Please complete all tasks before submitting your wallet address."
                )
        else:
            await update.message.reply_text(
                "Invalid XRP address. Must start with 'r' and be at least 25 characters long."
            )
    except Exception as e:
        logger.error(f"Error in wallet handler: {str(e)}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        query = update.callback_query
        await query.answer()
        
        if query.data == 'download_app':
            await download_app_handler(update, context)
        elif query.data == 'own_xrp':
            user_id = query.from_user.id
            user_data[user_id]['steps_completed']['own_xrp'] = True
            await query.edit_message_text(
                "✅ XRP ownership verified (self-reported)\n\n"
                "Now complete other tasks!",
                parse_mode=ParseMode.MARKDOWN
            )
        elif query.data == 'referral_info':
            await referral_info_handler(update, context)
        elif query.data == 'verify_tasks':
            await verify_tasks_handler(update, context)
        elif query.data == 'share_referral':
            user_id = query.from_user.id
            await query.edit_message_text(
                f"📤 *Share Your Referral Link*\n\n"
                f"Your code: `{user_data[user_id]['referral_code']}`\n\n"
                "Copy this message to share:\n\n"
                f"Join the XPM MEME airdrop using my referral code {user_data[user_id]['referral_code']} "
                f"and earn extra XRP! @{context.bot.username}",
                parse_mode=ParseMode.MARKDOWN
            )
        elif query.data == 'back_to_main':
            await start(update, context)
            
    except Exception as e:
        logger.error(f"Error in button handler: {str(e)}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling update:", exc_info=context.error)
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "An error occurred. Please try again later."
        )

def main() -> None:
    try:
        logger.info("Starting XPM MEME Airdrop Bot...")
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Register handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet))
        application.add_handler(CallbackQueryHandler(button_handler))
        
        # Error handler
        application.add_error_handler(error_handler)

        # Production (webhook) vs Development (polling)
        if os.getenv('RENDER'):
            PORT = int(os.environ.get('PORT', 10000))
            WEBHOOK_URL = os.getenv('WEBHOOK_URL')
            
            application.run_webhook(
                listen="0.0.0.0",
                port=PORT,
                secret_token='YOUR_SECRET_TOKEN',
                webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}",
                drop_pending_updates=True
            )
            logger.info(f"Running in webhook mode on port {PORT}")
        else:
            application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            logger.info("Running in polling mode")
            
    except Exception as e:
        logger.critical(f"Failed to start bot: {str(e)}")
        raise

if __name__ == '__main__':
    main()
