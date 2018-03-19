"""
Download movie trailers from youtube
"""

from __future__ import unicode_literals
import os
import shutil
import sys
import youtube_dl
import imdb
from imdb import IMDb
from bs4 import BeautifulSoup
import urllib.request

from search_yt import youtube_search

imdb_top_id_list = '/home/ashish/Code/Video/VideoAesthetics/data/top_list.txt'
imdb_bottom_id_list = '/home/ashish/Code/Video/VideoAesthetics/data/bottom_list.txt'
dataRoot = '/home/ashish/Code/Video/VideoAesthetics/data/'





def movie_names(list_path):
    ia = IMDb()
    with open(list_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            movie_id = str(line.strip('\n'))
            movie = ia.get_movie(movie_id)
            movie_title = movie['title']
            # movie_path = dataRoot + movie_title + '.mp4'
            # ydl_opts = {'quiet': False, 'simulate': False, 'default_search': 'ytsearch', 'format': 'mp4', 'outtmpl': '{}-trailer.mp4'.format(movie_title), 'width': 640, 'max-downloads': 1}
            # with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            #
            #     ydl.download([movie_path])
            text_to_search = movie_title + ' Official Trailer'
            query = text_to_search
            url = "https://www.youtube.com/results?search_query=" + query
            with urllib.request.urlopen(url) as response:
                html = response.read()
                soup = BeautifulSoup(html)
                for vid in soup.findAll(attrs={'class': 'yt-uix-tile-link'}, limit=1):
                    print('https://www.youtube.com' + vid['href'])




# for dirpath, dirnames, filenames in os.walk(u'.'):
#     if dirpath != '.' and not dirpath.endswith('extrafanart') and not dirpath.endswith('extrathumbs'):
#         ydl_opts = {'quiet': False, 'simulate': False, 'default_search': 'ytsearch', 'format': 'mp4',
#                     'outtmpl': '{0}/{1}-trailer.mp4'.format(dirpath, dirpath[2:])}
#         with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#             ydl.download([dirpath[2:] + " " + "trailer"])
#
# raw_input("Press return to exit.")


if __name__ == '__main__':
    movie_names(imdb_top_id_list)