import logging
import sys
import json

from google.appengine.ext import ndb


class DayStats(ndb.Expando):
    date = ndb.StringProperty()

    @classmethod
    def update(cls, coin="bitcoin", next=None):
        from stats.blockchair import BlockchairBitcoin        
        ret = BlockchairBitcoin().update(cls, next=next)
        
        if not next:
            try:    
                from stats.coinmarketcap import CoinmarketcapBitcoin
                CoinmarketcapBitcoin().update(cls, ret["date"])
            except:
                logging.exception("coinmarketcap")
                
            try:
                from stats.calc import calc_extra_attrs
                calc_extra_attrs(cls, ret["date"])
            except:
                logging.exception("extra_attrs")

        return ret
        
    @classmethod
    def get_data(cls):
        objs = cls.query().order(cls.date).fetch(1000)
        result = {
            "labels": ["block_count", "max_difficulty"],
            "data": [[], []],
        }
        for obj in objs:
            data = result["data"]
            data[0].append([obj.date, getattr(obj, "block_count", 0)])
            data[1].append([obj.date, getattr(obj, "max_difficulty", 0)])
        
        return result
