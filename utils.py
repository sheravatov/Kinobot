"""
Yordamchi funksiyalar
"""

import re
from datetime import datetime
from typing import Optional

def validate_channel_username(username: str) -> bool:
    """
    Kanal username validatsiyasi
    Args:
        username: Kanal username (@siz)
    Returns:
        bool: True agar to'g'ri bo'lsa
    """
    username = username.replace('@', '')
    pattern = r'^[a-zA-Z0-9_]{5,32}$'
    return bool(re.match(pattern, username))

def format_number(number: int) -> str:
    """
    Raqamni formatlash (masalan: 1000 -> 1K)
    Args:
        number: Raqam
    Returns:
        str: Formatlangan raqam
    """
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"
    return str(number)

def format_datetime(dt: datetime) -> str:
    """
    Datetime ni formatlash
    Args:
        dt: Datetime obyekti
    Returns:
        str: Formatlangan sana
    """
    return dt.strftime("%d.%m.%Y %H:%M")

def escape_markdown(text: str) -> str:
    """
    Markdown maxsus belgilarni escape qilish
    Args:
        text: Matn
    Returns:
        str: Escape qilingan matn
    """
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

def extract_hashtags(text: str) -> list:
    """
    Matndan hashtaglarni ajratib olish
    Args:
        text: Matn
    Returns:
        list: Hashtag ro'yxati
    """
    return re.findall(r'#\w+', text)

def sanitize_filename(filename: str) -> str:
    """
    Fayl nomini tozalash
    Args:
        filename: Fayl nomi
    Returns:
        str: Tozalangan fayl nomi
    """
    # Maxsus belgilarni olib tashlash
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Bo'shliqlarni underscore bilan almashtirish
    filename = filename.replace(' ', '_')
    return filename

def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Matnni qisqartirish
    Args:
        text: Matn
        max_length: Maksimal uzunlik
        suffix: Qo'shimcha (default: ...)
    Returns:
        str: Qisqartirilgan matn
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def is_valid_year(year: str) -> bool:
    """
    Yil validatsiyasi
    Args:
        year: Yil (string)
    Returns:
        bool: True agar to'g'ri bo'lsa
    """
    try:
        year_int = int(year)
        current_year = datetime.now().year
        return 1900 <= year_int <= current_year + 5
    except ValueError:
        return False

def format_file_size(size_bytes: int) -> str:
    """
    Fayl hajmini formatlash
    Args:
        size_bytes: Hajm (baytlarda)
    Returns:
        str: Formatlangan hajm
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def get_time_ago(timestamp: datetime) -> str:
    """
    Vaqt farqini hisoblash (masalan: 2 soat oldin)
    Args:
        timestamp: Datetime obyekti
    Returns:
        str: Vaqt farqi
    """
    now = datetime.now()
    diff = now - timestamp
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "hozirgina"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} daqiqa oldin"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} soat oldin"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} kun oldin"
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f"{weeks} hafta oldin"
    elif seconds < 31536000:
        months = int(seconds / 2592000)
        return f"{months} oy oldin"
    else:
        years = int(seconds / 31536000)
        return f"{years} yil oldin"

def clean_html(text: str) -> str:
    """
    HTML teglarini olib tashlash
    Args:
        text: HTML matn
    Returns:
        str: Tozalangan matn
    """
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def generate_movie_id_from_title(title: str) -> str:
    """
    Kino nomidan ID yaratish
    Args:
        title: Kino nomi
    Returns:
        str: Unique ID
    """
    # Faqat harflar va raqamlar
    clean_title = re.sub(r'[^a-zA-Z0-9]', '', title.lower())
    # Timestamp qo'shish
    timestamp = str(int(datetime.now().timestamp()))
    return f"{clean_title[:20]}_{timestamp[-6:]}"