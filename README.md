# Description
A small project to get me to learn Python; this will present an API that will allow you to create a new SFTP user on a Ubuntu host securely.

## Currently Working
* SFTP user created with all correct directory permissions for chroot to work
* pfsense is updated with the provided external IP to allow access
* setup.sh now configures a production apache2 web service, you still need to harden and configure https manually!

## Future Development
* remove users 
* update/add IPs to the pfsense alias

**This is not designed for production use yet, use with caution.**

# Setup
`wget -O - -q https://raw.githubusercontent.com/OneLogicalMyth/sftp-service/master/setup.sh | sudo bash`

Once installed you can then start making use of the API using curl or any application you have developed to work with it.
