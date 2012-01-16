import hashlib
import time
from google.appengine.ext.db import polymodel
import logging
import sys
from utils import strip_string

print sys.path
__author__ = 'darvin'


from google.appengine.ext import db


class Author(db.Model):
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

        m.update(strip_string(
            post["title"].encode("utf-8") +
            post["source"]["link"].encode("utf-8") +
            post["content"][0]["value"].encode("utf-8")))

        logging.info(m.hexdigest())
        return m.hexdigest()

    @classmethod
    def signatures(cls, since=0):
        s = cls.get_single()
        count = len(filter(lambda x: x>since, s.times))
        return s.hashes[-count:]


class Tags(SingleModel):
    enabled = db.StringListProperty()
    available = db.StringListProperty()


class BlogPost(db.Model):
    author = db.ReferenceProperty(Author)
    tags = db.StringListProperty()
    title = db.StringProperty()
    content = db.TextProperty()
    signature = db.StringProperty()
    url = db.URLProperty()


    @classmethod
    def blog_post_from_feed_entry(cls, entry):
        import pprint
        pprint.pprint(entry)
        author =  Author.get_or_insert(key_name=entry["source"]["link"],
            title=entry["source"]["title"],
            name=entry["author"])

        return cls(author=author,
            tags=[t["term"] for t in entry.get("tags", [])],
            title=entry["title"],
            content=entry["content"][0]["value"],
            signature=Signatures.signature_key_for_post(entry),
            url=entry["link"])
