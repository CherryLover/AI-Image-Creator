# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


import sys
import os
import time
import json
import base64
import requests
import logging
import random
import traceback
from http.client import HTTPConnection


logging.basicConfig(level=logging.DEBUG)
# 是否打印 header
# HTTPConnection.debuglevel = 1

GEMINI_KEY = ""

styles = [
"Renaissance", "Baroque", "Rococo", "Neoclassicism", "Romanticism", "Realism", "Surrealism", "Impressionism", "Post-Impressionism", "Modernism", "Post-Modernism"
]

def report_image(prompt, generate_image_by_sd_file_path, judge_image_by_gemini):
    url = "https://ai-image-manager.jiwzdj.workers.dev/saveImage"
    files = {'photo': (os.path.basename(generate_image_by_sd_file_path), open(generate_image_by_sd_file_path, 'rb'), 'image/png')}
    data = {
        'fileName': os.path.basename(generate_image_by_sd_file_path),
        'prompt': prompt,
        'score': judge_image_by_gemini['score'],
        'platform': 'sd'
    }
    response = requests.post(url, files=files, data=data)
    sys.stdout.write(response.text)


def generate_random_prompt():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_KEY}"
    data = {
        "contents": [{"parts": [{"text": "Please imagine a scene suitable for a photo or drawing and describe it in no more than 50 words. Thank you."}]}]
    }
    response = requests.post(url, json=data)
    if response.status_code != 200:
        raise Exception(f"Unexpected code {response.status_code}")
    response_text = response.json()
    return response_text['candidates'][0]['content']['parts'][0]['text'].replace("\n", "").strip()


def get_random_style():
    return random.choice(styles)

def generate_image_by_sd(prompt):
    url = "https://dpbot.jiwzdj.workers.dev/"

    sty = styles[int(time.time()) % len(styles)]
    final_prompt = f"Please paint a {prompt} in the {sty}."
    sys.stdout.write(f"finalPrompt: {final_prompt}\n")
    data = {
        'prompt': final_prompt
    }
    response = requests.post(url, json=data)
    if response.status_code != 200:
        return ""
    file_path = os.path.join(prepare_img_dir(), f"{int(time.time())}.png")
    with open(file_path, "wb") as f:
        f.write(response.content)
    f.close()
    sys.stdout.write(f"file_path: {file_path}\n")
    return file_path


def judge_image_by_gemini(file_path):
    with open(file_path, "rb") as f:
        file_base64 = base64.b64encode(f.read()).decode()

    prompt = """
    请你以一位对艺术要求严苛的美术家的身份对这张图片进行评估并打分，具体的打分标准如下：
    
    1. 技术能力（15分）：评判线条清晰度，颜色的选择和使用，作品的构图和布局，以及材料的使用。
    2. 创新性（15分）：评估作品的创新性，包括新颖的想法，独特的表达方式，和独特的视角。
    3. 主题清晰度（15分）：评价作品的主题是否清晰，是否能直观地理解作者的意图。
    4. 情感表达（15分）：评定作者是否能成功地通过作品传达情感，以及观者是否能感受到这些情感。
    5. 观赏性（10分）：评估作品的观赏性，包括能否吸引观者的注意力，以及是否具有一定的艺术魅力。
    6. 社会/文化影响力（10分）：评判作品的社会或文化影响力，如作品是否反映了社会现象，是否有深度的文化内涵。
    7. 场景真实度（10分）：评估作者在描绘场景时的真实度，包括色彩，光线，比例等方面。
    8. 人像五官及肢体完整性（10分）：如果作品中包含人像，评估人物的五官和肢体描绘是否准确，表情和姿态是否自然。
    
    只返回一个 json，包含两个字段：score 和 comment。score 是一个 0-100 的整数，comment 是一个字符串，不超过 50 个字。谢谢
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
    if response_text.startswith("```json"):
        response_text = response_text[7:-3]
    sys.stdout.write(response_text)
    return json.loads(response_text)


def prepare_img_dir():
    dir_path = os.path.join(os.getcwd(), "sd_img")
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise Exception("Please input gemini key")
    GEMINI_KEY = sys.argv[1]
    count = int(sys.argv[2]) + 1
    sys.stdout.write(f"Count: {count}\n")

    sys.stdout.write("Hello World!")
    current_run_dir = prepare_img_dir()
    sys.stdout.write(f"Current run dir: {current_run_dir}\n")
    for i in range(count):
        sys.stdout.write(f"Round {i}\n")
        try:
            prompt = generate_random_prompt()
            generate_image_by_sd_file_path = generate_image_by_sd(prompt)
            if not generate_image_by_sd_file_path:
                sys.stdout.write(f"generateImageBySd failed --> {generate_image_by_sd_file_path}\n ")
                continue
            judge_info = judge_image_by_gemini(generate_image_by_sd_file_path)
            report_image(prompt, generate_image_by_sd_file_path, judge_info)
        except Exception as e:
            traceback.print_exc()
        time.sleep(30)

