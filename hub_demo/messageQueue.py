#!/usr/bin/env python

## Message Queue Abstraction

import pika
import uuid
import sys
import logging

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
        

    def log(self, msg):
        print self.node_name + ' : ' + msg
    
    def setup(self, ):
        pass
    
    def create_queue(self, name=None):
        if name==None:
            result = self.channel.queue_declare(exclusive=True)
        else:
            result = self.channel.queue_declare(exclusive=True) #,queue=name)
        
        if not result:
            print 'Queue didnt declare properly!'
            sys.exit(1)
        return result

    def send(self, exchange, message, header={}, callback=False):
        callback_queue = None
        callback_name = ''
        self.response = None

        if (callback):
            callback_queue = self.create_queue()
            callback_name = callback_queue.method.queue
            self.channel.basic_consume(self.on_response_callback,
                              queue = callback_name,
                              no_ack=True)
        header.update({
                       "last_node":self.node_name,
                       "destination":exchange})
        self.corr_id = str(uuid.uuid4())
        self.corr_dict[self.corr_id]=True
        self.channel.basic_publish(exchange=exchange,
                                routing_key='',
                                body=message,
                                properties = pika.BasicProperties(
                                headers = header,
                                reply_to = callback_name,
                                correlation_id = self.corr_id,
                                user_id = self.user_id)
                            )
        self.log(" [x] Sent %r to %s" % (message,exchange))

        if (callback):
            while self.response is None:
                self.connection.process_data_events()
            #print "Response:"+str(self.response)
            #print str(dict(callback_queue))
            #self.callback_queue.delete()

    def queue_bind(self, exchange, header_match={}):
        print str(exchange)
        #self.channel.exchange_declare(exchange=exchange["name"], type=exchange["ex_type"])
        #self.create_queue(self.node_name)
        header_match.update({'x-match':'any'})

        self.channel.queue_bind(exchange=exchange["name"],
                           queue = self.queue_name,
                           routing_key = '',
                           arguments = header_match)
        return self.queue_name

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
        #self.log("[x] response %s,%s"%(props.correlation_id,str(self.corr_dict)))
        if props.correlation_id in self.corr_dict:
            #del self.corr_dict[props.correlation_id]
            self.response = body

    def start_consume(self,queue_name):
        #self.channel.basic_qos(prefetch_count=1)

        self.channel.basic_consume(self.on_recieve_callback,
                              queue = queue_name,
                              no_ack=True)

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.log('Bye')
        finally:
            self.connection.close()