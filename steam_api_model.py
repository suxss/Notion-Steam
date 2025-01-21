from typing import TypedDict


class GameInfo(TypedDict):
    appid: int
    name: str
    playtime_forever: int
    img_icon_url: str
    has_community_visible_stats: bool
    playtime_windows_forever: int
    playtime_mac_forever: int
    playtime_linux_forever: int
    playtime_deck_forever: int
    rtime_last_played: int
    capsule_filename: str
    has_workshop: bool
    has_market: bool
    has_dlc: bool
    content_description: list[int]
    playtime_disconnected: int


class OwnedGamesInfo(TypedDict):
    game_count: int
    games: list[GameInfo]


class AchievementInfo(TypedDict):
    apiname: str
    achieved: int
    unlocktime: int


class GameAchievementInfo(TypedDict):
    steamID: str
    gameName: str
    achievements: list[AchievementInfo]


class RequirementsInfo(TypedDict):
    minimum: str


class PriceInfo(TypedDict):
    currency: str
    initial: int
    final: int
    discount_percent: float
    initial_formatted: str
    final_formatted: str


class SupportPlatformInfo(TypedDict):
    windows: bool
    mac: bool
    linux: bool


class CatagoryInfo(TypedDict):
    id: int | str
    description: str


class ScreenshotsInfo(TypedDict):
    id: int
    path_thumbnail: str
    path_full: str


class GameMovieInfo(TypedDict):
    id: int
    name: str
    thumbnail: str
    webm: dict  # '480': url_str, 'max': url_str
    mp4: dict
    highlight: bool


class AchievementDetails(TypedDict):
    total: int
    highlighted: list[dict[str, str]]  # 'name': name_str, 'path': url_str


class GameDetails(TypedDict):
    type: str
    name: str
    steam_appid: int
    required_age: str
    is_free: bool
    dlc: list[int]
    detailed_description: str
    about_the_game: str
    short_description: str
    support_language: str
    reviews: str
    header_image: str
    capsule_image: str
    capsule_imagev5: str
    website: str
    pc_requirements: RequirementsInfo
    mac_requirements: RequirementsInfo
    linux_requirements: RequirementsInfo
    legal_notice: str
    developers: list[str]
    publishers: list[str]
    price_overview: PriceInfo
    packages: list[int]
    platforms: list[SupportPlatformInfo]
    categories: list[CatagoryInfo]
    genres: list[CatagoryInfo]
    screenshots: list[ScreenshotsInfo]
    movies: list[GameMovieInfo]
    recommendations: dict[str, int]  # 'total': int
    achievements: AchievementDetails
    release_date: dict  # 'coming_soon': bool, 'date': str
    background: str
    background_raw: str
