from google.appengine.ext import webapp
from webapp2_extras import json
from models import Signatures, Tags, Author
from settings import DEBUG, FEED_URL

__author__ = 'darvin'


class AbstractApiHandler(webapp.RequestHandler):
    def get_responce(self, *args, **kwargs):
        raise NotImplementedError

    def get(self, *args, **kwargs):
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(json.encode(self.get_responce(*args, **kwargs)))

class SignatureHandler(AbstractApiHandler):
    def get_responce(self, *args, **kwargs):
        if args:
            since = int(args[0])
        else:
            since = 0
        s = Signatures.get_single()
        return dict(((hash, timestamp) for hash,timestamp in zip(s.hashes, s.times) if timestamp>since))

class TagsHandler(AbstractApiHandler):
    def get_responce(self, *args, **kwargs):
        return Tags.get_single().enabled
        
        
class AuthorsHandler(AbstractApiHandler):
    def get_responce(self, *args, **kwargs):
        x = dict(
            ((author.key().name(), {"url":author.key().name(),
                             "image_url":author.image_url,
                             "title":author.title,
                             "subtitle":author.subtitle,
                             "name":author.name}) for author in Author.all())
        )
        return x


class InfoHandler(AbstractApiHandler):
    def get_responce(self, *args, **kwargs):
        return {
            "feedUrl":FEED_URL,
            "debug":DEBUG,
        }


app = webapp.WSGIApplication([
    ('/api/signatures', SignatureHandler),
    ('/api/signatures/([0-9]+)', SignatureHandler),

    ('/api/tags', TagsHandler),
    ('/api/authors', AuthorsHandler),
    ('/api/info', InfoHandler),
],
    debug=DEBUG)

