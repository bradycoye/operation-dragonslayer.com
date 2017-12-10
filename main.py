# -*- coding: utf-8 -*-

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect, url_for

from google.appengine.api.mail import send_mail

app = Flask(__name__)
app.config['DEBUG'] = True

# -- stats

@app.route('/stats/bitcoin/update')
def stats_bitcoin_update():
    from charts import DayStats
    ret = DayStats.update()
    return str(ret)

# -- general

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.errorhandler(404)
def page_not_found(e):
    return '404 No dragonslayers here.', 404

