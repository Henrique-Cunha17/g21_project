from classes.gclass import Gclass

class Carriers(Gclass):
    
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    att = ['_carrier_id','_vehicle_type','_capacity', '_name']
    header = 'Carriers'
    des = ['carrier_id','vehicle_type','capacity', 'name']
    
    def __init__(self, carrier_id, vehicle_type, capacity, name):
        super().__init__()
        self._carrier_id = carrier_id
        self._vehicle_type = vehicle_type
        self._capacity = capacity
        self._name = name
        Carriers.obj[self._carrier_id] = self
        Carriers.lst.append(self._carrier_id)
    
    @property
    def carrier_id(self):
        return self._carrier_id
    
    @property
    def vehicle_type(self):
        return self._vehicle_type
    
    @property
    def capacity(self):
        return self._capacity
    
    @property
    def name(self):
        return self._name

    @carrier_id.setter
    def carrier_id(self, num):
        self._carrier_id = num

    @vehicle_type.setter
    def vehicle_type(self, veh):
        self._vehicle_type = veh

    @capacity.setter
    def capacity(self, num):
        self._capacity = num

    @name.setter
    def name(self, nam):
        self._name = nam
    
    def __str__(self):
        return f"id: {self._carrier_id}\nvehicle_type: {self._vehicle_type}\ncapacity: {self._capacity}\name: {self._name}"

database_path = r'data\App.db'
Carriers.read(database_path)
   
