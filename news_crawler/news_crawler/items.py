import scrapy

class NewsArticle(scrapy.Item):
    headline = scrapy.Field()
    author = scrapy.Field()
    publication_date = scrapy.Field()
    article_text = scrapy.Field()
    url = scrapy.Field()