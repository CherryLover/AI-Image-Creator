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
Please assess and score this image as a demanding fine artist on the following scale:
    
    1. technical competence (15 marks): assess the clarity of line, the choice and use of colour, the composition and layout of the work, and the use of materials.
    2. Creativity (15 marks): assesses the creativity of the work, including novel ideas, unique expressions, and unique perspectives.
    3. clarity of subject matter (15 marks): assesses whether the subject matter of the work is clear and whether the author's intention can be understood intuitively.
    4. Emotional expression (15 points): assesses whether the author has succeeded in conveying emotions through the work and whether the viewer can feel these emotions.
    5. Appreciation (10 points): assesses the appreciation of the work, including whether it attracts the viewer's attention and whether it has a certain degree of artistic appeal.
    6. Social/Cultural Impact (10 points): Assess the social or cultural impact of the work, such as whether the work reflects social phenomena and whether it has deep cultural connotations.
    7. Scene realism (10 points): assess the realism of the author in depicting the scene, including colour, light and proportion.
    8. Completeness of Portraits (10 points): If the work contains portraits, assess whether the portrayal of the characters' features and limbs is accurate, and whether their expressions and postures are natural.
    
    Only return a json with two fields: score and comment. score is an integer from 0-100 and comment is a string with no more than 50 characters. Thank you for your help.
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
    if len(sys.argv) < 2:
        raise Exception("Please input gemini key")
    GEMINI_KEY = sys.argv[1]

    sys.stdout.write("Hello World!")
    current_run_dir = prepare_img_dir()
    sys.stdout.write(f"Current run dir: {current_run_dir}")
    for i in range(4):
        sys.stdout.write(f"Round {i}\n")
        try:
            prompt = generate_random_prompt()
            generate_image_by_sd_file_path = generate_image_by_sd(prompt)
            if not generate_image_by_sd_file_path:
                sys.stdout.write(f"generateImageBySd failed --> {generate_image_by_sd_file_path}\n ")
                continue
            judge_image_by_gemini = judge_image_by_gemini(generate_image_by_sd_file_path)
            report_image(prompt, generate_image_by_sd_file_path, judge_image_by_gemini)
        except Exception as e:
            sys.stdout.write(f"Exception: {e}")
        time.sleep(30)

