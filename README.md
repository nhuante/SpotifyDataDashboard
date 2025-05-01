# SpotifyDataDashboard
Deploys a website which displays a dashboard filled with stats from my personal Spotify listening history. 


Think of this project as my own personal version of Spotify Wrapped, except I get to see my monthly progress and customize which stats I want to see. The website automatically updates as well, so I simply have to look up the website to see my (mostly) updated spotify data. 


# My Spotify Data Dashboard

My personal Shiny dashboard built in Python to visualize my own Spotify listening habits using IFTTT-exported data. IFTTT allows me to automatically log every song I listen to on my Spotify account in a google spreadsheet. The dashboard fetches my song history from these sheets, displays top artists, songs, listening trends, and album covers, and uses local caching to make album data available without live API calls.

Think of this project as my own personal version of Spotify Wrapped, except it is year-round! I get to see my monthly progress and customize which stats I want to see. Visit the site now to see my music stats in real-time! (except for the top albums those are cached once a week).

As a note: This documentation is meant both for an external audience and to keep track of important important for myself as I continue to implement new features here and there. Hence, why I include instructions about running locally and deployig (although you could fork and update this to use your own listening history!)

## Author

Built with lurv by **@natalie** - designed to bring my (and maybe your) listening habits to life. Also, I am a data nerd, so I love to see my stats in just about anything. 



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

## Deploying

1. Log in to shinyapps.io (You'll need your own account if you've forked). You will prompted for your account name, token, and secret. Get these from shinyapps.io -> account -> tokens. Note that if this errors in shell, try running all on a single line with the \ characters.
```bash
rsconnect add --name shinyapps \
              --server shinyapps.io \
              --account YOUR_ACCOUNT_NAME \
              --token YOUR_TOKEN \
              --secret YOUR_SECRET
```
2. Deploy! Replace --app-name with the actual name of your app. This command will package all the files, install any dependencies, upload, and launch your app on shinyapps.io. 
```bash
rsconnect deploy shiny --app-name your-app-name app:app
```
3. To redeploy later (after pushing updates)
```bash
rsconnect deploy shiny . --name account-name --title my-music-dashboard
```
---

### How To Automate the Top Albums Caching:


## A Note on Credentials / How Shiny Deploys

You do not need to push credential files to the repo. In fact, you really shouldn't share that with the public! Keep it locally. When you deploy, shiny will package up your app (including the credentials file you have stored locally), send it to shinyapp.io, and that is what runs the app. 

So, you only need it present locally when you deploy. Visitors to the site don't need it when they hit reload since the deplyoed app is already authenticated. 


### Thing To Add List
* Automate updates to `cached_top_albums.json`
* Add a "Last Updated" timestamp for the albums