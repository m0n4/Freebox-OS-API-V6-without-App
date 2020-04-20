# coding: utf-8
import hashlib
import hmac
import json
import os
import requests
import subprocess
import sys
import texttable as tt
from sys import platform

password = 'CHANGE ME'

def getChallenge():
    r = s.get(url, headers=headers)
    j = json.loads(r.text)
    parts = j['result']['challenge']
    password_salt = j['result']['password_salt']
    challenge = ''
    if platform == "win32":
        with open("evalJS.js", "w") as f: 
            f.write("""WScript.ECho('###'+eval(WScript.arguments(0))+'###');""") 
        for part in parts:
            r = subprocess.check_output(["cscript", "evalJS.js", part])
            challenge += str(r).split('###')[1]
        os.remove("evalJS.js") 
    else:
        import PyV8
        ctx = PyV8.JSContext()
        ctx.enter()
        for letter in parts:
            challenge += ctx.eval(letter)
    return(password_salt, challenge)

def sendPassword(password_salt, challenge, password):
    sha1 = hashlib.sha1((password_salt+password).encode('utf-8')).hexdigest()
    if (sys.version_info > (3, 0)):
        sha1 = bytes(sha1, 'utf-8')
        challenge = bytes(challenge, 'utf-8')
    mac = hmac.new(sha1, challenge, hashlib.sha1).hexdigest()
    data = {"password": mac}
    r = s.post(url, data=data, headers=headers)
    return(r.status_code == 200)

def doWhatever():
    base = 'http://mafreebox.freebox.fr/api/v6/'
    apis = ['api_version', 'wifi/config/', 'connection/config/', 'system/', 'lcd/config', 'lan/config/']
    for api in apis:
        r = s.get(base+api, headers=headers)
        j = json.loads(r.text)
        tab = tt.Texttable()
        title = ['API', api]
        tab.header(title)
        if api == 'api_version':
            for key in j:
                tab.add_row([key, j[key]])             
        else:
            for key in j['result']:
                tab.add_row([key, j['result'][key]])            
        print(tab.draw()+'\n')

if __name__ == '__main__':
    s = requests.session()
    url = 'http://mafreebox.freebox.fr/api/v6/login/'
    headers = {'X-FBX-FREEBOX0S': '1', 'X-Requested-With': 'XMLHttpRequest'}
    password_salt, challenge = getChallenge()
    success = sendPassword(password_salt, challenge, password)  
    if success:
          doWhatever()
    else:
        print('Failed')
