import webapp2
import jinja2
import re
import urllib2
import time
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

class Calendar(Handler):
    def render_front(self, device="unknown", status="unknown", startTime="unknown", endTime="unknown"):
        self.render("calendar", device=device, status=status, startTime=startTime, endTime=endTime)
    def get(self):
        response = urllib2.urlopen('https://www.google.com/calendar/embed?src=berkeley.edu_373035363931382d363930@resource.calendar.google.com')
        r = response.read()
        starting = re.findall('(?<="startTime":").{19}', r)
        ending = re.findall('(?<="endTime":").{19}', r)
        startTimes = []
        endTimes = []
        status = "available"
        device = "Laser Cutter"
        for i in range(0, len(starting)):
            startTimes.append(time.strptime(starting[i], "%Y-%m-%dT%H:%M:%S"))
            endTimes.append(time.strptime(ending[i], "%Y-%m-%dT%H:%M:%S"))
        startTimes.sort()
        endTimes.sort()
        # PST time zone
        curPST = time.gmtime(time.time()-7*3600)
        curPSTString = time.strftime("%a %m-%d %H:%M:%S", curPST)
        startTime = curPSTString
        i = 0;
        while (i < len(starting)):
            if (curPST < startTimes[i]):
                if (time.mktime(startTimes[i])-time.mktime(curPST) < 3600):
                    status = "schedule soon"
                endTime = time.strftime("%a %m-%d %H:%M:%S", startTimes[i])
                break
            elif (curPST >= startTimes[i] and curPST < endTimes[i]):
                status = "in use"
                startTime = time.strftime("%a %m-%d %H:%M:%S", startTimes[i])
                endTime = time.strftime("%a %m-%d %H:%M:%S", endTimes[i])
                break
            i = i+1            
        self.render_front(device, status, startTime, endTime)

application = webapp2.WSGIApplication([
    ('/', Main),
    ('/update', Update),
    ('/json', Json),
    ('/calendar', Calendar)
], debug = True)
