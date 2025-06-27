import os
import random
import requests
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from openai import OpenAI
import json
import time

# Конфигурация
TELEGRAM_TOKEN = "YOUR_TELEGRAM_TOKEN"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
GOOGLE_TRENDS_URL = "https://trends.google.com/trends/api/explore"

# Инициализация клиентов
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def get_trending_topics():
    """Получение популярных тем из Google Trends"""
    try:
        response = requests.get(GOOGLE_TRENDS_URL, params={"hl": "ru"})
        data = json.loads(response.text)
        return [item["topic"] for item in data["default"]["trendingSearchesDays"][0]["trendingSearches"]]
    except Exception as e:
        print(f"Ошибка получения трендов: {e}")
        return ["технологии", "здоровье", "экономика", "разработка"]

def generate_article(topic):
    """Генерация статьи с помощью OpenAI"""
    prompt = f"Напиши статью объемом 500 слов на тему '{topic}'. Сделай ее интересной и информативной."
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка генерации статьи: {e}")
        return "Не удалось сгенерировать статью. Попробуйте позже."

def start(update, context):
    update.message.reply_text("Привет! Я бот, который пишу статьи по популярным темам. Напишите /generate, чтобы получить статью.")

def generate(update, context):
    trending_topics = get_trending_topics()
    selected_topic = random.choice(trending_topics)
    
    update.message.reply_text(f"Генерирую статью по теме: {selected_topic}...")
    article = generate_article(selected_topic)
    
    # Разбиваем длинный текст на части (Telegram имеет лимит 4096 символов)
    chunks = [article[i:i+4000] for i in range(0, len(article), 4000)]
    
    for chunk in chunks:
        update.message.reply_text(chunk)
        time.sleep(1)  # Задержка между частями

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("generate", generate))
    
    print("Бот запущен...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
