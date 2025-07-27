import requests
import random
import base64
import os
import time
from pathlib import Path
from html2image import Html2Image

# ==== CONSTANTS ====
MAX_TEAM_SIZE = 15
TAG_LIMITS = {
    "Assassin": [1, 3],
    "Marksman": [2, 4],
}

IMG_WIDTH = 1560
IMG_HEIGHT = 600

# ==== CACHE SETUP ====
_version_cache = None
_version_cache_time = 0
_champions_cache = {}
_champions_cache_time = {}
_tag_champion_cache = {} 
_tag_champion_cache_time = {} 

# Cache các tướng vừa random ở lần trước
# Cache riêng biệt cho từng đội
_last_blue_team_ids = set()
_last_red_team_ids = set()

# Biến cache expire dùng chung toàn project
CACHE_EXPIRE_SECONDS = 60*60*6  # 6 giờ

# Fetch the latest version from the League of Legends API, with cache
def fetch_latest_version(cache_expire=3600):
    global _version_cache, _version_cache_time
    now = time.time()
    if _version_cache and (now - _version_cache_time < cache_expire):
        return _version_cache
    response = requests.get(
        'https://ddragon.leagueoflegends.com/api/versions.json')
    _version_cache = response.json()[0]
    _version_cache_time = now
    return _version_cache

# Fetch champions from a specific version, with cache
def fetch_champions(version, cache_expire=3600):
    global _champions_cache, _champions_cache_time
    now = time.time()
    if (version in _champions_cache and
        (now - _champions_cache_time.get(version, 0) < cache_expire)):
        return _champions_cache[version]
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/vi_VN/champion.json"
    response = requests.get(url)
    data = response.json()
    champions = list(data['data'].values())
    _champions_cache[version] = champions
    _champions_cache_time[version] = now
    return champions

def build_tag_map(champions, version, cache_expire=3600):
    global _tag_champion_cache, _tag_champion_cache_time
    now = time.time()
    tag_map = {}
    for champ in champions:
        for tag in champ.get('tags', []):
            tag_map.setdefault(tag, []).append(champ)
    _tag_champion_cache[(version, cache_expire)] = tag_map
    _tag_champion_cache_time[(version, cache_expire)] = now
    return tag_map

def get_tag_map(version, cache_expire=3600):
    now = time.time()
    if ((version, cache_expire) in _tag_champion_cache and
        (now - _tag_champion_cache_time.get((version, cache_expire), 0) < cache_expire)):
        return _tag_champion_cache[(version, cache_expire)]
    champions = fetch_champions(version, cache_expire)
    return build_tag_map(champions, version, cache_expire)

def pick_team_with_tags(tag_map, used_champions, team_size, exclude_blue_ids=None, exclude_red_ids=None):
    if exclude_blue_ids is None:
        exclude_blue_ids = set()
    if exclude_red_ids is None:
        exclude_red_ids = set()
  
    blue_team = []
    red_team = []
    blue_tag_count = {}
    red_tag_count = {}
    used_ids = set(used_champions)

    # Step 1: Handle tags not in TAG_LIMITS (must have at least 1 per team if available)
    for tag, champs in tag_map.items():
        if tag in TAG_LIMITS:
            continue  # will handle separately

        available_champs = [c for c in champs if c['id'] not in used_ids]
        if len(available_champs) < 2:
            continue
        
        # Remove each from each team
        blue_candidates = [c for c in available_champs if c['id'] not in exclude_blue_ids]
        red_candidates = [c for c in available_champs if c['id'] not in exclude_red_ids and c['id'] not in (blue_candidates[0]['id'] if blue_candidates else set())]
        if not blue_candidates or not red_candidates:
            continue
        blue_pick = random.choice(blue_candidates)
        # Ensure not duplicate with blue_pick
        red_candidates = [c for c in red_candidates if c['id'] != blue_pick['id']]
        if not red_candidates:
            continue
        red_pick = random.choice(red_candidates)
        blue_team.append(blue_pick)
        red_team.append(red_pick)
        used_ids.add(blue_pick['id'])
        used_ids.add(red_pick['id'])
        for t in blue_pick.get('tags', []):
            blue_tag_count[t] = blue_tag_count.get(t, 0) + 1
        for t in red_pick.get('tags', []):
            red_tag_count[t] = red_tag_count.get(t, 0) + 1

    # Step 2: Handle tags in TAG_LIMITS (apply min if > 0, and max if != 0)
    for tag, (min_limit, max_limit) in TAG_LIMITS.items():
        if max_limit == 0:
            continue  # tag is banned entirely

        available_champs = [c for c in tag_map.get(tag, []) if c['id'] not in used_ids]
        if min_limit == 0:
            continue  # not required to have from the start, only handle if slots remain in next step

        if len(available_champs) < 2 * min_limit:
            continue  # not enough to split evenly

        # Remove each from each team
        blue_candidates = [c for c in available_champs if c['id'] not in exclude_blue_ids]
        red_candidates = [c for c in available_champs if c['id'] not in exclude_red_ids]
        if len(blue_candidates) < min_limit or len(red_candidates) < min_limit:
            continue
        blue_picks = random.sample(blue_candidates, min_limit)
        red_picks = random.sample(red_candidates, min_limit)
        for champ in blue_picks:
            if len(blue_team) < team_size:
                blue_team.append(champ)
                used_ids.add(champ['id'])
                for t in champ.get('tags', []):
                    blue_tag_count[t] = blue_tag_count.get(t, 0) + 1
        for champ in red_picks:
            if len(red_team) < team_size:
                red_team.append(champ)
                used_ids.add(champ['id'])
                for t in champ.get('tags', []):
                    red_tag_count[t] = red_tag_count.get(t, 0) + 1

    # Step 3: Distribute remaining champions into teams, respecting TAG_LIMITS max
    all_champ_ids = set()
    champ_id_to_obj = {}
    for champs in tag_map.values():
        for c in champs:
            all_champ_ids.add(c['id'])
            champ_id_to_obj[c['id']] = c

    remain_ids = [cid for cid in all_champ_ids if cid not in used_ids]
    random.shuffle(remain_ids)
    remain_pool = [champ_id_to_obj[cid] for cid in remain_ids]

    while remain_pool and (len(blue_team) < team_size or len(red_team) < team_size):
        champ = remain_pool.pop()
        tags = champ.get('tags', [])

        can_add_blue = len(blue_team) < team_size and champ['id'] not in exclude_blue_ids
        can_add_red = len(red_team) < team_size and champ['id'] not in exclude_red_ids

        for tag in tags:
            if tag in TAG_LIMITS:
                min_limit, max_limit = TAG_LIMITS[tag]
                if max_limit == 0:
                    can_add_blue = False
                    can_add_red = False
                if blue_tag_count.get(tag, 0) >= max_limit:
                    can_add_blue = False
                if red_tag_count.get(tag, 0) >= max_limit:
                    can_add_red = False

        if can_add_blue and len(blue_team) <= len(red_team):
            blue_team.append(champ)
            used_ids.add(champ['id'])
            for tag in tags:
                blue_tag_count[tag] = blue_tag_count.get(tag, 0) + 1
        elif can_add_red:
            red_team.append(champ)
            used_ids.add(champ['id'])
            for tag in tags:
                red_tag_count[tag] = red_tag_count.get(tag, 0) + 1

    return blue_team, red_team, used_ids


def generate_image(cache_expire=CACHE_EXPIRE_SECONDS):
    global _last_blue_team_ids, _last_red_team_ids
    # Fetch the latest version and champions data
    version = fetch_latest_version(cache_expire=cache_expire)
    champions = fetch_champions(version, cache_expire=cache_expire)
    tag_map = get_tag_map(version, cache_expire)
    team_size = MAX_TEAM_SIZE
    # Separate each team individually
    used_champions = set()
    blue_team, red_team, used_champions = pick_team_with_tags(
        tag_map, used_champions, team_size,
        exclude_blue_ids=_last_blue_team_ids,
        exclude_red_ids=_last_red_team_ids
    )
    # Ensure no duplicate champions between 2 teams
    assert len(set(c['id'] for c in blue_team).intersection(c['id'] for c in red_team)) == 0

    # Update cache for the next random
    _last_blue_team_ids = set(c['id'] for c in blue_team)
    _last_red_team_ids = set(c['id'] for c in red_team)

    # Read CSS content from file with absolute path
    current_dir = Path(__file__).parent.resolve()
    css_file_path = current_dir / 'css' / 'aram-style.css'
   
    # HTML content with the teams and their champions
    html_content = f"""
    <html>
    <head>
        <meta charset='utf-8'>
        <link rel="stylesheet" href="{css_file_path}">
    </head>
    <body>
      <div class="team-container">
        <div class="team-box">
            <h2 class="team-title">Blue Team</h2>
            <ul class="team-list">
                {''.join([f'<li class="team-member"><img class="team-img" src="https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{c["image"]["full"]}" /> {c["name"]}</li>' for c in blue_team])}
            </ul>
        </div>
        <div class="team-box">
            <h2 class="team-title">Red Team</h2>
            <ul class="team-list">
                {''.join([f'<li class="team-member"><img class="team-img" src="https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{c["image"]["full"]}" /> {c["name"]}</li>' for c in red_team])}
            </ul>
        </div>
      </div>
    </body>
    </html>
    """

    # Use html2image to render HTML to PNG
    hti = Html2Image(output_path='.')
    output_filename = 'aram_teams.png'
    hti.screenshot(
        html_str=html_content,
        save_as=output_filename,
        size=(IMG_WIDTH, IMG_HEIGHT)
    )

    # Read the newly created image file and encode base64
    with open(output_filename, 'rb') as img_file:
        base64_image = base64.b64encode(img_file.read()).decode('utf-8')

    # Delete temp image file if desired (optional)
    try:
        os.remove(output_filename)
    except Exception:
        pass

    # Create the Data URL for the image
    data_url = f"data:image/png;base64,{base64_image}"

    # Return the data URL
    return data_url
