#!/usr/bin/env python
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Response

class OpenBiometricBroker(object):

    def __init__(self,CONFIG_IN, service):
        self.url_map = [
                        Rule('/obb', endpoint='obb'),
                        Rule('/rabbit/<action>', endpoint='rabbit'),
        ]
        global CONFIG
        CONFIG = CONFIG_IN
        self.service = service
        self.redis = service.redis


        
    def on_obb(self, request):
        return self.service.render_template('obb.html', config=CONFIG, action={'url':"enroll",'name':"Enrolment Service"})

    def on_rabbit(self, request,action):
        import urllib2,json,base64
        req = urllib2.Request("http://localhost:15672/api/%s?%s"%(action,request.query_string),
                              None,
                              {'user-agent':'px','Authorization':"Basic " + base64.b64encode("guest" + ":" +
                                                   "guest")})
        f = urllib2.build_opener().open(req)

        return json.load(f)
    