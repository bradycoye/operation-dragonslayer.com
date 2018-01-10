import logging
import sys
import json
from datetime import datetime, timedelta

from google.appengine.ext import ndb

from flask import request
from flask import g

from stats import realtime

EXCLUDED_PROPERTIES = ["date"]
"""
PROPERTIES = [
    "max_id",
    "min_id",
    "block_count",
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
"""

from stats.blockchair import BlockchairBitcoin, BlockchairBitcoinCash
from stats.coinmarketcap import CoinmarketcapBitcoin, CoinmarketcapBitcoinCash


class DayStats(ndb.Expando):
    COIN = "bitcoin"
    BLOCKCHAIR = BlockchairBitcoin
    COINMARKETCAP = CoinmarketcapBitcoin

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
    
        ret = cls.BLOCKCHAIR().update(cls, next=next)
        
        if not next:
            try:    
                if request.values.get("path"):
                    cls.COINMARKETCAP().update(cls, path=request.values.get("path"))
                else:
                    cls.COINMARKETCAP().update(cls, date=ret["date"])
                
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
        date_start = datetime.strptime("2013-01-01", "%Y-%m-%d")
        date_end = datetime.now() - timedelta(days=g.user_model.get_actual_lag())
        if range == "1w":
            date_start = date_end - timedelta(days=7)
        if range == "1m":
            date_start = date_end - timedelta(days=30)
        if range == "1y":
            date_start = date_end - timedelta(days=365)
        
        date_start = date_start.strftime("%Y-%m-%d")
        date_end = date_end.strftime("%Y-%m-%d")
        
        objs = cls.query(cls.date >= date_start, cls.date <= date_end).order(cls.date).fetch(10000)
        PROPERTIES = set()
        for obj in objs:
            PROPERTIES = PROPERTIES.union(obj._properties.keys())
        PROPERTIES = PROPERTIES - set(EXCLUDED_PROPERTIES)
        PROPERTIES = sorted(list(PROPERTIES))
        result = {
            "labels": PROPERTIES,
            "data": [[] for x in PROPERTIES],
            "realtime": realtime.get_data(cls),
        }
        if not objs:
            return result
        
        
        for obj in objs:
            data = result["data"]
            for id, prop in enumerate(PROPERTIES):
                data[id].append([obj.date, getattr(obj, prop, 0)])
        
        return result
        
class DayStatsBCH(DayStats):
    COIN = "bitcoin-cash"
    BLOCKCHAIR = BlockchairBitcoinCash
    COINMARKETCAP = CoinmarketcapBitcoinCash

