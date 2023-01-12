# step 1: ask user for the link of a video and convert to mp3 and put in music folder x
# step 3: extract info from video and search in discogs for info and artwork   x
# step 4: input artwork and info into mp3 files info   x
# step 5: delete artwork file and move mp3 file to music folder x
# dependencies you have to warn users about (discogs client, yt_dlp, ffmpg, mutagen)

#TO DO: handle errors and remove code used for testing

from __future__ import unicode_literals
from secret import folder_path, discogs_token
import sys
import os
import yt_dlp
import discogs_client
import difflib
import urllib.request
from mutagen.mp3 import EasyMP3
from mutagen.id3 import APIC, ID3


class retrieveSong:
    # set local files folder for spotify in set_folder.txt
    # to start program write "python retrieve-song.py [link of youtube video]"

    def get_song_link(self): 
        #take user input
        song_link = sys.argv[1]
        
        #convert to mp3 
        ydl_opts = {
            'format': 'bestaudio',
            'outtmpl': '%(title)s.mp3',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl: 
            ydl.download([song_link])
            video_info = ydl.extract_info(song_link, download = False)
            video_title = video_info.get('title', None)
            print(video_title)
    
        #retrieve album title, artist, title of song, track number, genre
        d = discogs_client.Client('AutomateLocalFiles/1.0', user_token= discogs_token)
        results = d.search(video_title, type = 'release')
        # assume best match is first result in list 
        release = results[0]
        
        print(f'\n\t== discogs-id {release.id} ==')
        print(f'\tArtist\t: {", ".join(artist.name for artist in release.artists)}')
        print(f'\tTitle\t: {release.title}')
        print(f'\tYear\t: {release.year}')
        print(release.genres)
        album_year = release.year
        album_title = release.title
        artist_names = ', '.join(artist.name for artist in release.artists)
        genre = release.genres[0] 
        
        songlist = []  
        #all we need now is track name and number
        for songs in release.tracklist:
            songlist.append(songs.title)

        song_name = difflib.get_close_matches(video_title, songlist, 1, 0.3)
        print(song_name)
        print(songlist)
        song = ''.join(song_name)
        print(song)
        track_num = songlist.index(song) + 1
        print(track_num)
        
        #try: except ValueError: 
        image = release.images[0]['uri']
        
        with urllib.request.urlopen(image) as url:
            with open('temp.jpg', 'wb') as f:
                f.write(url.read())

        filename = video_title + '.mp3'

        file = EasyMP3(filename)
        #EasyID3.RegisterTextKey('year', 'TDRC'); pprint.pprint(EasyID3.valid_keys.keys())

        file['title'] = song
        file['artist'] = artist_names
        file['albumartist'] = artist_names
        file['tracknumber'] = str(track_num)
        file['date'] = str(album_year)
        file['album'] = album_title
        file['genre'] = genre
        file.save()

        audio = ID3(filename)
        with open('temp.jpg', 'rb') as art: 
            audio['APIC'] = APIC(
                                encoding=3,
                                mime='image/jpeg',
                                type=3,
                                data = art.read()
                            )
        audio.save(v2_version=3)

        #delete temp.jpg
        os.remove('temp.jpg')
        #place file into folder of choice 
        os.replace(filename, folder_path + filename) #can also use os.rename() (renames path of file)

if __name__ == '__main__':
    song = retrieveSong()
    song.get_song_link()