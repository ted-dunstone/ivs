#!/usr/bin/env python
import pika
import logging
import modules.bias

import json

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.CRITICAL)

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='OBTB',
                         type='direct')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue


channel.queue_bind(exchange='OBTB',
                       queue=queue_name,
                       routing_key='PASSPORTS_outgoing')

print ' [*] Waiting for logs. To exit press CTRL+C'

def callback(ch, method, properties, body):
    open('test.json','w').write(body)
    result =eval(body)

    print " [x] %r:%r" % (method.routing_key, result.keys(),)

channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()