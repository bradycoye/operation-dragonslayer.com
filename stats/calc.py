import logging

def update_obj_by_rules(obj, data, rules):
    for rule, attrs in rules.items():
        if rule == 'min':
            for attr in attrs:
                try:
                    new_val = data.get(attr, None)
                    old_val = getattr(obj, "min_%s" % attr, None)
                    if new_val is None:
                        continue
                    if old_val is not None and new_val > old_val:
                        continue
                    setattr(obj, "min_%s" % attr, int(float(new_val)))
                except:
                    logging.exception("min_%s" % attr)
        if rule == 'max':
            for attr in attrs:
                try:
                    new_val = data.get(attr, None)
                    old_val = getattr(obj, "max_%s" % attr, None)
                    if new_val is None:
                        continue
                    if old_val is not None and new_val < old_val:
                        continue
                    setattr(obj, "max_%s" % attr, int(float(new_val)))
                except:
                    logging.exception("max_%s" % attr)
                
        if rule == 'sum':
            for attr in attrs:
                try:
                    new_val = data.get(attr, None)
                    old_val = getattr(obj, "sum_%s" % attr, None)
                    if old_val is None:
                        setattr(obj, "sum_%s" % attr, int(float(new_val)))
                    elif new_val is not None:
                        setattr(obj, "sum_%s" % attr, int(float(old_val + int(float(new_val)) )))
                except:
                    logging.exception("sum_%s" % attr)
                                    

def get_supply(block):
    supply = 0
    for i in xrange(int(block)):
        reward = 50.0 / 2**((i+1) / 210000)
        supply += reward
    return supply

def calc_extra_attrs(cls, date):
    obj = cls.get_by_id("bitcoin|%s" % date)
    if not obj:
        return

    obj.supply = int(get_supply(obj.max_id))
    try:
        obj.market_cap = int(float(obj.supply)) * int(float(obj.max_price_usd))
    except:
        pass
    try:
        obj.sum_transaction_count_square = int(float(obj.sum_transaction_count)) ** 2
    except:
        pass
    obj.put()
    
