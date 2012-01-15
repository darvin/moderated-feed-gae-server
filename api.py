from google.appengine.ext import webapp
from webapp2_extras import json
from models import Signatures, Tags
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
    ('/api/info', InfoHandler),
],
    debug=DEBUG)

