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
