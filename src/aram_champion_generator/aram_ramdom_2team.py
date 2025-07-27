import requests
import random
import base64
import io
import os
import time
from weasyprint import HTML, CSS
from pdf2image import convert_from_bytes
from pathlib import Path
import sys

# ==== CONSTANTS ====
CSS_MINIFIED = f"""
@font-face {{
    font-family: 'Open Sans';
    src: url('../assets/Open_Sans/OpenSans-Regular.ttf') format('truetype');
    font-weight: 400;
    font-style: normal;
}}
@font-face {{
    font-family: 'Open Sans';
    src: url('../assets/Open_Sans/OpenSans-Bold.ttf') format('truetype');
    font-weight: 700;
    font-style: normal;
}}
body{{background:#1f2836;color:#ecf0f1;font-family:'Open Sans',sans-serif;justify-content:center;padding:20px}}.container{{display:flex;gap:40px}}.team-container{{display:flex;flex-direction:row;justify-content:space-around}}.team-box{{background-color:#374050;border-radius:4px;padding:1.25rem;width:100%;margin:0.5rem;padding-top:1rem;max-width:696px}}.team-title{{font-size:1.25rem;text-align:center;margin-bottom:1.25rem;margin-top:.5rem;font-family:'Open Sans',sans-serif;font-weight:700}}.team-list{{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;padding-inline-start:0}}.team-member{{display:flex;align-items:center}}.team-img{{width:4rem;height:4rem;margin-right:.75rem}}button{{display:block;margin:20px auto;padding:10px 20px;font-size:16px;background-color:#1abc9c;border:none;border-radius:5px;color:white;cursor:pointer}}
"""
CSS_PDF = CSS(string="""
@page {
    size: 1560px 550px;
    margin: 0;
}
""")
IMG_WIDTH = 1560
IMG_HEIGHT = 550

# ==== CACHE SETUP ====
_version_cache = None
_version_cache_time = 0
_champions_cache = {}
_champions_cache_time = {}
_tag_champion_cache = {} 
_tag_champion_cache_time = {} 

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

def pick_team_with_tags(tag_map, used_champions, team_size):
    """Chọn mỗi tag 1 tướng cho mỗi đội, trả về (blue_team, red_team, used_champions)"""
    import random
    blue_team = []
    red_team = []
    for tag in tag_map:
        tag_champs = [c for c in tag_map[tag] if c['id'] not in used_champions]
        if len(tag_champs) < 2:
            # Nếu chỉ còn 1 tướng cho tag này, chia cho 1 đội, đội còn lại sẽ random sau
            chosen = random.sample(tag_champs, 1)
            if len(blue_team) <= len(red_team):
                blue_team.extend(chosen)
            else:
                red_team.extend(chosen)
            used_champions.update(c['id'] for c in chosen)
        else:
            chosen = random.sample(tag_champs, 2)
            blue_team.append(chosen[0])
            red_team.append(chosen[1])
            used_champions.add(chosen[0]['id'])
            used_champions.add(chosen[1]['id'])
    return blue_team, red_team, used_champions

def pick_remaining_team_members(champions, used_champions, blue_team, red_team, team_size):
    import random
    remain_pool = [c for c in champions if c['id'] not in used_champions]
    need_blue = team_size - len(blue_team)
    need_red = team_size - len(red_team)
    if need_blue > 0:
        blue_team.extend(random.sample(remain_pool, need_blue))
        used_champions.update(c['id'] for c in blue_team)
        remain_pool = [c for c in remain_pool if c['id'] not in used_champions]
    if need_red > 0:
        red_team.extend(random.sample(remain_pool, need_red))
    return blue_team, red_team

def pick_random(arr, count):
    return random.sample(arr, count)

def generate_image(cache_expire=60*60*6):  # 6h = 21600s
    # Fetch the latest version and champions data
    version = fetch_latest_version(cache_expire=cache_expire)
    champions = fetch_champions(version, cache_expire=cache_expire)
    tag_map = get_tag_map(version, cache_expire)
    team_size = 15
    used_champions = set()
    blue_team, red_team, used_champions = pick_team_with_tags(tag_map, used_champions, team_size)
    blue_team, red_team = pick_remaining_team_members(champions, used_champions, blue_team, red_team, team_size)
    # Đảm bảo không trùng tướng giữa 2 đội
    assert len(set(c['id'] for c in blue_team).intersection(c['id'] for c in red_team)) == 0

    # HTML content with the teams and their champions
    html_content = f"""
    <html>
    <head>
        <meta charset='utf-8'>
        <style>
            {CSS_MINIFIED}
        </style>
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

    # Convert HTML to PDF using WeasyPrint
    html = HTML(string=html_content)
    pdf_bytes = html.write_pdf(stylesheets=[CSS_PDF])

    # Create poppler_path from project root using sys.path[0]
    root = Path(sys.path[0])
    poppler_path = root / "library" / "poppler-24.08.0" / "Library" / "bin"

    # Convert the PDF to images (PNG format)
    images = convert_from_bytes(
        pdf_bytes, dpi=200, poppler_path=str(poppler_path)
    )  # Optional: adjust DPI for better quality

    # Resize the first page image to 1560x550
    image = images[0]
    image = image.resize((IMG_WIDTH, IMG_HEIGHT))

    # Convert the resized image to a PNG and save it to BytesIO
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    # Convert the PNG image to Base64
    base64_image = base64.b64encode(image_bytes.read()).decode('utf-8')

    # Create the Data URL for the image
    data_url = f"data:image/png;base64,{base64_image}"

    # Return the data URL
    return data_url
