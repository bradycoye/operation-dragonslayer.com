import sys
from urllib import urlopen
import json

from stats.calc import update_obj_by_rules

RULES = {

    'max': ['price_usd', '24h_volume_usd'],

}

class CoinmarketcapBitcoin(object):
    URL = "https://api.coinmarketcap.com/v1/ticker/bitcoin/"
    
    def update(self, cls, date):
        data = json.loads(urlopen(self.URL).read())

        obj = cls.get_by_id("bitcoin|%s" % date)
        if not obj:
            obj = cls(id="bitcoin|%s" % date)

        update_obj_by_rules(obj, data[0], RULES)

        obj.put()
        
        return True
