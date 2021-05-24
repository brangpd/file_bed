import time
import os
import sys
import http
import http.client
import json
import base64

USERINFO_FILE = '.userinfo'
GITHUB_API = 'api.github.com'
UPDATE_FILE_CONTENT_API = '/repos/{}/{}/contents/{}'
OWNER = ''
EMAIL = ''
REPO = ''
PATH = ''
TOKEN = ''
TIME = time.localtime()
TIME_STRING = time.strftime('%Y-%m-%d-%H-%M-%S', TIME)

if not os.path.exists(USERINFO_FILE):
  OWNER = input('Username:')
  REPO = input('Repository:')
  EMAIL = input('Email:')
  TOKEN = input('Token:')
  with open(USERINFO_FILE, 'w') as f:
    f.write('{} {} {}'.format(OWNER, REPO, EMAIL, TOKEN))
else:
  with open(USERINFO_FILE, 'r') as f:
    OWNER, REPO, EMAIL, TOKEN = f.readline().split()

if len(sys.argv) <= 1:
  print('No input files')
  exit(1)

conn = http.client.HTTPSConnection(GITHUB_API)

for argi in range(1, len(sys.argv)):
  filename = sys.argv[argi]
  filename_base = os.path.basename(filename)
  filename_with_time = TIME_STRING + '-{:02}-'.format(argi) + filename
  path = UPDATE_FILE_CONTENT_API.format(OWNER, REPO, filename_with_time)
  with open(filename, 'rb') as f_content:
    content = f_content.read()
    content_base64 = base64.standard_b64encode(content).decode()
    json_data = json.dumps({
      'message': filename_with_time,
      'content': content_base64,
      'committer': {
        'name': OWNER,
        'email': EMAIL,
      }
    })
    headers = {
      'User-Agent': 'file_bed',
      'Content-Type':'application/json',
      'Authorization': 'token ' + TOKEN,
    }
    conn.request('PUT', path, json_data, headers)
    resp = conn.getresponse()
    code = resp.getcode()
    if code >= 300:
      print(resp.getcode())
    else:
      print('OK: https://github.com/{}/{}/raw/main/{}'.format(OWNER, REPO, filename_with_time))

conn.close()

