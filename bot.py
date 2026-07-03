import os
import logging
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

import database
import tts

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

AWAITING_TTS_TEXT = 1

def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎤 Convert Text to Speech", callback_data="menu_tts")],
        [InlineKeyboardButton("🌍 Change Language", callback_data="menu_lang"),
         InlineKeyboardButton("🎙 Change Voice", callback_data="menu_voice")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings"),
         InlineKeyboardButton("❓ Help", callback_data="menu_help")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    user = update.effective_user
    database.get_user_settings(user.id)
    
    welcome_text = (
        f"👋 Welcome to *VoiceScript Bot*, {user.first_name}!\n\n"
        "Turn any text into clear, natural-sounding speech in seconds.\n\n"
        "🎤 *Convert text to speech*\n"
        "🌍 *Choose your preferred language*\n"
        "🎙️ *Select your favorite voice*\n"
        "🎧 *Receive high-quality audio instantly*\n\n"
        "Tap a button below or simply send your text directly to get started."
    )
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /help command."""
    help_text = (
        "❓ *VoiceScript Bot Help Guide*\n\n"
        "1️⃣ *Convert Text to Speech:* Simply send any text message directly to the bot, or click the 🎤 button.\n"
        "2️⃣ *Change Language:* Tap 🌍 to see supported translation structures.\n"
        "3️⃣ *Change Voice:* Tap 🎙 to choose alternate OpenAI profiles (`alloy`, `echo`, `nova`, `shimmer`).\n"
        "4️⃣ *Settings:* Check your currently saved configuration configuration.\n\n"
        "Use /start to go back to the main dashboard."
    )
    if update.message:
        await update.message.reply_text(help_text, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.reply_text(help_text, parse_mode="Markdown")

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes inline buttons pressed from the main dashboard context."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == "menu_tts":
        await query.message.reply_text("Please type or paste the text you want converted into natural speech:")
        return AWAITING_TTS_TEXT
        
    elif query.data == "menu_lang":
        languages = ["English", "French", "Spanish", "German", "Arabic", "Portuguese", "Hindi"]
        keyboard = [[InlineKeyboardButton(lang, callback_data=f"set_lang_{lang}")] for lang in languages]
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="go_main")])
        await query.edit_message_text("🌍 *Select your preferred text input language:*", 
                                      reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
                                      
    elif query.data == "menu_voice":
        voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        keyboard = [[InlineKeyboardButton(v.capitalize(), callback_data=f"set_voice_{v}")] for v in voices]
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="go_main")])
        await query.edit_message_text("🎙 *Select your preferred target AI voice profile:*", 
                                      reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
                                      
    elif query.data == "menu_settings":
        settings = database.get_user_settings(user_id)
        settings_text = (
            "⚙️ *Your Current Saved Configurations:*\n\n"
            f"🌍 Input Mode Language: `{settings['language']}`\n"
            f"🎙 Active AI Voice Model: `{settings['voice'].capitalize()}`\n"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="go_main")]]
        await query.edit_message_text(settings_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif query.data == "menu_help":
        await help_command(update, context)
        
    elif query.data == "go_main":
        await query.edit_message_text("Main Menu Context - Please select an action:", reply_markup=get_main_menu_keyboard())
        
    return ConversationHandler.END

async def save_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.replace("set_lang_", "")
    database.update_user_language(query.from_user.id, lang)
    await query.edit_message_text(f"✅ Preferred language saved as: *{lang}*", parse_mode="Markdown")
    return ConversationHandler.END

async def save_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    voice = query.data.replace("set_voice_", "")
    database.update_user_voice(query.from_user.id, voice)
    await query.edit_message_text(f"✅ Active voice profile changed to: *{voice.capitalize()}*", parse_mode="Markdown")
    return ConversationHandler.END

async def handle_text_to_speech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Converts user text into an audio file, sends it, and deletes the temporary file."""
    user_id = update.effective_user.id
    text_to_convert = update.message.text
    
    if not text_to_convert or text_to_convert.strip() == "":
        await update.message.reply_text("❌ Sent message body cannot be evaluated as an empty payload.")
        return ConversationHandler.END
        
    processing_msg = await update.message.reply_text("⏳ Generating high-quality narration audio stream, please wait...")
    settings = database.get_user_settings(user_id)
    voice_profile = settings['voice']
    
    chunks = tts.split_text(text_to_convert, max_chars=4000)
    
    for idx, chunk in enumerate(chunks):
        temp_filename = f"tts_{user_id}_{idx}.mp3"
        try:
            success = await tts.generate_speech(chunk, voice_profile, temp_filename)
            if success and os.path.exists(temp_filename):
                with open(temp_filename, 'rb') as audio:
                    await update.message.reply_audio(
                        audio=audio, 
                        title=f"Audio Segment {idx+1}", 
                        performer="VoiceScript Bot"
                    )
            else:
                await update.message.reply_text("❌ Failed to transform raw text segment.")
        except Exception as err:
            logger.error(f"Failed inside generation loop: {err}")
            await update.message.reply_text("❌ System error experienced processing conversion.")
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
                
    await processing_msg.delete()
    return ConversationHandler.END

def main():
    database.init_db()
    
    if not BOT_TOKEN:
        logger.critical("FATAL: BOT_TOKEN Environment key missing.")
        return

    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("help", help_command),
            CallbackQueryHandler(save_language, pattern="^set_lang_"),
            CallbackQueryHandler(save_voice, pattern="^set_voice_"),
            CallbackQueryHandler(menu_handler, pattern="^menu_|^go_main$"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_to_speech)
        ],
        states={
            AWAITING_TTS_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_to_speech)]
        },
        fallbacks=[CommandHandler("start", start)]
    )
    
    application.add_handler(conv_handler)
    
    logger.info("VoiceScript Bot background listener service online.")
    application.run_polling()

if __name__ == '__main__':
    main()

