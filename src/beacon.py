from badge import *


class Beacon(Badge):

    @property
    def badge_id(self):
        return self.__badge_id

    @property   
    def project_id(self):
        return self.__project_id    

    @property
    def last_voltage(self):
        return self.last_voltage


    def __init__(self,addr,logger,key,badge_id,project_id, init_voltage=None):
        self.key = key        
        self.addr = addr
        self.logger = BadgeAddressAdapter(logger, {'addr': addr})
        self.badge_id = badge_id
        self.project_id = project_id
        self.last_voltage = init_voltage
        self.dlg = None
        self.conn = None