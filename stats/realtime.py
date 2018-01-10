from google.appengine.api import memcache
from flask import g

def update_data(master, obj, block):
    min_time = memcache.get("MIN_TIME")
    if min_time:
        if block["time"] < min_time:
            memcache.set(master.COIN + "_MIN_TIME", block["time"])
    else:
        memcache.set(master.COIN + "_MIN_TIME", block["time"])
    
    max_time = memcache.get(master.COIN + "_MAX_TIME")
    if max_time:
        if block["time"] > max_time:
            memcache.set(master.COIN + "_MAX_TIME", block["time"])
    else:
        memcache.set(master.COIN + "_MAX_TIME", block["time"])
    
    last_id = memcache.get(master.COIN + "_LAST_ID")
    if last_id:
        if block["id"] > last_id:
            memcache.set(master.COIN + "_LAST_ID", block["id"])
    else:
        memcache.set(master.COIN + "_LAST_ID", block["id"])
    
    memcache.set(master.COIN + "_BLOCK_COUNT", getattr(obj, "block_count", 1))



def get_data(master):
    enabled = False
    if g.user_model.get_actual_lag() == 0:
        enabled = True
    return {
        "min_time": memcache.get(master.COIN + "_MIN_TIME"),
        "max_time": memcache.get(master.COIN + "_MAX_TIME"),
        "last_id": memcache.get(master.COIN + "_LAST_ID"),
        "block_count": memcache.get(master.COIN + "_BLOCK_COUNT"),
        "enabled": enabled,
    }
