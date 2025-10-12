"""
Telegram Kino Bot
Professional Movie Bot for Telegram

Author: Sheravatov Shaxzod
Version: 1.0
"""

import logging
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, filters
from telegram.constants import ParseMode

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========================== CONFIG ==========================
# Bu sozlamalarni config.py dan import qilish mumkin
try:
    from config import BOT_TOKEN, ADMIN_ID
except ImportError:
    BOT_TOKEN = "8337442107:AAHzw0hp8qdT3FBfOv2YT6iQ9yVzDkhohFQ"
    ADMIN_ID = 8305539348
    logger.warning("config.py topilmadi! Default qiymatlar ishlatilmoqda.")

# Conversation States
(WAITING_VIDEO, WAITING_TITLE, WAITING_LANGUAGE, WAITING_COUNTRY, 
 WAITING_QUALITY, WAITING_YEAR, WAITING_GENRE, WAITING_HASHTAG) = range(8)

# ========================== DATABASE ==========================
class Database:
    """Database bilan ishlash uchun class"""
    
    def __init__(self, db_name='database.db'):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        """Database connection olish"""
        return sqlite3.connect(self.db_name)
    
    def init_db(self):
        """Database va jadvallarni yaratish"""
        conn = self.get_connection()
        c = conn.cursor()
        
        # Movies table
        c.execute('''CREATE TABLE IF NOT EXISTS movies
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      title TEXT NOT NULL,
                      language TEXT,
                      country TEXT,
                      quality TEXT,
                      year TEXT,
                      genre TEXT,
                      hashtag TEXT,
                      file_id TEXT NOT NULL,
                      views INTEGER DEFAULT 0,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Mandatory channels table
        c.execute('''CREATE TABLE IF NOT EXISTS mandatory_channels
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE NOT NULL,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Users table (statistika uchun)
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (user_id INTEGER PRIMARY KEY,
                      username TEXT,
                      first_name TEXT,
                      last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        conn.commit()
        conn.close()
        logger.info("Database muvaffaqiyatli yaratildi!")
    
    def add_movie(self, title, language, country, quality, year, genre, hashtag, file_id):
        """Yangi kino qo'shish"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''INSERT INTO movies (title, language, country, quality, year, genre, hashtag, file_id)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (title, language, country, quality, year, genre, hashtag, file_id))
            movie_id = c.lastrowid
            conn.commit()
            logger.info(f"Kino qo'shildi: ID {movie_id} - {title}")
            return movie_id
        except Exception as e:
            logger.error(f"Kino qo'shishda xatolik: {e}")
            return None
        finally:
            conn.close()
    
    def get_all_movies(self):
        """Barcha kinolarni olish"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM movies ORDER BY id DESC')
        movies = c.fetchall()
        conn.close()
        return movies
    
    def get_top_movies(self, limit=10):
        """Top kinolarni olish"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM movies ORDER BY views DESC LIMIT ?', (limit,))
        movies = c.fetchall()
        conn.close()
        return movies
    
    def search_movies(self, query):
        """Kino izlash"""
        conn = self.get_connection()
        c = conn.cursor()
        
        if query.startswith('#'):
            c.execute('SELECT * FROM movies WHERE hashtag LIKE ?', (f'%{query}%',))
        elif query.isdigit():
            c.execute('SELECT * FROM movies WHERE id = ?', (int(query),))
        else:
            c.execute('SELECT * FROM movies WHERE title LIKE ? OR genre LIKE ?', 
                     (f'%{query}%', f'%{query}%'))
        
        movies = c.fetchall()
        conn.close()
        return movies
    
    def get_movie_by_id(self, movie_id):
        """ID bo'yicha kino olish"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM movies WHERE id = ?', (movie_id,))
        movie = c.fetchone()
        conn.close()
        return movie
    
    def increment_views(self, movie_id):
        """Ko'rilganlar sonini oshirish"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('UPDATE movies SET views = views + 1 WHERE id = ?', (movie_id,))
        conn.commit()
        conn.close()
    
    def delete_movie(self, movie_id):
        """Kinoni o'chirish"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('DELETE FROM movies WHERE id = ?', (movie_id,))
        conn.commit()
        conn.close()
        logger.info(f"Kino o'chirildi: ID {movie_id}")
    
    def add_mandatory_channel(self, username):
        """Majburiy kanal qo'shish"""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute('INSERT INTO mandatory_channels (username) VALUES (?)', (username,))
            conn.commit()
            conn.close()
            logger.info(f"Kanal qo'shildi: @{username}")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Kanal allaqachon mavjud: @{username}")
            return False
    
    def get_mandatory_channels(self):
        """Majburiy kanallar ro'yxati"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('SELECT username FROM mandatory_channels')
        channels = [row[0] for row in c.fetchall()]
        conn.close()
        return channels
    
    def delete_channel(self, username):
        """Kanalni o'chirish"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('DELETE FROM mandatory_channels WHERE username = ?', (username,))
        conn.commit()
        conn.close()
        logger.info(f"Kanal o'chirildi: @{username}")
    
    def add_user(self, user_id, username, first_name):
        """Foydalanuvchini qo'shish/yangilash"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO users (user_id, username, first_name, last_activity)
                     VALUES (?, ?, ?, CURRENT_TIMESTAMP)''',
                  (user_id, username, first_name))
        conn.commit()
        conn.close()
    
    def get_stats(self):
        """Statistika olish"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) FROM movies')
        total_movies = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM mandatory_channels')
        total_channels = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM users')
        total_users = c.fetchone()[0]
        
        c.execute('SELECT SUM(views) FROM movies')
        total_views = c.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'movies': total_movies,
            'channels': total_channels,
            'users': total_users,
            'views': total_views
        }

# Database instance
db = Database()

# ========================== UTILITIES ==========================
async def check_subscription(user_id, context):
    """Kanal obunasini tekshirish"""
    channels = db.get_mandatory_channels()
    not_subscribed = []
    
    for channel in channels:
        try:
            member = await context.bot.get_chat_member(chat_id=f"@{channel}", user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                not_subscribed.append(channel)
        except Exception as e:
            logger.error(f"Kanal tekshirishda xatolik @{channel}: {e}")
            not_subscribed.append(channel)
    
    return not_subscribed

def main_keyboard(user_id):
    """Asosiy keyboard"""
    keyboard = [
        [KeyboardButton("🎞 Top kinolar"), KeyboardButton("🔍 Kino izlash")],
        [KeyboardButton("📩 Biz bilan aloqa")]
    ]
    
    if user_id == ADMIN_ID:
        keyboard.append([KeyboardButton("👨‍💼 Admin Panel")])
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_keyboard():
    """Admin keyboard"""
    keyboard = [
        [KeyboardButton("🎬 Kino qo'shish"), KeyboardButton("🎞 Kinolar ro'yxati")],
        [KeyboardButton("📢 Majburiy kanallar"), KeyboardButton("📊 Statistika")],
        [KeyboardButton("⬅️ Orqaga")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def format_movie_info(movie, show_full=True):
    """Kino ma'lumotlarini formatlash"""
    _, title, language, country, quality, year, genre, hashtag, file_id, views, _ = movie
    
    if show_full:
        return (
            f"🎬 <b>{title}</b>\n\n"
            f"🗣 <b>Til:</b> {language}\n"
            f"🌍 <b>Mamlakat:</b> {country}\n"
            f"📺 <b>Sifat:</b> {quality}\n"
            f"📅 <b>Yil:</b> {year}\n"
            f"🎭 <b>Janr:</b> {genre}\n"
            f"🏷 <b>Tag:</b> {hashtag}\n"
            f"👁 <b>Ko'rildi:</b> {views} marta"
        )
    else:
        return f"🎬 {title} ({year}) | 👁 {views}"

# ========================== HANDLERS ==========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start komandasi"""
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name)
    
    welcome_text = (
        f"👋 <b>Assalomu alaykum, {user.first_name}!</b>\n\n"
        "🎬 Kino botimizga xush kelibsiz!\n"
        "Bu yerda eng zo'r kinolarni topishingiz mumkin.\n\n"
        "📌 <b>Qanday foydalanish mumkin?</b>\n"
        "• 🎞 Top kinolar - Eng mashhur kinolar\n"
        "• 🔍 Kino izlash - Nom, ID yoki hashtag orqali qidirish\n"
        "• 📩 Biz bilan aloqa - Murojaat qilish\n\n"
        "Yaxshi tomosha! 🍿"
    )
    
    await update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(user.id)
    )
    logger.info(f"Start: {user.first_name} (@{user.username}) - ID: {user.id}")

async def top_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Top kinolarni ko'rsatish"""
    user_id = update.effective_user.id
    not_subscribed = await check_subscription(user_id, context)
    
    if not_subscribed:
        keyboard = [[InlineKeyboardButton(f"📢 {ch}", url=f"https://t.me/{ch}")] for ch in not_subscribed]
        keyboard.append([InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")])
        
        await update.message.reply_text(
            "❗️ <b>Kinolarni ko'rish uchun quyidagi kanallarga obuna bo'ling:</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    movies = db.get_top_movies(15)
    
    if not movies:
        await update.message.reply_text("📭 Hozircha kinolar mavjud emas.")
        return
    
    keyboard = []
    for movie in movies:
        movie_id = movie[0]
        title = movie[1]
        views = movie[9]
        keyboard.append([InlineKeyboardButton(
            f"🎬 {title} | 👁 {views}",
            callback_data=f"movie_{movie_id}"
        )])
    
    await update.message.reply_text(
        "🏆 <b>Eng ko'p ko'rilgan kinolar:</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def search_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Qidiruv promptini ko'rsatish"""
    await update.message.reply_text(
        "🔍 <b>Qidirish</b>\n\n"
        "Kino nomini, ID raqamini yoki hashtag kiriting:\n\n"
        "📝 <b>Masalan:</b>\n"
        "• Avatar\n"
        "• 123\n"
        "• #fantastika\n"
        "• #komediya",
        parse_mode=ParseMode.HTML
    )
    context.user_data['waiting_search'] = True

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Qidiruvni qayta ishlash"""
    if not context.user_data.get('waiting_search'):
        return
    
    user_id = update.effective_user.id
    not_subscribed = await check_subscription(user_id, context)
    
    if not_subscribed:
        keyboard = [[InlineKeyboardButton(f"📢 {ch}", url=f"https://t.me/{ch}")] for ch in not_subscribed]
        keyboard.append([InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")])
        
        await update.message.reply_text(
            "❗️ <b>Kinolarni ko'rish uchun quyidagi kanallarga obuna bo'ling:</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data['waiting_search'] = False
        return
    
    query = update.message.text.strip()
    movies = db.search_movies(query)
    
    if not movies:
        await update.message.reply_text(
            f"❌ <b>'{query}'</b> bo'yicha natija topilmadi.\n\n"
            "💡 Boshqa nom yoki hashtag bilan qayta urinib ko'ring.",
            parse_mode=ParseMode.HTML
        )
        context.user_data['waiting_search'] = False
        return
    
    keyboard = []
    for movie in movies[:20]:
        movie_id = movie[0]
        title = movie[1]
        views = movie[9]
        keyboard.append([InlineKeyboardButton(
            f"🎬 {title} | 👁 {views}",
            callback_data=f"movie_{movie_id}"
        )])
    
    result_text = f"🔍 <b>Natijalar:</b> {len(movies)} ta kino topildi"
    if len(movies) > 20:
        result_text += f"\n(Birinchi 20 tasi ko'rsatilmoqda)"
    
    await update.message.reply_text(
        result_text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    context.user_data['waiting_search'] = False

async def show_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kino ma'lumotlarini ko'rsatish"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    not_subscribed = await check_subscription(user_id, context)
    
    if not_subscribed:
        keyboard = [[InlineKeyboardButton(f"📢 {ch}", url=f"https://t.me/{ch}")] for ch in not_subscribed]
        keyboard.append([InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")])
        
        await query.edit_message_text(
            "❗️ <b>Kinolarni ko'rish uchun quyidagi kanallarga obuna bo'ling:</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    movie_id = int(query.data.split('_')[1])
    movie = db.get_movie_by_id(movie_id)
    
    if not movie:
        await query.edit_message_text("❌ Kino topilmadi.")
        return
    
    caption = format_movie_info(movie)
    keyboard = [[InlineKeyboardButton("▶️ Kino ko'rish", callback_data=f"watch_{movie_id}")]]
    
    await query.edit_message_text(
        caption,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def watch_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kinoni yuborish"""
    query = update.callback_query
    await query.answer("📤 Kino yuklanmoqda...")
    
    user_id = update.effective_user.id
    not_subscribed = await check_subscription(user_id, context)
    
    if not_subscribed:
        keyboard = [[InlineKeyboardButton(f"📢 {ch}", url=f"https://t.me/{ch}")] for ch in not_subscribed]
        keyboard.append([InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")])
        
        await query.edit_message_text(
            "❗️ <b>Kinolarni ko'rish uchun quyidagi kanallarga obuna bo'ling:</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    movie_id = int(query.data.split('_')[1])
    movie = db.get_movie_by_id(movie_id)
    
    if not movie:
        await query.edit_message_text("❌ Kino topilmadi.")
        return
    
    _, title, language, country, quality, year, genre, hashtag, file_id, views, _ = movie
    
    db.increment_views(movie_id)
    
    caption = (
        f"🎬 <b>{title}</b>\n\n"
        f"🗣 {language} | 🌍 {country} | 📺 {quality}\n"
        f"📅 {year} | 🎭 {genre}\n"
        f"🏷 {hashtag}\n"
        f"👁 Ko'rildi: {views + 1} marta\n\n"
        f"📲 @{context.bot.username}"
    )
    
    try:
        await context.bot.send_video(
            chat_id=query.message.chat_id,
            video=file_id,
            caption=caption,
            parse_mode=ParseMode.HTML
        )
        await query.edit_message_text("✅ Kino yuborildi! Yaxshi tomosha! 🍿")
        logger.info(f"Kino yuborildi: ID {movie_id} - {title} - User: {user_id}")
    except Exception as e:
        logger.error(f"Video yuborishda xatolik: {e}")
        await query.edit_message_text("❌ Video yuborishda xatolik yuz berdi. Admin bilan bog'laning.")

async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obunani tekshirish callback"""
    query = update.callback_query
    
    user_id = update.effective_user.id
    not_subscribed = await check_subscription(user_id, context)
    
    if not_subscribed:
        await query.answer("❌ Hali barcha kanallarga obuna bo'lmadingiz!", show_alert=True)
    else:
        await query.answer("✅ Obuna tasdiqlandi!", show_alert=True)
        await query.edit_message_text(
            "✅ <b>Obuna tasdiqlandi!</b>\n\nEndi botdan to'liq foydalanishingiz mumkin.",
            parse_mode=ParseMode.HTML
        )

# ========================== ADMIN ==========================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Sizda admin huquqi yo'q!")
        return
    
    stats = db.get_stats()
    
    stats_text = (
        "👨‍💼 <b>Admin Panel</b>\n\n"
        "📊 <b>Statistika:</b>\n"
        f"🎬 Kinolar: {stats['movies']} ta\n"
        f"📢 Majburiy kanallar: {stats['channels']} ta\n"
        f"👥 Foydalanuvchilar: {stats['users']} ta\n"
        f"👁 Jami ko'rishlar: {stats['views']} marta\n\n"
        "Kerakli bo'limni tanlang:"
    )
    
    await update.message.reply_text(
        stats_text,
        parse_mode=ParseMode.HTML,
        reply_markup=admin_keyboard()
    )

async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Batafsil statistika"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        return
    
    stats = db.get_stats()
    top_movies = db.get_top_movies(5)
    
    stats_text = (
        "📊 <b>Batafsil Statistika</b>\n\n"
        f"🎬 Jami kinolar: {stats['movies']} ta\n"
        f"📢 Majburiy kanallar: {stats['channels']} ta\n"
        f"👥 Foydalanuvchilar: {stats['users']} ta\n"
        f"👁 Jami ko'rishlar: {stats['views']} marta\n\n"
        "🏆 <b>Top 5 kino:</b>\n"
    )
    
    for i, movie in enumerate(top_movies, 1):
        stats_text += f"{i}. {movie[1]} - {movie[9]} ko'rish\n"
    
    await update.message.reply_text(stats_text, parse_mode=ParseMode.HTML)

# ========================== ADD MOVIE ==========================
async def add_movie_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kino qo'shishni boshlash"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        return ConversationHandler.END
    
    await update.message.reply_text(
        "🎬 <b>Yangi kino qo'shish</b>\n\n"
        "1️⃣ Video faylni yuboring:\n\n"
        "❌ Bekor qilish uchun /cancel",
        parse_mode=ParseMode.HTML
    )
    return WAITING_VIDEO

async def receive_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Video qabul qilish"""
    if update.message.video:
        context.user_data['file_id'] = update.message.video.file_id
        await update.message.reply_text(
            "2️⃣ Kino nomini kiriting:\n\n"
            "Masalan: Avatar 2: The Way of Water"
        )
        return WAITING_TITLE
    else:
        await update.message.reply_text("❌ Iltimos, video fayl yuboring!")
        return WAITING_VIDEO

async def receive_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Nomni qabul qilish"""
    context.user_data['title'] = update.message.text
    await update.message.reply_text(
        "3️⃣ Tilini kiriting:\n\n"
        "Masalan: O'zbek dublaj, Rus, Ingliz"
    )
    return WAITING_LANGUAGE

async def receive_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tilni qabul qilish"""
    context.user_data['language'] = update.message.text
    await update.message.reply_text(
        "4️⃣ Mamlakatini kiriting:\n\n"
        "Masalan: AQSH, Fransiya, Rossiya"
    )
    return WAITING_COUNTRY

async def receive_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mamlakatni qabul qilish"""
    context.user_data['country'] = update.message.text
    await update.message.reply_text(
        "5️⃣ Sifatini kiriting:\n\n"
        "Masalan: HD, Full HD, 4K, 1080p"
    )
    return WAITING_QUALITY

async def receive_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sifatni qabul qilish"""
    context.user_data['quality'] = update.message.text
    await update.message.reply_text(
        "6️⃣ Yilini kiriting:\n\n"
        "Masalan: 2024"
    )
    return WAITING_YEAR

async def receive_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yilni qabul qilish"""
    context.user_data['year'] = update.message.text
    await update.message.reply_text(
        "7️⃣ Janrini kiriting:\n\n"
        "Masalan: Fantastika, Komediya, Jangari"
    )
    return WAITING_GENRE

async def receive_genre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Janrni qabul qilish"""
    context.user_data['genre'] = update.message.text
    await update.message.reply_text(
        "8️⃣ Hashtag kiriting:\n\n"
        "Masalan: #fantastika #marvel #2024\n"
        "(Bir nechta hashtag kiritish mumkin)"
    )
    return WAITING_HASHTAG

async def receive_hashtag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hashtagni qabul qilish va kinoni saqlash"""
    context.user_data['hashtag'] = update.message.text
    
    movie_id = db.add_movie(
        context.user_data['title'],
        context.user_data['language'],
        context.user_data['country'],
        context.user_data['quality'],
        context.user_data['year'],
        context.user_data['genre'],
        context.user_data['hashtag'],
        context.user_data['file_id']
    )
    
    if movie_id:
        success_text = (
            "✅ <b>Kino muvaffaqiyatly qo'shildi!</b>\n\n"
            f"🆔 ID: <code>{movie_id}</code>\n"
            f"🎬 {context.user_data['title']}\n"
            f"🗣 {context.user_data['language']}\n"
            f"🌍 {context.user_data['country']}\n"
            f"📺 {context.user_data['quality']}\n"
            f"📅 {context.user_data['year']}\n"
            f"🎭 {context.user_data['genre']}\n"
            f"🏷 {context.user_data['hashtag']}"
        )
        await update.message.reply_text(
            success_text,
            parse_mode=ParseMode.HTML,
            reply_markup=admin_keyboard()
        )
    else:
        await update.message.reply_text(
            "❌ Kino qo'shishda xatolik yuz berdi.",
            reply_markup=admin_keyboard()
        )
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bekor qilish"""
    user_id = update.effective_user.id
    context.user_data.clear()
    
    await update.message.reply_text(
        "❌ Bekor qilindi.",
        reply_markup=admin_keyboard() if user_id == ADMIN_ID else main_keyboard(user_id)
    )
    return ConversationHandler.END

# ========================== MOVIES LIST ==========================
async def movies_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kinolar ro'yxati"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        return
    
    movies = db.get_all_movies()
    
    if not movies:
        await update.message.reply_text("📭 Hozircha kinolar yo'q.")
        return
    
    # Har sahifada 10 ta kino
    page = context.user_data.get('movies_page', 0)
    start = page * 10
    end = start + 10
    
    text = f"📋 <b>Barcha kinolar ({len(movies)} ta):</b>\n\n"
    
    for movie in movies[start:end]:
        movie_id, title, _, _, _, _, _, _, _, views, _ = movie
        text += f"🆔 <code>{movie_id}</code> | 🎬 {title} | 👁 {views}\n"
    
    keyboard = []
    
    # Pagination
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Orqaga", callback_data=f"movies_page_{page-1}"))
    if end < len(movies):
        nav_buttons.append(InlineKeyboardButton("➡️ Oldinga", callback_data=f"movies_page_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # O'chirish tugmasi
    keyboard.append([InlineKeyboardButton("🗑 Kino o'chirish (ID kiriting)", callback_data="delete_movie_prompt")])
    
    await update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
    )

async def movies_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sahifalarni almashtirish"""
    query = update.callback_query
    await query.answer()
    
    page = int(query.data.split('_')[2])
    context.user_data['movies_page'] = page
    
    movies = db.get_all_movies()
    start = page * 10
    end = start + 10
    
    text = f"📋 <b>Barcha kinolar ({len(movies)} ta):</b>\n\n"
    
    for movie in movies[start:end]:
        movie_id, title, _, _, _, _, _, _, _, views, _ = movie
        text += f"🆔 <code>{movie_id}</code> | 🎬 {title} | 👁 {views}\n"
    
    keyboard = []
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Orqaga", callback_data=f"movies_page_{page-1}"))
    if end < len(movies):
        nav_buttons.append(InlineKeyboardButton("➡️ Oldinga", callback_data=f"movies_page_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("🗑 Kino o'chirish (ID kiriting)", callback_data="delete_movie_prompt")])
    
    await query.edit_message_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def delete_movie_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kino o'chirish prompti"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🗑 <b>Kino o'chirish</b>\n\n"
        "O'chirmoqchi bo'lgan kino ID sini kiriting:",
        parse_mode=ParseMode.HTML
    )
    context.user_data['waiting_delete_id'] = True

async def handle_delete_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kinoni o'chirish"""
    if not context.user_data.get('waiting_delete_id'):
        return
    
    try:
        movie_id = int(update.message.text.strip())
        movie = db.get_movie_by_id(movie_id)
        
        if movie:
            title = movie[1]
            db.delete_movie(movie_id)
            await update.message.reply_text(
                f"✅ Kino o'chirildi!\n\n"
                f"🆔 ID: {movie_id}\n"
                f"🎬 {title}",
                reply_markup=admin_keyboard()
            )
        else:
            await update.message.reply_text("❌ Bunday ID li kino topilmadi.")
        
        context.user_data['waiting_delete_id'] = False
    except ValueError:
        await update.message.reply_text("❌ Noto'g'ri format! Faqat raqam kiriting.")

# ========================== CHANNELS ==========================
async def mandatory_channels_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Majburiy kanallar menyusi"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        return
    
    channels = db.get_mandatory_channels()
    
    text = "📢 <b>Majburiy kanallar:</b>\n\n"
    
    if channels:
        for i, ch in enumerate(channels, 1):
            text += f"{i}. @{ch}\n"
    else:
        text += "Hozircha kanallar yo'q.\n"
    
    text += "\n➕ <b>Yangi kanal qo'shish:</b>\n"
    text += "Kanal username ini kiriting (@ belgisiz)\n\n"
    text += "Masalan: kinolar_kanali"
    
    keyboard = []
    for ch in channels:
        keyboard.append([InlineKeyboardButton(f"❌ @{ch}", callback_data=f"delch_{ch}")])
    
    await update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
    )
    context.user_data['waiting_channel'] = True

async def handle_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kanal qo'shish"""
    if not context.user_data.get('waiting_channel'):
        return
    
    username = update.message.text.strip().replace('@', '')
    
    if db.add_mandatory_channel(username):
        await update.message.reply_text(
            f"✅ Kanal qo'shildi!\n\n@{username}",
            reply_markup=admin_keyboard()
        )
    else:
        await update.message.reply_text(f"❌ @{username} allaqachon ro'yxatda!")
    
    context.user_data['waiting_channel'] = False

async def delete_channel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kanalni o'chirish"""
    query = update.callback_query
    await query.answer()
    
    username = query.data.replace('delch_', '')
    db.delete_channel(username)
    
    channels = db.get_mandatory_channels()
    
    text = "📢 <b>Majburiy kanallar:</b>\n\n"
    
    if channels:
        for i, ch in enumerate(channels, 1):
            text += f"{i}. @{ch}\n"
    else:
        text += "Hozircha kanallar yo'q.\n"
    
    text += f"\n✅ @{username} o'chirildi!"
    
    keyboard = []
    for ch in channels:
        keyboard.append([InlineKeyboardButton(f"❌ @{ch}", callback_data=f"delch_{ch}")])
    
    await query.edit_message_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
    )

# ========================== CONTACT ==========================
async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Aloqa"""
    await update.message.reply_text(
        "📩 <b>Biz bilan bog'lanish</b>\n\n"
        "Xabaringizni yozing, admin tez orada javob beradi:",
        parse_mode=ParseMode.HTML
    )
    context.user_data['waiting_contact'] = True

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Aloqa xabarini qabul qilish"""
    if not context.user_data.get('waiting_contact'):
        return
    
    user = update.effective_user
    message = update.message.text
    
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"📩 <b>Yangi xabar:</b>\n\n"
                f"👤 {user.first_name} {user.last_name or ''}\n"
                f"🆔 <code>{user.id}</code>\n"
                f"📱 @{user.username or 'username yoq'}\n\n"
                f"💬 <b>Xabar:</b>\n{message}"
            ),
            parse_mode=ParseMode.HTML
        )
        
        
        await update.message.reply_text(
            "✅ Xabaringiz adminga yuborildi!\n"
            "Tez orada javob beramiz.",
            reply_markup=main_keyboard(user.id)
        )
    except Exception as e:
        logger.error(f"Xabar yuborishda xatolik: {e}")
        await update.message.reply_text("❌ Xatolik yuz berdi. Keyinroq urinib ko'ring.")
    
    context.user_data['waiting_contact'] = False

# ========================== BACK ==========================
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asosiy menyuga qaytish"""
    user_id = update.effective_user.id
    context.user_data.clear()
    
    await update.message.reply_text(
        "🏠 Asosiy menyu:",
        reply_markup=main_keyboard(user_id)
    )

# ========================== ERROR HANDLER ==========================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Xatolarni qayta ishlash"""
    logger.error(f"Xatolik yuz berdi: {context.error}", exc_info=context.error)
    
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring yoki admin bilan bog'laning."
        )

# ========================== MAIN ==========================
def main():
    """Asosiy funksiya"""
    logger.info("Bot ishga tushirilmoqda...")
    
    # Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler - Kino qo'shish
    add_movie_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🎬 Kino qo'shish$"), add_movie_start)],
        states={
            WAITING_VIDEO: [MessageHandler(filters.VIDEO, receive_video)],
            WAITING_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_title)],
            WAITING_LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_language)],
            WAITING_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_country)],
            WAITING_QUALITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_quality)],
            WAITING_YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_year)],
            WAITING_GENRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_genre)],
            WAITING_HASHTAG: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_hashtag)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True )
    
    # Handlerlar ro'yxati
    application.add_handler(CommandHandler("start", start))
    application.add_handler(add_movie_handler)
    
    # Tugmalar
    application.add_handler(MessageHandler(filters.Regex("^🎞 Top kinolar$"), top_movies))
    application.add_handler(MessageHandler(filters.Regex("^🔍 Kino izlash$"), search_prompt))
    application.add_handler(MessageHandler(filters.Regex("^📩 Biz bilan aloqa$"), contact))
    application.add_handler(MessageHandler(filters.Regex("^👨‍💼 Admin Panel$"), admin_panel))
    application.add_handler(MessageHandler(filters.Regex("^🎞 Kinolar ro'yxati$"), movies_list))
    application.add_handler(MessageHandler(filters.Regex("^📢 Majburiy kanallar$"), mandatory_channels_menu))
    application.add_handler(MessageHandler(filters.Regex("^📊 Statistika$"), statistics))
    application.add_handler(MessageHandler(filters.Regex("^⬅️ Orqaga$"), back_to_main))
    
    # Callback handlerlar
    application.add_handler(CallbackQueryHandler(show_movie, pattern="^movie_"))
    application.add_handler(CallbackQueryHandler(watch_movie, pattern="^watch_"))
    application.add_handler(CallbackQueryHandler(check_subscription_callback, pattern="^check_sub$"))
    application.add_handler(CallbackQueryHandler(delete_channel_callback, pattern="^delch_"))
    application.add_handler(CallbackQueryHandler(movies_page_callback, pattern="^movies_page_"))
    application.add_handler(CallbackQueryHandler(delete_movie_prompt, pattern="^delete_movie_prompt$"))
    
    # Text handlerlar (eng oxirida)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        lambda u, c: handle_search(u, c) if c.user_data.get('waiting_search') 
        else handle_channel(u, c) if c.user_data.get('waiting_channel')
        else handle_contact(u, c) if c.user_data.get('waiting_contact')
        else handle_delete_movie(u, c) if c.user_data.get('waiting_delete_id')
        else None
    ))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Botni ishga tushirish
    logger.info("✅ Bot muvaffaqiyatli ishga tushdi!")
    print("Bot ishga tushdi! To'xtatish uchun Ctrl+C bosing.")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi (Ctrl+C)")
    except Exception as e:
        logger.error(f"Bot ishga tushirishda xatolik: {e}")