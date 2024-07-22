import os
import time

import requests

from unsplash import prepare_img_dir


def generate_image_by_dalle(prompt):
    url = f'https://{os.getenv("OPEN_AI_HOST", "")}/v1/images/generations'
    final_prompt = f"{prompt}."
    print(f"finalPrompt: {final_prompt}\n")
    data = {
        'prompt': final_prompt,
        'n': 1,
        'model': 'dall-e-3',
        'size': '1024x1024'
    }
    head = {
        'Authorization': f'Bearer {os.getenv("OPEN_AI_KEY", "")}'
    }
    response = requests.post(url, json=data, headers=head)
    if response.status_code != 200:
        print(f"request dalle failed {response.status_code}")
        print(response.text)
        return ""
    print(response.json())
    file_url = response.json()['data'][0]['url']
    if not file_url:
        return ""
    response = requests.get(file_url)
    if response.status_code != 200:
        return ""
    file_path = os.path.join(prepare_img_dir(), f"dalle_{int(time.time())}.png")
    with open(file_path, "wb") as f:
        f.write(response.content)
    f.close()
    print(f"file_path: {file_path}\n")
    return file_path