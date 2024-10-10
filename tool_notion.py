import json
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
    mj_list: Midjourney 生成的图片路径集合
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
        },
        "children": [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "Unsplash"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "image",
                "image": {
                    "type": "external",
                    "external": {
                        "url": notion_args['unsplash_origin_url']
                    }
                }
            },
        ]
    }
    sd_path = notion_args['cf_sd_path'] or ''
    dalle_path = notion_args['dalle_path'] or ''
    if sd_path != '':
        data['children'].append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "Cloudflare Stable Diffusion"
                        }
                    }
                ]
            }
        })
        data['children'].append({
            "object": "block",
            "type": "image",
            "image": {
                "type": "external",
                "external": {
                    "url": sd_path
                }
            }
        })
    if dalle_path != '':
        data['children'].append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "DALL-E 3"
                        }
                    }
                ]
            }
        })
        data['children'].append({
            "object": "block",
            "type": "image",
            "image": {
                "type": "external",
                "external": {
                    "url": dalle_path
                }
            }
        })
    mj_list = notion_args['mj_list'] or []
    if len(mj_list) != 0:
        data['children'].append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "Midjourney"
                        }
                    }
                ]
            }
        })
    for index, mj in enumerate(mj_list):
        if index != 0:
            data['children'].append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"Upscale {str(index)}"
                            }
                        }
                    ]
                }
            })
        data['children'].append({
            "object": "block",
            "type": "image",
            "image": {
                "type": "external",
                "external": {
                    "url": mj
                }
            }
        })

    md_text = f"今日{today} AI 绘图"
    md_text += f"\n\n 提示词：\n\n{notion_args['prompt']}"
    md_text += "\n\n ## Unsplash"
    md_text += f"\n\n[Unsplash 原图]({notion_args['unsplash_origin_url']})"
    if sd_path != '':
        md_text += "\n\n ## Cloudflare Stable Diffusion"
        md_text += f"\n\n![Cloudflare Stable Diffusion]({sd_path})"
    if dalle_path != '':
        md_text += "\n\n ## DALL-E 3"
        md_text += f"\n\n![DALL-E 3]({dalle_path})"
    if len(mj_list) != 0:
        md_text += "\n\n ## Midjourney"
    for index, mj in enumerate(mj_list):
        if index != 0:
            md_text += f"\n\n ### Upscale {str(index)}"
        md_text += f"\n\n![Midjourney]({mj})"

    data['children'].append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": "Markdown"
                    }
                }
            ]
        }
    })
    # insert md as code
    data['children'].append({
        "object": "block",
        "type": "code",
        "code": {
            "language": "markdown",
            "text": md_text
        }
    })
    # page json
    page_json = {
        "prompt": notion_args['prompt'],
        "unsplash": {
            "url": notion_args['unsplash_url'],
            "path": notion_args['unsplash_path'],
            "origin_url": notion_args['unsplash_origin_url'],
            "count_like": notion_args['unsplash_count_like'],
            "count_download": notion_args['unsplash_count_download']
        },
        "cf_sd_path": notion_args['cf_sd_path'],
        "dalle_path": notion_args['dalle_path'],
        "mj_list": notion_args['mj_list']
    }
    data['children'].append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": "JSON"
                    }
                }
            ]
        }
    })
    # insert json as code
    data['children'].append({
        "object": "block",
        "type": "code",
        "code": {
            "language": "json",
            "text": json.dumps(page_json)
        }
    })
    print(json.dumps(data))
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        print(response.text)
        print(f"notion save page Unexpected code {response.status_code}")
    print(response.json())
