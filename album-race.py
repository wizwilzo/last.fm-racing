import requests
import csv
from datetime import datetime, timedelta
import pandas as pd

# Replace with your Last.fm API key
API_KEY = '0f3408d9341c62a740e2c7456fc10445'

def get_top_albums(username, from_date, to_date):
    url = f'http://ws.audioscrobbler.com//2.0/?method=user.getweeklyalbumchart&user={username}&api_key={API_KEY}&from={from_date}&to={to_date}&format=json'

    response = requests.get(url)
    data = response.json()
    return data

def generate_csv(username, artists):
    csv_filename = f'{username}_top_artists.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Rank', 'Artist', 'Play Count'])

        for rank, artist in enumerate(artists, start=1):
            csv_writer.writerow([rank, artist['name'], artist['playcount']])

    print(f'CSV file "{csv_filename}" generated successfully.')


if __name__ == '__main__':
    lastfm_username = input("Enter your Last.fm username: ")

    #https://www.unixtimestamp.com/
    endtime = 1729059963

    #Maps an artist name to arr of playcounts
    DICT = {}
    SET = set()
    date_ranges = []

    #getting user join date
    url = f"http://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={lastfm_username}&api_key={API_KEY}&format=json"
    response = requests.get(url)
    data = response.json()
    join_unix_timestamp = int(data['user']['registered']['unixtime'])

    currtime = join_unix_timestamp
    seconds_in_week = 604_800
    rep = 0

    while currtime <= endtime:
        rep += 1

        try:
            albums_data = get_top_albums(lastfm_username,
                                         currtime - seconds_in_week, currtime)
            date_range = str(currtime) + " - " + str(currtime +
                                                     seconds_in_week)
            datetime_obj = datetime.fromtimestamp(currtime)

            date_ranges.append(datetime_obj.strftime('%Y-%m-%d'))
            playcount = []

            for album_dict in albums_data['weeklyalbumchart']['album']:
                curr_name = album_dict['name']
                SET.add(curr_name)

                if curr_name not in DICT:
                    DICT[curr_name] = [0] * rep

                DICT[curr_name].append(album_dict['playcount'])

            for artist in DICT:
                while len(DICT[artist]) <= rep:
                    DICT[artist].append(0)
            currtime += seconds_in_week

        except:
            break

    #prefix sum each array
    DICT2 = {}
    for artist_name in DICT:
        for i in range(1, len(DICT[artist_name])):
            DICT[artist_name][i] = str(
                int(DICT[artist_name][i - 1]) + int(DICT[artist_name][i]))

        if int(DICT[artist_name][len(DICT[artist_name]) - 1]) >= 30:
            DICT2[artist_name] = DICT[artist_name]

    DICT = DICT2

    #creating a list of rows
    rows = [["Artist"] + date_ranges]  # Header row

    for artist_name in DICT:
        curr_playcount = DICT.get(artist_name, [])
        row = [artist_name] + curr_playcount
        rows.append(row)

    #writing to CSV file
    with open('album_playcounts.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(rows)

    print("CSV file generated.")