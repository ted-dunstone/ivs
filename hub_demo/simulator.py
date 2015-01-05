#!/usr/bin/env python
import pika
import sys
import getopt
import threading
from subprocess import call,check_call
import time

VERSION = 0.8

COUNTRIES = ['broker','test@Immi.gov.au','test@Immi.gov.my','test@Immi.gov.id','test@Immi.gov.th','test@Immi.gov.us']

class Simulator(object):


     #pass in the list of hub/server exchanges, client exchanges, and request types (i.e, match, enrol, etc..-).
    def __init__(self, countries ):
        call('pkill -f "python send_msg"',shell=True)
        
        # Start the broker
        check_call('python send_msg.py -b &',shell=True)
        time.sleep(5.0)
        
        # start the logger
        check_call('python send_msg.py -l &',shell=True)
        
 #       for exchange in ['Request','Identify','Results']:
 #           check_call('python rabbitmqadmin.py delete exchange name=%s'%exchange,shell=True)    
        for c in countries:
            print "*****"+c
            
            # setup user
            check_call('python rabbitmqadmin.py declare user name="%s" password="guest" tags="Australia_NZ,Bali"'%c,shell=True)
            s = 'python rabbitmqadmin.py declare permission vhost="/" user="%s" configure=".*" write=".*" read=".*"'%c
            check_call(s,shell=True)
            
            if c!='broker':
                #start the matching service
                check_call('python send_msg.py -m -n "%s" &'%c,shell=True)

                #start the results listening service
                check_call('python send_msg.py -e -n "%s" &'%c,shell=True)
                
        # simulate calls        
        #for i in range(1,20):
        #    for c in countries:
        #        check_call('python send_msg.py -r -n "%s" &'%c,shell=True)
            


    def getExchangeStats(self, exchange):
        pass




if __name__ == "__main__":
    import argparse


    # Parse command line args
    # note that args can be read from a file using the @ command
    parser = argparse.ArgumentParser(description='Identity Verification Service',fromfile_prefix_chars='@')
    parser.add_argument('--port','-p', default=8000,
                                       help='set the port (default 8000)')

    parser.add_argument('--version', action='version', version='%(prog)s '+str(VERSION))

    args = parser.parse_args()
    
    s = Simulator(COUNTRIES)
    
