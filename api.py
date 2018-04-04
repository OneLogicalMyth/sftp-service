from flask import Flask, abort, request, jsonify
from os.path import abspath, exists
from user import user
from pfsense import pfsense
from helper import helper
import sys, uuid, json, re, datetime

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
PFSENSE_URL = config.get('pfsense_url',None)
PFSENSE_USR = config.get('pfsense_usr',None)
PFSENSE_PWD = config.get('pfsense_pwd',None)
PFSENSE_AID = config.get('pfsense_aid',None)

if not PFSENSE_URL or not PFSENSE_USR or not PFSENSE_PWD or not PFSENSE_AID:
    print "pfsense configuration missing in config.json"
    sys.exit()

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

# mask all other methods to /adduser, /addip
@app.route('/adduser')
def void_adduser():
    abort(404)

@app.route('/addip')
def void_addip():
    abort(404)

@app.route('/getip')
def void_getip():
    abort(404)

# accept a POST request to /getip
@app.route('/getip',methods=['POST'])
def get_ip():
    u = user();
    data = request.get_json(silent=True)
    token = data.get('token',None)
    alias = data.get('alias',PFSENSE_AID)

    # return 400 for missing arguments
    if token is None or alias is None:
        abort(400,description="You have an argument missing")

    # if token is an empty string return 403
    if not token:
        abort(403,description="Token is not valid")

    # compare token provided is the same to the config/generated token
    if not token == CONFIG_TOKEN:
        abort(403,description="Token is not valid")

    # check if pfsense alias is valid
    if not re.match("^[0-9]+$", alias):
        abort(400,description="The pfsense alias is invalid")

    # check if you can login to pfsense first
    pf = pfsense(PFSENSE_URL)
    pfsession = pf.login(PFSENSE_USR,PFSENSE_PWD)
    if not pfsession:
        abort(400,description="Failed to login to pfsense")

    iplist = pf.get_alias(pfsession,alias)

    # return the result
    h = helper()
    rawout = h.make_iplist(iplist)
    out = json.dumps(rawout, ensure_ascii=False, indent=4)
    return out, 200

# accept a POST request to /addip
@app.route('/addip',methods=['POST'])
def add_ip():
    u = user()
    data = request.get_json(silent=True)
    token = data.get('token',None)
    username = data.get('username',None)
    extip = data.get('extip',None)
    alias = data.get('alias',PFSENSE_AID)

    # return 400 for missing arguments
    if token is None or username is None or extip is None:
        abort(400,description="You have an argument missing")

    # if token is an empty string return 403
    if not token:
        abort(403,description="Token is not valid")

    # compare token provided is the same to the config/generated token
    if not token == CONFIG_TOKEN:
        abort(403,description="Token is not valid")

    # check if username is valid
    if not re.match("^[a-z0-9]+$", username):
        abort(400,description="Username is invalid")

    # check if pfsense alias is valid
    if not re.match("^[0-9]+$", alias):
        abort(400,description="The pfsense alias is invalid")

    # check if username exists already
    username_exists = int(u.check_user(username))
    if not username_exists == 1:
        abort(400,description="Username does not exist, please create a user first")

    # validated the external IP
    if not re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", extip):
        abort(400,description="Invalid external IP address given")

    # check if you can login to pfsense first
    pf = pfsense(PFSENSE_URL)
    pfsession = pf.login(PFSENSE_USR,PFSENSE_PWD)
    if not pfsession:
        abort(400,description="Failed to login to pfsense")

    # add IP to alias for whitelisting
    alias_detail = username + '|' + str(datetime.datetime.now().isoformat())
    result_add = pf.add_alias(pfsession,alias,extip,alias_detail)
    result_apply = pf.apply_changes(pfsession)

    # return the result
    out = jsonify({'result': 'External IP added ok'})
    return out, 200

# accept a POST request to /adduser
@app.route('/adduser',methods=['POST'])
def add_user():
    u = user()
    data = request.get_json(silent=True)
    token = data.get('token',None)
    username = data.get('username',None)
    extip = data.get('extip',None)
    alias = data.get('alias',PFSENSE_AID)

    # return 400 for missing arguments
    if token is None or username is None or extip is None:
        abort(400,description="You have an argument missing")

    # if token is an empty string return 403
    if not token:
        abort(403,description="Token is not valid")

    # compare token provided is the same to the config/generated token
    if not token == CONFIG_TOKEN:
        abort(403,description="Token is not valid")

    # check if username is valid
    if not re.match("^[a-z0-9]+$", username):
        abort(400,description="Username is invalid")

    # check if pfsense alias is valid
    if not re.match("^[0-9]+$", alias):
        abort(400,description="The pfsense alias is invalid")

    # check if username exists already
    username_exists = int(u.check_user(username))
    if username_exists == 1:
        abort(400,description="Username already exists")

    # validated the external IP
    if not re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", extip):
        abort(400,description="Invalid external IP address given")

    # check if you can login to pfsense first
    pf = pfsense(PFSENSE_URL)
    pfsession = pf.login(PFSENSE_USR,PFSENSE_PWD)
    if not pfsession:
        abort(400,description="Failed to login to pfsense")

    # create the users home folder with correct permissions
    plaintext_password = str(uuid.uuid4())[0:13]
    user_created = u.new_user(username,plaintext_password)
    new_home = u.new_home(username)

    # add IP to alias for whitelisting
    alias_detail = username + '|' + str(datetime.datetime.now().isoformat())
    result_add = pf.add_alias(pfsession,alias,extip,alias_detail)
    result_apply = pf.apply_changes(pfsession)

    # return the result
    out = jsonify({'username': username, 'password': plaintext_password})
    return out, 201
