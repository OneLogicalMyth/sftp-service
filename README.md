# Description
A small project to get me to learn Python; this will present an API that will allow you to create a new SFTP user on a Ubuntu host securely. Additionally, my intention is then to get it to hook into pfsense and add an external IP to an alias on the service.

**This is not designed for production use yet, use with caution.**

# Setup
`wget -O - -q https://raw.githubusercontent.com/OneLogicalMyth/sftp-service/master/setup.sh | sudo bash`

# Running the App
`sudo -u sftp-service -i sudo /var/sftp/api/start.sh`
