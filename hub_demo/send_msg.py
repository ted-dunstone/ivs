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
WEB_EXCHANGE      = {"name":"Web", "ex_type":"headers"}

EXCHANGES = [REQUEST_EXCHANGE,IDENTIFY_EXCHANGE,RESULTS_EXCHANGE,WEB_EXCHANGE]

class MessageBrokerBase(MessageQueue):
    # Base class

    def __init__(self, node_name, user_id="guest",header={},exchange_info = REQUEST_EXCHANGE,routing_key='',settings=None):
        super(MessageBrokerBase, self).__init__(node_name, user_id,settings=settings)
        self.exchange = exchange_info
        self.setup()
        self.request_queue=self.queue_bind(self.exchange, header) #, routing_key)
        self.log( 'starting '+self.__class__.__name__+' binding to '+exchange_info["name"])
        
    def start(self, ):
        self.start_consume(self.request_queue)
    
    def local_exchage(self, ):
        return {"name":self.node_name, "ex_type":"headers"}
    
    def setup(self, ):
        pass
         
        #self.queue_name = self.channel.queue_declare( exclusive=False, queue = self.node_name).method.queue
        # queue = "aa_"+self.node_name
        

class Broker(MessageBrokerBase):
    # the broker class - binds to the REQUEST_EXCHANGE sends to the IDENTIFY_EXCHANGE
    
    def __init__(self, user_id="guest",header={},exchange_info = REQUEST_EXCHANGE,settings=None):
        super(Broker, self).__init__("Broker", user_id,header, exchange_info,settings=settings)
        
    def setup(self, ):
        #setup the exchanges
        super(Broker, self).setup()
        for exchange in EXCHANGES:
            self.channel.exchange_declare(exchange=exchange["name"], type=exchange["ex_type"])
        
    def on_return_status(self, properties):
        # called as RPC to return the status of a sent msg
        return "[OK] from %s"%self.node_name

    def on_recieve_callback(self, ch, method, properties, body):
        super(Broker,self).on_recieve_callback(ch, method, properties, body)
        self.send(IDENTIFY_EXCHANGE, body, properties.headers, False)

class MsgLog(MessageQueue):
    # the logging class - binds to the fire_host
    
    def __init__(self, user_id="guest",header={},settings=None):
        super(MsgLog, self).__init__("Logger", user_id,settings=settings)
        self.channel.queue_declare(queue='firehose-queue', durable=False,auto_delete=True, exclusive=True)
        self.request_queue=self.queue_bind({"name":"Results"},queue_name= 'firehose-queue', routing_key='#')
        #self.request_queue=self.queue_bind({"name":"Request"},queue_name= 'firehose-queue', routing_key='#')
        self.request_queue=self.queue_bind({"name":"Identify"},queue_name= 'firehose-queue', routing_key='#')
        
    def on_recieve_callback(self, ch, method, properties, body):
        #self.log(body)
        if 'requester' in properties.headers:
            self.log("from %s for %s to %s"%( properties.headers['requester'], properties.headers['destination']['name'], properties.headers['last_node']))
        #else:
        #self.log(str(properties))
        #self.log(str(method))
        self.log(str(body))
        
    def start(self, ):
        self.start_consume(self.request_queue)

            
    

class Matcher(MessageBrokerBase):
    # the matcher class - binds to the IDENTIFY_EXCHANGE
    # undertakes match and puts return on the RESULTS_EXCHANGE queue with the routing_key of the name
    def __init__(self, node_name, user_id="guest",header={},exchange_info = IDENTIFY_EXCHANGE,settings=None):
        header.update({"from_node":node_name})
        super(Matcher, self).__init__(node_name, user_id,header, exchange_info,settings=settings)
                    
    def on_recieve_callback(self, ch, method, properties, body):
        super(Matcher,self).on_recieve_callback(ch, method, properties, body)
        self.log('Matching '+str(properties.headers))
        if 'requester' in properties.headers and not(self.node_name == properties.headers['requester']): # make sure not to match our own request
            body = "Match score = %f from %s"%(random.random(),self.node_name)
            self.log("doing match - sending "+body)
            exchange = RESULTS_EXCHANGE
            if properties.headers['requester']=='Web':
                exchange = WEB_EXCHANGE
            self.send(exchange, body, properties.headers,routing_key=properties.headers['requester'])


class Requester(MessageQueue):
    # the match request class - sends a request on the REQUEST_EXCHANGE
    
    def __init__(self, node_name, user_id="guest",settings=None):
        super(Requester, self).__init__(node_name, user_id,settings=settings)

    def send(self, msg,header):
        header.update({self.node_name:True,'requester':self.node_name})
        super(Requester,self).send(REQUEST_EXCHANGE,msg,header,True)

class Receiver(MessageBrokerBase):
    # retrieve the results from the RESULTS_EXCHANGE
    
    def __init__(self, node_name, user_id="guest",header={},exchange_info = RESULTS_EXCHANGE,settings=None):
        super(Receiver, self).__init__(node_name, user_id,header, exchange_info, settings=settings,routing_key=node_name) #routing_key=node_name,

    def on_recieve_callback(self, ch, method, properties, body):
        super(Receiver,self).on_recieve_callback(ch, method, properties, body)
        self.log("recieved "+body)


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

    parser.add_argument('--is_logger','-l', action='store_true',
                                       help='Is a logger')

    parser.add_argument('--name','-n', default='[No Name]',
                                       help='Name of the agency/node')
    
    parser.add_argument('--version', action='version', version='%(prog)s '+str(VERSION))

    args = parser.parse_args()

    header={"test":"test"}
    if args.is_matcher:
        matcher = Matcher(args.name,args.name,header,settings=args)
        matcher.start()
    elif args.is_broker:
        broker = Broker("broker",header,settings=args)
        #queue=broker.queue_bind(dest_queue, header)
        broker.start() #_consume(queue)
    elif args.is_requester:
        requester = Requester(args.name,args.name,settings=args)
        requester.send("Hello",header)
    elif args.is_receiver:
        receiver = Receiver(args.name,args.name,{args.name:True},settings=args)
        receiver.start()
    elif args.is_logger:
        logger = MsgLog("broker",header,settings=args)
        logger.start()
    #sendRequest(my_queue, dest_queue, priority, m_type, d_file)

