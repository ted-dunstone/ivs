#!/usr/bin/env python
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Response

class OpenBiometricBroker(object):

    def __init__(self,CONFIG_IN, service):
        self.url_map = [
                        Rule('/obb', endpoint='obb'),
        ]
        global CONFIG
        CONFIG = CONFIG_IN
        self.service = service
        self.redis = service.redis


        
    def on_obb(self, request):
        return self.service.render_template('obb.html', config=CONFIG, action={'url':"enroll",'name':"Enrolment Service"})

    