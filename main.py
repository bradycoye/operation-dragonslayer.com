# -*- coding: utf-8 -*-

import logging
logging.basicConfig(level=logging.DEBUG)

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect, url_for, jsonify

from google.appengine.api.mail import send_mail

from charts import DayStats

app = Flask(__name__)
app.config['DEBUG'] = True

# -- stats

@app.route('/stats/bitcoin/update')
def stats_bitcoin_update():
    ret = DayStats.update(next=request.values.get("next", None))
    return str(ret)

@app.route('/charts/bitcoin')
def charts_bitcoin():
    return render_template('charts.html')

@app.route('/charts/bitcoin/data')
def charts_bitcoin_data():
    return jsonify(DayStats.get_data())

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

