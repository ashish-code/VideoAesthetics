
from __future__ import unicode_literals

from imdb import IMDb
import json
from urllib import *
from urllib.parse import urlparse, urlencode, parse_qs
from urllib.request import urlopen
import pytube

imdb_top_id_list = '../data/top_list.txt'
imdb_bottom_id_list = '../data/bottom_list.txt'
dataRoot = '../data/'
YOUTUBE_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'
YOUTUBE_VIDEO_PREFIX = 'https://www.youtube.com/watch?v='
trailer_term = 'official trailer HD'

imdb_top_trailer = '../data/top_trailer_list.txt'
imdb_bottom_trailer = '../data/bottom_trailer_list.txt'


def load_search_res(search_response):
    for search_result in search_response.get("items", []):
        movie_title = str(search_result["snippet"]["title"])
        video_id = search_result["id"]["videoId"]
        if 'official trailer' not in movie_title.lower():
            continue
        return movie_title, video_id


# def get_search_res(search_response):
#     result = 0
#     terms = ['trailer', 'official', 'HD']
#     count = 3
#     while not result:
#         _terms = terms[:count]
#         if not _terms:
#             return ''
#         count -= 1
#         for search_result in search_response.get("items", []):
#             movie_title = search_result["snippet"]["title"]
#             video_id = search_result["id"]["videoId"]
#             for _term in _terms:
#                 if _term not in movie_title:
#                     break
#                 # all terms in movie title found
#                 result = movie_title, video_id
#                 return result


def open_url(url, parms):
        f = urlopen(url + '?' + urlencode(parms))
        data = f.read()
        f.close()
        matches = data.decode("utf-8")
        return matches


def search_keyword(search_term, imdb_id, imdb_rating, mxRes = 19):
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
        if res == '':
            print('{} : No suitable trailer found'.format(search_term))
            return False
        else:
            yt = pytube.YouTube(YOUTUBE_VIDEO_PREFIX+res[1])
            _video = yt.streams.filter(mime_type='video/mp4').order_by('resolution').desc().all()[0]
            video_file_name = imdb_id
            _video.download(dataRoot, video_file_name)
            print('{} : {} : {}: {}'.format(search_term, res[0], res[1], video_file_name))
            return True

    except KeyboardInterrupt:
        print("User Aborted the Operation")

    except Exception:
        print("Cannot Open URL or Fetch comments at a moment")


def movie_names(list_path, trailer_list_path):
    ia = IMDb()
    with open(trailer_list_path, 'w+') as t:
        with open(list_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                movie_id = str(line.strip('\n'))
                movie = ia.get_movie(movie_id)
                movie_title = movie['title']
                movie_rating = movie['rating']
                res = search_keyword(movie_title, movie_id, movie_rating)
                if res:
                    t.write('{},{}\n'.format(movie_id, movie_rating))


if __name__ == '__main__':
    # movie_names(imdb_top_id_list, imdb_top_trailer)
    movie_names(imdb_bottom_id_list, imdb_bottom_trailer)