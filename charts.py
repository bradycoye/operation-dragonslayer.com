import logging
import sys
import json
from datetime import datetime, timedelta

from google.appengine.ext import ndb

from flask import request


PROPERTIES = [
    "max_size",
    "max_difficulty",
    "max_fee_per_kb_usd",
    'sum_transaction_count',
    'sum_input_count', 
    'sum_output_count',
    'sum_input_total_usd',
    'sum_output_total_usd',
    'sum_fee_total_usd',
    'sum_cdd_total',
    'sum_generation_usd',
    'sum_reward_usd',

    'max_price_usd',
    'min_price_usd',
    'max_24h_volume_usd',
    'max_volume_usd',
    
    'supply',
    'market_cap',
    'sum_transaction_count_square',
]

class DayStats(ndb.Expando):
    date = ndb.StringProperty()

    @classmethod
    def update(cls, coin="bitcoin", next=None):
        if request.values.get("calc_extra"):
            from stats.calc import calc_extra_attrs
            date = "2013-01-01"    
            objs = cls.query(cls.date > date).order(cls.date).fetch(10000)
            for obj in objs:
                try:
                    calc_extra_attrs(cls, obj.date)
                except:
                    logging.error("extra: failed %s" % obj.date)
            return "extra"
    
        from stats.blockchair import BlockchairBitcoin        
        ret = BlockchairBitcoin().update(cls, next=next)
        
        if not next:
            try:    
                from stats.coinmarketcap import CoinmarketcapBitcoin
                if request.values.get("path"):
                    CoinmarketcapBitcoin().update(cls, path=request.values.get("path"))
                else:
                    CoinmarketcapBitcoin().update(cls, date=ret["date"])
                
            except:
                logging.exception("coinmarketcap")
                
            try:
                from stats.calc import calc_extra_attrs
                calc_extra_attrs(cls, ret["date"])
            except:
                logging.exception("extra_attrs")

        return ret
        
    @classmethod
    def get_data(cls, range=None):
        date = "2013-01-01"
        if range == "1w":
            date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if range == "1m":
            date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if range == "1y":
            date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        objs = cls.query(cls.date > date).order(cls.date).fetch(10000)
        result = {
            "labels": PROPERTIES,
            "data": [[] for x in PROPERTIES],
        }
        for obj in objs:
            data = result["data"]
            for id, prop in enumerate(PROPERTIES):
                data[id].append([obj.date, getattr(obj, prop, 0)])
        
        return result
