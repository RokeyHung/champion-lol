from src.aram_champion_generator import aram_ramdom_2team as aram

def get_cache_stats(cache_expire=60*60*6):
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