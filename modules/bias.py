from werkzeug.routing import Map, Rule


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
    
connected_nodes = {}
logdata = []

global CONFIG

def log(value):
    global logdata
    from time import gmtime, strftime
    date = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()); 
    logdata.append([date,value])

from jsonrpc import dispatcher
def add_node(node_info):
    global connected_nodes
    connected_nodes[get_node_display_name(node_info)]=node_info
    print connected_nodes

def matching_servers(node_info,data):
    global connected_nodes, CONFIG

    
    if (len(connected_nodes)<2):
        local_name = get_node_display_name(Struct(get_current_node_info()))
        print "result "+local_name
        
        data_dir = os.path.join('static','data',local_name)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        lw = VerifySubjectResponse["VerifySubjectResponsePackage"]
        lw["Score"]=random.random()
        lw["Match"]=lw["Score"]>0.5
        #data[]
        #if data.get('Identity') and data.get
        open(
            os.path.join(
                data_dir,
                get_node_display_name(Struct(get_current_node_info()))+data['Identity']['BiometricData']['BIR']['FormatType'])
               ,'w'
        ).write(
            base64.b64decode(data['Identity']['BiometricData']['BIR']['BIR'])
        )
        return VerifySubjectResponse
    
    res={}
    node_url = get_node_url(node_info)
    for node_name,info in connected_nodes.items():
        if (node_url != get_node_url(info)):
            res[node_name]=send_request(info,"bias",data)
    return res

@dispatcher.add_method
def notify(**data):
    result=Struct(data)
    log("adding "+result.name)
    add_node(result)
    return get_current_node_info()

@dispatcher.add_method
def bias(**data):
    result=Struct(data)
    log("recieved bias request "+result.BIASOperationName+" from "+get_node_display_name(result._node))
    res = matching_servers(result._node,data)
    log("sending result of request "+result.BIASOperationName+" to "+get_node_display_name(result._node))
    return res




def deserialize_response(dict_obj_json):
    if dict_obj_json.status_code!=200:
        return {'error':dict_obj_json.reason}
    result = json.loads(dict_obj_json.json)
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
    
    log("sending to "+get_node_display_name(node))
    
    headers = {'content-type': 'application/json'}
    print "="*40
    
    dict_obj["_node"]=  get_current_node_info()

    payload = {
        "method": service,
        "params": dict_obj,
        "jsonrpc": "2.0",
        "id": 0,
    }
    
    response = requests.post(
       get_node_url(node), data=json.dumps(payload), headers=headers)
    
    log("received data from "+get_node_display_name(node))

    return deserialize_response(response)

# http://www.jsonrpc.org/specification

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

VerifySubjectResponse={
 	"VerifySubjectResponsePackage":{	
    	 "ResponseStatus": 	ResponseStatus,
    	 "Match":False,
    	 "Score":0.0
    }
}


class Struct(object):
    """Create an object from a dictonary for ease of use"""
    def __init__(self, data):
        for name, value in data.iteritems():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)): 
            return type(value)([self._wrap(v) for v in value])
        else:
            return Struct(value) if isinstance(value, dict) else value

def get_current_node_info():
    return {
                "url":None,        
                "port":CONFIG.port,
                'host':socket.gethostname(),
                'type':CONFIG.type,
                'country':CONFIG.country,            
                'location':CONFIG.location,
                'name':CONFIG.name,
                'services':{'verify':{},'identify':{},'enroll':{}}
                }

def create_hub_node_info():
    return Struct({
                "url":'http://'+CONFIG.hub_url,
                "name":"hub connection"
            })

class Verify(object):
    
    def __init__(self,CONFIG_IN):
        self.url_map = [Rule('/verify', endpoint='verify'),
                        Rule('/enroll', endpoint='enroll'),
                        Rule('/verify/assert', endpoint='assert'),
                        Rule('/v_request', endpoint='check'),
                        Rule('/log', endpoint='log')]
        global CONFIG
        CONFIG = CONFIG_IN
        if (CONFIG.hub_url):
            # if its a node then add it
            self.hub = create_hub_node_info()
            print str(send_request(self.hub,
                                "notify",
                                get_current_node_info()))
        
        
    def on_verify(self, request):
        print str(request.args.keys())
        #receive_dict(request.args)
        return {'verify':True}
    
    def on_upload(self, ):
        pass
    
    def on_log(self, request):
        global logdata

        return logdata

    def on_check(self, request):
        return send_request(self.hub,"bias",verifySubjectRequest)
    
    def on_enroll(self, request):
        import base64
        print str(request.form.to_dict())
        file = request.files.get('image')
        imgdata = 'None'
        if file:
            imgdata = base64.b64encode(file.read())
        verifySubjectRequest['Identity']['SubjectID']=request.form.get('Identity.SubjectID')
        (root, ext) = os.path.splitext(file.filename)
        verifySubjectRequest['Identity']['BiometricData']['BIR']['FormatType']=ext
        verifySubjectRequest['Identity']['BiometricData']['BIR']['BIR']=imgdata
        return send_request(self.hub,"bias",verifySubjectRequest)
        #return {'image':  imgdata} 
#        return send_request(self.hub,"bias",verifySubjectRequest)

    
    def on_assert(self, request):
        assert(False);
        pass
    
