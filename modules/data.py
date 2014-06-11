# -*- coding: utf-8 -*-
"""
    Performix
    ~~~~~~~

    
    :copyright: (c) 2014 by the Biometix, see AUTHORS for more details.
    :license: 
"""
import redis
import copy,datetime
import urlparse


from werkzeug.routing import Map, Rule
from werkzeug.security import generate_password_hash,check_password_hash,pbkdf2_hex

from util import test_url, test_finished


class PxData(object):
    def __init__(self,redis):
        
        self.url_map = [
            Rule('/px/<base_id>/create/<object_id>', endpoint='create_item'),
            Rule('/px/<base_id>/delete/<attribute>/<object_id>', endpoint='del_item'),
            Rule('/px/<base_id>/update/<object_id>/<attribute>/<time>/<attr_bin>', endpoint='update_score_item'),
            Rule('/px/<base_id>/update/<object_id>/<attribute>/<time>/<attr_bin>/<count>', endpoint='update_score_item'),
            Rule('/px/<base_id>/link/<attribute>/<time>/<object_id1>/<object_id2>', endpoint='link'),
            Rule('/px/<base_id>/links/<attribute>/<time>/<object_id>', endpoint='links'),
            Rule('/px/<base_id>/read', endpoint='read_items'),
            Rule('/px/<base_id>/render', endpoint='render'),
            Rule('/px/<base_id>/group/<attribute>', endpoint='group_attribute'),
            Rule('/px/<base_id>/hist/<attribute>', endpoint='hist'),
            Rule('/px/<base_id>/read/<object_id>/<attribute>/<time>', endpoint='read_attribute'),
            Rule('/px/<base_id>/read/<object_id>/<attribute>', endpoint='read_histograms'),
            Rule('/px/<base_id>/read/<object_id>', endpoint='read_item'),
            Rule('/px/<base_id>/validate/<object_id>/<field>/<value>', endpoint='validate'),
            Rule('/px/<base_id>/check_key/<object_id>', endpoint='check_key'),
            
            Rule('/px/test', endpoint='test'),
            
            #Rule('/<short_id>', endpoint='follow_short_link'),
            #Rule('/<short_id>+', endpoint='short_link_details')
        ]
        self.redis=redis
    
    def on_test(self, request):
        
        def do(param,getdict={},logging=True,assertval=None):
            return test_url("px/%s/"%"0",param,getdict,logging,assertval)
        user_list =  ["px1","px2","px3","px4","px5"]
        
        # Setup
        for user in user_list:
            do(["delete","score",user],logging=False)
            do(["delete","quality",user],logging=False)
            do(["create",user],getdict={"name":user},logging=False)
            for u2 in user_list:
                if u2!=user:
                    do(["link","score","time",user,u2],logging=False)    
            #do(["read",user],assertval="r['name']=='%s'"%user,logging=False)
            #return do(["group","score"])
            #return do(["update","px1","score","2014-05-04",1])
            data = {"2014-05-04":[1,1,2,6,4,4,3,2,2,7,7,7,7,-1,'error'],"2014-05-05":[1,1,2,6,4,4,3,'error']}
            for time,vals in data.items():
                for val in vals:
                    assert(do(["update",user,"score",time,val],logging=False))
            for time,vals in data.items():
                for val in vals:
                    assert(do(["update",user,"quality",time,val],logging=False))
        
        # Setup per volume categories
        for category in ['c1','c2']:        
            data = {"2014-05-04":{'location_1':70,'location_2':100},"2014-05-05":{'location_1':1000,'location_3':200}}
            for time,vals in data.items():
                for loc,count in vals.items():
                    assert(do(["update","system1",category,time,loc,count],logging=False))
        
        # Test
        do(["validate","px1","name",'none'],assertval="r['_error']==12")
        do(["validate","px1","name","px1"],assertval="r['id']=='%s'"%"px1")
        do(["read","px1"],assertval="r['name']=='px1'")
            
        do(["read","px1","score","2014-05-04"],assertval="len(r)>4")
        
        do(["read","px1","score","*"],assertval="len(r)>4")

        do(["read","*","score"]) # return all user histograms for score (summed)
        #do(["read","px1","score"]) # return all histograms for px1 for score
        
        do(["read",'*',"c2"]) # return all category volumes (summed)
        
        
        do(["links","score","time","px1"],assertval="len(r)==2")
        do(["group","score"],assertval="r['count']==28")
        do(["hist","score"])
        do(["group","quality"],assertval="r['count']==28 and len(r['sum'])>5")
        #do(["read","score"])
        #do(["group","quality"])
        
        # clean up
        for user in user_list:
            do(["delete","score",user],logging=False)
            do(["delete","quality",user],logging=False)
        do(["delete","c1","system1"],logging=False)
        
        return test_finished()
    
    # Helper functions
    
    def get_lookup_id(self, base_id, key, time=0):
        return base_id+':'+key+':'+str(time)+':'
    
    def add_item(self, base_id, object_id):
        return self.redis.sadd(self.get_lookup_id(base_id,"_items"), object_id)

    def get_items(self, base_id):
        return self.redis.smembers(self.get_lookup_id(base_id,"_items")) 

    def get_item(self, base_id,object_id):
        lookup_id =  self.get_lookup_id(base_id,object_id)
        return self.redis.hgetall(lookup_id)

    def add_time(self, base_id, time):
        return self.redis.sadd(self.get_lookup_id(base_id,"_time"), time)
    
    def get_times(self, base_id):
        return self.redis.smembers(self.get_lookup_id(base_id,"_time")) 

    def get_object_lookup_id(self, base_id,attribute,time, object_id):
        return self.get_lookup_id(base_id,attribute,time)+','+object_id        
    
    # Store functions
    
    def on_create_item(self, request, base_id, object_id ):
        # set the items hash
        self.add_item(base_id, object_id)
        
        lookup_id =  self.get_lookup_id(base_id,object_id)
        
        # set the person details
        item_dict = {}
        for k,v in request.args.items():
            if len(v)==1:
                item_dict[k]=v[0]
            # if its a password, hash it
            if k=='__password':
                item_dict[k]=generate_password_hash(v)
            else: item_dict[k]=v
        
        item_dict['id'] = object_id
        
        self.redis.hmset(lookup_id, item_dict)
       
        result = self.redis.hgetall(lookup_id)
        # if its a password remove it
        #if '_password' in result:
        #    del result['_password']
        
        return result
    
    def on_check_key(self, request, base_id, object_id):
        
        if len(self.get_item(base_id,object_id))==0:
            return False
        else:
            return True
    
    def on_validate(self, request, base_id, object_id, field, value):
        result = self.get_item(base_id,object_id)
        
        ERROR_PASSWORD_VALIDATION = 12
        ERROR_VALIDATION = 12
        ERROR_NO_USER = 13

        if len(result)=={}:
            result={'_error':NO_USER}
        
        # if its a password
        if field in result:
            if field=='__password':
                if not check_password_hash(result[field],value):
                    result={'_error':ERROR_PASSWORD_VALIDATION}
                else:
                    request.client_session["px_user"]=result
                    #return redirect("/login")
            else:
                if result[field]!=value:
                    result={'_error':ERROR_VALIDATION}
        else:
            result={}
        return result

    def on_link(self, request, base_id, attribute, time, object_id1, object_id2 ):
        lookup_id = self.get_lookup_id(base_id,attribute, time)
        self.add_time(base_id, time)
        r1=self.redis.zincrby(lookup_id+',from:'+object_id1,object_id2,1)
        r2=self.redis.zincrby(lookup_id+',to:'+object_id2,object_id1,1)
        return [r1,r2]
    
    def on_links(self, request, base_id, attribute, time, object_id):
        lookup_id = self.get_lookup_id(base_id,attribute, time)
        return {'from':self.redis.zrange(lookup_id+',from:'+object_id,0,-1,withscores=True),
                'to':self.redis.zrange(lookup_id+',to:'+object_id,0,-1,withscores=True)}
         
    def on_update_score_item(self, request, base_id, attribute, time, object_id, attr_bin, count=1 ):
        self.add_item(base_id, object_id)
        self.add_time(base_id, time)
        lookup_id =  self.get_object_lookup_id(base_id,attribute,time,object_id)
        if 'cand_id' in request.args:
            candidate_id = request.args['cand_id']
            self.on_link(None,base_id,attribute,time,object_id,candidate_id)
        result = self.redis.zincrby(lookup_id, attr_bin, count)
        return result

    def on_read_items(self, request, base_id):
        return [
            self.get_item(base_id,item)
           for item in self.get_items(base_id)]
    
    def on_read_histograms(self, request, base_id, attribute, time=None,object_id=None):
        # return all histograms
        if not object_id or object_id=='*':
            res =  dict([[obj,self.on_read_attribute(request, base_id, attribute, time, obj)] for obj in self.get_items(base_id)])
            for k,v in res.items():
                if len(v)==0: del res[k]
            return res
            
        else:
           pass
        
            
    def on_read_item(self, request, base_id, object_id):
        return self.redis.hgetall(
            self.get_lookup_id(base_id,object_id)
          ) 
    
    def on_del_item(self, request, base_id, attribute, object_id):
        lookup_id =  self.get_lookup_id(base_id,"_items")     
        self.redis.srem(lookup_id,object_id)
        
        for t in self.get_times(base_id):
            lookup_id = self.get_lookup_id(base_id,attribute, t) 
            self.redis.delete(lookup_id+','+object_id) 
            self.redis.delete(lookup_id+',from:'+object_id) 
            self.redis.delete(lookup_id+',to:'+object_id)
            
        #assert(False)
        return {}

    def on_read_attribute(self, request, base_id, attribute, time=None, object_id=None):
        
        if not time or time=='*':
            attr_ids = [self.get_lookup_id(base_id,attribute,t) for t in self.get_times(base_id) ]
            obj_ids = [attr_id+','+object_id for attr_id in attr_ids]
            self.redis.zunionstore(attr_id+"sum",obj_ids, aggregate='SUM')
            result = self.redis.zrange(attr_id+"sum",0,-1,withscores=True)
        
        else:
            lookup_id =  self.get_lookup_id(base_id,attribute,time)+','+object_id   
            result = self.redis.zrange(lookup_id,0,-1,withscores=True)
            
        return result

    def on_hist(self, request, base_id, attribute, time=None):
        results = self.on_group_attribute(request, base_id, attribute, time=None)
        rdict = dict(results["sum"])
        def xfrange(start, stop, step):
            while start <= stop:
                yield '{0:g}'.format(float(start))
                start += step
            
        step_max=10.0
        step_min=-5.0
        step_size=0.5;
        for idx in xfrange(step_min,step_max,step_size):
            if not idx in rdict:
                results["sum"].append([idx,0.0])
        
        count = results["count"]
        def conv(v):
            try:
                return float(v[0]);
            except:
                return v[0]
        
        r_sorted = sorted(results["sum"],key=conv)
        vals = []
        bins = []
        other=[]
        for i,r in enumerate(r_sorted):
            try:
                #r_sorted[i]=[float(r[0]),float(r[1])/count]
                vals.append(float(r[1])/count)
                bins.append(float(r[0]))
            except:
                other.append([r[0],float(r[1])/count])
        diffs = [v-bins[i-1] for i,v in enumerate(bins) if i>0]
        if len([d for d in diffs if not d==diffs[0]])!=0 or diffs[0]!=step_size:
            return {'_error':'bin values wrong!'}
        
        return {'values':vals,'bins':bins,'other':other}
    
    def on_group_attribute(self, request, base_id, attribute, time=None):
        """
        Group Calculate Statistics
        ==========================
        /px/<base_id>/group/<attribute>
        
        Add all attributes from the given attribue together
        
        """        
        # build list of attribute ids including all times
        attr_ids = [self.get_lookup_id(base_id,attribute,t) for t in self.get_times(base_id) ]
        
        # create list which is all times and all objects for the given attribute
        obj_ids = []
        for object_id in self.get_items(base_id):
            obj_ids.extend([attr_id+','+object_id for attr_id in attr_ids])

        
        # for a specific time
        #attr_id = self.get_lookup_id(base_id,attribute,time)
        #obj_ids = [attr_id+','+object_id for object_id in self.redis.smembers(lookup_id)]
        
        attr_id = attr_ids[0]
        
        self.redis.zunionstore(attr_id+"sum",obj_ids, aggregate='SUM')
        self.redis.zunionstore(attr_id+"max",obj_ids, aggregate='MAX')
        self.redis.zunionstore(attr_id+"min",obj_ids, aggregate='MIN')
        sum_result = self.redis.zrange(attr_id+"sum",0,-1,withscores=True)
        min_result = self.redis.zrange(attr_id+"min",0,-1,withscores=True)
        max_result = self.redis.zrange(attr_id+"max",0,-1,withscores=True)
        
        return {'sum':sum_result,
             'min':min_result,
             'max':max_result,
             'count':len(obj_ids),
             'attribute':attribute
             }
    
    def on_render(self,request,base_id):
        response = self.render_template('showlist.html',url=[{'n':'h1'},{'n':'h2'}])
        return response
    
