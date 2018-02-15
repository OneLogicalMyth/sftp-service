import subprocess

class user():

    def encrypt_pass(self,password):
        c = subprocess.Popen(['mkpasswd', '-m', 'sha-512', password], stdout=subprocess.PIPE)
        out, err = mkpass_c.communicate()
        exit_c = c.wait()

        return out.rstrip()

    def check_user(self,username):
        c = subprocess.Popen(['grep','-c','^' + username + ':','/etc/passwd'], stdout=subprocess.PIPE)
        out, err = c.communicate()
        exit_c = c.wait()

        return out.rstrip()
