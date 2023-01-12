# automate local files 🎧
A simple script that can download a mp3 file embedded with basic metadata retrieved from Discogs (ex. title, album artwork, track number, ect...) from the youtube link of a song. I use it to upload songs that are not available on any streaming services/music platforms and have no metadata on youtube to my Spotify local file library! Uploading songs with the artwork and correct metadata to Spotify manually took me a lot of time which was what prompted me to write this program. Nothing fancy but it does the job and writing this program really helped me practice how to structure classes in python and use different APIs.

# table of contents
- [Dependencies](#dependencies)
- [Usage](#usage)
- [To do](#to-do)

# dependencies
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
  - used to download youtube videos 
- [python3-discogs-client](https://www.discogs.com/developers)
  - used to retrieve metadata from Discogs database for mp3 file 
- [mutagen](https://mutagen.readthedocs.io/en/latest/)
  - python library used to edit tags (metadata) of multimedia files
- [ffmpg](https://ffmpeg.org/download.html)
  - yt-dlp dependency; used to convert videos to mp3
  - must be added to PATH to work for [windows](https://windowsloop.com/install-ffmpeg-windows-10/) (MacOs use Hombrew, Linux use apt)
 
 Can install most dependencies using: `pip install -r requirements.txt`

# usage
1. Before running the file, user must provide a download path for the mp3 file as well as a Discogs API user token in the secret.py file ([how to generate a token](https://www.discogs.com/developers/#page:authentication))
2. To run the program write the following command `python download_songs.py link` and replace 'link' with the youtube link of your choice. The link included as an argument can't be the link of the video within a playlist; this is not supported. 
3. If the program is not able to find a matching result on Discogs using the title of the youtube video, it will ask the user to provide the name of the song and main artist and will send out a new query to the Discogs API. 

# to do
- Formatting 
- Error Handling (ex. when user does not provide argument, invalid link...)
- Test
- Add more documentation






