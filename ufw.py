import subprocess
import itertools

class ufw():

    def add_ip(self,ip,comment):
        c = subprocess.Popen(['sudo', 'ufw', 'allow', 'from', ip, 'to', 'any', 'port', '22', 'proto', 'tcp', 'comment', "{}".format(comment)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = c.communicate()
        exit_c = c.wait()

        # check if ufw added ok
        if err.rstrip().startswith('ERROR'):
            return False

        return True

    def del_ip(self,username):
        list = self.get_iplist(True)
        for line in list:
            if "'{}|".format(username) in line:
                rule = line.replace('ufw allow ','').split("'")[0].replace(' comment ','')
                cmd = ['sudo', 'ufw', 'delete', 'allow']
                cmd = cmd + rule.split(' ')
                c = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = c.communicate()
                exit_c = c.wait()

                # check if ufw added ok
                if err.rstrip().startswith('ERROR'):
                    return False

        return True

    def get_iplist(self,rawout=False):
        c = subprocess.Popen(['sudo', 'ufw','show','added'], stdout=subprocess.PIPE, universal_newlines=True)
        exit_c = c.wait()
        list = []
        raw = []
        for line in c.stdout:
            if line.startswith('ufw allow from') and 'any port 22' in line and 'comment' in line and '|' in line:
                raw.append(line.rstrip())
                detail = line.rstrip().split("'")[1].split('|')
                ip = line.rstrip().split(' ')[3]
                username = detail[0]
                date = detail[1]
                list.append({"username": username, "ip": ip, "status": "Ok", "datetime": date})

        if rawout:
            return raw

        return list

    def get_iplistonly(self,username=None):
        c = subprocess.Popen(['sudo', 'ufw','show','added'], stdout=subprocess.PIPE, universal_newlines=True)
        exit_c = c.wait()
        raw_list = []
        for line in c.stdout:
            if line.startswith('ufw allow from') and 'any port 22' in line and 'comment' in line and '|' in line:
                raw_list.append({'ip': line.rstrip().split(' ')[3], 'comment': line.rstrip().split("'")[1]})

        # now sort and group data by username
        key = lambda userlst: userlst['comment'].split('|')[0]
        raw_list.sort(key=key)
        result = {}
        for key, group in itertools.groupby(raw_list, key=key):
            result[key] = [item['ip'] for item in group]

        # filter on username if needed
        if username:
            if username in result:
                return {username: result[username]}
            else:
                return None

        return result
