import logging
import sys
import json
from urllib import urlopen
from datetime import datetime, timedelta

from google.appengine.ext import ndb

from flask import request
from flask import g

class YoursPost(ndb.Expando):
    createdAt = ndb.StringProperty()
    userNameUrlString = ndb.StringProperty()
    userName = ndb.StringProperty()
    title = ndb.StringProperty()
    titleUrlString = ndb.StringProperty()
    data = ndb.TextProperty()
    worthPayingFor = ndb.StringProperty(repeated=True)
    notWorthPayingFor = ndb.StringProperty(repeated=True)

    @classmethod
    def update(cls):
          
        data = json.loads(urlopen("https://www.yours.org/api/contents/home/all/hot/0").read())
        count = 0
        for row in data:
            obj = cls.get_by_id(row["id"])
            if not obj:
                obj = cls(id=row["id"])
            
            obj.id = row["id"]
            obj.createdAt = row["createdAt"]
            obj.userName = row["userName"]
            obj.userNameUrlString = row["userNameUrlString"]
            obj.title = row["title"]
            obj.titleUrlString = row["titleUrlString"]
            obj.data = json.dumps(row)
            
            print "https://www.yours.org/api/contents/id/%s" % obj.id
            extra = json.loads(urlopen("https://www.yours.org/api/content/id/%s" % obj.id).read())
            earned = extra["content"]["totalPurchased"] + extra["content"]["totalTipped"] + extra["content"]["totalCommented"] + extra["content"]["amountVoted"]
            if earned > 500000:
                obj.worthPayingFor = extra["content"]["worthPayingFor"]                        
                obj.notWorthPayingFor = extra["content"]["notWorthPayingFor"]
                obj.put()
                count += 1
            
        return str(count)

    @classmethod
    def get_data(cls):
        data = {
            "comment": "Yours.org graph",
            "nodes": [],
            "edges": [],
        }
    
        nodes = data["nodes"]
        edges = data["edges"]
    
        posts = cls.query().order(-YoursPost.createdAt).fetch(100)
        for post in posts:
            nodes.append({
                "caption": post.userName,
                "type": "user",
                "id": post.userName,
                "root": post.userName in ["Ryan X. Charles", "clemens"],
            })
            for u in post.worthPayingFor:
                nodes.append({
                    "caption": u,
                    "type": "user",
                    "id": u,
                })
                edges.append({
                    "source": u,
                    "target": post.userName,
                    "caption": "",
                })
            
    
        return data
    
        
