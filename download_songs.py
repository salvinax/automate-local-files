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

#need og username!!!!!! to find it in our files!
class retrieveSong:
    # set local files folder for spotify in set_folder.txt
    # to start program write "python retrieve-song.py [link of youtube video]"
    def __init__(self, song_link, video_title, results, original_title):
        self.song_link = song_link
        self.video_title = video_title
        self.results = results
        self.original_title = original_title

    def convertlink2mp3(self): 

        ydl_opts = {
            'format': 'bestaudio',
            'outtmpl': '%(title)s.mp3',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl: 
            ydl.download([self.song_link])
            video_info = ydl.extract_info(self.song_link, download = False)
            self.video_title = self.original_title = video_info.get('title', None)
            print(self.video_title)
    
    #retrieve album title, artist, title of song, track number, genre
    def generatediscogsresults(self):
        d = discogs_client.Client('AutomateLocalFiles/1.0', user_token= discogs_token)
        self.results = d.search(self.video_title, type = 'release')
        if self.results.count == 0:
            while self.results.count == 0: 
                print('Hey! We were not able to find the album of the song in the Discogs Database using the title of the youtube video.')
                self.video_title = input('Write the name of the song and the main artist here and we will look again:')
                self.results = d.search(self.video_title, type = 'release')

    
    def browsediscogsresults(self):
        i = 0
        song_name = []
        release = self.results[0]
        print(f'How many results: {self.results.count}')

        while song_name == []:
            songlist = []  

            for songs in release.tracklist:
                songlist.append(songs.title)

            song_name = difflib.get_close_matches(self.video_title, songlist, 1, 0.25)

            if song_name == []:
                if i < (self.results.count-1): 
                    i+=1
                    print(i)
                    release = self.results[i]
                else: 
                    print("Hey! We weren't able to find the track in the Discogs Database using the title of the youtube video.")
                    self.video_title = input('Write the name of the song and the main artist here and we will look again (if the song is not in english, write it in its original language):')
                    self.generatediscogsresults()
                    i = 0
                    release = self.results[0]

        print(f'Album Tracklist: {songlist}')
        song = ''.join(song_name) #convert to string 
        print(f'Track Name: {song}')
        track_num = songlist.index(song) + 1
        print(f'Track Number: {track_num}')

        #print info for user 
        print(f'\n\t== discogs-id {release.id} ==')
        print(f'\tArtist\t: {", ".join(artist.name for artist in release.artists)}')
        print(f'\tTitle\t: {release.title}')
        print(f'\tYear\t: {release.year}')
        print(f'\tGenres\t: {release.genres}')
        print('\n')

        album_year = release.year
        album_title = release.title
        artist_names = ', '.join(artist.name for artist in release.artists)
        genre = release.genres[0] 

        image = release.images[0]['uri']
        
        with urllib.request.urlopen(image) as url:
            with open('temp.jpg', 'wb') as f:
                f.write(url.read())

        filename = self.original_title + '.mp3'

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

    
    def reset(self):
        filename = self.original_title + '.mp3'
        #delete temp.jpg
        os.remove('temp.jpg')
        #place file into folder of choice 
        os.replace(filename, folder_path + filename) #can also use os.rename() (renames path of file)
        print('All done! Mp3 file is called {} and can be found in {}\n'.format(self.original_title, folder_path))
        #can also use %s instead of {} and end string with % (x, y) to print


if __name__ == '__main__':
    #take user input
    song_link = sys.argv[1]
    video_title = results = original_title = ''
    song = retrieveSong(song_link, video_title, results, original_title)
    song.convertlink2mp3()
    song.generatediscogsresults()
    song.browsediscogsresults()
    song.reset()