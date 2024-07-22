# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


import sys
import os

import cf_sd_creator
import unsplash
from dotenv import load_dotenv

if __name__ == '__main__':
    # 加载 .env 文件
    load_dotenv()

    print("Hello World!")
    # cf_sd_creator.draw(GEMINI_KEY)
    unsplash.get_random_image()

