import requests


def clean_multi_selection(text):
    chr = (",")
    for c in chr:
        text = text.replace(c, "")
    return text


class NotionApi:
    def __init__(self, notion_token, notion_db_id, notion_daily_report_db_id):
        self.notion_token = notion_token
        self.notion_db_id = notion_db_id
        self.notion_daily_report_db_id = notion_daily_report_db_id
        self.headers = {"Authorization": notion_token,
                        "Notion-Version": "2022-06-28"}
        self.session = requests.Session()

    def query(self, with_query=True, query=None, db_id=None):
        url = f"https://api.notion.com/v1/databases/{self.notion_db_id if db_id is None else db_id}"
        if with_query:
            url += "/query"
            if query:
                response = self.session.post(url, headers=self.headers,
                                     json={"filter": query})
            else:
                response = self.session.post(url, headers=self.headers)
        else:
            response = self.session.get(url, headers=self.headers)
        return response.json()

    def add_game_page(self, data):
        url = f"https://api.notion.com/v1/pages"
        post_data = {
            "parent": {"database_id": self.notion_db_id},
            "icon": {
                "type": "external",
                "external": {
                    "url": data["icon"]
                }
            },
            "cover": {
                "external": {
                    "url": data.get("header_image", "")
                },
                "type": "external"
            },
            "properties": {
                "背景图片": {
                    "files": [
                        {
                            "external": {
                                "url": data.get("background_raw", "")
                            },
                            "name": "background_image",
                            "type": "external"
                        }
                    ]
                },
                "发行商": {
                    "multi_select": [{"name": clean_multi_selection(publisher)} for publisher in data.get("publishers", [])]
                },
                "游戏类型": {
                    "multi_select": [{"name": clean_multi_selection(type.get('description'))} for type in data.get("genres", [])]
                },
                "steamdb链接": {
                    "url": f"https://steamdb.info/app/{data['steam_appid']}"
                },
                "appid": {
                    "number": data["steam_appid"]
                },
                "游戏时长": {
                    "number": data["total_time"]
                },
                "游戏封面": {
                    "files": [
                        {
                            "external": {
                                "url": data.get("header_image", "")
                            },
                            "name": "cover",
                            "type": "external"
                        }
                    ]
                },
                "已达成成就": {
                    "number": data["completed_achievements"]
                },
                "图标": {
                    "files": [
                        {
                            "external": {
                                "url": data["icon"]
                            },
                            "name": "icon",
                            "type": "external"
                        }
                    ]
                },
                "发售日期": {
                    "date": {
                        'start': data["release_date"]["date"],
                        'end': None,
                        'time_zone': None
                    }
                },
                "总成就数": {
                    "number": data["total_achievements"]
                },
                "游玩平台": {
                    "multi_select": [{"name": "steam"}]
                },
                "游戏简介": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": data["detailed_description"][:1500]
                            }
                        }
                    ]
                },
                # "原价": {
                #     "number": data["initial_price"]
                # },
                "游戏名": {
                    "title": [
                        {
                            "text": {
                                "content": data["name"]
                            }
                        }
                    ]
                },
                "游戏图片": {
                    "files": [
                        {"external": {"url": photos["path_full"]}, "name": f"screenshots_{photos['id']}",
                         "type": "external"} for photos in data["screenshots"]
                    ]
                },
                "游戏视频": {
                    "files": [
                        {"external": {"url": movies["mp4"]['max']}, "name": f"movies_{movies['name']}_{movies['id']}",
                         "type": "external"} for movies in data["movies"]
                    ]
                }
            }
        }
        # print(post_data)
        response = self.session.post(url, json=post_data, headers=self.headers)
        print(response.json())
        return response.json()

    def query_by_appid(self, appid):
        filter = {
            "property": "appid",
            "number": {
                "equals": appid
            }
        }
        data = self.query(with_query=True, query=filter)
        return data.get("results", [])

    def has_appid(self, appid):
        return len(self.query_by_appid(appid)) > 0

    def update_info_by_page_id(self, id, total_time=None, completed_achievements=None, type=None):
        data = dict()
        if total_time is not None:
            data["游戏时长"] = {"number": total_time}
        if completed_achievements is not None:
            data["已达成成就"]= {"number": completed_achievements}
        if type is not None:
            data["游玩状态"] = {"multi_select": [{"name": t} for t in type]}
        url = f"https://api.notion.com/v1/pages/{id}"
        response = self.session.patch(url, headers=self.headers, json={"properties": data})
        return response.json().get("id", None)

    def add_daily_report(self, name, appid, daily_time, daily_achievements, game_list_id):
        url = f"https://api.notion.com/v1/pages"
        post_data = {
            "parent": {"database_id": self.notion_daily_report_db_id},
            "properties": {
                "游戏名": {
                    "title": [
                        {
                            "text": {
                                "content": name
                            }
                        }
                    ]
                },
                "appid": {
                    "number": appid
                },
                "日游玩时长": {
                    "number": daily_time
                },
                "日达成成就数": {
                    "number": daily_achievements
                },
                "游戏列表": {
                    'relation': [
                        {
                            'id': game_list_id
                        }
                    ]
                }
            }
        }
        response = self.session.post(url, headers=self.headers, json=post_data)
        print(response.json())
        return response.json()


if __name__ == '__main__':
    my_notion = NotionApi(NOTION_API_TOKEN, NOTION_DB_ID, NOTION_DAILY_REPORT_DB_ID)
    data = {
        "icon": "https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/apps/233450/c166c7911beec4d63a74cdddf25f26b73c84556b.jpg",
        "header_image": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/233450/header_schinese.jpg?t=1737117114",
        "background_raw": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/233450/page.bg.jpg",
        "steam_appid": 233450,
        "publishers": ['Paradox Interactive'],
        "genres": ["独立", "模拟", "策略"],
        "total_time": 284,
        "release_date": "2021-08-27",
        "detailed_description": '<strong>欢迎各位典狱长！</strong><br><br>只有世界上最残酷无情的典狱长能镇住世界上最惨无人道的囚犯。在《Prison Architect》中设计并发展独具个人风格的监狱。<br><br><i>主要特色：</i><h2 class="bb_tag">自定义监禁</h2>配置资源来让监狱发挥最大效益，但别限制人群流动，因为若遇上洪水、火灾、斗殴或严重暴动将酿成严重后果。<h2 class="bb_tag">投资与创新</h2>运用联邦拨款的基金来对抗疾病、帮派活动和诉讼案件等项目！<h2 class="bb_tag">恩威并施</h2>雇用顶尖的武装安保、心理学家、医生、律师和告密者，确保您的监狱“绝大部分”都符合道德与安全规范。<h2 class="bb_tag">特设矫正</h2>需根据每位囚犯的犯罪记录安排不同的治疗项目、劳动计划和自新工作坊。<h2 class="bb_tag">封锁对决</h2>于逃狱模式中，尝试冒着高风险逃离自己门禁森严的监狱，或是于在线模式中，从 12,000 名玩家建造的监狱中择其一来尝试逃狱。还能在沙盒模式中不受拘束地扩展您的矫正伟业。+',
        "completed_achievements": 3,
        "total_achievements": 18,
        "initial_price": 228,
        "name": "Prison Architect",
        'movies': [
            {
                'id': 256657032,
                'name': 'Prison Architect V1.0 trailer',
                'thumbnail': 'https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/256657032/movie.293x165.jpg?t=1447378356',
                'webm': {
                    '480': 'http://video.akamai.steamstatic.com/store_trailers/256657032/movie480.webm?t=1447378356',
                    'max': 'http://video.akamai.steamstatic.com/store_trailers/256657032/movie_max.webm?t=1447378356'
                },
                'mp4': {
                    '480': 'http://video.akamai.steamstatic.com/store_trailers/256657032/movie480.mp4?t=1447378356',
                    'max': 'http://video.akamai.steamstatic.com/store_trailers/256657032/movie_max.mp4?t=1447378356'
                },
                'highlight': True
            }
        ],
        'screenshots': [
            {
                'id': 0,
                'path_thumbnail': 'https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/233450/ss_0c13ec061d922fbe8ad518eb58487cff09d3fd40.600x338.jpg?t=1737117114',
                'path_full': 'https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/233450/ss_0c13ec061d922fbe8ad518eb58487cff09d3fd40.1920x1080.jpg?t=1737117114'
            }
        ],
    }
    print(my_notion.query_by_appid(appid=12))
    # print(my_notion.query(db_id=NOTION_DAILY_REPORT_DB_ID))
    # print(my_notion.update_info_by_page_id("182a2d6e-4d3c-8042-ba03-e54d1e76bb0b", total_time=2, completed_achievements=1))
    # print(my_notion.add_daily_report(12, 20, 2, "182a2d6e-4d3c-8042-ba03-e54d1e76bb0b"))
    # print(my_notion.add_game_page(data))
