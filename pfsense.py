#!/usr/bin/env python

from requests import Session
from re import findall
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('--pfsense', type=str, metavar='address', required=True, help="Firewall base url")
parser.add_argument('--username', type=str, metavar='username', required=True, help="Firewall login username")
parser.add_argument('--password', type=str, metavar='password', required=True, help="Firewall login password")
parser.add_argument('--ip', type=str, default="IP to add", help="The reason the given IPs get blocked")
parser.add_argument('--description', type=str, default="IP to add", help="A description to add to the alias entry")
args = parser.parse_args()


def get_csrf(content):
	csrf_token = findall('name=\'__csrf_magic\'\s*value="([^"]+)"', content)[0]
	return csrf_token

def update_alias(pfsense,username,password,alias,ip,description):

	base_url = pfsense
	alias_edit_url = '/firewall_aliases_edit.php'

	s = Session()
	r = s.get(base_url, verify=False)
	text = r.text
	csrf_token = get_csrf(text)

	login_payload = {'__csrf_magic': csrf_token,'usernamefld': username,'passwordfld': password,'login': 'Sign+In'}
	s.post(base_url, data=login_payload, verify=False)

	r = s.get(base_url + alias_edit_url + '?id=' + alias, verify=False)
	text = r.text

	alias_name = findall('addressarray = \["([^"]+)', text)[0]
	addresses  = findall('name="(address\d+)".*?value="([^"]+)', text)

	return text


result = update_alias(args.pfsense,args.username,args.password,'o','r','r')

print result
