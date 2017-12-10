import sys
from urllib import urlopen
import json
from collections import OrderedDict
from datetime import datetime

from stats.calc import update_obj_by_rules

RULES = {

    'max': ['price_usd', '24h_volume_usd', 'volume_usd'],
    'min': ['price_usd'],

}

class CoinmarketcapBitcoin(object):
    URL = "https://api.coinmarketcap.com/v1/ticker/bitcoin/"
    
    def update(self, cls, date=None, path=None):
        data = json.loads(urlopen(self.URL).read())

        if date:
            obj = cls.get_by_id("bitcoin|%s" % date)
            if not obj:
                obj = cls(id="bitcoin|%s" % date)

            update_obj_by_rules(obj, data[0], RULES)

            obj.put()

        if path:
            D = OrderedDict()

            url = "https://graphs.coinmarketcap.com/currencies/bitcoin/%s/" % path
            data = json.loads(urlopen(url).read())

            for row in data["price_usd"]:
                ts = row[0] / 1000
                date = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")

                if date in D:
                    obj = D[date]
                else:
                    obj = cls.get_by_id("bitcoin|%s" % date)
                    if not obj:
                        obj = cls(id="bitcoin|%s" % date)
                    D[date] = obj
                obj.date = date
                update_obj_by_rules(obj, {"price_usd": row[1]}, RULES)
                print obj.max_price_usd

            for row in data["volume_usd"]:
                ts = row[0] / 1000
                date = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")

                if date in D:
                    obj = D[date]
                else:
                    obj = cls.get_by_id("bitcoin|%s" % date)
                    if not obj:
                        obj = cls(id="bitcoin|%s" % date)
                    D[date] = obj
                update_obj_by_rules(obj, {"volume_usd": row[1]}, RULES)


            for date, obj in D.iteritems():
                print date
                obj.put()
                
                
        return True
        
       
