import requests

from steam_api_model import *


class SteamApi:
    API_URL = "https://api.steampowered.com/{interface}/{method}/v{version}/?appid={appid}&key={key}&steamid={userid}&format={format}"
    HEADERS = {'Accept': 'application/json',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0',
               'Accept-language': 'zh-CN,zh;q=0.9'}

    def __init__(self, steam_id, steam_api_key):
        # self.steam_account_id = steam_account_id
        self.steam_id = steam_id
        self.steam_api_key = steam_api_key
        self.session = requests.Session()

    def get_api_url(self, interface, method, version='1', appid='', key=None, userid=None, format='json',
                    **kwargs) -> str:
        if key is None:
            key = self.steam_api_key
        if userid is None:
            userid = self.steam_id
        return self.API_URL.format(interface=interface, method=method, version=version, appid=appid, key=key,
                                   userid=userid, format=format) + ''.join([f'&{k}={v}' for k, v in kwargs.items()])

    def get_owned_games(self) -> OwnedGamesInfo | None:
        url = self.get_api_url(interface="IPlayerService", method="GetOwnedGames", include_played_free_games=True,
                               include_appinfo=True, include_extended_appinfo=True)
        response = self.session.get(url, headers=self.HEADERS)
        if response.status_code == 200:
            data = response.json()
            return data.get('response', {})

    def get_achievements(self, appid) -> GameAchievementInfo | None:
        url = self.get_api_url(interface="ISteamUserStats", method="GetPlayerAchievements", appid=appid)
        response = self.session.get(url, headers=self.HEADERS)
        if response.status_code == 200:
            data = response.json()
            return data.get('playerstats', {})
        else:
            return {}

    def count_achievements(self, appid) -> tuple[int, int]:
        achievements = self.get_achievements(appid).get('achievements', [])
        achieved = sum([achievement['achieved'] for achievement in achievements])
        return achieved, len(achievements)

    def get_game_details(self, appid) -> GameDetails | None:
        url = f"https://store.steampowered.com/api/appdetails/?appids={appid}&language=zh-CN&cc=CN"
        response = self.session.get(url, headers=self.HEADERS)
        if response.status_code == 200:
            data = response.json()
            return data.get(str(appid), {}).get('data', None)


if __name__ == '__main__':
    steam_data = SteamApi(STEAM_ACCOUNT_ID, STEAM_ID, STEAM_API_KEY)
    # data = steam_data.get_api_url(interface="IPlayerService", method="GetOwnedGames")
    # data = steam_data.get_achievements('233450')
    data = steam_data.get_game_details('233450')
    data = steam_data.get_owned_games()
    print(data)
