from flask import Flask, abort, request, jsonify
from os.path import abspath, exists
from user import user
from pfsense import pfsense
from helper import helper
from blacklist import blacklist
from slack import slack
from database import database
import sys, uuid, json, re, datetime, logging

f_config = abspath("config.json")
bl = blacklist()

# check database tables
db = database()
db.setup()
db.close()

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
SLACK_WEBHOOK = config.get('slack_webhook',None)
BLACKLIST_TIMEOUT = int(config.get('blacklist_expiry_mins',60))
DAYS_VALID = config.get('days_valid',30)

if not PFSENSE_URL or not PFSENSE_USR or not PFSENSE_PWD or not PFSENSE_AID:
    print "pfsense configuration missing in config.json"
    sys.exit()

print ' * API starting'
print ' * Access token is ' + CONFIG_TOKEN
if SLACK_WEBHOOK:
    print 'Slack notifications enabled ' + SLACK_WEBHOOK
    s = slack(SLACK_WEBHOOK)

# start the application
app = Flask(__name__)

@app.before_request
def run_prereq_tasks():

    # check if IP is black listed
    blacklisted = bl.check(request.remote_addr,BLACKLIST_TIMEOUT)
    if blacklisted:
        abort(403,description="You have been blacklisted")

    # this API only supports POST
    if not request.method == 'POST':
        abort(404)

    # this API only supports JSON
    if not request.is_json:
        abort(404)

    # this API expects data
    if not request.data:
        abort(404)

    # validate the token before any requests
    data = request.get_json(silent=True)
    token = data.get('token',None)

    # if token is an empty string or does not match return 403
    if not token or not token == CONFIG_TOKEN:
        bl.add(request.remote_addr)
        if SLACK_WEBHOOK:
            s.send_message('The IP ' + request.remote_addr + ' has been blacklisted due to an incorrect token')
        abort(403,description="Token is not valid")

# accept a POST request to /getip
@app.route('/getip',methods=['POST'])
def get_ip():
    u = user();
    data = request.get_json(silent=True)
    token = data.get('token',None)
    alias = data.get('alias',PFSENSE_AID)

    # return 400 for missing arguments
    if alias is None:
        abort(400,description="You have an argument missing")

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
    if username is None or extip is None:
        abort(400,description="You have an argument missing")

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

    # send slack messaage
    if SLACK_WEBHOOK:
        s.send_message('The user ' + username + ' has had the additional IP of ' + extip + ' added to the whitelisting. Requested from IP ' + request.remote_addr)

    # return the result
    out = jsonify({'username': username,'ip_added': extip})
    return out, 200

# accept a POST request to /adduser
@app.route('/adduser',methods=['POST'])
def add_user():
    u = user()
    data = request.get_json(silent=True)
    token = data.get('token',None)
    username = data.get('username',None)
    extip = data.get('extip',None)
    daysvalid = data.get('daysvalid',DAYS_VALID)
    alias = data.get('alias',PFSENSE_AID)

    # return 400 for missing arguments
    if username is None or extip is None:
        abort(400,description="You have an argument missing")

    # check if username is valid
    if not re.match("^[a-z0-9]+$", username):
        abort(400,description="Username is invalid")

    # check if pfsense alias is valid
    if not re.match("^[0-9]+$", alias):
        abort(400,description="The pfsense alias is invalid")
    
    # check if pfsense alias is valid
    if not re.match("^[0-9]+$", daysvalid):
        abort(400,description="The number of days valid is invalid")

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
    user_created = u.new_user(username,plaintext_password,daysvalid,request.remote_addr)
    new_home = u.new_home(username)

    # add IP to alias for whitelisting
    alias_detail = username + '|' + str(datetime.datetime.now().isoformat())
    result_add = pf.add_alias(pfsession,alias,extip,alias_detail)
    result_apply = pf.apply_changes(pfsession)

    # send slack message
    if SLACK_WEBHOOK:
            s.send_message('The user ' + username + ' has been created. The IP of ' + extip + ' has been whitelisted. This was requested by ' + request.remote_addr)

    # return the result
    out = jsonify({'username': username, 'password': plaintext_password, 'ip_added': extip})
    return out, 201

# accept a POST request to /getuser
@app.route('/getuser',methods=['POST'])
def get_user():
    u = user()
    data = request.get_json(silent=True)
    username = data.get('username',None)
    alias = data.get('alias',PFSENSE_AID)

    # check if you can login to pfsense first
    pf = pfsense(PFSENSE_URL)
    pfsession = pf.login(PFSENSE_USR,PFSENSE_PWD)
    if not pfsession:
        abort(400,description="Failed to login to pfsense")

    iplist = pf.get_alias(pfsession,alias)

    # allow no username value to return all users
    if not username is None:
        # check if username is in the valid format
        if not re.match("^[a-z0-9]+$", username):
            abort(400,description="Username is invalid")

        # check if username exists already
        username_exists = int(u.check_user(username))
        if not username_exists == 1:
            abort(400,description="Username does not exist")

    h = helper()
    iplistonly = h.make_iplistonly(iplist)
    user_data = u.get_user(username,iplistonly)

    return jsonify(user_data), 200
