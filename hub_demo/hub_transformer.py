#!/usr/bin/env python
import pika
import uuid
import sys
import threading
import os
import getopt


class HubTransformer(threading.Thread):


    def __init__(self, my_exchange):
        threading.Thread.__init__(self)
	self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	self.channel = self.connection.channel()
	self.channel.exchange_declare(exchange=my_exchange, type='topic')
	self.result = self.channel.queue_declare(exclusive=True)
	self.queue_name = self.result.method.queue
        self.my_exchange=my_exchange
	self.channel.queue_bind(exchange=my_exchange, queue=self.queue_name, routing_key="transform.#")
	self.channel.basic_consume(self.handleRequest, self.queue_name, no_ack=True)
#	self.channel.basic_consume(onRequest, self.queue_name, no_ack=True)


    def run(self):
        print ' [*] Hub Tranfromer waiting for messages. To exit press CTRL+C... Exchange is '+self.my_exchange
	self.channel.start_consuming()


    def handleRequest(self, ch, method, props, body):
        print ' [*] hub_transformer received message '+body
        body=body+" TRANSFORMED"
        key=(method.routing_key).replace("transform", "match")
        print " [*] hub_transform sending message "+ body+ " from source "+key
        ch.basic_publish(exchange=self.my_exchange, routing_key=key, body=body)



#def on_request(ch, method, props, body):
#    key=(method.routing_key).replace("request", "transform")
#    print "Sending %s to be transformed with new key %s and sent to exc %s" %(body, key, my_exchange)
#    ch.basic_publish(exchange=my_exchange, routing_key=key, body=body)

#def main(argv):
#   my_exchange=""
#   try:
#      opts, args = getopt.getopt(argv,"i:",["my_agency_id="])
#   except getopt.GetoptError:
#      print 'hub_transformer.py -i<MY_AGENCY_ID> '
#      sys.exit(2)
#   for opt, arg in opts:
#      print arg 
#      if opt == '-h':
#         print 'hub_transformer.py -i<MY_AGENCY_ID> '
#         sys.exit(1)
#      elif opt in ("-i", "--my_agency_id"):
#         my_exchange = arg
 

#   hub_trans = HubTransformer(my_exchange)
#   hub_trans.waitRequest()
       

#if __name__ == "__main__":
#   try:
#      opts, args = getopt.getopt(sys.argv,"i:",["MY_AGENCY_ID="])
#      print args
#   except getopt.GetoptError: 
#      pass    
#   main(sys.argv[1:])
