from classes.gclass import Gclass
import os
from sqlalchemy import create_engine, text

# Caminho absoluto para a base de dados
database_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'App.db'))
engine = create_engine(f'sqlite:///{database_path}')

class Shipment_details(Gclass):
    
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    att = ['_id','_shipment_id','_carrier_id']
    header = 'Shipment_details'
    des = ['id','shipment_id','carrier_id']
    
    def __init__(self, id, shipment_id, carrier_id):
        super().__init__()
        self._id = id
        self._shipment_id = shipment_id
        self._carrier_id = carrier_id
        Shipment_details.obj[id] = self
        Shipment_details.lst.append(id)

    @property
    def id(self):
        return self._id
    
    @property
    def shipment_id(self):
        return self._shipment_id
    
    @property
    def carrier_id(self):
        return self._carrier_id

    @id.setter
    def id(self, num):
        self._id = num

    @shipment_id.setter
    def shipment_id(self, num):
        self._shipment_id = num

    @carrier_id.setter
    def carrier_id(self, num):
        self._carrier_id = num
    
    def __str__(self):
        return f"id: {self._id}\nshipment_id: {self._shipment_id}\ncarrier_id: {self._carrier_id}"

    
