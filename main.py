# -*- coding: utf-8 -*-

import logging
logging.basicConfig(level=logging.DEBUG)

from datetime import datetime, timedelta
import json
from urllib import urlopen, urlencode
import re

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect, url_for, jsonify
from flask import g

import requests

from google.appengine.ext import ndb
from google.appengine.api.mail import send_mail
from google.appengine.api import users

from charts import DayStats, DayStatsBCH
from stats.blockchair import BlockchairBitcoin, BlockchairBitcoinCash

from local.config import predictions_url, proxy_auth

app = Flask(__name__)
app.config['DEBUG'] = True

class UserModel(ndb.Expando):
    EXPIRED_LAG = 7

    email = ndb.StringProperty()
    expires = ndb.StringProperty()
    lag = ndb.IntegerProperty()
    
    @classmethod
    def get_model(cls, user):
        model = None
        if user:
            model = cls.get_by_id(user.email())
            if model:
                logging.debug(model.__dict__)
                return model
            model = cls(id=user.email())
            model.email = user.email()
            model.expires = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            model.lag = 0
            model.put()
            return model
        model = cls(id="guest@example.com")
        model.email = "guest@example.com"
        model.expires = "3000-01-01"
        model.lag = cls.EXPIRED_LAG
        return model
        
    def is_expired(self):
        return datetime.now().strftime("%Y-%m-%d") > self.expires
        
    def get_actual_lag(self):
        if self.is_expired():
            return self.EXPIRED_LAG
        return self.lag

@app.before_request
def my_before_request():
    g.user = users.get_current_user()
    g.user_model = UserModel.get_model(g.user)
    if g.user:
        g.logout_url = users.create_logout_url('/')
    else:
        g.login_url = users.create_login_url('/')

@app.context_processor
def my_ctx():
    return {"g": g, "json": json}


def fetch_url(url, data=None):
    proxies = {
        'http': 'http://%s@us-wa.proxymesh.com:31280' % proxy_auth,
        'https': 'http://%s@us-wa.proxymesh.com:31280' % proxy_auth
    }
    if data is None:
        response = urlopen(url, proxies=proxies).read()
    else:
        response = urlopen(url, data=urlencode(data), proxies=proxies).read()
    return response
    
# -- predictions
@app.route('/' + predictions_url)
def predictions():
    return render_template('predictions.html')

@app.route('/predictions/compare.reddits')
def predictions_compare_reddits():
    data = json.loads(fetch_url("http://redditmetrics.com/ajax/compare.reddits", data={"reddit0": request.values.get("reddit0")}))
    return jsonify(data)

@app.route('/predictions/marketcap/currencies/<coin>/<ts1>/<ts2>/')
def predictions_marketcap(coin, ts1, ts2):
    try:
        data = json.loads(fetch_url("https://graphs.coinmarketcap.com/currencies/%s/%s/%s/" % (coin, ts1, ts2)))
        return jsonify(data)
    except Exception, e:
        return jsonify({'error': e})

@app.route('/predictions/subreddit/<coin>')
def predictions_subreddit(coin):
    html = fetch_url("https://coinmarketcap.com/currencies/%s/" % (coin))
    matches = re.findall("https://www.reddit.com/r/(.+).embed", html)
    if matches:
        subreddit = matches[0]
    else:
        subreddit = "none"
    return jsonify({'subreddit': subreddit})

    
    
# -- buzz
@app.route('/buzz/search')
def buzz_search():
    import tweepy
    from pprint import pprint
    import json

    from local.config import twitter_consumer, twitter_token
    
    auth = tweepy.OAuthHandler(twitter_consumer[0], twitter_consumer[1])
    auth.set_access_token(twitter_token[0], twitter_token[1])

    api = tweepy.API(auth)
       
    res = api.search(q=request.values.get("q"), count=100)   

    return jsonify({'result': [t._json for t in res]})


# -- stats

@app.route('/stats/bitcoin/update')
def stats_bitcoin_update():
    ret = DayStats.update(next=request.values.get("next", None))
    return str(ret)

@app.route('/charts/bitcoin')
def charts_bitcoin():
    return render_template('charts.html', CHARTS_DATA={"coin": "bitcoin"})

@app.route('/charts/bitcoin/data')
def charts_bitcoin_data():
    return jsonify(DayStats.get_data(range=request.values.get("range")))

@app.route('/stats/bitcoin-cash/update')
def stats_bch_update():
    ret = DayStatsBCH.update(next=request.values.get("next", None))
    return str(ret)

@app.route('/charts/bitcoin-cash')
def charts_bch():
    return render_template('charts_bch.html', CHARTS_DATA={"coin": "bitcoin-cash"})

@app.route('/charts/bitcoin-cash/data')
def charts_bch_data():
    return jsonify(DayStatsBCH.get_data(range=request.values.get("range")))


# -- transactions

@app.route('/transactions/bitcoin-cash/outputs/<recipient>/update')
def transactions_bch_outputs_update(recipient):
    data = BlockchairBitcoinCash().update_output(None, recipient, next=request.values.get("next", None))
    return jsonify(data)


from yours import YoursPost

# -- misc
@app.route('/misc/yours/update')
def misc_yours_update():
    return YoursPost.update()


@app.route('/misc/yours')
def misc_yours():
    return render_template('yours.html')

@app.route('/misc/yours/rank')
def misc_yours_rank():
    return render_template('yours_rank.html')
    
@app.route('/misc/yours/data.json')
def misc_yours_data():
    return jsonify(YoursPost.get_data())



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

