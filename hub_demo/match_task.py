#!/usr/bin/env python
import pika
import uuid
import sys
import threading
import os
import getopt
import random




class MatchTask (threading.Thread):

	def __init__(self, my_exchange, my_agency, dest_exchange, priority, m_type, d_file):
		threading.Thread.__init__(self)
		self.my_agency = my_agency
		self.my_exchange = my_exchange
		self.dest_exchange = dest_exchange
		self.priority = priority
		self.m_type = m_type
		self.d_file = d_file


	def run(self):
		m_id=0
		connection = pika.BlockingConnection(pika.ConnectionParameters(
		host='localhost'))
		channel = connection.channel()
		channel.exchange_declare(exchange=self.dest_exchange, type='topic')
		routing_key = "result."+self.priority+"."+self.m_type+"."+self.my_agency+"."+str(m_id)+".test"
		message = 'AFIS MATCH SCORE IS '+str(random.random()) + ' from '+self.my_agency
		channel.basic_publish(exchange=self.dest_exchange,
								routing_key=routing_key,
								body=message)
		print " [x] MatchTask Sent %r:%r to %r" % (routing_key, message, self.dest_exchange)



