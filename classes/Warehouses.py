from classes.gclass import Gclass
import os
from sqlalchemy import create_engine, text

# Caminho absoluto para a base de dados
database_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'App.db'))
engine = create_engine(f'sqlite:///{database_path}')

class Warehouses(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    att = ['_warehouse_id','_location','_capacity']
    header = 'Warehouses'
    des = ['warehouse_id','location','capacity']
    
    def __init__(self, warehouse_id, location, capacity):
        super().__init__()
        self._warehouse_id = warehouse_id
        self._location = location
        self._capacity = capacity
        Warehouses.obj[self._warehouse_id] = self
        Warehouses.lst.append(self._warehouse_id)
    
    @property
    def warehouse_id(self):
        return self._warehouse_id
    
    @property
    def location(self):
        return self._location
    
    @property
    def capacity(self):
        return self._capacity

    @warehouse_id.setter
    def warehouse_id(self, num):
        self._warehouse_id = num

    @location.setter
    def location(self, loc):
        self._location = loc

    @capacity.setter
    def capacity(self, cap):
        self._capacity = cap
    
    def __str__(self):
        return f"id: {self._warehouse_id}\nlocation: {self._location}\ncapacity: {self._capacity}"

    
    
    
    
    
