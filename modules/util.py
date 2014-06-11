import redis
import copy,datetime
import urlparse
from werkzeug.wrappers import Response
import json


def remove_private(inData):
        out=inData
        if (type(inData)==type({})):
            out={}
            for k,v in inData.items():
                if type(k) == type('') and k.startswith('__'):
                    v='*******'
                if type(v)==type({}):
                    v=remove_private(v)
                out[k]=v
        elif (type(inData)==type([])):
            out=[]
            for v in inData:
                if type(v)==type({}) or type(v)==type([]):
                    v=remove_private(v)
                out.append(v)
        return out
        
def returnJson(val):
        val=remove_private(val)
        return Response(json.dumps(val), mimetype='application/json')

def checkAuth(request):
    try:
        return request.client_session["px_user"]
    except:
        return False

def requireAuth(f):
    def proxy(*args, **kwargs):
        data = request.values.to_dict()
        request = args[1]
        if checkAuth(args[1]):
            pass
        else:
            raise BadRequest('Authenticatuion Failed')
        #try:
        #    args, kwargs = validate_arguments(f, (request,), data)
        return f(*args, **kwargs)
    return proxy

test_cnt=0
test_failed_cnt=0
test_log = []

def test_url(baseurl,param,getdict={},logging=True,assertval=None):
    import urllib
    global test_log,test_cnt,test_failed_cnt
    
    def execute(url):
        result = urllib.urlopen(''+url).read()
        if result.startswith('<!'):
                return result
        result.replace('true','True')
        result.replace('false','False')
        return eval(result)
    
    baseid = '0'
    baseurl = "http://127.0.0.1:5000/"+baseurl
    baseurl+='/'.join([str(p) for p in param])
    baseurl+='?'+urllib.urlencode(getdict)
    results = execute(baseurl)
    if type(results)==type("") and results.startswith('<!'):
        return results
    status = ''
    r=results
    if assertval:
        test_cnt+=1
        if eval(assertval):
            status = '_PASSED_'
        else:
            status = '_FAILED_'
            test_failed_cnt+=1
    if logging or status=='_FAILED_':
        test_log.append(status+' **** '+param[0]+' **** '+' : '+baseurl)
        if  status=='_FAILED_' or not assertval:
            test_log.append({'url':baseurl,'assert':assertval,'results':results})
    return results

def test_finished():
    global test_log,test_cnt,test_failed_cnt
    
    test_log.insert(0,"====== %i Tests done, %i Tests failed ====="%(test_cnt,test_failed_cnt))
    
    out_log = copy.copy(test_log)
    test_cnt = test_failed_cnt = 0
    test_log = []
    return out_log