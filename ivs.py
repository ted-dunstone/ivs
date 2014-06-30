#!/usr/bin/env python
"""
	Performix
	~~~~~~~



	:copyright: (c) 2014 by the Biometix, see AUTHORS for more details.
	:license:
"""

import os,sys
import redis
import copy,datetime
import urlparse

import sqlite3

from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.utils import redirect
from werkzeug.utils import cached_property
from werkzeug.security import generate_password_hash,check_password_hash,pbkdf2_hex

from werkzeug.wrappers import BaseRequest
from werkzeug.contrib.securecookie import SecureCookie

COOKIE_SECRET = '\xfa\xdd\xb8z\xae\xe0}4\x8b\xea'

from modules.util import remove_private,returnJson,test_url, test_finished

from modules.data import PxData

from modules.bias import Verify

import argparse

VERSION = "0.1b"

class Request(BaseRequest):

	@cached_property
	def client_session(self):
		return SecureCookie.load_cookie(self, secret_key=COOKIE_SECRET)


import json,datetime


from jinja2 import Environment, FileSystemLoader


def base36_encode(number):
	assert number >= 0, 'positive integer required'
	if number == 0:
		return '0'
	base36 = []
	while number != 0:
		number, i = divmod(number, 36)
		base36.append('0123456789abcdefghijklmnopqrstuvwxyz'[i])
	return ''.join(reversed(base36))


def is_valid_url(url):
	parts = urlparse.urlparse(url)
	return parts.scheme in ('http', 'https')


def get_hostname(url):
	return urlparse.urlparse(url).netloc



class PxLogin(object):
	def __init__(self):
		self.url_map = [
			Rule('/login', endpoint='login_page'),
			Rule('/login', endpoint='login_user')
		  ]

	def on_login_page(self,request):
		response = self.render_template('link_view.html',url=[{'n':'h1'},{'n':'h2'}])
		return response
	#def on_login_user(self, ):
	#    request.client_session["test4"]="h2"


from jsonrpc import JSONRPCResponseManager, dispatcher

class Struct(object):
    """Comment removed"""
    def __init__(self, data):
        for name, value in data.iteritems():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)): 
            return type(value)([self._wrap(v) for v in value])
        else:
            return Struct(value) if isinstance(value, dict) else value


class IdentityVerificationService(object):

	def __init__(self, CONFIG):
		self.redis = redis.Redis(CONFIG.redis_host, int(CONFIG.redis_port))
		template_path = os.path.join(os.path.dirname(__file__), 'templates')
		self.jinja_env = Environment(loader=FileSystemLoader(template_path),
									 autoescape=True)
		self.jinja_env.filters['hostname'] = get_hostname

		self.pxClasses = [PxData(self.redis),
						  PxLogin(),Verify(CONFIG,self)]

		self.urls = [
			Rule('/', endpoint='index'),
			#Rule('/new', endpoint='new_url'),
			Rule('/sessonid', endpoint='session_id'),
			Rule('/gitpull', endpoint='gitpull')
		]

		for c in self.pxClasses:
			self.urls.extend(c.url_map)

		self.url_map = Map(self.urls)

	@cached_property
	def read_index(self, ):
		return open("templates/index.html").read()
	
	def on_index(self, request ):
		return Response(self.read_index,mimetype='text/html')

	def error_404(self,request):
		if not request.url.endswith('.html'):
			return redirect(request.url+'.html')
		response = self.render_template('404.html')
		response.status_code = 404
		return response

	def render_template(self, template_name, **context):
		t = self.jinja_env.get_template(template_name)
		return Response(t.render(context), mimetype='text/html')

	def dispatch_request(self, request):
		print "hello"
			
		# JSON RPC Handler
		
		response = JSONRPCResponseManager.handle(
					request.data, dispatcher)
		#	print "dispatch", response.json,response.error
		if response.error:
			# if the error is a parse json error (-32700) means it is not an RPC call
			if response.error['code']!=-32700:
				# return the error json
				return returnJson(response.json) 
			else:
				pass # continue to process request below
		else:
			#print "*********#### "+help(request)
			print  request.remote_addr, request.remote_user #.host_url+" "+request.url
			return returnJson(response.json)
		
		adapter = self.url_map.bind_to_environ(request.environ)
		
		# Normal Request Handler
		try:
			endpoint, values = adapter.match()
			if hasattr(self, 'on_' + endpoint):
				return getattr(self, 'on_' + endpoint)(request, **values)
			else:
				for pxClass in self.pxClasses:
					if hasattr(pxClass, 'on_' + endpoint):
						pxClass.render_template=self.render_template
						if 'docs' in request.args:
							return Response("<pre>Documentation"+str(dir(request))+"\n"+request.path+'\n'+request.remote_addr+
											getattr(pxClass, 'on_' + endpoint).__doc__+"</pre>",
											mimetype='text/html')
						result = getattr(pxClass, 'on_' + endpoint)(request, **values)
						if result.__class__!=Response:
							return returnJson(result)
						return result

		except NotFound, e:
			return self.error_404(request)
		except HTTPException, e:
			return e

	def on_session_id(self, request):
		#shjd=sdds
		return returnJson(request.client_session.values())

	def on_gitpull(self, request):
		#shjd=sdds
		from subprocess import check_output,STDOUT
		pull_out = check_output('git pull',stderr=STDOUT, shell=True)
		status_out = check_output('git status',stderr=STDOUT, shell=True)
		return returnJson({'result':pull_out, 'git status':status_out})

	def wsgi_app(self, environ, start_response):
		request = Request(environ)
		response = self.dispatch_request(request)

		request.client_session.save_cookie(response)
		return response(environ, start_response)

	def __call__(self, environ, start_response):
		return self.wsgi_app(environ, start_response)


def create_app(CONFIG, with_static=True):
	app = IdentityVerificationService(CONFIG)
	if with_static:
		app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
			'/static':  os.path.join(os.path.dirname(__file__), 'static')
		})
	return app



if __name__ == '__main__':
	from werkzeug.serving import run_simple
	import argparse

	
	# Parse command line args
	# note that args can be read from a file using the @ command
	parser = argparse.ArgumentParser(description='Identity Verification Service',fromfile_prefix_chars='@')
	parser.add_argument('--port','-p', default=8000,
					   help='set the port (default 8000)')
	parser.add_argument('--redis_host', default='localhost',
					   help='set the redis url (default localhost)')
	parser.add_argument('--redis_port', default=6379,
					   help='set the redis port (default 6379)')
	
	parser.add_argument('--hub_url','-u', default=False,
					   help='Set the hub address')
	
	parser.add_argument('--no_matcher', default=False,
					   help='Do not enable matcher')
	
	parser.add_argument('--type','-t', default="DLA",
					   help='Set the type of System (DLA=Drivers Licence, PASS=Passport')
	parser.add_argument('--country','-c', default="AU",
					   help='Set the country code (default=AU)')
	parser.add_argument('--location','-l', default="unknown",
					   help='Set location (default=unknown)')
	parser.add_argument('--name','-n', default=None,
					   help='Set name (default=unknown)')
	parser.add_argument('--logo', default='',
					   help='Set logo url')
	parser.add_argument('--bgcolor', default='',
					   help='Set background color')
	
	parser.add_argument('--version', action='version', version='%(prog)s '+str(VERSION))
	
	args = parser.parse_args()
	import time,random
	threaded = True;
	if (args.hub_url):	
		time.sleep(2+random.random()*3)
		threaded = False
	
	
	app = create_app(args)
	
	run_simple('0.0.0.0', int(args.port), app, use_debugger=True, use_reloader=True, threaded = threaded) #, ssl_context = 'adhoc')
