"""
Acquire trailer youtube video ids

"""

from __future__ import unicode_literals
import os
import shutil
import sys
import youtube_dl
import imdb
from imdb import IMDb
from bs4 import BeautifulSoup
from search_yt import youtube_search
import json
import sys
from urllib import *
import argparse
from urllib.parse import urlparse, urlencode, parse_qs
from urllib.request import urlopen
import pytube
from random import shuffle


imdb_top_id_list = '/home/ashish/Code/Video/VideoAesthetics/data/top_1000_list.txt'
imdb_bottom_id_list = '/home/ashish/Code/Video/VideoAesthetics/data/bottom_1000_list.txt'

dataRoot = '/home/ashish/Code/Video/VideoAesthetics/data/trailer_video/'
YOUTUBE_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'
YOUTUBE_VIDEO_PREFIX = 'https://www.youtube.com/watch?v='
trailer_terms = ['Trailer', 'Official', 'HD']

imdb_top_trailer = '/home/ashish/Code/Video/VideoAesthetics/data/top_1000_trailer_list.txt'
imdb_bottom_trailer = '/home/ashish/Code/Video/VideoAesthetics/data/bottom_1000_trailer_list.txt'

import threading


class TimeoutError(Exception): pass


def timelimit(timeout):
    def internal(function):
        def internal2(*args, **kw):
            class Calculator(threading.Thread):
                def __init__(self):
                    threading.Thread.__init__(self)
                    self.result = None
                    self.error = None

                def run(self):
                    try:
                        self.result = function(*args, **kw)
                    except:
                        self.error = sys.exc_info()[0]

            c = Calculator()
            c.start()
            c.join(timeout)
            if c.isAlive():
                raise TimeoutError
            if c.error:
                raise c.error
            return c.result

        return internal2

    return internal


def load_search_res(search_response):
    result_title = ''
    result_id = ''
    while not result_id:
        for search_result in search_response.get("items", []):
            mt = str(search_result["snippet"]["title"])
            video_id = search_result["id"]["videoId"]
            mt = mt.lower()
            if 'trailer' not in mt and 'official' not in mt and 'hd' not in mt:
                continue
            else:
                result_title = mt
                result_id = video_id
                break

        for search_result in search_response.get("items", []):
            mt = str(search_result["snippet"]["title"])
            video_id = search_result["id"]["videoId"]
            mt = mt.lower()
            if 'trailer' not in mt and 'official' not in mt:
                continue
            else:
                result_title = mt
                result_id = video_id
                break

        for search_result in search_response.get("items", []):
            mt = str(search_result["snippet"]["title"])
            video_id = search_result["id"]["videoId"]
            mt = mt.lower()
            if 'trailer' not in mt:
                continue
            else:
                result_title = mt
                result_id = video_id
                break

    return result_title, result_id


def get_search_res(search_response):
    result = 0
    terms = ['trailer', 'official', 'HD']
    count = 3
    while not result:
        _terms = terms[:count]
        if not _terms:
            return ''
        count -= 1
        for search_result in search_response.get("items", []):
            movie_title = search_result["snippet"]["title"]
            video_id = search_result["id"]["videoId"]
            for _term in _terms:
                if _term not in movie_title:
                    break
                # all terms in movie title found
                result = movie_title, video_id
                return result


def open_url(url, parms):
        f = urlopen(url + '?' + urlencode(parms))
        data = f.read()
        f.close()
        matches = data.decode("utf-8")
        return matches

@timelimit(240)
def search_keyword(search_term, imdb_id, imdb_rating, trailer_term, mxRes = 25):
    parms = {
        'q': search_term + trailer_term,
        'part': 'id,snippet',
        'maxResults': mxRes,
        'regionCode': 'US',
        'key': 'AIzaSyDNBOzX3cBTUOROTBGO9FP4Gv9sGS16M3Y'
    }

    try:
        matches = open_url(YOUTUBE_SEARCH_URL, parms)
        search_response = json.loads(matches)
        res = load_search_res(search_response)
        if res[0] == '':
            print('{} : No suitable trailer found'.format(search_term))
            return False
        else:
            try:
                yt = pytube.YouTube(YOUTUBE_VIDEO_PREFIX+res[1])
                _video = yt.streams.filter(mime_type='video/mp4').order_by('resolution').desc().all()[0]
                video_file_name = imdb_id
                _video.download(dataRoot, video_file_name)
                print('{} : {} : {}: {}'.format(res[0], res[1], imdb_rating, video_file_name))
                return True
            except Exception:
                print('Error with {}'.format(res[0]))

    except KeyboardInterrupt:
        print("User Aborted the Operation")

    except Exception:
        print("Cannot Open URL or Fetch comments at a moment")


def movie_names(list_path, trailer_list_path):
    ia = IMDb()
    with open(trailer_list_path, 'w+') as t:
        with open(list_path, 'r') as f:
            lines = f.readlines()
            # shuffle the lines
            shuffle(lines)
            for line in lines:
                movie_id = str(line.strip('\n'))
                trailer_file_path = dataRoot + str(movie_id) + '.mp4'
                if os.path.exists(trailer_file_path):
                    print('{} already downloaded'.format(trailer_file_path))
                    # t.write('{},{}\n'.format(movie_id, movie_rating))
                    continue
                movie = ia.get_movie(movie_id)
                try:
                    movie_title = movie['title']
                    movie_rating = movie['rating']
                    search_arr = trailer_terms
                    while not search_arr == []:
                        search_term = ' '.join(search_arr)
                        try:
                            res = search_keyword(movie_title, movie_id, movie_rating, search_term)
                            if res:
                                t.write('{},{}\n'.format(movie_id, movie_rating))
                                search_arr = []
                            else:
                                search_arr.pop()
                        except Exception:
                            print('time out error: {}'.format(movie_title))
                except Exception:
                    print('Unable to acquire imdb title or rating for {}'.format(movie_id))


if __name__ == '__main__':
    if sys.argv[1] == 'top':
        movie_names(imdb_top_id_list, imdb_top_trailer)
    elif sys.argv[1] == 'bottom':
        movie_names(imdb_bottom_id_list, imdb_bottom_trailer)
    else:
        pass
