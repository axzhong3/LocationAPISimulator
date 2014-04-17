import webapp2
import jinja2
from google.appengine.ext import db

DEFAULT_LAT = 30.87564
DEFAULT_LON = -120.35866
name = "test"

jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader("."), autoescape=True)

class Location(db.Model):
    name = db.StringProperty(required = True)
    latitude = db.FloatProperty(required = True)
    longitude = db.FloatProperty(required = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)
        
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Main(Handler):
    def render_front(self, lat="", lon=""):
        self.render("index.html", lat=lat, lon=lon)
    
    def get(self):
        location = db.GqlQuery("select * from Location where name = :name", name=name).get()
        if not location:
            l = Location(name = name, latitude = DEFAULT_LAT, longitude = DEFAULT_LON)
            l.put()
            lat = DEFAULT_LAT
            lon = DEFAULT_LON
        else:
            lat = location.latitude
            lon = location.longitude
        self.render_front(lat, lon)

class Update(Handler):
    def post(self):
        lat = float(self.request.get('lat'))
        lon = float(self.request.get('lon'))
        location = db.GqlQuery("select * from Location where name = :name", name=name).get()
        if not location:
            l = Location(name = name, latitude = lat, longitude = lon)
            l.put()
        else:
            location.latitude = lat
            location.longitude = lon
            location.put()

class Json(Handler):
    def render_front(self, lat="", lon=""):
        self.render("json", lat=lat, lon=lon)
    def get(self):
        location = db.GqlQuery("select * from Location where name = :name", name=name).get()
        if not location:
            l = Location(name = name, latitude = DEFAULT_LAT, longitude = DEFAULT_LON)
            l.put()
            lat = DEFAULT_LAT
            lon = DEFAULT_LON
        else:
            lat = location.latitude
            lon = location.longitude
        self.render_front(lat, lon)

application = webapp2.WSGIApplication([
    ('/', Main),
    ('/update', Update),
    ('/json', Json)
], debug = True)
