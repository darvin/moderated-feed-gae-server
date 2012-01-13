from google.appengine.ext import webapp


class FetchShowsNamesHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('fetch shows')

class FetchArticlesHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('fetch blogs')


app = webapp.WSGIApplication([('/tasks/fetch_articles', FetchArticlesHandler),
    ('/tasks/fetch_shows_names', FetchShowsNamesHandler),
                            ],
                             debug=True)

