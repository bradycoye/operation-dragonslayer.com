def update_obj_by_rules(obj, data, rules):
    for rule, attrs in rules.items():
        if rule == 'min':
            for attr in attrs:
                new_val = data.get(attr, None)
                old_val = getattr(obj, "min_%s" % attr, None)
                if old_val is None or new_val is not None and new_val < old_val:
                    setattr(obj, "min_%s" % attr, int(new_val))
        if rule == 'max':
            for attr in attrs:
                new_val = data.get(attr, None)
                old_val = getattr(obj, "max_%s" % attr, None)
                if old_val is None or new_val is not None and new_val > old_val:
                    setattr(obj, "max_%s" % attr, int(new_val))
        if rule == 'sum':
            for attr in attrs:
                new_val = data.get(attr, None)
                old_val = getattr(obj, "sum_%s" % attr, None)
                if old_val is None:
                    setattr(obj, "sum_%s" % attr, int(new_val))
                elif new_val is not None:
                    setattr(obj, "sum_%s" % attr, int(old_val + int(new_val)))
                    

def get_supply(block):
    supply = 0
    for i in xrange(block):
        reward = 50.0 / 2**((i+1) / 210000)
        supply += reward
    return supply

def calc_extra_attrs(cls, date):
    obj = cls.get_by_id("bitcoin|%s" % date)
    if not obj:
        return

    obj.supply = int(get_supply(obj.max_id))
    obj.market_cap = round(float(obj.supply)) * round(float(obj.max_price_usd))
    obj.sum_transaction_count_square = round(float(obj.sum_transaction_count)) ** 2
    obj.put()
    
