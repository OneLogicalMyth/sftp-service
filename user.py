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
        mkdir_c = subprocess.Popen(['sudo','mkdir','-p','/var/sftp/' + username + '/upload'], stdout=subprocess.PIPE)
        mkdir_out, mkdir_err = mkdir_c.communicate()
        mkdir_exit_c = mkdir_c.wait()

        chown_c = subprocess.Popen(['sudo','chown','root','/var/sftp/' + username], stdout=subprocess.PIPE)
        chown_out, chown_err = chown_c.communicate()
        chown_exit_c = chown_c.wait()

        chmod_c = subprocess.Popen(['sudo','chmod','go-w','/var/sftp/' + username], stdout=subprocess.PIPE)
        chmod_out, chmod_err = chmod_c.communicate()
        chmod_exit_c = chmod_c.wait()

        chownu_c = subprocess.Popen(['sudo','chown',username + ':sftp','/var/sftp/' + username + '/upload'], stdout=subprocess.PIPE)
        chownu_out, chownu_err = chownu_c.communicate()
        chownu_exit_c = chownu_c.wait()

        chmodu_c = subprocess.Popen(['sudo','chmod','ug+rwX','/var/sftp/' + username + '/upload'], stdout=subprocess.PIPE)
        chmodu_out, chmodu_err = chmodu_c.communicate()
        chmodu_exit_c = chmodu_c.wait()

        exit_code = mkdir_exit_c + chown_exit_c + chmod_exit_c + chownu_exit_c + chmodu_exit_c

        return int(exit_code)


    def new_user(self,username,password):
	enc_password = self.encrypt_pass(password)
        c = subprocess.Popen(['sudo','useradd','-g','sftp','-d','/var/sftp/' + username,'-N','-p',enc_password,username], stdout=subprocess.PIPE)
        out, err = c.communicate()
        exit_c = c.wait()

        return exit_c

    def remove_user(self,username):
        deluser_c = subprocess.Popen(['sudo','deluser',username], stdout=subprocess.PIPE)
        deluser_out, deluser_err = deluser_c.communicate()
        deluser_exit_c = deluser_c.wait()

        rm_c = subprocess.Popen(['sudo','rm','-rf','/var/sftp/' + username], stdout=subprocess.PIPE)
        rm_out, rm_err = rm_c.communicate()
        rm_exit_c = rm_c.wait()

        exit_code = rm_exit_c + deluser_exit_c

        return int(exit_code)
