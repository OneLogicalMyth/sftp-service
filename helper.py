import subprocess
from user import user

class helper():

    def make_iplist(self,rawlist):
        u = user()

        count = 0
        output = []
        number = len(rawlist["address_detail"])

        for _ in range(number):
            detail = str(rawlist["address_detail"][count][1]).split('|')

            if len(detail) == 2:
                username = detail[0]
                date = detail[1]
                status = "Ok"

                # check if username exists already
                username_exists = int(u.check_user(username))
                if not username_exists == 1:
                    status = "Orphaned"
            else:
                username = detail[0]
                date = None
                status = "Manually Created"

            ip = str(rawlist["address_ip"][count][1])

            output.append({"username": username, "ip": ip, "status": status, "datetime": date})
            count += 1

        return output
