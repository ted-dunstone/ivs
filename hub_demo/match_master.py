#!/usr/bin/env python
import pika
import sys
import getopt
from match_handler import MatchResultHandler



class MatchMaster(object):


    def __init__(self, agency, exchange_list):
        controls_exchange=agency+".Controls"
        self.my_agency=agency
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=controls_exchange, type='topic')
        self.result = self.channel.queue_declare(exclusive=True)
        self.queue_name = self.result.method.queue
        self.my_exchange=controls_exchange
        self.channel.queue_bind(exchange=controls_exchange, queue=self.queue_name, routing_key="control.#")
        self.channel.basic_consume(self.handleRequest, self.queue_name, no_ack=True)
        self.match_handlers=self.loadMatchHandlers(exchange_list)
        self.startMatchHandlers()


    #load hubs and 
    def loadMatchHandlers(self, exchange_list):
        match_handlers={}

        for e in exchange_list:
          m_handler=MatchResultHandler(self.my_agency, e)
          match_handlers[e]=m_handler
        return match_handlers


    def startMatchHandlers(self):
        for key in self.match_handlers:
          self.match_handlers[key].waitRequest()


    def waitRequest(self):
        print ' [*] MatchMaster waiting for messages. To exit press CTRL+C... Exchange is '+self.my_exchange
        self.channel.start_consuming()


    def handleRequest(self, ch, method, props, body):
        key=(method.routing_key).replace("request", "transform")
        print "Sending %s to be transformed with new key %s and sent to exc %s" %(body, key, self.my_exchange)
        ch.basic_publish(exchange=self.my_exchange, routing_key=key, body=body)



def main(argv):

   try:
      opts, args = getopt.getopt(argv,"a:e:",["agency=", "exchanges="])
   except getopt.GetoptError:
      print 'match_master.py -a agency -e<EXC_ID1>:<EXC_ID2>:...:<EXC_IDX> '
      sys.exit(2)
   for opt, arg in opts:
      print arg
      if opt == '-h':
         print 'match_master.py -a agency -e<EXC_ID1>:<EXC_ID2>:...:<EXC_IDX> '
         sys.exit(1)
      elif opt in ("-e", "--exchanges="):
         exchange_list = arg
      elif opt in ("-a", "--agency="):
         agency = arg



   matcher_master = MatchMaster(agency, exchange_list.split(':'))
   matcher_master.waitRequest()


if __name__ == "__main__":
   try:
      opts, args = getopt.getopt(sys.argv,"a:e:",["agency=", "exchanges="])
      print args
   except getopt.GetoptError:
      pass
   main(sys.argv[1:])


