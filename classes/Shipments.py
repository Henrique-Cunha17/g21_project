from classes.gclass import Gclass
from sqlalchemy import create_engine, text

database_path = r'data\App.db'
engine = create_engine(f'sqlite:///{database_path}')

class Shipments(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    att = ['_shipment_id','_status','_origin', '_destination', '_shipment_date', '_tracking_number']
    header = 'Shipments'
    des = ['shipment_id','status','origin', 'destination', 'shipment_date', 'tracking_number']
    
    def __init__(self, shipment_id, status, origin, destination, shipment_date, tracking_number):
        super().__init__()
        self._shipment_id = shipment_id
        self._status = status
        self._origin = origin
        self._destination = destination
        self._shipment_date = shipment_date
        self._tracking_number = tracking_number
        Shipments.obj[self._shipment_id] = self
        Shipments.lst.append(self._shipment_id)
    
    @property
    def shipment_id(self):
        return self._shipment_id
    
    @property
    def status(self):
        return self._status
    
    @property
    def origin(self):
        return self._origin
    
    @property
    def destination(self):
        return self._destination
    
    @property
    def shipment_date(self):
        return self._shipment_date
    
    @property
    def tracking_number(self):
        return self._tracking_number

    @shipment_id.setter
    def shipment_id(self, num):
        self._shipment_id = num

    @status.setter
    def status(self, stt):
        self._status = stt

    @origin.setter
    def origin(self, org):
        self._origin = org

    @destination.setter
    def destination(self, dst):
        self._destination = dst

    @shipment_date.setter
    def shipment_id(self, dat):
        self._shipment_date = dat

    @tracking_number.setter
    def tracking_number(self, num):
        self._tracking_number = num
    
    def __str__(self):
        return f"id: {self._shipment_id}\nstatus: {self._status}\norigin: {self._origin}\ndestination: {self._destination}\nshipment_date: {self._shipment_date}\ntracking_number: {self._tracking_number}"
    
    @classmethod
    def update_status_in_db(cls, shipment_id, new_status):
        with engine.connect() as conn:
            conn.execute(
                text("UPDATE Shipments SET status = :status WHERE shipment_id = :shipment_id"),
                {"status": new_status, "shipment_id": shipment_id}
            )
            conn.commit()
