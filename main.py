# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


import sys
import os

import creator_cf_sd
import creator_dalle
import tg_sender
import unsplash
from dotenv import load_dotenv

if __name__ == '__main__':
    # 加载 .env 文件
    load_dotenv()

    print("Hello World!")
    # cf_sd_creator.draw(GEMINI_KEY)
    prompt = unsplash.get_random_image()

    sd_path = creator_cf_sd.generate_image_by_sd(prompt)
    if sd_path:
        tg_sender.send_to_tg(sd_path, "Cloudflare Stable Diffusion Draw: " + prompt, None)
    dalle_path = creator_dalle.generate_image_by_dalle(prompt)
    if dalle_path:
        tg_sender.send_to_tg(dalle_path, "Dall-E-3 Draw: " + prompt, None)

