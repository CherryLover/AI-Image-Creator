import os
import time

import jwt
import requests
from dotenv import load_dotenv

import tool_download

jwt_token = ""

base_url = "https://api.klingai.com"


def encode_jwt_token():
    global jwt_token
    if jwt_token != "":
        return jwt_token
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }
    ak = os.getenv("KELING_AK", "")
    sk = os.getenv("KELING_SK", "")
    print("ak is empty ", str(ak == ""))
    print("sk is empty ", str(ak == ""))
    payload = {
        "iss": ak,
        "exp": int(time.time()) + 18000,  # 有效时间，此处示例代表当前时间+1800s(30min)
        "nbf": int(time.time()) - 10  # 开始生效的时间，此处示例代表当前时间-5秒
    }
    token = jwt.encode(payload, sk, headers=headers)
    jwt_token = token
    return token


def generate_headers():
    token = encode_jwt_token()
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }
    return headers


def submit_job(prompt, img_count=4, aspect_ratio="16:9"):
    if img_count < 1:
        img_count = 1
    elif img_count > 9:
        img_count = 9
    data = {
        "model": "kling-v1",
        "prompt": prompt,
        "n": img_count,
        "aspect_ratio": aspect_ratio
    }
    response = requests.post(f"{base_url}/v1/images/generations", headers=generate_headers(), json=data)
    if response.status_code != 200:
        print("submit job failed:", response.text)
        return ""
    response_body = response.json()
    if response_body["code"] != 0:
        print("submit job failed:" + response_body["message"] + " " + response_body["request_id"])
        return ""
    return response_body["data"]["task_id"]


def query_job(task_id):
    response = requests.get(f"{base_url}/v1/images/generations/{task_id}", headers=generate_headers())
    if response.status_code != 200:
        print("query job failed:", response.text)
        return []
    response_body = response.json()
    print(response_body)
    if response_body["code"] != 0:
        print("query job failed:" + response_body["message"] + " " + response_body["request_id"])
        return []
    status = response_body["data"]["task_status"]
    if status == "submitted":
        print("task submit")
        return []
    if status == "processing":
        print("processing")
        return []
    if status != "succeed":
        print("query job failed or processed: " + status + " " + response_body["data"]["task_status_msg"] + " by task_id: " + task_id)
        return []
    result = []
    for result_elem in response_body["data"]["task_result"]["images"]:
            result.append({
                "url": result_elem["url"],
                "caption": result_elem["index"]
            })
    return result


def query_job_wait(task_id, wait_seconds=10, max_retry=10):
    print("query task_id:", task_id)
    list = query_job(task_id)
    retry = 0
    while len(list) == 0 and retry < max_retry:
        print("query times ", retry)
        time.sleep(wait_seconds)
        list = query_job(task_id)
        retry += 1
    return list


def download_list(list):
    local_path_list = []
    for element in list:
        path = tool_download.download(element["url"], "keling")
        local_path_list.append(path)
    return local_path_list


def draw(prompt):
    task_id = submit_job(prompt)
    if task_id == "":
        return []
    return download_list(query_job_wait(task_id))


if __name__ == '__main__':
    load_dotenv()
    print("draw result ", draw("a cat"))
