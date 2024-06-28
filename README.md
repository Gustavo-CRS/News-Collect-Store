# News-Collect-Store

Solution that crawls for articles from a news website, cleanses the response, stores in BigQuery, then makes it available to search via an API.

## Requirements

All the requeriments needs to be installed in your machine are in the requirements.txt file. You can install them by running the following command:

```bash
pip install -r requirements.txt
```

## Setting up the Google Cloud Project

To run the project you need to have a Google Cloud Project and a BigQuery table. You can create a project by following the steps in the following link: https://cloud.google.com/resource-manager/docs/creating-managing-projects

After creating the project you need to create a BigQuery table. You can do this by following the steps in the following link: https://cloud.google.com/bigquery/docs/tables

## Setting up the Google Cloud Credentials

To run the project you need to have a Google Cloud Credentials. You can create a service account key by following the steps in the following link: https://cloud.google.com/iam/docs/creating-managing-service-account-keys

After creating the service account key you need to make sure that Dotenv is configured with the necessary credentials. You can do this by following the .env.example file and creating a .env file with your project credentials.

## Running the Web Crawler

To run the web crawler and sends the data to the BigQuery you need to run the following command:

```bash
scrapy crawl bbc
```

or you can create a file containing the news by adding this to previous command:

```bash
scrapy crawl bbc -o name_of_your_choice.json
```

_obs_: Make sure to run the command in the news_crawler directory.

More information can be found in scrapy documentation: https://docs.scrapy.org/en/latest/topics/commands.html

## Running the API

To run the API you need to run the following command:

```bash
python search_article.py
```

_obs_: Make sure to run the command in the api directory.

Once the Flask application is running, you can search for articles by making a GET request to the /search endpoint with a keyword parameter:

```bash
http://127.0.0.1:5000/search?keyword=your_keyword
```
