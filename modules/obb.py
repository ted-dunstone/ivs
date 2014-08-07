#!/usr/bin/env python
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Response

class OpenBiometricBroker(object):

    def __init__(self,CONFIG_IN, service):
        self.url_map = [
                        Rule('/obb', endpoint='obb'),
                        Rule('/rabbit', endpoint='rabbit'),
        ]
        global CONFIG
        CONFIG = CONFIG_IN
        self.service = service
        self.redis = service.redis


        
    def on_obb(self, request):
        return self.service.render_template('obb.html', config=CONFIG, action={'url':"enroll",'name':"Enrolment Service"})

    def on_rabbit(self, request):
        import urllib2,json
        
        req = urllib2.Request("http://localhost:15672/api/overview?lengths_age=600&lengths_incr=5&msg_rates_age=60&msg_rates_incr=5", None, {'user-agent':'px'})
        opener = urllib2.build_opener().open(req)

        #print str(request)
        #http://localhost:15672/api/overview?lengths_age=600&lengths_incr=5&msg_rates_age=60&msg_rates_incr=5
        return json.load(f)
    