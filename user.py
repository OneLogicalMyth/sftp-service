import subprocess

class user():

    def encrypt_pass(self,password):
        c = subprocess.Popen(['mkpasswd', '-m', 'sha-512', password], stdout=subprocess.PIPE)
        out, err = c.communicate()
        exit_c = c.wait()

        return out.rstrip()

    def check_user(self,username):
        c = subprocess.Popen(['grep','-c','^' + username + ':','/etc/passwd'], stdout=subprocess.PIPE)
        out, err = c.communicate()
        exit_c = c.wait()

        return out.rstrip()

    def new_home(self,username):
        mkdir_c = subprocess.Popen(['mkdir','-p','/var/sftp/' + username + '/upload'], stdout=subprocess.PIPE)
        mkdir_out, mkdir_err = mkdir_c.communicate()
        mkdir_exit_c = mkdir_c.wait()

        chown_c = subprocess.Popen(['chown','root','/var/sftp/' + username], stdout=subprocess.PIPE)
        chown_out, chown_err = chown_c.communicate()
        chown_exit_c = chown_c.wait()

        chmod_c = subprocess.Popen(['chmod','go-w','/var/sftp/' + username], stdout=subprocess.PIPE)
        chmod_out, chmod_err = chmod_c.communicate()
        chmod_exit_c = chmod_c.wait()

        chownu_c = subprocess.Popen(['chown',username + ':sftp','/var/sftp/' + username + '/upload'], stdout=subprocess.PIPE)
        chownu_out, chownu_err = chownu_c.communicate()
        chownu_exit_c = chownu_c.wait()

        chmodu_c = subprocess.Popen(['chmod','ug+rwX','/var/sftp/' + username + '/upload'], stdout=subprocess.PIPE)
        chmodu_out, chmodu_err = chmodu_c.communicate()
        chmodu_exit_c = chmodu_c.wait()

        exit_code = mkdir_exit_c + chown_exit_c + chmod_exit_c + chownu_exit_c + chmodu_exit_c

        return int(exit_code)


    def new_user(self,username,password):
	enc_password = self.encrypt_pass(password)
        c = subprocess.Popen(['useradd','-g','sftp','-d','/var/sftp/' + username,'-N','-p',enc_password,username], stdout=subprocess.PIPE)
        out, err = c.communicate()
        exit_c = c.wait()

        return exit_c
