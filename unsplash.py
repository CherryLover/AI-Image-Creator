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

import tg_sender

# logging.basicConfig(level=logging.DEBUG)
# # 是否打印 header
# HTTPConnection.debuglevel = 1

orientation_list = ["landscape", "portrait", "squarish"]


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
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key={os.getenv("GEMINI_KEY", "")}'
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


def get_random_image():
    url = f'https://api.unsplash.com/photos/random?client_id={os.getenv("UNSPLASH_KEY", "")}&count=1&orientation={random.choice(orientation_list)}'
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
    file_path = ''
    try:
        tg_sender.send_to_tg(file_path_map['full'], message, tg_button)
        file_path = file_path_map['full']
    except Exception as e:
        print(e)
        try:
            tg_sender.send_to_tg(file_path_map['small'], message, tg_button)
            file_path = file_path_map['small']
        except Exception as e:
            print(e)
            tg_sender.send_to_tg_msg('Failed to send image, please view on Unsplash: ' + link)

    prompt = response_text[0]['alt_description']
    print("prompt: " + prompt)
    print("file_path: " + file_path)
    if not prompt:
        prompt = get_image_desc_by_gemini(file_path_map['small'])
    return {
        "prompt": prompt,
        "file_path": file_path,
        "url": link,
        "count_like": count_like,
        "count_download": count_download,
        "origin_url": img_urls['full']
    }


def download_img(img_id, img_urls):
    prepare_img_dir()
    full_img_url = img_urls['full']
    small_img_url = img_urls['small']

    # tg 无法发送大图，不过也没必要了，有个 View on Unsplash 的按钮，可以直接跳转到原图
    img_response = requests.get(full_img_url)
    img_file_path = os.path.join(prepare_img_dir(), f"{img_id}.jpg")
    with open(img_file_path, "wb") as img_file:
        img_file.write(img_response.content)
    img_file.close()

    small_img_response = requests.get(small_img_url)
    small_img_file_path = os.path.join(prepare_img_dir(), f"{img_id}_small.jpg")
    with open(small_img_file_path, "wb") as small_img_file:
        small_img_file.write(small_img_response.content)
    small_img_file.close()

    return {
        "full": img_file_path,
        "small": small_img_file_path
    }
