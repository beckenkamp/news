# -*- coding: utf-8 -*-
import os.path
import datetime
import atexit
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from newspaper import Article
from slugify import slugify
from apscheduler.schedulers.background import BackgroundScheduler

from get_urls import get_urls


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/news.db'
app.config['SECRET_KEY'] = 'dev key'

db = SQLAlchemy(app)
cron = BackgroundScheduler()

# Explicitly kick off the background thread
cron.start()


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_url = db.Column(db.String(500))
    slug = db.Column(db.String(500))
    title = db.Column(db.String(500))
    text = db.Column(db.Text)
    top_image = db.Column(db.String(500))
    summary = db.Column(db.Text)
    article_html = db.Column(db.Text)
    created_at = db.Column(db.DateTime)

    def __init__(self, source_url):
        self.source_url = source_url

    def __repr__(self):
        return self.title


@cron.scheduled_job('interval', id='get_news', hours=8)
def get_news():
    urls = get_urls()
    news = News.query.with_entities(News.source_url).all()

    used_urls = []
    for n in news:
        used_urls.append(n[0])

    for url in urls:
        if not url in used_urls:
            used_urls.append(url)

            article = Article(url, language='pt', keep_article_html=True)
            article.download()
            article.parse()
            article.nlp()

            news_article = News(url)
            news_article.slug = slugify(article.title)
            news_article.title = article.title
            news_article.text = article.text
            news_article.top_image = article.top_image
            news_article.summary = article.summary
            news_article.article_html = article.article_html
            news_article.created_at = datetime.datetime.now()

            exists_this_news = News.query.filter_by(source_url=url).first()

            if not exists_this_news:
                print(url)
                db.session.add(news_article)
                db.session.commit()


@app.route('/')
def show_news():
    news = News.query.all()
    return render_template('index.html', news=news)


@app.route('/<slug>')
def show_article(slug):
    article = News.query.filter_by(slug=slug).first()
    return render_template('detail.html', article=article)


# Shutdown your cron thread if the web process is stopped
atexit.register(lambda: cron.shutdown(wait=False))

if __name__ == '__main__':
    if not os.path.isfile(app.config['SQLALCHEMY_DATABASE_URI']):
        db.create_all()

    app.run(debug=True)
