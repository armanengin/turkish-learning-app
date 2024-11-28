from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-key')  # Use environment variable in production
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///turkish_learning.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    progress = db.Column(db.Integer, default=0)
    last_word_date = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    turkish = db.Column(db.String(100), nullable=False)
    english = db.Column(db.String(100), nullable=False)
    example = db.Column(db.String(200))
    difficulty = db.Column(db.Integer, default=1)

# Sample data
DAILY_WORDS = [
    {"turkish": "merhaba", "english": "hello", "example": "Merhaba, nasılsın?", "category": "greetings"},
    {"turkish": "teşekkürler", "english": "thank you", "example": "Teşekkürler, çok naziksin.", "category": "greetings"},
    {"turkish": "lütfen", "english": "please", "example": "Lütfen buraya gel.", "category": "common"},
    {"turkish": "günaydın", "english": "good morning", "example": "Günaydın! Nasıl uyudun?", "category": "greetings"},
    {"turkish": "iyi akşamlar", "english": "good evening", "example": "İyi akşamlar! Hoş geldiniz.", "category": "greetings"},
    {"turkish": "hoşça kal", "english": "goodbye", "example": "Hoşça kal, yarın görüşürüz.", "category": "greetings"},
    {"turkish": "evet", "english": "yes", "example": "Evet, ben de öyle düşünüyorum.", "category": "common"},
    {"turkish": "hayır", "english": "no", "example": "Hayır, teşekkür ederim.", "category": "common"},
    {"turkish": "su", "english": "water", "example": "Bir bardak su, lütfen.", "category": "food"},
    {"turkish": "ekmek", "english": "bread", "example": "Taze ekmek aldım.", "category": "food"},
    {"turkish": "kahve", "english": "coffee", "example": "Türk kahvesi içer misin?", "category": "food"},
    {"turkish": "çay", "english": "tea", "example": "Çay her zaman iyidir.", "category": "food"},
    {"turkish": "kitap", "english": "book", "example": "Bu kitap çok ilginç.", "category": "objects"},
    {"turkish": "kalem", "english": "pen", "example": "Mavi kalem var mı?", "category": "objects"},
    {"turkish": "masa", "english": "table", "example": "Masa üstünde ne var?", "category": "furniture"},
    {"turkish": "sandalye", "english": "chair", "example": "Lütfen sandalyeye otur.", "category": "furniture"},
    {"turkish": "ev", "english": "house", "example": "Evimiz çok güzel.", "category": "places"},
    {"turkish": "okul", "english": "school", "example": "Okula yürüyerek gidiyorum.", "category": "places"},
    {"turkish": "park", "english": "park", "example": "Parkta yürüyüş yapalım.", "category": "places"},
    {"turkish": "hastane", "english": "hospital", "example": "Hastane nerede?", "category": "places"},
    {"turkish": "araba", "english": "car", "example": "Yeni bir araba aldım.", "category": "transportation"},
    {"turkish": "otobüs", "english": "bus", "example": "Otobüs beşte gelecek.", "category": "transportation"},
    {"turkish": "telefon", "english": "phone", "example": "Telefonum çalıyor.", "category": "technology"},
    {"turkish": "bilgisayar", "english": "computer", "example": "Bilgisayarım bozuldu.", "category": "technology"},
    {"turkish": "güzel", "english": "beautiful", "example": "Ne güzel bir gün!", "category": "adjectives"}
]

GRAMMAR_LESSONS = [
    {
        "title": "Basic Pronouns",
        "content": """Turkish personal pronouns are essential for basic communication:
        - Ben (I)
        - Sen (You, informal)
        - O (He/She/It)
        - Biz (We)
        - Siz (You, plural or formal)
        - Onlar (They)
        
        These pronouns change form based on their role in the sentence (subject, object, possessive).""",
        "examples": [
            "Ben Türkçe öğreniyorum. (I am learning Turkish)",
            "Sen nerelisin? (Where are you from?)",
            "O öğretmen. (He/She is a teacher)"
        ],
        "video_link": "https://www.youtube.com/watch?v=EhqZBt7Uhyk",
        "difficulty": "beginner"
    },
    {
        "title": "Present Continuous Tense (-yor)",
        "content": """The present continuous tense in Turkish is formed by adding -yor to the verb stem.
        Steps:
        1. Remove the -mek/-mak from the infinitive
        2. Add appropriate buffer vowel (ı, i, u, ü)
        3. Add -yor
        4. Add personal ending""",
        "examples": [
            "Yürü-yor-um (I am walking)",
            "Gel-iyor-sun (You are coming)",
            "Gid-iyor (He/She is going)"
        ],
        "video_link": "https://www.youtube.com/watch?v=r-2osByMQGg",
        "difficulty": "intermediate"
    },
    {
        "title": "Vowel Harmony",
        "content": """Turkish has two types of vowel harmony:
        1. Two-fold (e/a): If the last vowel is 'e' or 'i', use 'e'; if it's 'a' or 'ı', use 'a'
        2. Four-fold (i/ı/ü/u): Follow the rules of back/front and rounded/unrounded vowels""",
        "examples": [
            "ev-ler (houses) - last vowel 'e' → use 'e'",
            "kitap-lar (books) - last vowel 'a' → use 'a'",
            "göz-lük (glasses) - last vowel 'ö' → use 'ü'"
        ],
        "video_link": "https://www.youtube.com/watch?v=_FFQQAB2ds4",
        "difficulty": "intermediate"
    },
    {
        "title": "Simple Past Tense (-di)",
        "content": """The simple past tense in Turkish uses the -di suffix (with vowel harmony):
        -di, -dı, -du, -dü (after voiced consonants)
        -ti, -tı, -tu, -tü (after unvoiced consonants)""",
        "examples": [
            "Gel-di-m (I came)",
            "Bak-tı-n (You looked)",
            "Git-ti (He/She went)"
        ],
        "video_link": "https://www.youtube.com/watch?v=fh1ptOu8Jl8",
        "difficulty": "intermediate"
    },
    {
        "title": "Possession Suffixes",
        "content": """Possession in Turkish is shown by adding suffixes to nouns:
        -(i)m - my
        -(i)n - your
        -(s)i - his/her
        -(i)miz - our
        -(i)niz - your (plural)
        -leri - their""",
        "examples": [
            "ev-im (my house)",
            "kitab-ın (your book)",
            "araba-sı (his/her car)"
        ],
        "video_link": "https://www.youtube.com/watch?v=bH2iRwfBFPs",
        "difficulty": "intermediate"
    },
    {
        "title": "Locative Case (-de/-da)",
        "content": """The locative case indicates location and uses -de/-da (with consonant harmony):
        -de/-da (after voiced consonants)
        -te/-ta (after unvoiced consonants)""",
        "examples": [
            "ev-de (at home)",
            "okul-da (at school)",
            "park-ta (at the park)"
        ],
        "video_link": "https://www.youtube.com/watch?v=sGYfKuYgyos",
        "difficulty": "beginner"
    }
]

# Popular words by category
POPULAR_WORDS = {
    "Essential Phrases": [
        {"turkish": "nasılsın", "english": "how are you", "example": "Merhaba, nasılsın?", "usage_frequency": "very high"},
        {"turkish": "hoş geldin", "english": "welcome", "example": "Evimize hoş geldin!", "usage_frequency": "very high"},
        {"turkish": "görüşürüz", "english": "see you", "example": "Yarın görüşürüz!", "usage_frequency": "very high"},
        {"turkish": "afiyet olsun", "english": "enjoy your meal", "example": "Afiyet olsun, güzel görünüyor.", "usage_frequency": "very high"},
        {"turkish": "kolay gelsin", "english": "may it be easy (said to someone working)", "example": "Kolay gelsin, iyi çalışmalar!", "usage_frequency": "very high"}
    ],
    "Common Verbs": [
        {"turkish": "gitmek", "english": "to go", "example": "Okula gidiyorum.", "usage_frequency": "very high"},
        {"turkish": "gelmek", "english": "to come", "example": "Eve geliyorum.", "usage_frequency": "very high"},
        {"turkish": "yapmak", "english": "to do/make", "example": "Yemek yapıyorum.", "usage_frequency": "very high"},
        {"turkish": "istemek", "english": "to want", "example": "Su istiyorum.", "usage_frequency": "very high"},
        {"turkish": "bilmek", "english": "to know", "example": "Bilmiyorum.", "usage_frequency": "very high"}
    ],
    "Food & Drinks": [
        {"turkish": "çorba", "english": "soup", "example": "Mercimek çorbası çok lezzetli.", "usage_frequency": "high"},
        {"turkish": "pilav", "english": "rice", "example": "Tavuklu pilav yedim.", "usage_frequency": "high"},
        {"turkish": "döner", "english": "döner kebab", "example": "Bir döner alabilir miyim?", "usage_frequency": "high"},
        {"turkish": "ayran", "english": "yogurt drink", "example": "Dönerle ayran iyi gider.", "usage_frequency": "high"},
        {"turkish": "baklava", "english": "baklava", "example": "Tatlı olarak baklava aldım.", "usage_frequency": "high"}
    ],
    "Question Words": [
        {"turkish": "ne", "english": "what", "example": "Ne yapıyorsun?", "usage_frequency": "very high"},
        {"turkish": "nerede", "english": "where", "example": "Nerede oturuyorsun?", "usage_frequency": "very high"},
        {"turkish": "ne zaman", "english": "when", "example": "Ne zaman geleceksin?", "usage_frequency": "very high"},
        {"turkish": "neden", "english": "why", "example": "Neden geç kaldın?", "usage_frequency": "very high"},
        {"turkish": "nasıl", "english": "how", "example": "Nasıl giderim?", "usage_frequency": "very high"}
    ],
    "Numbers & Time": [
        {"turkish": "bir", "english": "one", "example": "Bir dakika bekle.", "usage_frequency": "very high"},
        {"turkish": "iki", "english": "two", "example": "İki kişiyiz.", "usage_frequency": "very high"},
        {"turkish": "üç", "english": "three", "example": "Üç gün sonra.", "usage_frequency": "very high"},
        {"turkish": "saat", "english": "hour/clock", "example": "Saat kaç?", "usage_frequency": "very high"},
        {"turkish": "dakika", "english": "minute", "example": "Beş dakika kaldı.", "usage_frequency": "very high"}
    ]
}

def get_daily_word():
    # Get total number of words
    total_words = len(DAILY_WORDS)
    
    # Use the current date to determine which word to show
    current_date = datetime.now()
    # Create a number from 0 to total_words-1 based on the date
    # This ensures the same word appears for everyone on the same day
    day_number = (current_date.year * 366 + current_date.month * 31 + current_date.day) % total_words
    
    return DAILY_WORDS[day_number]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/daily-word')
def daily_word():
    return jsonify(get_daily_word())

@app.route('/grammar-lesson')
def grammar_lesson():
    lesson_id = request.args.get('lesson', 0, type=int)
    return jsonify(GRAMMAR_LESSONS[lesson_id])

@app.route('/progress')
def progress():
    # For demo, return fixed progress
    return jsonify({"progress": 30})

@app.route('/popular-words')
def popular_words():
    return jsonify(POPULAR_WORDS)

@app.route('/popular-words/<category>')
def popular_words_category(category):
    return jsonify(POPULAR_WORDS.get(category, []))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Only use debug mode when running locally
    is_development = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 5004))
    app.run(host='0.0.0.0', port=port, debug=is_development)
