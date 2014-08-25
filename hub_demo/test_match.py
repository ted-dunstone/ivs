import pika
import sys
import logging
logging.basicConfig()

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='Australia_NZ_Exchange',
                         type='headers')

result = channel.queue_declare(exclusive=True)
if not result:
    print 'Queue didnt declare properly!'
    sys.exit(1)
queue_name = result.method.queue

channel.queue_bind(exchange='Australia_NZ_Exchange',
                   queue = queue_name,
                   routing_key = '',
                   arguments = {'test': 'test', 'x-match':'any'})

def callback(ch, method, properties, body):
    print properties.user_id
    print "{headers}:{body}".format(headers = properties.headers,
                                    body = body)

channel.basic_consume(callback,
                      queue = queue_name,
                      no_ack=True)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print 'Bye'
finally:
    connection.close()
