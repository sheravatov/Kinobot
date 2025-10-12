#!/bin/bash

echo "🎬 Telegram Kino Bot ishga tushirilmoqda..."
echo ""

# Virtual environment borligini tekshirish
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment yaratilmoqda..."
    python3 -m venv venv
    echo "✅ Virtual environment yaratildi!"
    echo ""
fi

# Virtual environment ni aktivlashtirish
echo "🔄 Virtual environment aktivlashtirilmoqda..."
source venv/bin/activate
echo "✅ Virtual environment aktiv!"
echo ""

# Kutubxonalarni o'rnatish
echo "📚 Kutubxonalar tekshirilmoqda..."
pip install -q -r requirements.txt
echo "✅ Kutubxonalar tayyor!"
echo ""

# Config.py borligini tekshirish
if [ ! -f "config.py" ]; then
    echo "⚠️  config.py topilmadi!"
    echo "📝 config.example.py dan nusxa olib, ma'lumotlarni kiriting."
    echo ""
    echo "Davom ettirasizmi? (y/n)"
    read -r response
    if [ "$response" != "y" ]; then
        echo "❌ Bekor qilindi."
        exit 1
    fi
fi

# Botni ishga tushirish
echo "🚀 Bot ishga tushirilmoqda..."
echo "⏹  To'xtatish uchun: Ctrl+C"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python bot.py