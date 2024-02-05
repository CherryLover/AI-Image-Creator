#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/2/4 18:32
# @Desc    :

import os
import random
import requests

orientation_list = ["landscape", "portrait", "squarish"]


def prepare_img_dir():
    dir_path = os.path.join(os.getcwd(), "unsplash_img")
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def send_to_tg(img_file_path, tg_key, message, link):
    url = f'https://tg-sender.flyooo.uk/sendPhoto?bot=AIImage'
    files = {'photo': open(img_file_path, 'rb')}
    data = {'caption': message,
            'reply_markup': f'{{"inline_keyboard":[[{{"text":"View on Unsplash","url":"{link}"}}]]}}'
            }
    headers = {'Authorization': f'{tg_key}'}
    response = requests.post(url, files=files, data=data, headers=headers)
    if response.status_code != 200:
        print(response.text)
        raise Exception(f"Unexpected code {response.status_code}")


def get_random_image(unsplash_key, tg_key):
    orientation = random.choice(orientation_list)
    url = f'https://api.unsplash.com/photos/random?client_id={unsplash_key}&count=1&orientation={orientation}'
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Unexpected code {response.status_code}")
    response_text = response.json()
    if len(response_text) == 0:
        raise Exception("No image found")
    img_id = response_text[0]['id']
    img_url = response_text[0]['urls']['full']
    author = response_text[0]['user']
    # author = response_text[0]['user']['name']
    count_like = response_text[0]['likes']
    count_download = response_text[0]['downloads']
    share_info = f"Photo by {author['name']} on Unsplash"
    message = f"Likes: {count_like}\nDownloads: {count_download}\n{share_info}"
    link = response_text[0]['links']['html']

    prepare_img_dir()
    img_response = requests.get(img_url)
    img_file_path = os.path.join(prepare_img_dir(), f"{img_id}.jpg")
    with open(img_file_path, "wb") as img_file:
        img_file.write(img_response.content)
    img_file.close()

    send_to_tg(img_file_path, tg_key, message, link)