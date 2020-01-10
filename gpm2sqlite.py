import gmusicapi
import sqlite3
import os


def init_db(database):
    conn = sqlite3.connect(database)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS artist
                 (id text primary key, name text)''')
    c.execute('''CREATE TABLE IF NOT EXISTS album
                 (id text primary key, name text, artist text, year integer, foreign key(artist) references artist(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS song
                 (id text primary key, name text, album text, play_count integer, foreign key(album) references album(id))''')
    conn.commit()
    return conn


def auth(oauth_credentials):
    client = gmusicapi.Mobileclient()
    if not os.path.exists(oauth_credentials):
        client.perform_oauth(oauth_credentials, open_browser=True)
    client.oauth_login(gmusicapi.Mobileclient.FROM_MAC_ADDRESS, oauth_credentials=oauth_credentials)
    return client


def insert_library(client, conn):
    songs = client.get_all_songs()
    c = conn.cursor()
    for song in songs:
        artistId = song.get('artistId', [song['artist']])[0]
        albumId = song.get('albumId', song['album'])
        c.execute('''INSERT OR IGNORE INTO artist (id, name) VALUES (?, ?)''',
                  (artistId, song['artist']))
        c.execute('''INSERT OR IGNORE INTO album (id, name, artist, year) VALUES (?, ?, ?, ?)''',
                  (albumId, song['album'], artistId, song.get('year', 0)))
        c.execute('''INSERT OR IGNORE INTO song (id, name, album, play_count) VALUES (?, ?, ?, ?)''',
                  (song['id'], song['title'], albumId, song.get('playCount', 0)))
    conn.commit()


if __name__ == '__main__':
    client = auth(os.path.join(os.getcwd(), 'gpm.cred'))
    conn = init_db(os.path.join(os.getcwd(), 'gpm.sqlite'))
    insert_library(client, conn)
    conn.close()
