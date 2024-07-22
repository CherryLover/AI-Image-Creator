import os
import requests


def send_to_tg(img_file_path, message, buttons):
    url = f'https://api.telegram.org/bot{os.getenv("TG_KEY", "")}/sendPhoto?bot=AIImage'
    files = {'photo': open(img_file_path, 'rb')}
    data = {'caption': message, 'chat_id': os.getenv("TG_CHAT_ID", 0)}
    if buttons:
        data['reply_markup'] = buttons
    response = requests.post(url, files=files, data=data)
    if response.status_code != 200:
        print(response.text)
        raise Exception(f"Unexpected code {response.status_code}")


def send_to_tg_msg(message):
    url = f'https://api.telegram.org/bot{os.getenv("TG_KEY", "")}/sendMessage'
    data = {'text': message, 'chat_id': os.getenv("TG_CHAT_ID", 0)}
    response = requests.post(url, json=data)
    if response.status_code != 200:
        print(response.text)
        raise Exception(f"Unexpected code {response.status_code}")


# 用于批量发送，DALL-E 3 可以生成多张图片
def send_to_tg_media_group(img_file_url_list, message, buttons):
    if len(img_file_url_list) < 1:
        return
    url = f'https://api.telegram.org/bot{os.getenv("TG_KEY", "")}/sendMediaGroup'
    media = []
    for img_file_url in img_file_url_list:
        media.append({'type': 'photo', 'media': img_file_url, 'caption': message, 'parse_mode': 'Markdown'})
    data = {'media': media, 'chat_id': os.getenv("TG_CHAT_ID", 0)}
    if buttons:
        data['reply_markup'] = buttons
    response = requests.post(url, json=data)
    if response.status_code != 200:
        print(response.text)
        raise Exception(f"Unexpected code {response.status_code}")