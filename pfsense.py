#!/usr/bin/env python

from requests import Session
from re import findall
from argparse import ArgumentParser
import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class pfsense(object):

    def __init__(self,url):
        self.alias_edit_url = url + '/firewall_aliases_edit.php'
        self.alias_list_url = url + '/firewall_aliases.php'
        self.url = url

    def merge_dicts(self,*dict_args):
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result

    def get_csrf(self,content):
        csrf_token = findall('name=\'__csrf_magic\'\s*value="([^"]+)"', content)[0]
        return csrf_token

    def apply_changes(self,pfsession):
        response = pfsession.get(self.alias_list_url, verify=False)
        csrf_token = self.get_csrf(response.text)
        apply_payload = {
                        '__csrf_magic': csrf_token,
                        'apply': 'Apply changes',
                        'tab': 'ip'
                        }
        response = pfsession.post(self.alias_list_url, data=apply_payload, verify=False)
        return response.status_code

    def add_alias(self,pfsession,alias,address,detail):
        alias_data = self.get_alias(pfsession,alias)
        descr_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        next_id = str(len(alias_data['address_ip']))
        alias_data['address_ip'].append((u'address' + next_id,u'' + address))
        alias_data['address_detail'].append((u'detail' + next_id,u'' + detail))
        addresses = dict(alias_data['address_ip'])
        details = dict(alias_data['address_detail'])
        alias_payload_base = {
                             '__csrf_magic': alias_data['csrf'],
                             'origname': alias_data['alias_name'],
                             'name': alias_data['alias_name'],
                             'id': alias,
                             'tab': 'ip',
                             'descr': 'Last updated on the ' + descr_date,
                             'type': 'host',
                             'save': 'Save',
                             }
        alias_payload = self.merge_dicts(alias_payload_base,addresses,details)
        response = pfsession.post(self.alias_edit_url, data=alias_payload, verify=False)
        return response.status_code

    def get_alias(self,pfsession,alias):
        response = pfsession.get(self.alias_edit_url + '?id=' + alias, verify=False)
        alias_name = findall('name="origname".*?value="([^"]+)', response.text)[0]
        addresses  = findall('name="(address\d+)".*?value="([^"]+)', response.text)
        details = findall('name="(detail\d+)".*?value="([^"]+)', response.text)
	csrf_token = self.get_csrf(response.text)
        results = {
                  'alias_name': alias_name,
                  'address_ip': addresses,
                  'address_detail': details,
                  'csrf': csrf_token
                  }
        return results

    def login(self,username,password):
        print 'Logging in with ' + username + ' - ' + password
        pfsession = Session()
        response = pfsession.get(self.url, verify=False)
        csrf_token = self.get_csrf(response.text)
        login_payload = {
                        '__csrf_magic': csrf_token,
                        'usernamefld': username,
                        'passwordfld': password,
                        'login': 'Sign+In'
                        }
        pfsession.post(self.url, data=login_payload, verify=False)

        check_login = pfsession.get(self.url, verify=False)
        login_user  = findall('usepost>Logout \((.*?)\)', check_login.text)
        if len(login_user) == 1:
            return pfsession
	else:
            return false
