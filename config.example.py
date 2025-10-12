"""
Konfiguratsiya fayli namunasi
Bu faylni nusxalab config.py yarating va o'z ma'lumotlaringizni kiriting
"""

# ========================== BOT SOZLAMALARI ==========================

# BotFather dan olingan bot tokeni
# Olish uchun: https://t.me/BotFather -> /newbot
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"

# Admin Telegram ID
# Olish uchun: https://t.me/userinfobot -> /start
ADMIN_ID = 123456789

# ========================== DATABASE SOZLAMALARI ==========================

# Database fayl nomi
DATABASE_NAME = 'database.db'

# ========================== BOT PARAMETRLARI ==========================

# Har sahifada nechta kino ko'rsatilsin
MOVIES_PER_PAGE = 10

# Top kinolar soni
TOP_MOVIES_LIMIT = 15

# Qidiruv natijalari limiti
SEARCH_RESULTS_LIMIT = 20

# ========================== XABARLAR ==========================

WELCOME_MESSAGE = """
👋 Assalomu alaykum!

🎬 Kino botimizga xush kelibsiz!
Bu yerda eng zo'r kinolarni topishingiz mumkin.

📌 Qanday foydalanish mumkin?
• 🎞 Top kinolar - Eng mashhur kinolar
• 🔍 Kino izlash - Nom, ID yoki hashtag orqali
• 📩 Biz bilan aloqa - Murojaat qilish

Yaxshi tomosha! 🍿
"""

SUBSCRIPTION_REQUIRED_MESSAGE = """
❗️ Kinolarni ko'rish uchun quyidagi kanallarga obuna bo'ling:
"""

NO_MOVIES_MESSAGE = "📭 Hozircha kinolar mavjud emas."

MOVIE_NOT_FOUND_MESSAGE = "❌ Kino topilmadi."

SEARCH_NO_RESULTS_MESSAGE = "❌ Qidiruv bo'yicha natija topilmadi."

ADMIN_ONLY_MESSAGE = "❌ Bu funksiya faqat adminlar uchun!"

# ========================== LOG SOZLAMALARI ==========================

# Log fayl nomi
LOG_FILE = 'bot.log'

# Log format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Log darajasi (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = 'INFO'

# ========================== QO'SHIMCHA SOZLAMALAR ==========================

# Video maksimal hajmi (baytlarda, 50MB = 50 * 1024 * 1024)
MAX_VIDEO_SIZE = 52428800

# Kanal username validatsiyasi (regex)
CHANNEL_USERNAME_PATTERN = r'^[a-zA-Z0-9_]{5,32}$'

# Rate limiting (soniyalarda)
RATE_LIMIT_SECONDS = 3