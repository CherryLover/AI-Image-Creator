import json
import os
import time

import requests

import tool_download


def generate_mj(prompt):
    img_path_list = []
    result = {}
    task_id = submit_main_generate(prompt)
    for i in range(1, 20):
        print(f'query random {i}')
        result = query_result(task_id)
        if result:
            break
        time.sleep(30)

    if not result:
        print(f'generate_mj failed {prompt} spend too much time')
        return img_path_list

    img_url = result['image_url']
    path = tool_download.download(img_url, "mj")
    print(f'download success {path} by {img_url}')
    img_path_list.append(path)
    print('\n current action upscale\n')
    for button in result['upscale']:
        upscale_id = upscale(result['task_id'], button['customId'])
        time.sleep(30)
        upscale_result = query_result(upscale_id)
        if not upscale_result:
            continue
        if upscale_result['status'] != 'success':
            continue
        img_url = upscale_result['image_url']
        print(f'upscale success {img_url} by {upscale_id}')
        upscale_path = tool_download.download(img_url, "mj")
        img_path_list.append(upscale_path)

    print(f"img_path_list size: {len(img_path_list)} json {json.dumps(img_path_list)}")
    return img_path_list


def submit_main_generate(prompt):
    url = "https://api.huiyan-ai.com/mj/submit/imagine"
    payload = json.dumps({
        "botType": "MID_JOURNEY",
        "prompt": prompt
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("HUIYAN_MJ_KEY", "")}'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()['result']


def upscale(task_id, action_code):
    url = "https://api.huiyan-ai.com/mj/submit/action"
    payload = json.dumps({
        "customId": action_code,
        "taskId": task_id
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("HUIYAN_MJ_KEY", "")}'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()['result']


def query_result(task_id):
    url = f"https://api.huiyan-ai.com/mj/task/{task_id}/fetch"

    payload = json.dumps({
        "botType": "MID_JOURNEY",
        "prompt": "A cute baby sea otter"
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("HUIYAN_MJ_KEY", "")}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code != 200:
        print(f"query_result({task_id}) failed {response.status_code}")
        return None
    response_json = response.json()
    print(response_json)
    if response_json['status'] != 'SUCCESS':
        print(f"query_result({task_id}) failed {response_json['status']}")
        return None
    if response_json['progress'] != '100%':
        print(f"query_result({task_id}) failed {response_json['progress']}")
        return None
    image_url = response_json['imageUrl']
    if not image_url or image_url == "":
        print(f"query_result({task_id}) failed {image_url}")
    print(f"task({task_id}) result {response_json['imageUrl']}")
    if response_json['action'] == "IMAGINE":
        up_list = []
        for button in response_json['buttons']:
            if str(button['customId']).__contains__("upsample"):
                up_list.append(button)
        return {
            'status': 'success',
            'image_url': image_url,
            'task_id': response_json['id'],
            'upscale': up_list
        }
    return {
        'status': 'success',
        'image_url': image_url
    }
