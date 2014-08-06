#!/usr/bin/env python
import pika
import uuid
import sys
import os
import getopt

def callback(ch, method, properties, body):
    print " [x] Received %r" % (body,)



def sendRequest(my_agency, dest_exchange, priority, m_type, d_file):
  m_id=1
  connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
  channel = connection.channel()
  channel.exchange_declare(exchange=dest_exchange, type='topic')
  routing_key = "request."+priority+"."+m_type+"."+my_agency+"."+str(m_id)+".test"
  message = 'Hello World!'
  channel.basic_publish(exchange=dest_exchange,
                      routing_key=routing_key,
                      body=message) 
  print " [x] Sent %r:%r" % (routing_key, message)
  m_id+=1  


    
def main(argv):
   my_queue=""
   dest_queue=""
   priority=0
   m_type=""
   d_file=""
 
   try:
      opts, args = getopt.getopt(argv,"i:q:t:p:f:",["my_agency_id=","to_queue=","type=", "priority=", "datafile="])
   except getopt.GetoptError:
      print 'send_msg.py -i<MY_AGENCY_ID> -q <TO_QUEUE> -t <TYPE> -p <PRIORITY> [-f <DATAFILE>]'
      sys.exit(2)
   print opts   
   for opt, arg in opts:
      print arg 
      if opt == '-h':
         print 'send_msg.py -i<MY_AGENCY_ID> -q <TO_QUEUE> -t <TYPE> -p <PRIORITY> [-f <DATAFILE>]'
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
         d_file = arg
   sendRequest(my_queue, dest_queue, priority, m_type, d_file)


       

if __name__ == "__main__":
   try:
      opts, args = getopt.getopt(sys.argv,"i:q:t:p:f:",["MY_AGENCY_ID=","TO_QUEUE=","TYPE=", "PRIORITY=", "DATAFILE="])
   except getopt.GetoptError: 
      pass    
   main(sys.argv[1:])


