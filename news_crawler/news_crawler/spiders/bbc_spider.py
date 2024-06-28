import scrapy
import requests
import os

from news_crawler.items import NewsArticle
from readability import Document
from bs4 import BeautifulSoup
from google.cloud import bigquery
from dotenv import load_dotenv
from google.oauth2 import service_account

load_dotenv()

class BbcSpider(scrapy.Spider):
    name = "bbc"
    allowed_domains = ["bbc.com"]
    start_urls = [
        'https://www.bbc.com/news'
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        credentials = service_account.Credentials.from_service_account_file(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
        self.client = bigquery.Client(credentials=credentials)
        self.dataset_id = str(os.getenv('BIGQUERY_DATASET_ID'))
        self.table_id = str(os.getenv('BIGQUERY_TABLE_ID')) 

    def parse(self, response):
        self.logger.info('Parsing main news page: %s', response.url)
        self.logger.info('Response status: %d', response.status)
        article_urls = response.css('a[data-testid="internal-link"]::attr(href)').getall()
        self.logger.info('Found %d article URLs', len(article_urls))
        filtered_urls = [url for url in article_urls if '/news/articles' in url]
        self.logger.info('Filtered %d article URLs', len(filtered_urls))
        for url in filtered_urls:
            yield response.follow(url, self.parse_article)

    def parse_article(self, response):
        self.logger.info('Parsing article page: %s', response.url)
        article = NewsArticle()
        article['url'] = response.url

        doc = Document(requests.get(response.url).content)
        article['headline'] = doc.short_title()
        
        author_parts = response.css('span[data-testid="byline-name"]::text').getall()
        article['author'] = author_parts[1] if author_parts else None
        article['publication_date'] = response.css('div[data-testid="byline"] time::text').get()
        soup = BeautifulSoup(doc.summary(), 'html.parser')
        article['article_text'] = soup.get_text(separator="\n", strip=True)

        self.logger.info('Scraped article: %s', article['headline'])
        yield article

    def send_to_bigquery(self, article):
        table_ref = self.client.dataset(self.dataset_id).table(self.table_id)
        table = self.client.get_table(table_ref)
        rows_to_insert = [{
            'url': article['url'],
            'headline': article['headline'],
            'article_text': article['article_text'],
            'author': article['author'],
            'publication_date': article['publication_date']
        }]
        errors = self.client.insert_rows_json(table, rows_to_insert)
        if errors:
            self.logger.error('Error inserting rows into BigQuery: %s', errors)
        else:
            self.logger.info('Successfully inserted row into BigQuery')