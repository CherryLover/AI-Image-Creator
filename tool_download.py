import os
import requests
import time


def prepare_img_dir():
    dir_path = os.path.join(os.getcwd(), "unsplash_img")
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def download(url, file_name_prefix):
    response = requests.get(url)
    file_path = os.path.join(prepare_img_dir(), f"{file_name_prefix}_{int(time.time())}.png")
    with open(file_path, "wb") as f:
        f.write(response.content)
    f.close()
    print(f"file_path: {file_path}\n")
    return file_path
