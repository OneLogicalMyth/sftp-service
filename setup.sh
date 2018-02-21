#!/bin/bash
# Tested on Ubuntu 16.04.2
# Perform a system update first
echo "[*] Updating the Ubuntu system"
apt update
apt upgrade -y

# Install requried packages
echo "[*] Installing the required packages"
apt install pwgen whois python-pip openssh-server -y

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

# Create the start.sh script
echo "[*] Creating the start.sh script, this starts the development flask service"
echo "#!/bin/bash" > /var/sftp/api/start.sh
echo 'cd $(dirname "$0")' >> /var/sftp/api/start.sh
echo "export FLASK_APP=api.py" >> /var/sftp/api/start.sh
echo "flask run" >> /var/sftp/api/start.sh
chmod 445 /var/sftp/api/start.sh

# download api files
wget -O /var/sftp/api/api.py -q https://raw.githubusercontent.com/OneLogicalMyth/sftp-service/master/api.py
wget -O /var/sftp/api/user.py -q https://raw.githubusercontent.com/OneLogicalMyth/sftp-service/master/user.py
wget -O /var/sftp/api/config.json -q https://raw.githubusercontent.com/OneLogicalMyth/sftp-service/master/config.json

# Configure sudo access for the sftp-service user
echo "[*] Adding sftp_script sudo file to allow no password for sftp-service for start.sh"
echo "sftp-service ALL=(ALL) NOPASSWD:/var/sftp/api/start.sh" > /etc/sudoers.d/sftp_script
chmod 440 /etc/sudoers.d/sftp_script

# Configure pip and Flask
echo "[*] Upgrading pip"
pip install --upgrade pip
echo "[*] Installing flask"
pip install Flask

# Output username and password
echo "[*] Setup complete"
echo ""
echo "[Credentials]"
echo "Username: sftp-service"
echo "Password: $newpass"
echo ""
echo "[To Start the Service Run...]"
echo "sudo -u sftp-service -i sudo /var/sftp/api/start.sh"
