from user import user
from pfsense import pfsense
from slack import slack
from database import database
from datetime import datetime, timedelta
from os.path import abspath, exists
import json, subprocess

# first load the configuration
f_config = abspath("config.json")
with open(f_config, 'r') as json_data:
    config = json.load(json_data)

# set config vars
PFSENSE_URL = config.get('pfsense_url',None)
PFSENSE_USR = config.get('pfsense_usr',None)
PFSENSE_PWD = config.get('pfsense_pwd',None)
PFSENSE_AID = config.get('pfsense_aid',None)
SLACK_WEBHOOK = config.get('slack_webhook',None)

# set up slack
if SLACK_WEBHOOK:
    print 'Slack notifications enabled ' + SLACK_WEBHOOK
    s = slack(SLACK_WEBHOOK)

# connect to db and set user class
db = database()
u = user()

# login to pfsense
pf = pfsense(PFSENSE_URL)
pfsession = pf.login(PFSENSE_USR,PFSENSE_PWD)

# remove expired users
userlist = db.get_user()
del_userlist = []
for user in userlist:
    created = datetime.strptime(user["created"], '%Y-%m-%d %H:%M:%S.%f')
    expiry = created + timedelta(days = 1)#user["daysvalid"])
    if datetime.now() > expiry:
        del_userlist.append(user["username"])

out_delusers = ""
for duser in del_userlist:
    # delete all IPs that the user had    
    result_del = pf.del_alias(pfsession, PFSENSE_AID, duser)    

    # delete user and all data from the home folder    
    result_user = u.remove_user(duser)

    out_delusers += duser + '\n'

# check for security and package updates
c = subprocess.Popen('/usr/lib/update-notifier/apt-check', stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
out, err = c.communicate()
exit_c = c.wait()
if not out == '0;0':
	update_count = out.split(';')
	update_summary = '\n\n~~Host Updates~~\n' + update_count[0] + ' packages can be updated. ' + update_count[1] + ' updates are security updates.'
else:
    update_summary = '\n\n~~Host Updates~~\nNo pending updates.'

# apply changes to pfsense and send slack notification
if del_userlist:    
    result_apply = pf.apply_changes(pfsession)
    message = 'SFTP Serivce automated maintenance has just run, the following users had expired and have been removed:\n' + out_delusers + update_summary
else:
    message = 'SFTP Serivce automated maintenance has just run. You have no expired users to delete. Total user count is: ' + str(len(userlist)) + update_summary

# print output
if SLACK_WEBHOOK:
    s.send_message(message)
else:
    print message
