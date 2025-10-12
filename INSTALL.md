# 📦 O'rnatish qo'llanmasi

Bu qo'llanma Telegram Kino Botni turli platformalarda o'rnatish bo'yicha batafsil ko'rsatmalar beradi.

## 📋 Talablar

- Python 3.8 yoki undan yuqori
- pip (Python package manager)
- Git (ixtiyoriy)
- Telegram bot tokeni

## 🚀 Tezkor o'rnatish

### Windows

1. **Fayllarni yuklab oling**
   ```cmd
   git clone https://github.com/username/telegram-movie-bot.git
   cd telegram-movie-bot
   ```

2. **run.bat ni ishga tushiring**
   ```cmd
   run.bat
   ```
   
   Bu script avtomatik ravishda:
   - Virtual environment yaratadi
   - Kutubxonalarni o'rnatadi
   - Botni ishga tushiradi

3. **config.py ni sozlang**
   - `config.example.py` ni nusxalang
   - `config.py` ga o'zgartiring
   - Bot tokenini va Admin ID ni kiriting

### Linux/Mac

1. **Fayllarni yuklab oling**
   ```bash
   git clone https://github.com/username/telegram-movie-bot.git
   cd telegram-movie-bot
   ```

2. **run.sh ga ruxsat bering va ishga tushiring**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

3. **config.py ni sozlang**
   ```bash
   cp config.example.py config.py
   nano config.py  # yoki vim, code, etc.
   ```

## 🔧 Qo'lda o'rnatish

### 1. Python o'rnatish

#### Windows:
- [python.org](https://python.org) dan yuklab oling
- O'rnatishda "Add Python to PATH" ni belgilang

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### Mac:
```bash
brew install python3
```

### 2. Virtual Environment yaratish

```bash
# Virtual environment yaratish
python -m venv venv

# Aktivlashtirish (Linux/Mac)
source venv/bin/activate

# Aktivlashtirish (Windows)
venv\Scripts\activate
```

### 3. Kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 4. Konfiguratsiya

```bash
# config.example.py dan nusxa olish
cp config.example.py config.py

# Tahrirlash
nano config.py
```

**config.py da o'zgartiring:**

```python
BOT_TOKEN = "YOUR_BOT_TOKEN"  # BotFather dan
ADMIN_ID = YOUR_TELEGRAM_ID    # @userinfobot dan
```

### 5. Botni ishga tushirish

```bash
python bot.py
```

## 🎯 Bot tokenini olish

1. Telegram da [@BotFather](https://t.me/BotFather) ni oching
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting (masalan: "Mening Kino Botim")
4. Bot username ini kiriting (bot bilan tugashi kerak, masalan: "my_movie_bot")
5. Tokenni nusxalang va `config.py` ga joylashtiring

**Namuna:**
```
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567
```

## 🆔 Admin ID ni olish

1. Telegram da [@userinfobot](https://t.me/userinfobot) ni oching
2. `/start` buyrug'ini yuboring
3. O'z ID ingizni nusxalang

**Namuna:**
```
123456789
```

## 🐳 Docker bilan o'rnatish

### Prerequisites:
- Docker o'rnatilgan bo'lishi kerak
- docker-compose o'rnatilgan bo'lishi kerak

### O'rnatish:

```bash
# Repository ni klonlash
git clone https://github.com/username/telegram-movie-bot.git
cd telegram-movie-bot

# config.py yaratish
cp config.example.py config.py
nano config.py  # Tokenni kiriting

# Docker image yaratish va ishga tushirish
docker-compose up -d

# Loglarni ko'rish
docker-compose logs -f

# To'xtatish
docker-compose down
```

## 🖥️ Server da o'rnatish (Ubuntu)

### 1. Serverga ulanish

```bash
ssh user@your-server-ip
```

### 2. Zarur paketlarni o'rnatish

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git -y
```

### 3. Bot fayllarini yuklab olish

```bash
cd ~
git clone https://github.com/username/telegram-movie-bot.git
cd telegram-movie-bot
```

### 4. Virtual environment va kutubxonalar

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Konfiguratsiya

```bash
cp config.example.py config.py
nano config.py  # Tokenlarni kiriting
```

### 6. Screen yoki tmux da ishga tushirish

**Screen bilan:**
```bash
# Screen o'rnatish
sudo apt install screen -y

# Yangi session yaratish
screen -S moviebot

# Botni ishga tushirish
python bot.py

# Detach qilish: Ctrl+A, keyin D
# Qaytish: screen -r moviebot
```

**tmux bilan:**
```bash
# tmux o'rnatish
sudo apt install tmux -y

# Yangi session yaratish
tmux new -s moviebot

# Botni ishga tushirish
python bot.py

# Detach qilish: Ctrl+B, keyin D
# Qaytish: tmux attach -t moviebot
```

### 7. Systemd Service (tavsiya etiladi)

**Service fayl yaratish:**
```bash
sudo nano /etc/systemd/system/moviebot.service
```

**Quyidagi konfiguratsiyani kiriting:**
```ini
[Unit]
Description=Telegram Movie Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/telegram-movie-bot
Environment="PATH=/home/ubuntu/telegram-movie-bot/venv/bin"
ExecStart=/home/ubuntu/telegram-movie-bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Service ni yoqish:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable moviebot

# Start service
sudo systemctl start moviebot

# Status ko'rish
sudo systemctl status moviebot

# Loglarni ko'rish
sudo journalctl -u moviebot -f
```

**Service komandalar:**
```bash
# To'xtatish
sudo systemctl stop moviebot

# Qayta ishga tushirish
sudo systemctl restart moviebot

# O'chirish
sudo systemctl disable moviebot
```

## 🔄 Yangilash

### Git bilan:
```bash
cd telegram-movie-bot
git pull
pip install -r requirements.txt
# Bot ni qayta ishga tushiring
```

### Qo'lda:
1. Yangi fayllarni yuklab oling
2. Eski `database.db` va `config.py` ni saqlang
3. Yangi fayllarni joylashtiring
4. Kutubxonalarni yangilang: `pip install -r requirements.txt`

## ❗ Muammolarni hal qilish

### Bot ishga tushmayapti

**1. Token xatosi:**
```
telegram.error.InvalidToken
```
✅ `config.py` da tokenni tekshiring

**2. Module topilmadi:**
```
ModuleNotFoundError: No module named 'telegram'
```
✅ Virtual environment aktivligini tekshiring:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
✅ Kutubxonalarni qayta o'rnating:
```bash
pip install -r requirements.txt
```

**3. Permission denied (Linux):**
```bash
chmod +x run.sh
./run.sh
```

**4. Database xatosi:**
```bash
# Database faylini o'chiring (MA'LUMOTLAR YO'QOLADI!)
rm database.db
# Botni qayta ishga tushiring
python bot.py
```

### Bot sekin ishlayapti

- Server resurslarini tekshiring
- Database hajmini tekshiring
- Loglarni tahlil qiling

### Video yuborilmayapti

- Video hajmi 50MB dan oshmaganligini tekshiring
- Telegram API limitlarini tekshiring
- Bot admin kanalga qo'shilganligini tekshiring

## 📊 Monitoring

### Loglarni ko'rish

**Fayl orqali:**
```bash
tail -f bot.log
```

**Systemd orqali:**
```bash
sudo journalctl -u moviebot -f
```

### Database backup

```bash
# Backup yaratish
cp database.db database.backup.db

# Cron job o'rnatish (har kuni)
crontab -e
# Quyidagini qo'shing:
0 2 * * * cp /path/to/database.db /path/to/backups/database.$(date +\%Y\%m\%d).db
```

## 🔒 Xavfsizlik

1. **config.py ni GitHub ga joylashmang!**
   - `.gitignore` da qo'shilgan

2. **Database ni himoyalang**
   - Faqat bot user ga ruxsat bering

3. **Server xavfsizligi**
   - Firewall sozlang
   - SSH key authentication ishlating
   - Muntazam yangilanmalar

4. **Backup qiling**
   - Database
   - Config fayllar
   - Loglar

## 📞 Yordam

Muammolar yuzaga kelsa:

1. Loglarni tekshiring: `tail -f bot.log`
2. README.md ni o'qing
3. GitHub da issue yarating
4. [Telegram](https://t.me/your_username) orqali bog'laning

## ✅ O'rnatish checklist

- [ ] Python o'rnatildi
- [ ] Virtual environment yaratildi
- [ ] Kutubxonalar o'rnatildi
- [ ] config.py yaratildi va sozlandi
- [ ] Bot tokeni kiritildi
- [ ] Admin ID kiritildi
- [ ] Bot ishga tushdi
- [ ] /start komandasi ishladi
- [ ] Database yaratildi
- [ ] Monitoring sozlandi (ixtiyoriy)
- [ ] Backup sozlandi (ixtiyoriy)

---

🎉 **Omad! Bot tayyor!**