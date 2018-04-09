import os, json, requests, subprocess

class slack(object):

    def __init__(self,webhook):
        self.webhook = webhook

    def send_message(self,message):
        body = {"text": message}
        r = requests.post(self.webhook, json.dumps(body), headers={'content-type': 'application/json'})

        if r.status_code == requests.codes.ok:
            return bool(1)
        else:
            return bool(0)
