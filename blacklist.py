import json
from database import database
from datetime import datetime, timedelta

class blacklist():

    blacklist = 'blacklist.json'

    def check(self,ip,timeout):
        db = database()
        result = db.get_blacklist(ip)
        if result:
            created = datetime.strptime(result[0]["created"], '%Y-%m-%d %H:%M:%S.%f')
            expiry = created + timedelta(minutes = timeout)
            print created
            print expiry
            if datetime.now() > expiry:
                self.remove(ip)
                return False
            else:
                return True
        else:
            return False

    def add(self,ip):
        db = database()
        db.add_blacklist(ip)

    def remove(self,ip):
        db = database()
        db.del_blacklist(ip)
