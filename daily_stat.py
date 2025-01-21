import os

from notion_api import NotionApi
from steam_api import SteamApi
# from steam_api_model import *
from datetime import datetime


class DailyStat:
    def __init__(self, steam_api_key, steam_id, notion_api_token, game_list_id, daily_stat_id):
        self.steam_api_key = steam_api_key
        self.steam_id = steam_id
        self.steam_api = SteamApi(steam_id, steam_api_key)
        self.notion_api_token = notion_api_token
        self.game_list_id = game_list_id
        self.daily_stat_id = daily_stat_id
        self.notion_api = NotionApi(notion_api_token, game_list_id, daily_stat_id)

    def update_game_list(self):
        owned_games_info = self.steam_api.get_owned_games()
        total_appid = []
        for game in owned_games_info.get('games', []):
            appid = game.get('appid')
            if not appid:
                continue
            total_time = game.get('playtime_forever')
            completed_achievements, total_achievements = self.steam_api.count_achievements(appid)
            if not self.notion_api.has_appid(appid):
                game_details = self.steam_api.get_game_details(appid)
                if not game_details or not game_details.get("success", True):
                    continue
                try:
                    game_details["release_date"]["date"] = datetime.strptime(game_details["release_date"]["date"], "%Y 年 %m 月 %d 日").strftime("%Y-%m-%d")
                except ValueError:
                    try:
                        game_details["release_date"]["date"] = datetime.strptime(game_details["release_date"]["date"],
                                                                                 "%Y 年 %m 月").strftime(
                            "%Y-%m-01")
                    except ValueError:
                        pass
                except KeyError:
                    game_details["release_date"] = {"date": ""}
                game_details["icon"] = f"https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/apps/{appid}/{game.get('img_icon_url')}.jpg"
                game_details["total_time"] = total_time
                game_details["completed_achievements"] = completed_achievements
                game_details["total_achievements"] = total_achievements
                game_details["initial_price"] = game_details.get('price_overview', {}).get('initial')
                result = self.notion_api.add_game_page(game_details)
                id = result.get('id')
                if id:
                    self.notion_api.add_daily_report(game_details.get("name", ""), appid, total_time, total_achievements, id)
            else:
                query_info = self.notion_api.query_by_appid(appid)
                if len(query_info):
                    game_info = query_info[0]['properties']
                    name = game_info["游戏名"]["title"][0]["plain_text"]
                    previous_time = game_info['游戏时长']['number']
                    previous_achievements = game_info['已达成成就']['number']
                    params = dict()
                    if total_time > previous_time:
                        params['total_time'] = total_time
                    if completed_achievements > previous_achievements:
                        params['completed_achievements'] = completed_achievements
                    if params.keys():
                        id = query_info[0]['id']
                        self.notion_api.update_info_by_page_id(id, **params)
                        self.notion_api.add_daily_report(name, appid, total_time - previous_time, completed_achievements - previous_achievements, id)


if __name__ == '__main__':

    STEAM_ID = os.environ["STEAM_ID"]
    STEAM_API_KEY = os.environ["STEAM_API_KEY"]
    NOTION_API_TOKEN = os.environ["NOTION_API_TOKEN"]
    NOTION_DB_ID = os.environ["NOTION_DB_ID"]
    NOTION_DAILY_REPORT_DB_ID = os.environ["NOTION_DAILY_REPORT_DB_ID"]
    my_daily_stat = DailyStat(STEAM_API_KEY, STEAM_ID, NOTION_API_TOKEN, NOTION_DB_ID, NOTION_DAILY_REPORT_DB_ID)
    my_daily_stat.update_game_list()






