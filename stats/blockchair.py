import sys
from urllib import urlopen
import json
from util.slugify import slugify
from stats.calc import update_obj_by_rules
from stats import realtime
RULES = {

    'min': ['id'],
    'max': ['id', 'size', 'weight', 'difficulty', 'fee_per_kb_usd'],
    'sum': [
        'transaction_count',
        'witness_count',
        'input_count', 
        'output_count',
        'input_total_usd',
        'output_total_usd',
        'fee_total_usd',
        'cdd_total',
        'generation_usd',
        'reward_usd',
    ],

}

class BlockchairBitcoin(object):
    COIN = "bitcoin"
    URL = "https://api.blockchair.com/bitcoin"
    
    def update(self, cls, next=None):
        url = self.URL + "/blocks"
        if next:
            url += "?s=id(asc)&next=%s&next_sort=%s" % (next, next)
    
        data = json.loads(urlopen(url).read())
        if not next:
            data["data"].reverse()

        date = data["data"][-1]["date"]

        obj = cls.get_by_id("bitcoin|%s" % date)
        if not obj:
            obj = cls(id="bitcoin|%s" % date)
        
        count = 0
        for block in data["data"]:
            if block["date"] != date:
                continue
            if getattr(obj, "max_id", None):
                if block["id"] <= obj.max_id:
                    continue
            
            self.update_obj(obj, block)
            realtime.update_data(self, obj, block)
            count += 1

        obj.put()
        return {"date": date, "count": count}

    def update_obj(self, obj, block):
        obj.date = block.get("date", "none")
        obj.block_count = getattr(obj, "block_count", 0) + 1
        miner = slugify(block.get("guessed_miner", "none"))
        setattr(obj, "miner_%s" % miner, getattr(obj, "miner_%s" % miner, 0) + 1)
        return update_obj_by_rules(obj, block, RULES)
    
    def update_output(self, cls, recipient, next=None):
        url = self.URL + "/outputs?q=recipient(%s)" % recipient

        if next:
            url += "&next=%s" % next
    
        data = json.loads(urlopen(url).read())
        
        for item in data["data"]:
            txdata = json.loads(urlopen(self.URL + '/outputs?q=spending_transaction_id(%s)' % item["transaction_id"]).read())
            item["txdata"] = txdata
        
        #obj = cls.get_by_id("bitcoin|%s" % date)
        #if not obj:
        #    obj = cls(id="bitcoin|%s" % date)
        
        #obj.put()
        
        return data

    
class BlockchairBitcoinCash(BlockchairBitcoin):
    COIN = "bitcoin-cash"
    URL = "https://api.blockchair.com/bitcoin-cash"

