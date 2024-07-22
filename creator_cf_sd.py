import os
import time

import requests

from unsplash import prepare_img_dir


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