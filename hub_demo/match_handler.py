#!/usr/bin/env python
import pika
import uuid
import sys
import threading
import os
import getopt
from match_task import MatchTask



class MatchResultHandler(object):


	def __init__(self, my_agency, my_exchange):
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
		self.channel = self.connection.channel()
		print ' [*] MatchResultHandler Exchange is '+my_exchange
		self.channel.exchange_declare(exchange=my_exchange, type='topic')
		self.result = self.channel.queue_declare(exclusive=True)
		self.queue_name = self.result.method.queue
		self.my_exchange=my_exchange
		self.channel.queue_bind(exchange=my_exchange, queue=self.queue_name, routing_key="match.#")
		print ' [*] MatchResultHandler Waiting for messages. To exit press CTRL+C'
		self.channel.basic_consume(self.handleRequest, self.queue_name, no_ack=True)
                self.my_agency=my_agency


	def waitRequest(self):
		self.channel.start_consuming()


        def handleRequest(self, ch, method, props, body):
                start = method.routing_key.find(".")
                start = method.routing_key.find(".",start+1)
                start = method.routing_key.find(".",start+1)
                end = method.routing_key.find(".",start+1)
                print ' [*] MatchResultHandler Received message: '+body
                exchange=method.routing_key[start+1:end ]
#        print "exchange is " + exchange +" routing key is " +method.routing_key
                mT=MatchTask(self.my_exchange, self.my_agency, exchange, "1", "result", "");
                mT.start()



def main(argv):
	my_exchange=""

	try:
		opts, args = getopt.getopt(argv,"i:",["my_agency_id="])
	except getopt.GetoptError:
		print 'match_listener.py -i<MY_AGENCY_ID> '
		sys.exit(2)
	for opt, arg in opts:
		print arg
		if opt == '-h':
			print 'match_listener.py -i<MY_AGENCY_ID> '
			sys.exit(1)
		elif opt in ("-i", "--my_agency_id"):
			my_exchange = arg

	match_listener = MatchResultHandler(my_exchange)
	match_listener.waitRequest()





#if __name__ == "__main__":
#	try:
#		opts, args = getopt.getopt(sys.argv,"i:",["MY_AGENCY_ID="])
#		print args
#	except getopt.GetoptError:
#		pass
#	main(sys.argv[1:])
