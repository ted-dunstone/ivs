#!/usr/bin/env python
import pika
import uuid
import sys
import threading
import os
import getopt
from hub_transformer import HubTransformer
from hub_receiver import HubReceiver


#stores the transformer and receiver classes for each instance
class HubPair(object):

    def __init__(self, my_exchange):
        self.my_exchange = my_exchange
        self.transformer = HubTransformer(my_exchange)
        self.receiver =    HubReceiver(my_exchange)

    def getTransformer(self):
        return self.transformer

    def getReciever(self):
        return self.receiver

    def getExchange(self):
        return self.my_exchange

    def changeExchange(new_exchange):
        self.my_exchange=new_exchange;
        self.transformer = HubTransformer(my_exchange)
        self.receiver =    HubReceiver(my_exchange)

    #make transformers and receivers wait for request.
    def waitRequest(self):
        self.transformer.start()
        self.receiver.start()

    # Todo: return the stats of the exchange
    def getStats():
        return None


