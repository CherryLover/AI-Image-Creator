#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/2/4 18:32
# @Desc    :
import json
import logging
import os
import random
import requests
import base64
import PIL.Image
import time

from urllib3.connection import HTTPConnection

# logging.basicConfig(level=logging.DEBUG)
# # 是否打印 header
# HTTPConnection.debuglevel = 1

orientation_list = ["landscape", "portrait", "squarish"]

GEMINI_KEY = "AIzaSyD24oWO1cWAn8keEpZCAe9fa6sdXIagd-I"
TG_KEY = "sdfsf"


def download_img_pure(url, file_name):
    img_response = requests.get(url)
    img_file_path = os.path.join(prepare_img_dir(), f"{file_name}.jpg")
    with open(img_file_path, "wb") as img_file:
        img_file.write(img_response.content)
    img_file.close()
    return img_file_path


def prepare_img_dir():
    dir_path = os.path.join(os.getcwd(), "unsplash_img")
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def send_to_tg(img_file_path, tg_key, message, buttons):
    url = f'https://tg-sender.flyooo.uk/sendPhoto?bot=AIImage'
    files = {'photo': open(img_file_path, 'rb')}
    data = {'caption': message}
    if buttons:
        data['reply_markup'] = buttons
    headers = {'Authorization': f'{tg_key}'}
    response = requests.post(url, files=files, data=data, headers=headers)
    if response.status_code != 200:
        print(response.text)
        raise Exception(f"Unexpected code {response.status_code}")


def send_to_tg_media_group(img_file_url_list, tg_key, message, buttons):
    if len(img_file_url_list) < 1:
        return
    url = f'https://tg-sender.flyooo.uk/sendMediaGroup?bot=AIImage'
    media = []
    for img_file_url in img_file_url_list:
        media.append({'type': 'photo', 'media': img_file_url, 'caption': message, 'parse_mode': 'Markdown'})
    data = {'media': media, 'chat_id': '799133753'}
    if buttons:
        data['reply_markup'] = buttons
    headers = {'Authorization': f'{tg_key}'}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        print(response.text)
        raise Exception(f"Unexpected code {response.status_code}")


def get_image_desc_by_gemini(file_path):
    img = PIL.Image.open(file_path)
    img.resize((512, int(img.height * 512 / img.width)))
    with open(file_path, "rb") as f:
        file_base64 = base64.b64encode(f.read()).decode()

    prompt = """
    This is an image, describe what this image is about, including the people, objects, scenes, etc. in it. And extract keywords from the description, sorting them in order of relevance. Replying with text keywords only is fine, thank you.
    """
    json_data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    },
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": file_base64
                        }
                    }
                ]
            }
        ]
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key={GEMINI_KEY}"
    response = requests.post(url, json=json_data)
    if response.status_code != 200:
        raise Exception(f"Unexpected code {response.status_code}")
    response_text = response.json()
    response_text = response_text['candidates'][0]['content']['parts'][0]['text'].replace("\n", "").strip()
    print(response_text)
    contains = ":" in response_text
    if not contains:
        return
    response_text = response_text.split(":")[1].strip()
    print(response_text)
    return response_text


def get_random_image(gemini_key, unsplash_key, tg_key):
    global GEMINI_KEY
    GEMINI_KEY = gemini_key
    global TG_KEY
    TG_KEY = tg_key
    orientation = random.choice(orientation_list)
    url = f'https://api.unsplash.com/photos/random?client_id={unsplash_key}&count=1&orientation={orientation}'
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Unexpected code {response.status_code}")
    response_text = response.json()
    if len(response_text) == 0:
        raise Exception("No image found")
    img_id = response_text[0]['id']
    img_urls = response_text[0]['urls']
    author = response_text[0]['user']
    # author = response_text[0]['user']['name']
    count_like = response_text[0]['likes']
    count_download = response_text[0]['downloads']
    share_info = f"Photo by {author['name']} on Unsplash"
    message = f"Likes: {count_like}\nDownloads: {count_download}\n{share_info}"
    link = response_text[0]['links']['html']

    file_path_map = download_img(img_id, img_urls)
    tg_button = f'{{"inline_keyboard":[[{{"text":"View on Unsplash","url":"{link}"}}]]}}'
    send_to_tg(file_path_map['full'], tg_key, message, tg_button)

    prompt = response_text[0]['alt_description']
    if not prompt:
        prompt = get_image_desc_by_gemini(file_path_map['small'])
    sd_path = generate_image_by_sd(prompt)
    send_to_tg(sd_path, TG_KEY, prompt, None)

    dalle_draw_map = generate_image_by_dalle(prompt)
    if not isinstance(dalle_draw_map, dict):
        if isinstance(dalle_draw_map, str):
            print(dalle_draw_map)
        print("dalle draw request failed")
        return
    request_id = dalle_draw_map['requestId']
    print("requestId: " + request_id)
    # 休眠 30s，等待图片生成
    print("waiting 30s......")
    time.sleep(30)
    imgs = query_dalle_result(request_id, prompt)
    while len(imgs) == 0:
        print("waiting 10s......")
        time.sleep(10)
        imgs = query_dalle_result(request_id, prompt)
    send_to_tg_media_group(imgs, TG_KEY, "test", None)


def download_img(img_id, img_urls):
    prepare_img_dir()
    full_img_url = img_urls['full']
    small_img_url = img_urls['small']

    # tg 无法发送大图，不过也没必要了，有个 View on Unsplash 的按钮，可以直接跳转到原图
    # img_response = requests.get(full_img_url)
    # img_file_path = os.path.join(prepare_img_dir(), f"{img_id}.jpg")
    # with open(img_file_path, "wb") as img_file:
    #     img_file.write(img_response.content)
    # img_file.close()

    small_img_response = requests.get(small_img_url)
    small_img_file_path = os.path.join(prepare_img_dir(), f"{img_id}_small.jpg")
    with open(small_img_file_path, "wb") as small_img_file:
        small_img_file.write(small_img_response.content)
    small_img_file.close()

    return {
        "full": small_img_file_path,
        "small": small_img_file_path
    }


def generate_image_by_sd(prompt):
    url = "https://dpbot.jiwzdj.workers.dev/"

    final_prompt = f"{prompt}."
    print(f"finalPrompt: {final_prompt}\n")
    data = {
        'prompt': final_prompt
    }
    response = requests.post(url, json=data)
    if response.status_code != 200:
        return ""
    file_path = os.path.join(prepare_img_dir(), f"sd_{int(time.time())}.png")
    with open(file_path, "wb") as f:
        f.write(response.content)
    f.close()
    print(f"file_path: {file_path}\n")
    return file_path


def generate_image_by_dalle(prompt):
    url = "https://ai-image-creator.jiwzdj.workers.dev/draw"

    final_prompt = f"{prompt}."
    print(f"finalPrompt: {final_prompt}\n")
    data = {
        'prompt': final_prompt,
        'owner': 'monster',
        'platform': 'Dall-E'
    }
    head = {
        'x-token': '1uf0xfp%7C2%7Cfii%7C0%7C1478'
    }
    response = requests.post(url, json=data, headers=head)
    if response.status_code != 200:
        print(f"request dalle failed {response.status_code}")
        print(response.text)
        return ""
    return response.json()


def query_dalle_result(request_id, prompt):
    url = "https://ai-image-creator.jiwzdj.workers.dev/queryDallEResult?requestId=" + request_id
    head = {
        'x-token': '1uf0xfp%7C2%7Cfii%7C0%7C1478'
    }
    response = requests.get(url, headers=head)
    if response.status_code != 200:
        return ""
    text = response.text
    if "In Progress" in text:
        return []
    print(text)
    result_json = json.loads(text)
    attempt_img = result_json['images']
    # 判断 attempt_img 类型是否为 list,
    # 如果是 list 类型，直接返回
    if isinstance(attempt_img, list):
        return attempt_img
    # 如果不是 list 类型，尝试解析为 json
    images = []
    print("attempt_img text " + json.dumps(attempt_img))
    print("attempt_img type " + str(type(attempt_img)))
    try:
        images = json.loads(attempt_img)
    except Exception as e:
        print(e)
    return images