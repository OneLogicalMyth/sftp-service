# Description
A small project to get me to learn Python; this will present an API that will allow you to create a new SFTP user on a Ubuntu host securely. Additionally, my intention is then to get it to hook into pfsense and add an external IP to an alias on the service.

**This is not designed for production use, it is purely project for interest.**

# Setup
On the Ubuntu host install Python pip by issuing the command `sudo apt install python-pip` and then install Flask by issuing the command `sudo pip installl Flask`.

# Running the App
Launch a terminal and change directory to the apps location, then issue `FLASK_APP=api.py flask run`.
