# Description
A small project to get me to learn Python; this will present an API that will allow you to create a new SFTP user on a Ubuntu host securely.

## Currently Working
* SFTP user created with all correct directory permissions for chroot to work
* pfsense is updated with the provided external IP to allow access

## Future Development
* remove users 
* update/add IPs to the pfsense alias
* configure the setup script to configure Flask for production using best practices

**This is not designed for production use yet, use with caution.**

# Setup
`wget -O - -q https://raw.githubusercontent.com/OneLogicalMyth/sftp-service/master/setup.sh | sudo bash`

# Running the App
`sudo -u sftp-service -i sudo /var/sftp/api/start.sh`
