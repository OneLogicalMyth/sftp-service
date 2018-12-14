import subprocess
#from database import database

class ufw():

    def add_ip(self,ip,user):
        c = subprocess.Popen(['ufw', 'allow', 'from', ip, 'to', 'any', 'port', '22', 'proto', 'tcp', 'comment', "'{}'".format(user)], stdout=subprocess.PIPE)
        out, err = c.communicate()
        exit_c = c.wait()

        return out.rstrip()

    def get_ip(self,user=None):
        c = subprocess.Popen(['ufw','show','added'], stdout=subprocess.PIPE, universal_newlines=True)
        exit_c = c.wait()
        out = []
        for line in c.stdout:
            if line.startswith('ufw'):
                print {'ip': line.rstrip().split(' ')[3], 'user': line.rstrip().split("'")[1]}

ufw().get_ip()
