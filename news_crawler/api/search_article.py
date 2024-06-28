from flask import Flask, request, jsonify
from google.cloud import bigquery
from google.oauth2 import service_account
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
credentials = service_account.Credentials.from_service_account_file(credentials_path)
client = bigquery.Client(credentials=credentials)
dataset_id = os.getenv('BIGQUERY_DATASET_ID').split('.')[-1]
table_id = os.getenv('BIGQUERY_TABLE_ID').split('.')[-1]
table_ref = f"{dataset_id}.{table_id}"

@app.route('/search', methods=['GET'])
def search_articles():
    keyword = request.args.get('keyword', None)
    if not keyword:
        return jsonify({'error': 'Keyword is required'}), 400

    query = f"""
    SELECT url, headline, article_text, author, publication_date
    FROM `{table_ref}`
    WHERE
        headline LIKE '%{keyword}%' OR
        article_text LIKE '%{keyword}%' OR
        author LIKE '%{keyword}%'
    """

    query_job = client.query(query)

    results = []
    for row in query_job:
        results.append({
            'url': row['url'],
            'headline': row['headline'],
            'article_text': row['article_text'],
            'author': row['author'],
            'publication_date': row['publication_date']
        })

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
