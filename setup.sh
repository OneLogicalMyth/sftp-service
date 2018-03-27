#!/bin/bash
# Tested on Ubuntu 16.04.2
# Perform a system update first
echo "[*] Updating the Ubuntu system"
apt update
apt upgrade -y

# Install requried packages
echo "[*] Installing the required packages"
apt install pwgen whois python-pip openssh-server apache2 libapache2-mod-wsgi -y

# Create sftp user, groups and directories
echo "[*] Creating the SFTP directory"
mkdir -p /var/sftp/api
echo "[*] Creating the sftp group"
groupadd sftp
echo "[*] Creating the sftp-service user"
newpass=$(pwgen 25 1)
encpass=$(mkpasswd -m sha-512 $newpass)
useradd -m sftp-service -p $encpass

# Configure chroot and sftp options
echo "[*] Configuring the SSH server for chroot SFTP"
sed -ibackup 's/Subsystem/#Subsystem/' /etc/ssh/sshd_config
echo "" >> /etc/ssh/sshd_config
echo "Subsystem sftp internal-sftp" >> /etc/ssh/sshd_config
echo "" >> /etc/ssh/sshd_config
echo "Match Group sftp" >> /etc/ssh/sshd_config
echo "    ChrootDirectory %h" >> /etc/ssh/sshd_config
echo "    AllowTCPForwarding no" >> /etc/ssh/sshd_config
echo "    X11Forwarding no" >> /etc/ssh/sshd_config
echo "    ForceCommand internal-sftp" >> /etc/ssh/sshd_config
echo "" >> /etc/ssh/sshd_config

# download api files
wget -O /var/sftp/api/api.py -q https://raw.githubusercontent.com/OneLogicalMyth/sftp-service/master/api.py
wget -O /var/sftp/api/user.py -q https://raw.githubusercontent.com/OneLogicalMyth/sftp-service/master/user.py
wget -O /var/sftp/api/pfsense.py -q https://raw.githubusercontent.com/OneLogicalMyth/sftp-service/master/pfsense.py
wget -O /var/sftp/api/config.json -q https://raw.githubusercontent.com/OneLogicalMyth/sftp-service/master/config.json
wget -O /var/sftp/api/api.wsgi -q https://raw.githubusercontent.com/OneLogicalMyth/sftp-service/master/api.wsgi
wget -O /etc/apache2/sites-available/api.conf -q https://raw.githubusercontent.com/OneLogicalMyth/sftp-service/master/api.conf

# Configure sudo access for the sftp-service user
echo "[*] Adding sftp sudo file to allow some root access for the api"
echo "sftp-service ALL=(ALL) NOPASSWD:/bin/chown" > /etc/sudoers.d/sftp
echo "sftp-service ALL=(ALL) NOPASSWD:/bin/chmod" >> /etc/sudoers.d/sftp
echo "sftp-service ALL=(ALL) NOPASSWD:/usr/sbin/useradd" >> /etc/sudoers.d/sftp
echo "sftp-service ALL=(ALL) NOPASSWD:/bin/mkdir" >> /etc/sudoers.d/sftp
chmod 440 /etc/sudoers.d/sftp_script

# Configure pip, requests and Flask
echo "[*] Upgrading pip"
pip install --upgrade pip
echo "[*] Installing flask"
pip install Flask
pip install requests

# Add localhost entry for the site, this can be changed to anything later...
printf "\n127.0.0.1 api-service.local\n" >> /etc/hosts

# Enabling site and restarting apache2
a2ensite api.conf
service apache2 reload

# Output username and password
echo "[*] Setup complete"
echo ""
echo "[Credentials]"
echo "Username: sftp-service"
echo "Password: $newpass"
echo ""
echo "[READY]"
echo "use curl against http://api-service.local/adduser"
