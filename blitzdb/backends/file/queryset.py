from blitzdb.queryset import QuerySet as BaseQuerySet
import time
import copy

class QuerySet(BaseQuerySet):

    def delete(self):
        collection = self.backend.get_collection_for_cls(self.cls)
        self.backend.delete_by_store_keys(collection,self.keys)
        self.keys = []
        self.objects = {}

    def filter(self,*args,**kwargs):
        return self.backend.filter(self.cls,*args,initial_keys = self.keys,**kwargs)

    def filter_by_key(self,key,expression):
        return self.backend.filter_by_key(self.cls,expression,initial_keys = self.keys)

    def _clone(self,keys):
        return self.__class__(self.backend,self.cls,self.store,copy.copy(keys))

    def __init__(self,backend,cls,store,keys):
        super(QuerySet,self).__init__(backend,cls)
        self.store = store
        self.keys = list(keys)
        self.objects = {}

    def __getitem__(self,i):
        key = self.keys[i]
        if not key in self.objects:
            self.objects[key] = self.backend.get_object(self.cls,key)
            self.objects[key]._store_key = key
        return self.objects[key]

    def __and__(self,other):
        return self._clone(set(self.keys) & set(other.keys))

    def __or__(self,other):
        return self._clone(set(self.keys) | set(other.keys))

    def __len__(self):
        return len(self.keys)

    def __ne__(self,other):
        return not self.__eq__(other)

    def __invert__(self):
        collection = self.backend.get_collection_for_cls(self.cls)
        pk_index = self.backend.get_pk_index(collection)
        all_keys = pk_index.get_all_keys()
        keys = [key for key in all_keys if not key in self.keys]        
        return self._clone(keys)

    def __contains__(self,obj):
        if not isinstance(obj,list) and not isinstance(obj,tuple):
            obj_list = [obj]
        else:
            obj_list = obj
        for obj in obj_list:
            try:
                storage_key = self.backend.get_storage_key_for(obj)
            except obj.DoesNotExist:
                return False
            if not storage_key in self.keys:
                return False
        return True

    def __eq__(self,other):
        if isinstance(other,QuerySet): 
            if self.cls == other.cls and set(self.keys) == set(other.keys):
                return True
        elif isinstance(other,list):
            if len(other) != len(self.keys):
                return False
            objs = list(self)
            if other == objs:
                return True
        return False

