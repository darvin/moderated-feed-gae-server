import hashlib
import time
from google.appengine.ext.db import polymodel

__author__ = 'darvin'


from google.appengine.ext import db


class Author(db.Model):
#    url = db.URLProperty(required=True)
    image_url = db.URLProperty()
    name = db.StringProperty(required=True)
    title = db.StringProperty(required=True)
    subtitle = db.StringProperty()


class SingleModel(polymodel.PolyModel):
    @classmethod
    def get_single(cls):
        return cls.get_or_insert(cls.__name__)


class Signatures(SingleModel):
    times = db.ListProperty(int)
    hashes = db.StringListProperty()

    @classmethod
    def add_signature(cls, hash):
        s = cls.get_single()
        s.times.append(int(time.time()))
        s.hashes.append(hash)
        s.put()

    @classmethod
    def remove_signature(cls, hash):
        s = cls.get_single()
        i = s.hashes.index(hash)
        s.hashes.remove(hash)
        del s.times[i]
        s.put()


    @classmethod
    def signature_key_for_post(cls, post):
        m = hashlib.md5()
        m.update(post["title"].encode("utf-8"))
        m.update(post["content"][0]["value"].encode("utf-8"))
        m.update(post["source"]["id"].encode("utf-8"))
        return m.hexdigest()

    @classmethod
    def signatures(cls, since=0):
        s = cls.get_single()
        count = len(filter(lambda x: x>since, s.times))
        return s.hashes[-count:]

