import os
import requests
import time


def save_file(path):
    files = [
        ('file', (open(path, 'rb')))
    ]
    headers = {
        'Authorization': 'Bear ' + os.environ['CF_R2_API_KEY']
    }
    payload = {
        'fileName': time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.jpg'
    }
    url = os.environ['CF_R2_HOST'] + '/api/v1/static'
    response = requests.request("POST", url, headers=headers, files=files, data=payload)
    print('response code ' + str(response.status_code))
    print('response content ' + response.text)
    json = response.json()
    return os.environ['CF_R2_HOST'] + '/api/v1/path/' + json['fileName']
