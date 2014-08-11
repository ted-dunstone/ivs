#!/usr/bin/env python
import pika
import sys
import getopt
from hub_pair import HubPair



class HubMaster(object):


    def __init__(self, controls_exchange, exchange_list):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=controls_exchange, type='topic')
        self.result = self.channel.queue_declare(exclusive=True)
        self.queue_name = self.result.method.queue
        self.my_exchange=controls_exchange
        self.channel.queue_bind(exchange=controls_exchange, queue=self.queue_name, routing_key="control.#")
        self.channel.basic_consume(self.handleRequest, self.queue_name, no_ack=True)
        self.hub_pairs=self.loadHubs(exchange_list)
        self.startHubs()


    #load hubs and 
    def loadHubs(self, exchange_list):
        hub_pairs={}

        for e in exchange_list:
          hub_pair=HubPair(e)
          hub_pairs[e]=hub_pair
        return hub_pairs

    def startHubs(self):
        for key in self.hub_pairs:
          self.hub_pairs[key].waitRequest()


    def waitRequest(self):
        print ' [*] Hub waiting for messages. To exit press CTRL+C... Exchange is '+self.my_exchange
        self.channel.start_consuming()


    def handleRequest(self, ch, method, props, body):
        start = method.routing_key.find(".")
        end = method.routing_key.find(".",start+1)
        print ' [*] hub_master Received message: '+body
        command=method.routing_key[start+1:end ]

        start = method.routing_key.find(".")
        start = method.routing_key.find(".",start+1)
        end = method.routing_key.find(".",start+1)
        argument=method.routing_key[start+1:end ]

        #TODO: Handle commands + arguments



    def stopExchange(self, exchange):
        pass

    def restartExchange(self, exchange):
        pass


    def getExchangeStats(self, exchange):
        pass
 


def main(argv):

   try:
      opts, args = getopt.getopt(argv,"e:",["exchanges="])
   except getopt.GetoptError:
      print 'hub_master.py -e<EXC_ID1>:<EXC_ID2>:...:<EXC_IDX> '
      sys.exit(2)
   for opt, arg in opts:
      print arg
      if opt == '-h':
         print 'hub_master.py -e<EXC_ID1>:<EXC_ID2>:...:<EXC_IDX> '
         sys.exit(1)
      elif opt in ("-e", "--exchanges="):
         exchange_list = arg

   hub_master = HubMaster("MasterControl", exchange_list.split(':'))
   hub_master.waitRequest()


if __name__ == "__main__":
   try:
      opts, args = getopt.getopt(sys.argv,"e:",["exchanges="])
      print args
   except getopt.GetoptError:
      pass
   main(sys.argv[1:])


