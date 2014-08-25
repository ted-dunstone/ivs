#!/usr/bin/env python
import sys
import os
import getopt
import time
import random

from messageQueue import MessageQueue


VERSION = 0.5

REQUEST_EXCHANGE = {"name":"Request", "ex_type":"headers"}
IDENTIFY_EXCHANGE = {"name":"Identify", "ex_type":"headers"}
RESULTS_EXCHANGE = {"name":"Results", "ex_type":"headers"}

EXCHANGES = [REQUEST_EXCHANGE,IDENTIFY_EXCHANGE,RESULTS_EXCHANGE]

class MessageBrokerBase(MessageQueue):
    def __init__(self, node_name, user_id="guest",header={},exchange_info = REQUEST_EXCHANGE,routing_key=''):
        super(MessageBrokerBase, self).__init__(node_name, user_id)
        #self.exchange_name = exchange_info["name"]
        self.exchange = exchange_info
        self.setup()
        print self.queue_name
        self.request_queue=self.queue_bind(self.exchange, header, routing_key)
        self.log( self.__class__.__name__)
        
    def start(self, ):
        self.start_consume(self.request_queue)
        
    def setup(self, ):
        self.queue_name = self.channel.queue_declare( exclusive=False, queue = "ab_"+self.node_name).method.queue # queue = "aa_"+self.node_name
        print self.queue_name




class Broker(MessageBrokerBase):
    def __init__(self, user_id="guest",header={},exchange_info = REQUEST_EXCHANGE):
        super(Broker, self).__init__("Broker", user_id,header, exchange_info)
        
    def setup(self, ):
        super(Broker, self).setup()
        for exchange in EXCHANGES:
            self.channel.exchange_declare(exchange=exchange["name"], type=exchange["ex_type"])
        
    def on_return_status(self, properties):
        # called as RPC to return the status of a sent msg
        return "[OK] from %s"%self.node_name

    def on_recieve_callback(self, ch, method, properties, body):
        super(Broker,self).on_recieve_callback(ch, method, properties, body)
        self.send(IDENTIFY_EXCHANGE["name"], body, properties.headers, False)


class Matcher(MessageBrokerBase):
    def __init__(self, node_name, user_id="guest",header={},exchange_info = IDENTIFY_EXCHANGE):
        header.update({"from_node":node_name})
        super(Matcher, self).__init__(node_name, user_id,header, exchange_info)
                    
    def on_recieve_callback(self, ch, method, properties, body):
        super(Matcher,self).on_recieve_callback(ch, method, properties, body)
        if not(self.node_name in properties.headers): # make sure not to match our own request
            body = "Match score = %f from %s"%(random.random(),self.node_name)
            self.send(RESULTS_EXCHANGE["name"], body, properties.headers,routing_key=node_name)


class Requester(MessageQueue):
    def __init__(self, node_name, user_id="guest"):
        super(Requester, self).__init__(node_name, user_id)

    def send(self, msg,header):
        header.update({self.node_name:True})
        super(Requester,self).send(REQUEST_EXCHANGE["name"],msg,header,True)

class Receiver(MessageBrokerBase):
    def __init__(self, node_name, user_id="guest",header={},exchange_info = RESULTS_EXCHANGE):
        super(Receiver, self).__init__(node_name, user_id,header, exchange_info, routing_key=node_name)

    def on_recieve_callback(self, ch, method, properties, body):
        super(Receiver,self).on_recieve_callback(ch, method, properties, body)
        #self.log("**** Result from %s"%(str(properties.headers)))
        self.log(body)


if __name__ == "__main__":

    import argparse


    # Parse command line args
    # note that args can be read from a file using the @ command
    parser = argparse.ArgumentParser(description='Identity Verification Service',fromfile_prefix_chars='@')
    parser.add_argument('--rabbitmq_host', default='localhost',
                                       help='set the rabbitmq url (default localhost)')
    parser.add_argument('--redis_host', default='localhost',
                                           help='set the redis url (default localhost)')
    parser.add_argument('--redis_port', default=6379,
                                       help='set the redis port (default 6379)')

    parser.add_argument('--is_broker','-b',  action='store_true',
                                       help='Is the broker')
    
    parser.add_argument('--is_matcher','-m', action='store_true',
                                       help='Is a matcher')

    parser.add_argument('--is_requester','-r', action='store_true',
                                       help='Is a requester')
    
    parser.add_argument('--is_receiver','-e', action='store_true',
                                       help='Is a reciever')

    parser.add_argument('--name','-n', default='[No Name]',
                                       help='Name of the agency/node')

    parser.add_argument('--country','-c', default="AU",
                                       help='Set the country code (default=AU)')
    parser.add_argument('--location','-l', default="unknown",
                                       help='Set location (default=unknown)')
    
    parser.add_argument('--version', action='version', version='%(prog)s '+str(VERSION))

    args = parser.parse_args()

    header={"test":"test"}
    if args.is_matcher:
        matcher = Matcher(args.name,args.name,header)
        matcher.start()
    elif args.is_broker:
        broker = Broker("broker",header)
        #queue=broker.queue_bind(dest_queue, header)
        broker.start() #_consume(queue)
    elif args.is_requester:
        requester = Requester(args.name,args.name)
        requester.send("Hello",header)
        
    elif args.is_receiver:
        receiver = Receiver(args.name,args.name,{args.name:True})
        receiver.start()
    #sendRequest(my_queue, dest_queue, priority, m_type, d_file)

