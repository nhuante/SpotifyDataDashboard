# import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import time
import os

''' THIS FILE WILL BE RAN LOCALLY AT A SCHEDULED TIME TO UPDATE THE CACHED TOP ALBUMS. 
    WHEN ANYONE ACCESSES THE DEPLOYED SITE, IT SHOULD REFERENCE THESE CACHED VALUES TO 
    DISPLAY ON THE SITE. OTHERWISE, WE WILL HAVE ISSUES WITH THE SPOTIFY API KEY (IT 
    LOOKS AT YOUR REDIRECT URL SO IT MATTERS WHERE THE REQUEST IS COMING FROM - HENCE WHY 
    IT NEEDS TO HAPPEN LOCALLY ON MY COMPUTER)'''

''' EDIT: AS OF 5/1/25
    THIS FILE WILL BE EXECUTED ON AN AUTOMATED SCHEDULE USING GITHUB ACTIONS
    MY CREDENTIALS ARE STORED AS GITHUB SECRETS, SO EVERY X NUMBER OF DAYS, THIS 
    SCHEDULE WILL 1. CACHE UPDATES 2. GIT PUSH 3. SHINY REDEPLOYEMENT'''

# === config stuff ===
# for cached top albums 
YEAR = 2025
OUTPUT_FILE = "..\data\cached_top_albums.json"
SERVICE_ACCOUNT_FILE = "..\data\service-account-key.json"
SHEET_QUERY = "Test_SpotifyData"  # Matches name of all IFTTT sheets

# get client id and secret from secret file 
# secret_file = open("my_spotify_credentials.txt", "r")
# secret_file_rows = secret_file.readlines()

# my spotify api keys
SPOTIPY_CLIENT_ID = os.environ["SPOTIPY_CLIENT_ID"]
SPOTIPY_CLIENT_SECRET = os.environ["SPOTIPY_CLIENT_SECRET"]
SPOTIPY_REDIRECT_URI = os.environ["SPOTIPY_REDIRECT_URI"]
# scope = "user-top-read"



# load all of the ifttt logged spotify sheet from my google drive (uses a service account with view permissions 
# to access instead of my own google account)
def load_spotify_data_from_google() -> pd.DataFrame:
    # what are we accessing in google cloud (drive and spreadsheets)
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 
              'https://www.googleapis.com/auth/drive.readonly']
    # get google credentials from our friendly service account JSON file in the data folder
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, 
                                                  scopes=SCOPES)
    
    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)
    
    # find all the IFTTT-exported sheets 
    query = f"name contains '{SHEET_QUERY}' and mimeType='application/vnd.google-apps.spreadsheet'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    
    # start out pandas data frame
    all_data = pd.DataFrame()
    # load our data frame with the info from the sheets we pulled 
    for file in files:
        # get the current sheet's values 
        sheet_id = file['id']
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range="A:E"
        ).execute()
        rows = result.get('values', [])
        if not rows: # if no data, skip obv, no need to try to process
            continue
        
        # if it contains a header row, ignore the first row or it will mess with our formatting 
        if rows[0][0].lower() == 'time':
            rows = rows[1:]
        
        # concat to the data frame current sheet's values 
        df = pd.DataFrame(rows, columns=['time', 'song', 'artist', 'track_id', 'spotify_link'])
        all_data = pd.concat([all_data, df], ignore_index=True)
    
    # reformat the timestamps of the time column and add some columns
    all_data['time'] = pd.to_datetime(all_data['time'].str.replace(' at ', ' '), format='%B %d, %Y %I:%M%p')
    all_data['duration_min'] = 3.5
    all_data['year'] = all_data['time'].dt.year
    all_data['month'] = all_data['time'].dt.month
    return all_data

# my personal spotify authentication (why this needs to happen locally bro)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="user-read-private", 
    open_browser=False, 
    show_dialog=False, 
    cache_path=".cache"
))

# gets the album info using the spotify api
def get_album_info(song, artist):
    query = f"{song} artist:{artist}"
    try:
        results = sp.search(q=query, type='track', limit=1)
        items = results.get('tracks', {}).get('items', [])
        if not items:
            return None
        album = items[0]['album']
        return {
            'album_name': album['name'],
            'album_image': album['images'][0]['url'],
            'album_url': album['external_urls']['spotify']
        }
    except Exception as e:
        print(f"Error for {song} - {artist}: {e}")
        return None




# main 
# loads and processes my listening data using above functions
df = load_spotify_data_from_google()
# df['time'] = pd.to_datetime(df['time'].str.replace(' at ', ' '))
# df['year'] = df['time'].dt.year
# df['month'] = df['time'].dt.month
df = df[df['year'] == YEAR]

# get the top 100 songs by frequency of being listened to by me 
top_songs = df.groupby(['song', 'artist']).size().reset_index(name='count').sort_values('count', ascending=False).head(100)


album_counter = {}
album_info_map = {}

# for each top song, pull info from spotify API and tally how many times each album is seen 
for _, row in top_songs.iterrows():
    song = row['song']
    artist = row['artist']
    info = get_album_info(song, artist)
    if info:
        name = info['album_name']
        album_counter[name] = album_counter.get(name, 0) + 1
        album_info_map[name] = info
        time.sleep(0.1)

# grab the 6 albums with the most counts 
top_albums = sorted(album_counter.items(), key=lambda x: -x[1])[:6]
final = [album_info_map[name] for name, _ in top_albums]

# === write this info to the top albums cache ===
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, 'w') as f:
    json.dump(final, f, indent=2)

print(f"✅ Cached top albums saved to {OUTPUT_FILE}")
