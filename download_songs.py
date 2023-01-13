
# step 1: ask user for the link of a video and convert to mp3 and put in music folder x
# step 3: extract info from video and search in discogs for info and artwork   x
# step 4: input artwork and info into mp3 files info   x
# step 5: delete artwork file and move mp3 file to music folder x
# dependencies you have to warn users about (discogs client, yt_dlp, ffmpg, mutagen)

#TO DO: handle errors

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

class DownloadSong:
    # set local files folder for spotify and discogs token in set_folder.txt
    # to start program write "python retrieve-song.py [link of youtube video]"

    def __init__(self, song_link, video_title, results, original_title):
        self.song_link = song_link
        self.video_title = video_title
        self.results = results
        self.original_title = original_title

    #convert video to mp3
    def convert_link(self): 

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
    
    #send a query to the Discogs API; if no results prompt user for other search terms and send another query
    def generate_discogs_results(self):
        d = discogs_client.Client('AutomateLocalFiles/1.0', user_token= discogs_token)
        self.results = d.search(self.video_title, type = 'release')
        if self.results.count == 0:
            while self.results.count == 0: 
                print('Hey! We were not able to find the album of the song in the Discogs Database using the title of the youtube video.')
                self.video_title = input('Write the name of the song and the main artist here and we will look again:')
                self.results = d.search(self.video_title, type = 'release')

    #retrieve album title, artist, title of song, track number, genre for song
    def retrieve_metadata(self):
        i = 0
        song_name = []
        release = self.results[0]
        print(f'Number of Discogs search results: {self.results.count}')

        while song_name == []:
            songlist = []  

            for songs in release.tracklist:
                songlist.append(songs.title)

            #find closest track name to search terms 
            song_name = difflib.get_close_matches(self.video_title, songlist, 1, 0.25)

            if song_name == []:
                # try other next search result; maybe better luck 
                if i < self.results.count-1: 
                    i+=1
                    release = self.results[i]
                else: 
                    print("Hey! We weren't able to find the track in the Discogs Database using the title of the youtube video.")
                    user_input = input('Write the name of the song and main artist here and we will look again (tip: write name of song it in its original language) or press s to exit:')
                    
                    if user_input  == 's':
                        sys.exit("Progam ended by user\n")
                    else: 
                        self.video_title = user_input
                        self.generate_discogs_results()
                        release = self.results[0]
                        i = 0

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

        image = release.images[0]['uri'] #retrieve image uri

        # write image to current directory
        with urllib.request.urlopen(image) as url:
            with open('temp.jpg', 'wb') as f:
                f.write(url.read())

        filename = self.original_title + '.mp3'

        #set metadata 
        file = EasyMP3(filename)

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

    
    #remove temp files and move mp3 file to folder selected by user 
    def reset(self):
        filename = self.original_title + '.mp3'
        #delete temp.jpg
        os.remove('temp.jpg')
        #place file into folder of choice 
        os.replace(filename, folder_path + filename) #can also use os.rename() (renames path of file)
        print('All done! Mp3 file is called {} and can be found in {}\n'.format(self.original_title, folder_path))
        #can also use %s instead of {} and end string with % (x, y) to print


if __name__ == '__main__':
    song_link = sys.argv[1] #take user input
    video_title = results = original_title = ''
    song = DownloadSong(song_link, video_title, results, original_title)
    song.convert_link()
    song.generate_discogs_results()
    song.retrieve_metadata()
    song.reset()