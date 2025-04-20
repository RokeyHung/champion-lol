import requests
import random
import base64
import io
from weasyprint import HTML, CSS
from pdf2image import convert_from_bytes


# Fetch the latest version from the League of Legends API
def fetch_latest_version():
    response = requests.get(
        'https://ddragon.leagueoflegends.com/api/versions.json')
    return response.json()[0]


# Fetch champions from a specific version
def fetch_champions(version):
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/vi_VN/champion.json"
    response = requests.get(url)
    data = response.json()
    return list(data['data'].values())


# Pick a random selection of champions
def pick_random(arr, count):
    return random.sample(arr, count)


# Generate the image and convert it to base64
async def generate_image():
    # Fetch the latest version and champions data
    version = fetch_latest_version()
    champions = fetch_champions(version)

    # Split the champions into two teams
    all_champions = champions[:]
    blue_team = pick_random(all_champions, 15)
    red_team = pick_random([c for c in all_champions if c not in blue_team],
                           15)

    # Minified CSS for styling the HTML content
    css = """
    body{background:#1f2836;color:#ecf0f1;font-family:sans-serif;justify-content:center;padding:20px}.container{display:flex;gap:40px}.team-container{display:flex;flex-direction:row;justify-content:space-around}.team-box{background-color:#374050;border-radius:4px;padding:1.25rem;width:100%;margin:0.5rem;padding-top:1rem;max-width:696px}.team-title{font-size:1.25rem;text-align:center;margin-bottom:1.25rem;margin-top:.5rem}.team-list{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;padding-inline-start:0}.team-member{display:flex;align-items:center}.team-img{width:4rem;height:4rem;margin-right:.75rem}button{display:block;margin:20px auto;padding:10px 20px;font-size:16px;background-color:#1abc9c;border:none;border-radius:5px;color:white;cursor:pointer}
    """

    # HTML content with the teams and their champions
    html_content = f"""
    <html>
    <head>
        <style>
            {css}
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

    # CSS for PDF rendering
    cssPdf = CSS(string="""
    @page {
        size: 1560px 550px;
        margin: 0;
    }
    """)

    # Convert HTML to PDF using WeasyPrint
    html = HTML(string=html_content)
    pdf_bytes = html.write_pdf(
        stylesheets=[cssPdf])  # Pass the CSS as a string to stylesheets

    # Convert the PDF to images (PNG format)
    images = convert_from_bytes(
        pdf_bytes, dpi=200, poppler_path=r"D:\GitClone\poppler-24.08.0\Library\bin"
    )  # Optional: adjust DPI for better quality

    # Resize the first page image to 1560x550
    image = images[0]
    image = image.resize((1560, 550))  # Resize to the target dimensions

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
