import logging
import sys
import json

from google.appengine.ext import ndb


class DayStats(ndb.Expando):
    @classmethod
    def update(cls, coin="bitcoin"):
        from stats.blockchair import BlockchairBitcoin        
        ret = BlockchairBitcoin().update(cls)
        
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
