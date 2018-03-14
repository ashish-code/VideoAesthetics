"""
Download movie trailers from youtube
"""

from __future__ import unicode_literals
import os
import shutil
import sys
import youtube_dl
import imdb


imdb_top_id_list = '../data/top_list.txt'
imdb_bottom_id_list = '../data/bottom_list.txt'


def movie_names(list_path):
    with open(list_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            movie_id = str(line.strip('\n'))
            print(movie_id)



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