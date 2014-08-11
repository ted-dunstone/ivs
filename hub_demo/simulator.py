#!/usr/bin/env python
import pika
import sys
import getopt
from hub_master import HubMaster
import threading


class ClientTask (threading.Thread):





class Simulator(object):


     #pass in the list of hub/server exchanges, client exchanges, and request types (i.e, match, enrol, etc..-). 
    def __init__(self, server_exchanges, client_exchanges, requests ):
        self.server_exchanges=server_exchanges
        self.client_exchanges=client_exchanges
        self.requests=requests
        self.hub_master = HubMaster("MasterControl", server_exchanges)



    def getExchangeStats(self, exchange):
        pass
 


def main(argv):

   try:
      opts, args = getopt.getopt(argv,"s:c:",["server_exchanges=", "client_exchanges="])
   except getopt.GetoptError:
      print 'simulator.py -s<EXC_ID1>:<EXC_ID2>:...:<EXC_IDX> -c <CLI_EXC_ID1>:<CLI_EXC_ID2>:...:<CLI_EXC_IDX> '
      sys.exit(2)
   for opt, arg in opts:
      print arg
      if opt == '-h':
         print 'simulator.py -s<EXC_ID1>:<EXC_ID2>:...:<EXC_IDX> -c <CLI_EXC_ID1>:<CLI_EXC_ID2>:...:<CLI_EXC_IDX> '
         sys.exit(1)
      elif opt in ("-e", "--server_exchanges="):
         exchange_list = arg



if __name__ == "__main__":
   try:
      opts, args = getopt.getopt(sys.argv,"s:c:",["server_exchanges=", "client_exchanges="])
      print args
   except getopt.GetoptError:
      pass
   main(sys.argv[1:])


