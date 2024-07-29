import os
import time

import requests


def save_day_img(notion_args):
    """
    保存每日图片到 Notion
    :param notion_args:
    prompt 图片描述
    unsplash_url Unsplash 图片的 URL

    unsplash_path: Unsplash 图片路径

    unsplash_count_like: Unsplash 点赞数
    unsplash_count_download: Unsplash 下载数
    unsplash_count_view: Unsplash 查看数

    cf_sd_path: Cloudflare Stable Diffusion 生成的图片路径
    dalle_path: DALL-E 3 生成的图片路径
    mjml_path: Midjourney 生成的图片路径
    :return:
    """
    url = "https://api.notion.com/v1/pages"
    headers = {
        'Authorization': f"Bearer {os.getenv('NOTION_KEY', '')}",
        'Content-Type': 'application/json',
        'Notion-Version': '2022-02-22'
    }
    today = time.strftime("%Y-%m-%d", time.localtime())
    data = {
        "parent": {
            "database_id": os.getenv('NOTION_DATABASE_ID', '')
        },
        "properties": {
            "Date": {
                "title": [
                    {
                        "text": {
                            "content": today
                        }
                    }
                ]
            },
            "Prompt": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": notion_args['prompt']
                        }
                    }
                ]
            },
            "URL": {
                "url": notion_args['unsplash_url']
            },
            "UnsplashLike": {
                "number": notion_args['unsplash_count_like']
            },
            "UnsplashDownload": {
                "number": notion_args['unsplash_count_download']
            }
            # "Unsplash": {
            #     "files": [
            #         {
            #             "name": "unsplash.jpg",
            #             "external": {
            #                 "url": notion_args['unsplash_path']
            #             }
            #         }
            #     ]
            # },
            # "Cloudflare": {
            #     "files": [
            #         {
            #             "name": "cf_sd.jpg",
            #             "external": {
            #                 "url": notion_args['cf_sd_path']
            #             }
            #         }
            #     ]
            # },
            # "DALL-E": {
            #     "files": [
            #         {
            #             "name": "dalle.jpg",
            #             "external": {
            #                 "url": notion_args['dalle_path']
            #             }
            #         }
            #     ]
            # },
            # "Midjourney": {
            #     "files": [
            #         {
            #             "name": "mjml.jpg",
            #             "external": {
            #                 "url": notion_args['mjml_path']
            #             }
            #         }
            #     ]
            # }
        },
        "children": [
            {
                "object": "block",
                "type": "image",
                "image": {
                    "type": "external",
                    "external": {
                        "url": notion_args['unsplash_path']
                    }
                }
            },
            {
                "object": "block",
                "type": "image",
                "image": {
                    "type": "external",
                    "external": {
                        "url": notion_args['cf_sd_path']
                    }
                }
            },
            {
                "object": "block",
                "type": "image",
                "image": {
                    "type": "external",
                    "external": {
                        "url": notion_args['dalle_path']
                    }
                }
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        print(response.text)
        raise Exception(f"Unexpected code {response.status_code}")
    print(response.json())
