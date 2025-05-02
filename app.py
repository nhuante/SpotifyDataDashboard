from shiny import App, reactive, render, ui
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.figure import Figure
from googleapiclient.discovery import build
# from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import os.path
# import pickle
# import time 
# import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import os

# Set up Google Sheets API scopes
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = os.path.join("data", "service-account-key.json")

# # Spotify API Keys
# SPOTIPY_CLIENT_ID = "a118665aaffa47508939659b9ecd2227"
# SPOTIPY_CLIENT_SECRET = "4522956332f94a519f7b85edeee44b96"
# SPOTIPY_REDIRECT_URI = "http://127.0.0.1:8000/"



# APP UI DEFINED HERE
app_ui = ui.page_fluid(
    # HTML formatting for entire page applied here 
    ui.HTML("""
    <style>
        /* Import Cantarell font */
        @import url('https://fonts.googleapis.com/css2?family=Cantarell:wght@400;700&display=swap');
        
        /* Apply Cantarell font to everything */
        {
            font-family: 'Cantarell', sans-serif !important;
        }
        
        /* Apply formatting to tables */
        .table th {
            text-align: left !important;
            font-weight: bold;
        }

        /* Add padding to plot containers */
        .card-body:has(.shiny-plot-output) {
            padding-bottom: 20px;
        }
    </style>
    """),

    # emojis and title card
    ui.card(
        ui.card_body(
            ui.HTML("""
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Cantarell:wght@400;700&display=swap');
                    
                    * {
                        font-family: 'Cantarell', sans-serif !important;
                    }

                    .card {
                        border: 0 !important;
                        box-shadow: none !important; 
                    }
                    
                    #custom-title {
                        text-align: center;
                        font-size: 45px;
                        font-weight: bold;
                        color: black;
                        padding-top: 5px;
                        padding-bottom: 5px;
                        margin-bottom: 0;
                    }
                    
                    #emoji-container {
                        text-align: center;
                        font-size: 24px;
                        margin-bottom: 5px;
                        padding: 5px;
                        color: black;
                    }
                    /* Base emoji pattern */
                    #emoji-container:before, #emoji-container:after {
                        content: "♫⋆｡♪ ₊˚♬ ﾟ.♫⋆｡♪ ₊˚♬";
                    }
                    /* Add more emoji at larger screen sizes */
                    @media (min-width: 576px) {
                        #emoji-container:before, #emoji-container:after {
                            content: "♫｡♪ ₊｡♪˚♬ ﾟ.♫⋆｡♪";
                        }
                    }
                    @media (min-width: 768px) {
                        #emoji-container:before, #emoji-container:after {
                            content: "♫⋆｡♪ ₊˚♬ ﾟ.♫♪ .♫⋆｡♪ ₊˚♬ ﾟ.";
                        }
                    }
                    @media (min-width: 992px) {
                        #emoji-container:before, #emoji-container:after {
                            content: "♫⋆｡♪ ₊˚♬ ﾟ.♫⋆｡♪ ₊˚♬ ﾟ.♫⋆｡♪ ₊˚♬ ﾟ.♫⋆｡♪";
                        }
                    }
                    @media (min-width: 1200px) {
                        #emoji-container:before, #emoji-container:after {
                            content: "♫⋆｡♪ ₊˚♬ ﾟ.₊˚♬ ﾟ. ₊₊˚♬ ﾟ.♫⋆｡♪ ˚♬ ﾟ.♫⋆｡♪ ₊˚♬ ﾟ.♫⋆｡♪";
                        }
                    }
                </style>
                <div id="emoji-container">♫⋆｡♪ ₊˚♬ ﾟ.♫</div>
                <div id="custom-title">Nat's Music Dashboard</div>
                <div id="emoji-container">♫⋆｡♪ ₊˚♬ ﾟ.♫</div>
            """),
        class_="border-0 shadow-none bg-light",
        style="""        
            # background-color: #87ae73 !important; 
            box-shadow: none !important; 
            margin-top: 0; 
            margin-bottom: 0;
            padding-top: 0;
            padding-bottom: 0;
            border-radius: 0 !important;
            # -webkit-border-radius: 0 !important;
        """
        )
    ),


    # reload button card
    ui.card(
        ui.card_header("Welcome to Nat's Super Fun Spotify Dashboard!"),
        ui.card_body(
            ui.p("Here you will see some graphics and statistics representing my IFTTT-logged Spotify listening activity. Click on the button below to pull the most recent data."),
            ui.input_action_button("reload_data", "Reload Data", class_="btn-primary"),
            ui.output_text("last_updated")
        )
    ),

    # top albums of the year card
    ui.card(
        ui.card_header("📀 Top Albums of the Year"),
        ui.card_body(
            ui.output_ui("top_albums_ui")
        )
    ),
    
    # top artists and songs (side by side)
    ui.layout_columns(
        ui.card(
            ui.card_header("Top 10 Artists"),
            ui.card_body(ui.output_plot("top_artists"))
        ),
        ui.card(
            ui.card_header("Top 10 Songs"),
            ui.card_body(ui.output_plot("top_songs"))
        ),
        col_widths=[6, 6]
    ),
    
    # recent songs
    ui.card(
        ui.card_header("Songs Last Listened To"),
        ui.card_body(ui.output_table("recent_songs"))
    ),

    
    # monthly listening activity - in numbers of songs
    ui.card(
        ui.card_header("Monthly Listening Activity"),
        ui.card_body(
            ui.row(
                ui.column(3, ui.input_select(
                    "year_select", 
                    "Select Year:", 
                    choices=["2024", "2025", "2026", "2027"],
                    selected="2025"
                )),
                ui.column(9, "")
            ),
            ui.output_plot("monthly_listening")
        )
    ),

    # monthly listening activity - in number of hours 
    ui.card(
        ui.card_header("🎧 Total Listening Hours (Estimated)"),
        ui.card_body(
            ui.output_ui("total_hours_summary"),
            # ui.output_plot("monthly_hours_plot")
        )
    ),

    # exploration stats and monthly favorites
    ui.card(
        ui.card_header("🗺️ Exploration & Monthly Favorites"),
        ui.card_body(
            ui.output_ui("exploration_summary")
        )
    ),


    # background of entire page
    class_="bg-light", 
)

# Server logic
def server(input, output, session):
    # reactive value to store the data
    spotify_data = reactive.value(None)
    
    # Function to authenticate and load Google Sheets data using that service account i made 
    def get_google_credentials():
        return service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=SCOPES
        )
    
    # pulls the data from my google spreadsheets  
    def load_spotify_data():
        creds = get_google_credentials()
        
        # Connect to Drive API to find all Spotify data files
        drive_service = build('drive', 'v3', credentials=creds)
        sheets_service = build('sheets', 'v4', credentials=creds)
        
        # Search for files with the name pattern
        query = "name contains 'Test_SpotifyData' and mimeType='application/vnd.google-apps.spreadsheet'"
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        
        all_data = pd.DataFrame()
        
        # Read each sheet and combine
        for file in files:
            sheet_id = file['id']
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id, range="A:E").execute()
            
            rows = result.get('values', [])
            if not rows:
                continue
                
            # Skip header row
            if rows[0][0] == 'time':
                rows = rows[1:]
                
            # Convert to DataFrame
            df = pd.DataFrame(rows, columns=['time', 'song', 'artist', 'track_id', 'spotify_link'])
            all_data = pd.concat([all_data, df], ignore_index=True)
        
        # Clean and transform data
        all_data['time'] = pd.to_datetime(all_data['time'].str.replace(' at ', ' '), format='%B %d, %Y %I:%M%p')
        
        # Add duration estimate (in minutes) since IFTTT doesn't provide it
        all_data['duration_min'] = 3.5
        
        return all_data
    
    # Load data on button press
    @reactive.effect
    @reactive.event(input.reload_data)
    def _():
        try:
            # Simple message without notifications
            print("Connecting to Google...")
            data = load_spotify_data()
            print("Processing data...")
            spotify_data.set(data)
            print("Data successfully loaded!")
        except Exception as e:
            print(f"Error loading data: {str(e)}")
    
    # Display last updated time
    @output
    @render.text
    def last_updated():
        if spotify_data() is None:
            return "No data loaded yet. Click 'Reload Data' to fetch my Spotify listening data."
        else:
            return f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M%p')}"
    
    # Top 10 artists plot
    @output
    @render.plot
    def top_artists():
        if spotify_data() is None:
            return Figure()
        
        data = spotify_data()
        top_artists = data['artist'].value_counts().head(10).reset_index()
        top_artists.columns = ['artist', 'count']
        
        fig, ax = plt.subplots(figsize=(8, 6))
        plt.subplots_adjust(left=0.35)
        colors = plt.cm.viridis(np.linspace(0, 0.8, len(top_artists)))
        bars = ax.barh(top_artists['artist'], top_artists['count'], color=colors)
        ax.set_xlabel('Number of Plays')
        ax.set_title('Top 10 Artists')
        ax.invert_yaxis()

        ax.tick_params(axis='y', pad=10)
        ax.tick_params(axis='x', pad=10)

        plt.yticks(rotation=25, ha='right', fontsize=9)

        plt.subplots_adjust(left=0.3, bottom=0.15)
        
        # plt.tight_layout()
        return fig
    
    # Top 10 songs plot
    @output
    @render.plot
    def top_songs():
        if spotify_data() is None:
            return Figure()
        
        data = spotify_data()
        song_counts = data.groupby(['song', 'artist']).size().reset_index(name='count')

         # Truncate long song names and artist names
        song_counts['song_short'] = song_counts['song'].apply(
            lambda x: x[:10] + '...' if len(x) > 15 else x
        )
        song_counts['artist_short'] = song_counts['artist'].apply(
            lambda x: x[:10] + '...' if len(x) > 15 else x
        )

        # combine the shortened names 
        song_counts['display_name'] = song_counts['song_short'] + '(' + song_counts['artist_short'] + ')'

        # sort based on song counts to get the top 10
        top_songs = song_counts.sort_values('count', ascending=False).head(10)


        # graph formatting details 
        fig, ax = plt.subplots(figsize=(8, 6))
        colors = plt.cm.viridis(np.linspace(0, 0.8, len(top_songs)))
        bars = ax.barh(top_songs['display_name'], top_songs['count'], color=colors)
        ax.set_xlabel('Number of Plays')
        ax.set_title('Top 10 Songs')
        ax.invert_yaxis()
        ax.tick_params(axis='y', labelsize=9, pad=10)
        ax.tick_params(axis='x', pad=10)

        # Rotate y-axis labels by 45 degrees and adjust fontsize
        plt.yticks(rotation=25, ha='right', fontsize=9)

        plt.subplots_adjust(left=0.3, bottom=0.15)

        plt.tight_layout(pad=2.2)
        return fig
    
    # Recent unique songs
    @output
    @render.table
    def recent_songs():
        if spotify_data() is None:
            return pd.DataFrame()
        
        data = spotify_data()
        # Sort by time and keep first occurrence of each song-artist pair
        recent_unique = data.sort_values('time', ascending=False)
        recent_unique = recent_unique.drop_duplicates(subset=['song', 'artist'])
        
        # Select and format columns for display
        recent_songs = recent_unique[['time', 'song', 'artist']].head(10)
        recent_songs['time'] = recent_songs['time'].dt.strftime('%m/%d')
        
        # rename the headers of each column 
        recent_songs.columns = ["Date", "Track Name", "Artist"]
        return recent_songs
    
    # Monthly listening activity chart - by number of songs 
    @output
    @render.plot
    def monthly_listening():
        if spotify_data() is None:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.text(0.5, 0.5, "Oop, no data detected.", 
                    ha='center', va='center', fontsize=12)
            ax.set_axis_off()
            return fig
            
        data = spotify_data()
        
        # Extract year and month from timestamp
        data['year'] = data['time'].dt.year
        data['month'] = data['time'].dt.month
        
        # Filter data for selected year
        selected_year = int(input.year_select())
        yearly_data = data[data['year'] == selected_year]
        
        # If no data for selected year, show message
        if len(yearly_data) == 0:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.text(0.5, 0.5, f"We can't predict the future! \nNo listening data for {selected_year}", 
                    ha='center', va='center', fontsize=14)
            ax.set_axis_off()
            return fig
        
        # Group by month and count songs
        monthly_counts = yearly_data.groupby('month').size().reindex(range(1, 13), fill_value=0)
        
        # Create month labels
        month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Create line chart
        fig, ax = plt.subplots(figsize=(10, 5))

        # Add padding to prevent cut-off
        plt.subplots_adjust(left=1.2, bottom=0.15, top=1, right=1.3)
                
        # Plot line chart with points
        ax.plot(month_labels, monthly_counts.values, marker='o', linestyle='-', linewidth=2, 
                color='#6c5ce7', markersize=8, markerfacecolor='#a29bfe')
        
        # Fill area under the line
        ax.fill_between(month_labels, monthly_counts.values, color='#a29bfe', alpha=0.3)
        
        # Add labels and title
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylabel('Number of Songs', fontsize=12)
        ax.set_title(f'Monthly Listening Activity in {selected_year}', fontsize=14)
        
        # Add data labels
        for i, count in enumerate(monthly_counts.values):
            if count > 0:  # Only show labels for non-zero values
                ax.annotate(str(count), (month_labels[i], count), 
                           textcoords="offset points", xytext=(0,10), 
                           ha='center', fontweight='bold')
        
        # Add grid for better readability
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Set y-axis to start at 0
        ax.set_ylim(bottom=0, top=max(monthly_counts.values)+200)
        
        # plt.tight_layout(pad=5)
        return fig

    # monthly listening activity chart - by number of hours 
    @output
    @render.ui
    def total_hours_summary():
        if spotify_data() is None:
            return ui.p("No data loaded.")
        
        data = spotify_data()
        selected_year = int(input.year_select())
        data['year'] = data['time'].dt.year
        data['month'] = data['time'].dt.month
        year_data = data[data['year'] == selected_year]
        
        # Total hours
        total_songs = len(year_data)
        total_hours = round(total_songs * 3 / 60, 1)
        
        # Monthly breakdown
        monthly_counts = year_data.groupby('month').size().reindex(range(1,13), fill_value=0)
        monthly_hours = (monthly_counts * 3 / 60).round(1)
        max_hours = monthly_hours.max() if not monthly_hours.empty else 1
        
        month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Build styled bars
        bar_html = ""
        for i, hours in enumerate(monthly_hours):
            hours_val = 0 if pd.isna(hours) else hours
            percent = (hours_val / max_hours) * 100 if max_hours > 0 else 0
            bar_html += f"""
            <div style="margin-bottom:10px;">
                <div style="font-weight:bold; color:#2d3436;">🎧 {month_labels[i]}:</div>
                <div style="
                    height: 16px;
                    background: linear-gradient(to right, #6c5ce7, #a29bfe);
                    width: {percent:.1f}%;
                    border-radius: 6px;
                    margin-top: 4px;
                    position: relative;">
                </div>
                <div style="font-size:13px; margin-top:4px; color:#636e72;">{hours_val:.1f} hours</div>
            </div>
            """
        
        html = f"""
        <div style="padding: 10px;">
            <h4 style="font-weight:bold;">Total Listening Time in {selected_year}:</h4>
            <p style="font-size:24px; color:#6c5ce7;"><strong>{total_hours:.1f} hours</strong></p>
            {bar_html}
        </div>
        """
        
        return ui.HTML(html)

    # exploration summary - number of unique songs/artists 
    # and top artist/song monthly recap 
    @output
    @render.ui
    def exploration_summary():
        if spotify_data() is None:
            return ui.p("No data loaded.")
        
        data = spotify_data()
        selected_year = int(input.year_select())
        
        # Filter to selected year
        data['year'] = data['time'].dt.year
        data['month'] = data['time'].dt.month
        year_data = data[data['year'] == selected_year]
        
        # Unique artists & songs
        unique_artists = year_data['artist'].nunique()
        unique_songs = year_data[['song', 'artist']].drop_duplicates().shape[0]
        
        # Monthly top song & artist
        top_months_html = ""
        month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        for month in range(1, 13):
            month_data = year_data[year_data['month'] == month]
            if month_data.empty:
                continue
            
            top = (month_data
                .groupby(['song', 'artist'])
                .size()
                .reset_index(name='count')
                .sort_values('count', ascending=False)
                .iloc[0])
            
            song, artist = top['song'], top['artist']
            top_months_html += f"""
            <div style="margin-bottom: 8px; padding: 6px 10px; background: #f5f6fa; border-left: 4px solid #6c5ce7; border-radius: 4px;">
                <strong>\t{month_labels[month - 1]}:</strong> 🎤 {artist} — 🎵 <em>{song}</em>
            </div>
            """

        return ui.HTML(f"""
        <div style="padding: 15px; border-radius: 10px;">
            <h4 style="font-weight:bold; color:#6c5ce7; margin-bottom: 10px;">
                Exploration Highlights in {selected_year}
            </h4>
            <p style="font-size:18px; margin: 10px 0; color:#2d3436;">
                Nat listened to <strong style="color:#d63031;">{unique_artists}</strong> different artists and 
                <strong style="color:#0984e3;">{unique_songs}</strong> unique songs this year.
            </p>
            <h5 style="margin-top: 20px; font-weight:bold; color:#6c5ce7;">
                Top Artist & Song Each Month:
            </h5>
            {top_months_html}
        </div>
        """)

    # my top albums - loaded from the cached JSON file 
    @output
    @render.ui
    def top_albums_ui():
        selected_year = int(input.year_select())
        cache_file = os.path.join("data", "cached_top_albums.json")

        # check if the JSON exists
        if not os.path.exists(cache_file):
            return ui.p("No album data cache was found. Hmm...Better contact Nat.")
        # open and load in JSON values 
        with open(cache_file, "r") as file:
            data = json.load(file)
            top_albums = data.get("albums", [])
            last_updated = data.get("last_updated", "Unknown")
        # if empty JSON file
        if not top_albums:
            return ui.p("No albums found in the cache. Weird! Contact Nat for this one.")
        
        album_html = ""
        for album in top_albums:
            name = album['album_name']
            img_url = album['album_image']
            link = album['album_url']
            album_html += f"""
                <div style="display:inline-block; text-align:center; margin:10px;">
                    <a href="{link}" target="_blank">
                        <img src="{img_url}" style="width:140px; border-radius:10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                    </a>
                    <div style="margin-top:8px; font-size:14px; font-weight:bold; color:#2d3436;">{name}</div>
                </div>
                """

        return ui.HTML(f"""
            <div style="text-align:center; padding:15px;">
                <h4 style="color:#6c5ce7;">Top Albums of {selected_year}</h4>
                {album_html}
                <p style="font-size:13px; color:#636e72;">Last updated: {last_updated}</p>
            </div>
            """)



# Create and run the app
app = App(app_ui, server)