import scrapy
import requests
import os
import pandas as pd

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
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        self.client = bigquery.Client(credentials=credentials)
        self.dataset_id = os.getenv('BIGQUERY_DATASET_ID').split('.')[-1]
        self.table_id = os.getenv('BIGQUERY_TABLE_ID').split('.')[-1]

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
        self.send_to_bigquery(article)
        yield article

    def send_to_bigquery(self, article):
        data = [{
            'url': article['url'],
            'headline': article['headline'],
            'article_text': article['article_text'],
            'author': article['author'],
            'publication_date': article['publication_date']
        }]

        df = pd.DataFrame(data)

        schema = [
            bigquery.SchemaField("url", "STRING"),
            bigquery.SchemaField("headline", "STRING"),
            bigquery.SchemaField("article_text", "STRING"),
            bigquery.SchemaField("author", "STRING"),
            bigquery.SchemaField("publication_date", "STRING")
        ]

        table_ref = self.client.dataset(self.dataset_id).table(self.table_id)
        job_config = bigquery.LoadJobConfig(schema=schema)
        job = self.client.load_table_from_dataframe(df, table_ref, job_config=job_config)

        job.result()

        if job.errors:
            self.logger.error('Error inserting rows into BigQuery: %s', job.errors)
        else:
            self.logger.info('Successfully inserted row into BigQuery')