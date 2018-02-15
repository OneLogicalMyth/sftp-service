from flask import Flask, abort, request, jsonify
from os.path import abspath, exists
from user import user
import sys, uuid, json, subprocess

f_config = abspath("config.json")

# check if the config.json file is present
if not exists(f_config):
    print "config.json not found"
    sys.exit()

# first load the configuration
with open(f_config, 'r') as json_data:
    config = json.load(json_data)

# set vars based on config file
SERVER_NAME = config.get('server','SFTP API Beta')
CONFIG_TOKEN = config.get('token',str(uuid.uuid4()))

print ' * API starting'
print ' * Access token is ' + CONFIG_TOKEN

# class to overide the flask server so that the server response header is changed
class localFlask(Flask):
    def process_response(self, response):
        #Every response will be processed here first
        response.headers['server'] = SERVER_NAME
        return(response)

# start the application
app = localFlask(__name__)

# mask all other methods to /adduser
@app.route('/adduser')
def void_adduser():
    abort(404)

# accept a POST request to /adduser
@app.route('/adduser',methods=['POST'])
def add_user():
    data = request.get_json(silent=True)
    token = data.get('token',None)
    username = data.get('username',None)
    extip = data.get('extip',None)

    # return 400 for missing arguments
    if token is None or username is None or extip is None:
        abort(400)

    # if token is an empty string return 403
    if not token:
        abort(403)

    # compare token provided is the same to the config/generated token
    if not token == CONFIG_TOKEN:
        abort(403)

    # now create the user and secure for SFTP
    nu = user()
    plaintext_password = str(uuid.uuid4())[0:13]
    encrypted_password = nu.encrypt_pass(plaintext_password)

    # return the result
    out = jsonify({'username': username, 'password': plaintext_password, 'result': 'OK'})
    return out, 200
