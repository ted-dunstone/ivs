#!/usr/bin/env python
import pika
import uuid
import sys
import os
import getopt
import time
import logging
import random

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.CRITICAL)


class MessageQueue(object):
    def __init__(self, node_name, # the name of node
                        user_id="guest", # the user id
                        ):
        credentials = pika.PlainCredentials(user_id, 'guest')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
              host='localhost', credentials=credentials))
        self.channel = self.connection.channel()
        self.node_name = node_name
        self.user_id = user_id
        self.corr_dict = {}
        print "start node %s"%node_name

    def create_queue(self, exchange):
        self.channel.exchange_declare(exchange=exchange, type='headers')
        result = self.channel.queue_declare(exclusive=True)
        if not result:
            print 'Queue didnt declare properly!'
            sys.exit(1)
        return result.method.queue

    def send(self, exchange, message, header={}, callback=False):
        callback_queue = None
        self.create_queue(exchange)
        self.response = None

        if (callback):
            callback_queue = self.create_queue(exchange)
            self.channel.basic_consume(self.on_response_callback,
                              queue = callback_queue,
                              no_ack=True)

        header.update({self.node_name:True,
                       "from_node":self.node_name,
                       "destination":exchange})
        self.corr_id = str(uuid.uuid4())
        self.corr_dict[self.corr_id]=True
        self.channel.basic_publish(exchange=exchange,
                                routing_key='',
                                body=message,
                                properties = pika.BasicProperties(
                                headers = header,
                                reply_to = callback_queue,
                                correlation_id = self.corr_id,
                                user_id = self.user_id)
                            )
        print " [x] Sent %r to %s" % (message,exchange)

        if (callback):
            while self.response is None:
                self.connection.process_data_events()
            print "Response:"+str(self.response)

    def queue_bind(self, exchange, header_match={}):
        queue_name = self.create_queue(exchange)
        header_match.update({'x-match':'any'})

        self.channel.queue_bind(exchange=exchange,
                           queue = queue_name,
                           routing_key = '',
                           arguments = header_match)
        return queue_name

    def on_return_status(self, properties):
        # called as RPC to return the status of a sent msg (probably synchronously)
        return "[Nothing implemented]"

    def on_recieve_callback(self, ch, method, properties, body):
        #print properties.user_id
        #print properties.reply_to
        #print "{headers}:{body}".format(headers = properties.headers,
        #                                body = body)
        #print "wait...."
        #time.sleep(10.0)
        if properties.reply_to:
            response = "Success"
            ch.basic_publish(exchange='',
                         routing_key=properties.reply_to,
                         properties=pika.BasicProperties(correlation_id = \
                                                         properties.correlation_id),
                         body=str(self.on_return_status(properties)))

    def on_response_callback(self, ch, method, props, body):
        print "[x] response %s,%s"%(props.correlation_id,str(self.corr_dict))
        if props.correlation_id in self.corr_dict:
            #del self.corr_dict[props.correlation_id]
            self.response = body

    def start_consume(self,queue_name):
        self.channel.basic_qos(prefetch_count=1)

        self.channel.basic_consume(self.on_recieve_callback,
                              queue = queue_name,
                              no_ack=True)

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print 'Bye'
        finally:
            self.connection.close()

VERSION = 0.5

REQUEST_EXCHANGE_NAME = "Request"
IDENTIFY_EXCHANGE_NAME = "Identify"
RESULTS_EXCHANGE_NAME = "Results"

class MessageBrokerBase(MessageQueue):
    def __init__(self, node_name, user_id="guest",header={},exchange_name = REQUEST_EXCHANGE_NAME):
        super(MessageBrokerBase, self).__init__(node_name, user_id)
        self.exchange_name = exchange_name
        self.request_queue=self.queue_bind(self.exchange_name, header)
        print self.__class__.__name__

    def start(self, ):
        self.start_consume(self.request_queue)


class Broker(MessageBrokerBase):
    def __init__(self, user_id="guest",header={},exchange_name = REQUEST_EXCHANGE_NAME):
        super(Broker, self).__init__("Broker", user_id,header, exchange_name)
        
    def on_return_status(self, properties):
        # called as RPC to return the status of a sent msg
        return "[OK] from %s"%self.node_name

    def on_recieve_callback(self, ch, method, properties, body):
        super(Broker,self).on_recieve_callback(ch, method, properties, body)
        self.send(IDENTIFY_EXCHANGE_NAME, body, properties.headers, False)


class Matcher(MessageBrokerBase):
    def __init__(self, node_name, user_id="guest",header={},exchange_name = IDENTIFY_EXCHANGE_NAME):
        super(Matcher, self).__init__(node_name, user_id,header, exchange_name)
        
    def on_recieve_callback(self, ch, method, properties, body):
        super(Matcher,self).on_recieve_callback(ch, method, properties, body)
        body = "Match score = %f from %s"%(random.random(),self.node_name)
        self.send(RESULTS_EXCHANGE_NAME, body, properties.headers)


class Requester(MessageQueue):
    def __init__(self, node_name, user_id="guest"):
        super(Requester, self).__init__(node_name, user_id)

    def send(self, msg,header):
        super(Requester,self).send(REQUEST_EXCHANGE_NAME,msg,header,True)

class Receiver(MessageBrokerBase):
    def __init__(self, node_name, user_id="guest",header={},exchange_name = RESULTS_EXCHANGE_NAME):
        super(Receiver, self).__init__(node_name, user_id,header, exchange_name)

    def on_recieve_callback(self, ch, method, properties, body):
        super(Receiver,self).on_recieve_callback(ch, method, properties, body)
        print "**** Result from %s"%(str(properties.headers))
        print body


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
        matcher = Matcher(args.name,"t1@t1.com",header)
        matcher.start()
    elif args.is_broker:
        broker = Broker("t1@t1.com",header)
        #queue=broker.queue_bind(dest_queue, header)
        broker.start() #_consume(queue)
    elif args.is_requester:
        requester = Requester(args.name,"t1@t1.com")
        requester.send("Hello",header)
    elif args.is_receiver:
        receiver = Receiver(args.name,"t1@t1.com",{args.name:True})
        receiver.start()
    #sendRequest(my_queue, dest_queue, priority, m_type, d_file)

