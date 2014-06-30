from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Response

import pika # RabbitMQ Interface
import logging
from betaface import BetaFaceAPI

from json import JSONEncoder
from collections import namedtuple
import base64

class BiasEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__    

#d_named = namedtuple('Struct', verify_obj.keys())(*verify_obj.values())


import requests
import json
import random
import os, os.path


#################

GenericRequestParameters = {
	 "Application":"AppID",
	 "ApplicationUser":"ApplicationUserIdentifier",
	 "BIASOperationName":""
}

BinaryBIR = {
    "Binary":"base64encoded"
}

CBEFF_BIR_Type={
	 "FormatOwner":0,
	 "FormatType":0,
	 "BIR_Information":{	
		 "BIR_Info":"BIRInfoType"
      },
	 "BIR":BinaryBIR
}

BiometricDataElementType= {	
	 "BiometricType":"The type of biological or behavioral data stored in the biometric record, as defined by CBEFF",
	 "BiometricTypeCount":	0,
	 "BiometricSubType":	"More specifically defines the type of biometric data stored in the biometric record, as defined by CBEFF",
     "BDBFormatOwner":	0,
	 "BDBFormatType":	0
}

BIASBiometricDataType = {	
	 "BIRList":[],
	 "BIR":CBEFF_BIR_Type,
	 "InputBIR":CBEFF_BIR_Type,
	 "ReferenceBIR":CBEFF_BIR_Type,
	 "BiometricDataList":[BiometricDataElementType]
}


BIASIDType = ""

BiographicDataItemType = {
	 'Name':'', #The name of the biographic data item
	 'Type':'', #The data type for the biographic data item
	 'Value':'' #The value assigned to the biographic data item.
}

BiographicDataSetType = {
    #for specific data formats non-XML (FBI-EFTS, FBI-EBTS, DOD-EBTS, or INT-I), XML (e.g., for NIEM, xNAL, and HR-XML or future versions of FBI-EBTS)
}

BiographicDataType={	
	 'LastName':'',
	 'FirstName':'',
	 'BiographicDataItems':	[BiographicDataItemType],
	 'BiographicDataSet':BiographicDataSetType
}

BIASIdentity = {
	 "SubjectID":BIASIDType,
	 "IdentityClaim":BIASIDType,
	 "EncounterID":BIASIDType,
	 "EncounterList":[],
	 "BiographicData":BiographicDataType,
	 "BiographicDataElements":BiographicDataType,
	 "BiometricData":BIASBiometricDataType
}

ResponseStatus={
		 "Return":"0",
		 "Message":"None"
}


verifySubjectRequest={   
    "GenericRequestParameters":GenericRequestParameters,
    
    "BIASOperationName":"Verify",
    
     "GalleryID": {
       "galleries":["12","23","2323","2323"]
    },
        
    "ProcessingOptions": {
       "Options":{}
    },
    "Identity":BIASIdentity,   
    "InputData":{},
    
}

enrollSubjectRequest={   
    "GenericRequestParameters":GenericRequestParameters,
    
    "BIASOperationName":"Enroll",
    
     "GalleryID": {
       "galleries":["12","23","2323","2323"]
    },
        
    "ProcessingOptions": {
       "Options":{}
    },
    "Identity":BIASIdentity,   
    "InputData":{},
    
}

VerifySubjectResponse={
 	"VerifySubjectResponsePackage":{	
    	 "ResponseStatus": 	ResponseStatus,
    	 "Match":False,
    	 "Score":0.0
    }
}

#####################
    
connected_nodes = {}
logdata = []

logging.basicConfig(level = logging.INFO)

global CONFIG

def log(value,logtype=None,data=None):
    global logdata
    from time import gmtime, strftime
    date = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime());
    time = strftime("%I:%M:%S %p", gmtime()); 
    day = strftime("%a, %d %b", gmtime());
    if logtype=='Add Node':
        classtype = 'info'
        icon = 'plus'
    elif logtype=='Verify':
        classtype = 'success'
        icon = 'question-sign'
    elif logtype=='Send Data':
        classtype = 'error'
        icon = 'upload'
    else:
        classtype = 'warning'
        icon =''
        
        
    print "LOG :"+logtype
    
    logdata.insert(0,{'date':date,'value':value,'index':len(logdata),'day':day,'time':time,'logtype':logtype,'data':data,'class':classtype,'icon':icon})

from jsonrpc import dispatcher
def add_node(node_info):
    global connected_nodes
    connected_nodes[get_node_display_name(node_info)]=node_info
    print connected_nodes

def storeimage(fname,imgdata):
    local_name = get_node_display_name(Struct(get_current_node_info()))
    data_dir = os.path.join('static','data',local_name)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    fullpath = os.path.join(data_dir,fname)
    open(
            fullpath,
               'w'
        ).write(
            imgdata
        )
    return fullpath
        
    

def matching_servers(node_info,data):
    global connected_nodes, CONFIG

    print "OPERATION "+data['BIASOperationName']
    
    if (len(connected_nodes)<2):
        
        subjectID = data['Identity']['SubjectID']

        nodename = get_node_display_name(Struct(get_current_node_info()))
        fname = subjectID # + data['Identity']['BiometricData']['BIR']['FormatType']
        imgdata = base64.b64decode(data['Identity']['BiometricData']['BIR']['BIR'])
        
        lw = VerifySubjectResponse["VerifySubjectResponsePackage"]
        lw["Score"]=0
        lw["Match"]=False
        
        lw["ImageUrl"] = storeimage(fname,imgdata)
    
        client = BetaFaceAPI()
        if data['BIASOperationName']=='Verify':
            
            print lw["ImageUrl"]
            print  '@'+nodename
            print len(open(lw["ImageUrl"]).read())
            
            fr_result = (client.recognize_faces(lw["ImageUrl"], nodename))
            matches = {}
            for pid,score in fr_result.iteritems():
                if (score>=0.8):
                    lw["Score"]=score
                    lw["Match"]=True
                    matches[pid]=score
            lw["Gallery"]  = str(matches)
            
            
            print "verify"
        elif data['BIASOperationName']=='Enroll':
            print "enroll"
#            client.upload_face(os.path.join(data_dir,fname), subjectID)
            
        
        log('Underaking Facial Match','Matching',lw)
        return VerifySubjectResponse
    
    res={}
    node_url = get_node_url(node_info)
    for node_name,info in connected_nodes.items():
        if (node_url != get_node_url(info)):
            print ".. sending to "+node_name
            res[node_name]=send_request(info,"bias",data)
    print str(res)
    return res

@dispatcher.add_method
def notify(**data):
    result=Struct(data)
    log(result.name,"Add Node", data)
    add_node(result)
    return get_current_node_info()

@dispatcher.add_method
def bias(**data):
    result=Struct(data)
    local_node = get_current_node_info()
    #self.redis.lpush('incoming queue '+local_node.name,data)
    log("recieved request from "+get_node_display_name(result._node),result.BIASOperationName,data)
    res = matching_servers(result._node,data)
    log("sending result of request to "+get_node_display_name(result._node),result.BIASOperationName,data)
    return res




def deserialize_response(dict_obj_json):
    if dict_obj_json.status_code!=200:
        return {'error':dict_obj_json.reason}
    try:
      result = json.loads(dict_obj_json.json())
    except:
      print '********** ERROR ******'+dict_obj_json.json()
      raise

    if "result" in result:
        return result["result"]
    else:
        return result

import socket

def get_node_url(node):
    if node.url:
        return node.url
    return 'http://'+node.host+':'+node.port

def get_node_display_name(node):
    if node.name:
        return node.name
    else:
        get_node_url(node)


def send_request(node,service,dict_obj):
    global CONFIG
    Q_MGR.push(get_current_node_info()['name']+'_outgoing',dict_obj) 
    
    headers = {'content-type': 'application/json'}
    print "="*40
    
    dict_obj["_node"]=  get_current_node_info()

    log("sending to "+get_node_display_name(node),"Send Data",dict_obj)

    payload = {
        "method": service,
        "params": dict_obj,
        "jsonrpc": "2.0",
        "id": 0,
    }
    
    response = requests.post(
       get_node_url(node), data=json.dumps(payload), headers=headers)
    
    log("received data from "+get_node_display_name(node),"Received Data",dict_obj)
    #log("received data from "+get_node_display_name(node))

    return deserialize_response(response)

# http://www.jsonrpc.org/specification




class Struct(object):
    """Create an object from a dictonary for ease of use"""
    def __init__(self, data):
        for name, value in data.iteritems():
            setattr(self, name, self._wrap(value))
        self.__data = data

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)): 
            return type(value)([self._wrap(v) for v in value])
        else:
            return Struct(value) if isinstance(value, dict) else value
    
    def data(self, ):
        return self.__data
    

def get_current_node_info():
    return {
                "url":None,        
                "port":CONFIG.port,
                'host':socket.gethostname(),
                'type':CONFIG.type,
                'country':CONFIG.country,            
                'location':CONFIG.location,
                'name':CONFIG.name,
                'logo':CONFIG.logo,
                'services':{'verify':{},'identify':{},'enroll':{}}
                }

def create_hub_node_info():
    return Struct({
                "url":'http://'+CONFIG.hub_url,
                "name":"hub connection",
                'logo':CONFIG.logo
            })

class HubQueue(object):
    def __init__(self, queueName, channel, exchange=''):
        self.queueName = queueName
        self.channel = channel
        self.exchange = exchange
    
    def create(self):
        self.channel.queue_declare(queue=self.queueName)
        
    def push(self, contents):
        return self.channel.basic_publish(exchange=self.exchange,
                      routing_key=self.queueName,
                      body=str(contents))
    
    def pull(self):
        for method_frame, properties, body in self.channel.consume(self.queueName):
            # Display the message parts and ack the message
            #print method_frame, properties, body
            channel.basic_ack(method_frame.delivery_tag)
            return body
            # Escape out of the loop after 10 messages
            #if method_frame.delivery_tag == 10:
            #    break

    

class QueueManager(object):
    
    def __init__(self, ):
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.CRITICAL)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
        self.channel = self.connection.channel()
        self.queues = {}
        
    def createQueue(self, queueName):
        q = HubQueue(queueName, self.channel)
        q.create()
        self.queues[queueName]=q
        
    def push(self, queueName, contents):
        if queueName not in self.queues:
            self.createQueue(queueName)
        self.queues[queueName].push(contents)

    def pull(self, queueName):
        return self.queues[queueName].pull(contents)
    

    
    

class Verify(object):
    
    def __init__(self,CONFIG_IN, service):
        self.url_map = [Rule('/verify', endpoint='verify'),
                        Rule('/enroll', endpoint='enroll'),
                        Rule('/demo/enroll', endpoint='demo_enroll'),
                        Rule('/demo/verify', endpoint='demo_verify'),
                        Rule('/verify/assert', endpoint='assert'),
                        Rule('/v_request', endpoint='check'),
                        Rule('/log', endpoint='log')]
        global CONFIG
        CONFIG = CONFIG_IN
        global Q_MGR
        Q_MGR = QueueManager()
        
        self.service = service
        self.redis = service.redis
        
        
        if (CONFIG.hub_url):
            # if its a node then add it
            self.hub = create_hub_node_info()
            print str(send_request(self.hub,
                                    "notify",
                                    get_current_node_info()))
        
        Q_MGR.createQueue(CONFIG.name+'_incomming')
        Q_MGR.createQueue(CONFIG.name+'_outgoing')
        
    def on_verify(self, request):
        print str(request.args.keys())
        #receive_dict(request.args)
        return {'verify':True}
    
    def on_upload(self, ):
        pass
    
    def on_demo_enroll(self, request):
        return self.service.render_template('enroll.html', config=CONFIG, action={'url':"enroll",'name':"Enrolment Service"})
    
    def on_demo_verify(self, request):
        return self.service.render_template('enroll.html', config=CONFIG, action={'url':"verify",'name':"Authentication Service"})
    
    def on_log(self, request):
        global logdata
        
        
        return self.service.render_template('timeline.html', log=logdata,config=CONFIG)
        

    def on_check(self, request):
        return send_request(self.hub,"bias",verifySubjectRequest)
    
    def on_enroll(self, request):
        import base64, re
        file = request.files.get('image')
        client = BetaFaceAPI()
        nodename = get_node_display_name(Struct(get_current_node_info()))
        SubjectID= request.form.get('Identity.SubjectID')+'.png'
        if file:
            fullpath = storeimage(file.filename,file.read())
            client.upload_face(fullpath,  os.path.basename(file.filename)+'@'+nodename)
        else:
            imgdata=re.search(r'base64,(.*)', request.form['cameraImage']).group(1)
            fullpath = storeimage(SubjectID,base64.b64decode(imgdata))
            client.upload_face(fullpath,  SubjectID+'@'+nodename)
        return self.on_demo_enroll(request)
        

    def on_verify(self, request):
        import base64,re
        print str(request.form.to_dict())
        file = request.files.get('image')
        imgdata = 'None'
        if file:
            imgdata = base64.b64encode(file.read())
            (root, ext) = os.path.splitext(file.filename)
            SubjectID= os.path.basename(root)
            print "uploaded file "+str(len(imgdata)) + " "+ SubjectID + " " + ext
        else:
            imgdata=re.search(r'base64,(.*)', request.form['cameraImage']).group(1)
            SubjectID= request.form.get('Identity.SubjectID')
            ext = '.png'
        verifySubjectRequest['Identity']['SubjectID']=SubjectID
        
        verifySubjectRequest['Identity']['BiometricData']['BIR']['FormatType']=ext
        verifySubjectRequest['Identity']['BiometricData']['BIR']['BIR']=imgdata
        results =  send_request(self.hub,"bias",verifySubjectRequest)
        
        return self.service.render_template('results.html', results=results, config=CONFIG)
        
    
    def on_assert(self, request):
        assert(False);
        pass
    
