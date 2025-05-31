from classes.gclass import Gclass
import os
from sqlalchemy import create_engine, text
import random

# Caminho absoluto para a base de dados
database_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'App.db'))
engine = create_engine(f'sqlite:///{database_path}')

class Warehouses(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    att = ['_warehouse_id', '_location', '_capacity', '_latitude', '_longitude']  # <-- adiciona
    header = 'Warehouses'
    des = ['warehouse_id', 'location', 'capacity', 'latitude', 'longitude']       # <-- adiciona

    def __init__(self, warehouse_id, location, capacity, latitude = None, longitude = None, *args, **kwargs):
        super().__init__()
        self._warehouse_id = warehouse_id
        self._location = location
        self._capacity = capacity
        self._latitude = float(latitude) if latitude not in (None, 'None', '') else None
        self._longitude = float(longitude) if longitude not in (None, 'None', '') else None
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

    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

    @warehouse_id.setter
    def warehouse_id(self, num):
        self._warehouse_id = num

    @location.setter
    def location(self, loc):
        self._location = loc

    @capacity.setter
    def capacity(self, cap):
        self._capacity = cap

    @latitude.setter
    def latitude(self, lat):
        self._latitude = float(lat)

    @longitude.setter
    def longitude(self, lon):
        self._longitude = float(lon)

    def __str__(self):
        return f"id: {self._warehouse_id}\nlocation: {self._location}\ncapacity: {self._capacity}\nlatitude: {self._latitude}\nlongitude: {self._longitude}"
    
if __name__ == "__main__":
    # Dicionário com as coordenadas reais de cada warehouse_id
    warehouse_coords = {
        10: (38.722252, -9.139337),      # Lisboa
        23: (41.157944, -8.629105),      # Porto
        20: (40.640505, -8.653754),      # Aveiro
        25: (41.195999, -8.495800),      # Valongo
        17: (40.203314, -8.410257),      # Coimbra
        8:  (37.017963, -7.930834),      # Faro
        21: (38.802868, -9.381659),      # Sintra
        12: (41.300621, -7.744129),      # Vila Real
        27: (39.750000, -8.933333),      # Marinha Grande
        3:  (40.286011, -7.504530),      # Covilhã
        19: (41.182836, -8.689084),      # Matosinhos
        13: (41.007599, -8.641400),      # Espinho
        22: (41.767368, -8.583160),      # Ponte de Lima
        14: (41.545448, -8.426507),      # Braga
        29: (41.444858, -8.296193),      # Guimarães
        7:  (41.410328, -8.519728),      # Famalicão
        4:  (40.577801, -8.444420),      # Águeda
        11: (38.881153, -7.162814),      # Elvas
        26: (37.598801, -8.645540),      # Odemira
        24: (37.956081, -8.868890),      # Sines
        2:  (38.569801, -8.901930),      # Palmela
        28: (38.955601, -8.989230),      # Vila Franca de Xira
        5:  (39.293800, -7.428880),      # Portalegre
        15: (41.806439, -6.756742),      # Bragança
        30: (38.697948, -9.316354),      # Oeiras
        6:  (40.661011, -7.909710),      # Viseu
        18: (39.404999, -8.486000),      # Golegã
        1:  (40.748349, -8.651919),      # Murtosa
    }

    # Carrega os dados da base de dados
    Warehouses.read(database_path)

    # Atualiza os objetos em memória e guarda na base de dados
    for wid, (lat, lon) in warehouse_coords.items():
        w = Warehouses.obj.get(str(wid))
        if w:
            w._latitude = lat
            w._longitude = lon
            Warehouses.update(w.warehouse_id)

    print("Coordenadas atualizadas na base de dados.")
    print(Warehouses.obj['15'].latitude)