# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import creator_cf_sd
import creator_dalle
import tg_sender
import tool_cf_r2
import tool_notion
import unsplash
from dotenv import load_dotenv

if __name__ == '__main__':
    # 加载 .env 文件
    load_dotenv()

    print("Hello World!")
    unsplash_obj = unsplash.get_random_image()
    prompt = unsplash_obj['prompt']
    file_path = unsplash_obj['file_path']

    notion_args = {
        'prompt': prompt,
        'unsplash_url': unsplash_obj['url'],

        'unsplash_path': file_path,
        'unsplash_count_like': unsplash_obj['count_like'],
        'unsplash_count_download': unsplash_obj['count_download'],
        'cf_sd_path': '',
        'dalle_path': ''
    }

    sd_path = creator_cf_sd.generate_image_by_sd(prompt)
    if sd_path:
        tg_sender.send_to_tg(sd_path, "Cloudflare Stable Diffusion Draw: " + prompt, None)
        sd_url = tool_cf_r2.save_file(sd_path)
        notion_args['cf_sd_path'] = sd_url
    dalle_path = creator_dalle.generate_image_by_dalle(prompt)
    if dalle_path:
        tg_sender.send_to_tg(dalle_path, "Dall-E-3 Draw: " + prompt, None)
        dalle_url = tool_cf_r2.save_file(dalle_path)
        notion_args['dalle_path'] = dalle_url
    tool_notion.save_day_img(notion_args)

