import os
import random
import time
import feedparser
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from transformers import pipeline
import wikipediaapi

# Инициализация локальной модели для генерации текста
summarizer = pipeline("summarization", model="Falconsai/text_summarization")  # Бесплатная модель

def get_rss_trends():
    """Получение трендов из RSS-лент мировых новостей"""
    try:
        # Список открытых RSS-лент
        sources = [
            "https://news.google.com/rss?hl=ru",
            "https://www.bbc.co.uk/news/world/rss.xml",
            "https://www.reuters.com/sitemap.xml"
        ]
        
        trends = []
        for source in sources:
            feed = feedparser.parse(source)
            for entry in feed.entries[:5]:  # Берем первые 5 статей
                title = entry.title.lower()
                if any(word in title for word in ["важно", "новое", "обновление"]):
                    trends.append(title.split()[0])  # Берем ключевое слово
        return list(set(trends))  # Удаляем дубликаты
    except Exception as e:
        print(f"Ошибка RSS: {e}")
        return ["технологии", "здоровье", "экономика"]

def generate_free_article(topic):
    """Генерация статьи через суммаризацию Википедии + шаблон"""
    wiki_wiki = wikipediaapi.Wikipedia('ru')
    
    try:
        # Поиск статьи по теме
        page_py = wiki_wiki.page(topic)
        if not page_py.exists():
            return f"Не найдено информации по теме '{topic}'"
            
        # Создаем шаблонную статью
        article = f"""
📌 Тема: {topic}
📊 Популярность: {random.randint(80, 95)}%
📅 Последнее обновление: {time.strftime("%Y-%m-%d")}
        
🔍 Основные факты:
1. {page_py.summary.split('.')[0]}
2. {page_py.summary.split('.')[1]}
3. {page_py.summary.split('.')[2]}

💡 Выводы:
{summarizer(page_py.summary, max_length=150, min_length=50, do_sample=False)[0]['summary_text']}
        """
        return article.strip()
    except Exception as e:
        print(f"Ошибка генерации: {e}")
        return "Не удалось создать статью. Попробуйте другую тему."

def start(update, context):
    update.message.reply_text(
        "Привет! Я - бесплатный бот для генерации статей.\n"
        "Напишите /generate, чтобы получить статью по актуальным темам."
    )

def generate(update, context):
    # Получаем тренды из RSS
    topics = get_rss_trends()
    selected_topic = random.choice(topics)
    
    update.message.reply_text(f"Генерирую статью по теме: {selected_topic}...")
    article = generate_free_article(selected_topic)
    
    # Разбиваем на части (Telegram лимит - 4096 символов)
    for i in range(0, len(article), 4000):
        update.message.reply_text(article[i:i+4000])
        time.sleep(1)  # Задержка между частями

def main():
    updater = Updater(os.getenv("TELEGRAM_TOKEN"), use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("generate", generate))
    
    print("Бот запущен... (бесплатная версия)")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
