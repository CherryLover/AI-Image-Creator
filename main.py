# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


import sys
import os

import cf_sd_creator
import unsplash

if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise Exception("Please input gemini key")
    GEMINI_KEY = ""
    TG_KEY = sys.argv[1]
    tg_chat_id = int(sys.argv[2])
    UNSPLASH_KEY = sys.argv[3]

    open_ai_host = sys.argv[4]
    open_ai_key = sys.argv[5]

    print("Hello World!")
    # cf_sd_creator.draw(GEMINI_KEY)
    unsplash.get_random_image(GEMINI_KEY, UNSPLASH_KEY, TG_KEY, tg_chat_id, open_ai_host, open_ai_key)

