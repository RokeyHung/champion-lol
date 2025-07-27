from src.aram_champion_generator import aram_ramdom_2team as aram
import time

def get_cache_stats(cache_expire=None):
    if cache_expire is None:
        cache_expire = aram.CACHE_EXPIRE_SECONDS
    version = aram._version_cache
    champion_count = len(aram._champions_cache.get(version, []))
    tag_map = aram._tag_champion_cache.get((version, cache_expire), {})
    tag_count = len(tag_map)
    cache_time = aram._champions_cache_time.get(version, 0)
    return {
        'version': version,
        'champion_count': champion_count,
        'tag_count': tag_count,
        'cache_time': cache_time
    }

def get_cache_stats_more(cache_expire=None):
    if cache_expire is None:
        cache_expire = aram.CACHE_EXPIRE_SECONDS
    version = aram._version_cache
    champion_count = len(aram._champions_cache.get(version, []))
    tag_map = aram._tag_champion_cache.get((version, cache_expire), {})
    tag_count = len(tag_map)
    tag_list = list(tag_map.keys())
    cache_time = aram._champions_cache_time.get(version, 0)
    now = time.time()
    cache_age_hours = (now - cache_time) / 3600 if cache_time else None
    api_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/vi_VN/champion.json" if version else None
    return {
        'version': version,
        'api_url': api_url,
        'champion_count': champion_count,
        'tag_count': tag_count,
        'tag_list': tag_list,
        'cache_time': cache_time,
        'cache_age_hours': cache_age_hours,
        'cache_expire': cache_expire
    } 