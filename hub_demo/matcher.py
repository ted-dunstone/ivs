#!/usr/bin/env python
import pika
import uuid
import sys
import threading
import os
import getopt
import random

m_id=0


def on_request(ch, method, props, body):
    print "Sending %s to be transformed"  % (body,)
    key=(method.routing_key).replace("request", "transform")
    ch.basic_publish(exchange='Australia_NZ_Exchange', routing_key=key, body=body)


class MatchTask (threading.Thread):

    def __init__(self, my_agency, dest_exchange, priority, m_type, d_file):
      threading.Thread.__init__(self)
      self.my_agency = my_agency
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
      message = 'AFIS MATCH SCORE IS '+str(random.random())
      channel.basic_publish(exchange=self.dest_exchange,
		              routing_key=routing_key,
		              body=message) 
      print " [x] MatchTask Sent %r:%r to %r" % (routing_key, message, self.dest_exchange)



class MatchRequestHandler(object):


    def __init__(self, my_exchange):
	self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	self.channel = self.connection.channel()
	print ' [*] MatchRequestHandler Exchange is '+my_exchange
	self.channel.exchange_declare(exchange=my_exchange, type='topic')
	self.result = self.channel.queue_declare(exclusive=True)
	self.queue_name = self.result.method.queue
        self.my_exchange=my_exchange
	self.channel.queue_bind(exchange=my_exchange, queue=self.queue_name, routing_key="match.#")
	print ' [*] MatchRequestHandler Waiting for messages. To exit press CTRL+C'
	self.channel.basic_consume(self.handleRequest, self.queue_name, no_ack=True)
#	self.channel.basic_consume(onRequest, self.queue_name, no_ack=True)


    def waitRequest(self):
	self.channel.start_consuming()


    def handleRequest(self, ch, method, props, body):
        start = method.routing_key.find(".")
        start = method.routing_key.find(".",start+1)
        start = method.routing_key.find(".",start+1)
        end = method.routing_key.find(".",start+1)
	print ' [*] MatchRequestHandler Received message: '+body
#        print start
#        print end
        exchange=method.routing_key[start+1:end ]
#        print exchange
#        print "exchange is " + exchange +" routing key is " +method.routing_key
        mT=MatchTask(self.my_exchange, exchange, "1", "result", "");
        mT.start()


    
def main(argv):
   my_exchange=""
 
   try:
      opts, args = getopt.getopt(argv,"i:",["my_agency_id="])
   except getopt.GetoptError:
      print 'matcher.py -i<MY_AGENCY_ID> '
      sys.exit(2)
   for opt, arg in opts:
      print arg 
      if opt == '-h':
         print 'matcher.py -i<MY_AGENCY_ID> '
         sys.exit(1)
      elif opt in ("-i", "--my_agency_id"):
         my_exchange = arg

   matcher = MatchRequestHandler(my_exchange) #'Australia_NZ_Exchange')
   matcher.waitRequest()



       

if __name__ == "__main__":
   try:
      opts, args = getopt.getopt(sys.argv,"i:",["MY_AGENCY_ID="])
      print args
   except getopt.GetoptError: 
      pass    
   main(sys.argv[1:])


