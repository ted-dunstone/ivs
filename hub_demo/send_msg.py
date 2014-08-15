#!/usr/bin/env python
import pika
import uuid
import sys
import os
import getopt

def callback(ch, method, properties, body):
    print " [x] Received %r" % (body,)

class MessageBroker(object):
    def __init__(self, my_agency, user_id="guest"):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
              host='localhost'))
        self.channel = self.connection.channel()
        self.my_agency = my_agency
        self.user_id = user_id
        
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
        
        header.update({self.my_agency:True,
                       "agency":self.my_agency,
                       "destination":exchange})
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange=exchange,
                                routing_key='',
                                body=message,
                                properties = pika.BasicProperties(
                                headers = header,
                                reply_to = callback_queue,
                                correlation_id = self.corr_id,
                                user_id = self.user_id)
                            )
        print " [x] Sent %r" % (message)
        
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

    def on_recieve_callback(self, ch, method, properties, body):
        print properties.user_id
        print properties.reply_to
        print "{headers}:{body}".format(headers = properties.headers,
                                        body = body)
        response = "Success"
        if properties.reply_to:
            ch.basic_publish(exchange='',
                         routing_key=properties.reply_to,
                         properties=pika.BasicProperties(correlation_id = \
                                                         properties.correlation_id),
                         body=str(response))

    def on_response_callback(self, ch, method, props, body):
        print "[x] response"
        if self.corr_id == props.correlation_id:
            self.response = body
            
    def start_consume(self,queue_name):
        self.channel.basic_consume(self.on_recieve_callback,
                              queue = queue_name,
                              no_ack=True)

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print 'Bye'
        finally:
            self.connection.close()


def main(argv):
    
    my_queue=""
    dest_queue=""
    priority=0
    m_type=""
    d_file=""
    brokerFlag=False
    try:
        opts, args = getopt.getopt(argv,"i:q:t:p:f:",["my_agency_id=","to_queue=","type=", "priority=", "datafile="])
    except getopt.GetoptError:
        print 'send_msg.py -i<MY_AGENCY_ID> -q <TO_QUEUE> -t <TYPE> -p <PRIORITY> [-f <DATAFILE>] [-b broker]'
        sys.exit(2)
    for opt, arg in opts:
        print arg
        if opt == '-h':
            print 'send_msg.py -i<MY_AGENCY_ID> -q <TO_QUEUE> -t <TYPE> -p <PRIORITY> [-f <DATAFILE>] [-b broker]'
            sys.exit(1)
        elif opt in ("-i", "--my_agency_id"):
            my_queue = arg
        elif opt in ("-q", "--to_queue"):
            dest_queue = arg
        elif opt in ("-t", "--type"):
            m_type = arg
        elif opt in ("-p", "--priority"):
            priority = arg
        elif opt in ("-f", "--datafile"):
            brokerFlag = True
#            d_file = arg
        elif opt in ("-b", "--broker"):
            broker = True
            
    broker = MessageBroker(my_queue)
    header={"test":"test"}
    if brokerFlag:
        queue=broker.queue_bind(dest_queue, header)
        broker.start_consume(queue)
    else:    
        broker.send(dest_queue,"Hello",header,False)
    #sendRequest(my_queue, dest_queue, priority, m_type, d_file)




if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv,"i:q:t:p:f:",["MY_AGENCY_ID=","TO_QUEUE=","TYPE=", "PRIORITY=", "DATAFILE="])
    except getopt.GetoptError:
        pass
    main(sys.argv[1:])
