# SpotifyDataDashboard
Deploys a website which displays a dashboard filled with stats from my personal Spotify listening history. 


Think of this project as my own personal version of Spotify Wrapped, except I get to see my monthly progress and customize which stats I want to see. The website automatically updates as well, so I simply have to look up the website to see my (mostly) updated spotify data. 


# My Spotify Data Dashboard

My personal Shiny dashboard built in Python to visualize my own Spotify listening habits using IFTTT-exported data. IFTTT allows me to automatically log every song I listen to on my Spotify account in a google spreadsheet. The dashboard fetches my song history from these sheets, displays top artists, songs, listening trends, and album covers, and uses local caching to make album data available without live API calls.

Think of this project as my own personal version of Spotify Wrapped, except it is year-round! I get to see my monthly progress and customize which stats I want to see. Visit the site now to see my music stats in real-time! (except for the top albums those are cached once a week).


---

## Tech Stack

### Frontend / Dashboard
- [**Shiny for Python**](https://shiny.posit.co/py/) — for interactive dashboard UI and logic
- [Matplotlib](https://matplotlib.org/) — for plotting graphs
- HTML/CSS (via `ui.HTML`) — for customized visuals

### Backend / Data
- [IFTTT](https://ifttt.com/) Spotify logging applet — logs listening events to Google Sheets
- [Google Sheets API](https://developers.google.com/sheets/api) — for reading multiple data sheets
- [Spotipy (Spotify API wrapper)](https://spotipy.readthedocs.io/) — for album metadata (one-time fetch only)
- [gspread](https://docs.gspread.org/) and [google-auth](https://google-auth.readthedocs.io/) — to access Sheets using a service account

---

## Deployment Overview

The app is deployed to [shinyapps.io](https://www.shinyapps.io/) using the `rsconnect-python` CLI. This allows anyone to visit my site and...
- View and interact with all charts
- Click the "Reload Data" button to pull the latest IFTTT logs from my drive 

The app does **not require any OAuth** or user login because:
- Data is pulled from a **Google Sheet shared with a service account**. Image I have a guest account that can view my logged spreadsheets and every time someone visits my site, they are "borrowing" that guest account to take a peek at my most current logs. This is much better than me giving everyong MY own personal login info. 
- **Top Albums data is cached** into `data/cached_top_albums.json` using a separate script and this is ran locally on my computer (on a schedule). 

---

## Repository Structure

```bash
.
├── app.py                      # Main Shiny app
├── requirements.txt            # Python dependencies
├── .gitignore                  # Sensitive files ignored
├── V01                         # Sensitive files ignored
│   └── main_V01.py             # My very first iteration of this project 
├── data/
│   └── cached_top_albums.json  # Locally cached top album info
│   └── album_cache.json        # Locally cached general album info (to lessen the number of API calls used every reload)
├── scheduled_runs    
│   └── generate_album_cache.py # Script to update album cache via Spotify API
```

---

## How Caching Works

Album info (cover art, name, and link) is fetched from Spotify **once** via `generate_album_cache.py`. It pulls the top 100 tracks, determines the top 6 albums, and saves this to `data/cached_top_albums.json`.

The main Shiny app then reads from this file instead of calling Spotify live. This allows **public users** to load the dashboard without needing Spotify login.

---

## API Keys & Services Used

| Service       | Use Case                 | Auth Type           |
|---------------|--------------------------|---------------------|
| Google Sheets | Load IFTTT listening logs| Service Account     |
| Spotify API   | Fetch album metadata     | OAuth (Spotipy)     |

- My Spotify Client ID and Secret are used **only locally** during cache generation. 
- Google Sheets is accessed using a `service_account_credentials.json` file **shared with the sheet**.

---

## Running Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. (One-time) Generate album cache:
```bash
python generate_album_cache.py
```

3. Run the Shiny app:
```bash
shiny run app:app
```

Make sure your `data\cached_top_albums.json` exists before launching.

---

## Fork & Modify

Want to customize it with your own data?

### To use your own Spotify IFTTT logs:
1. Set up [IFTTT](https://ifttt.com/) to log Spotify plays to Google Sheets. 
2. Share the Sheet(s) with your own service account. You should do this by creating a new project in google cloud. 
3. Replace `service_account_credentials.json` with your own service account details.
4. Create a file `my_spotify_credentials.txt` in the scheduled_runs folder and place only two lines of text in there. The first is your Spotify API client ID and the second your Client Secret. You can sign up for a [Spotify Developer Account](https://developer.spotify.com/) and get these values here. 
5. Run `generate_album_cache.py` to fetch top albums and cache them locally. If you would like to automate this process, keep reading below. 
6. Deploy!

If you are familiar with programming, you can also:
- Modify the chart styles
- Add more stats (e.g. top genres, listening streaks)
- Integrate with other data sources 

---

### How To Automate the Top Albums Caching:

## Author

Built with lurv by **@natalie** - designed to bring my (and maybe your) listening habits to life. Also, I am a data nerd, so I love to see my stats in just about anything. 

