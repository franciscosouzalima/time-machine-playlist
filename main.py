import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# SPOTIFY INFORMATION
CLIENT_ID = 'YOUR_ID'
CLIENT_SECRET = 'YOUR_SECRET'
REDIRECT_URI = 'http://example.com'

def get_songs(date):
    response = requests.get(f"https://www.billboard.com/charts/hot-100/{date}/")
    web_page = response.text

    soup = BeautifulSoup(web_page, "html.parser")

    title_elements = soup.select(selector='li ul li h3')
    titles = [title_element.getText().replace("\n", "") for title_element in title_elements][:100]

    singer_elements = soup.select(selector="li ul li span")
    singers_raw = [singer_element.getText() for singer_element in singer_elements]
    singers = []
    for i in range(0, len(singers_raw), 7):
        singers.append(singers_raw[i].replace("\n", ""))

    return titles, singers

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri=REDIRECT_URI,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt"
    )
)

user_id = sp.current_user()["id"]
print("🔌 :: Conectado! User ID: ", user_id)

print("\nVamos criar uma lista com as 100 top músicas da Billboard para uma data no passado.")

date = input("\n📆 :: Informe uma data no formato 'YYYY-MM-DD': ")
year = date.split('-')[0]

titles, artists = get_songs(date)

songs_list = []
for i, song in enumerate(titles):
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]

    except IndexError:
        continue
    else:
        songs_list.append(uri)

playlist = sp.user_playlist_create(user=user_id, name=f"{date} - top 100", public=False)

sp.playlist_add_items(playlist_id=playlist["id"], items=songs_list)

print(f"""
🎵 :: PLAYLIST :: 🎵
Nome: {playlist["name"]}
Total de Músicas: {len(songs_list)}
Acesse em: {playlist["external_urls"]["spotify"]}
""")
