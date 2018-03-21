"""
Create a list of film trailer videos with associated film IMDb rating. 
Create training and validation sets.

author: Ashish Gupta
email: ashish.gupta@rit.edu
date: 03/19/2018
"""
from __future__ import unicode_literals

# inbuilt library imports
import os
import sys
import threading
import numpy as np
import matplotlib.pyplot as plt 
# third-party imports
from imdb import IMDb


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
            # if c.error:
            #     raise c.error
            return c.result

        return internal2

    return internal

# global variables
data_root = '/home/ashish/Data/VideoAesthetics/'
trailer_video_dir = 'trailer_video'
video_file_type = 'mp4'
trailer_classes = ['top', 'bottom']
rating_file_name = 'trailer_ratings.txt'

@timelimit(30)
def retrieve_rating(trailer_id):
    # create imdb object to retrieve rating from imdb given the imdb-id
    _imdb = IMDb()
    try:
        _movie = _imdb.get_movie(trailer_id)
        try:
            movie_title = _movie['title']
            movie_rating = _movie['rating']
            return movie_rating, movie_title
        except:
            raise Exception('{} : unable to get movie title or rating'.format(trailer_id))
    except:
        raise Exception('{}: unable to retrieve info'.format(trailer_id))


def create_rating_list(data_dir):
    file_list_raw = os.listdir(data_dir)
    trailer_imdb_id_list = [_file.split('.')[0] for _file in file_list_raw if _file.split('.')[-1] == video_file_type]
    rating_file_path = os.path.join(data_root, rating_file_name)
    
    with open(rating_file_path, 'w+') as f:
        for i, trailer_id in enumerate(trailer_imdb_id_list):
            try:
                print('{},{}'.format(i, trailer_id))
                trailer_rating, trailer_title = retrieve_rating(trailer_id)
                f.write('{},{},{}\n'.format(trailer_id, trailer_rating, trailer_title))
                print('{},{},{}'.format(trailer_id, trailer_rating, trailer_title))
            except Exception as err:
                print(repr(err))


def histogram_ratings(trailer_list_file):
    movie_id_list = []
    movie_rating_list = []
    with open(trailer_list_file, 'r') as f:
        lines = f.readlines()
    for line in lines:
        movie_id_list.append(line.split(',')[0])
        movie_rating_list.append(float(line.split(',')[1]))
    ratings = np.array(movie_rating_list)
    N = len(movie_rating_list)
    _hist = np.histogram(ratings, bins=100, range=(0.0, 10.0))
    fig = plt.figure(1)
    # plt.hist(ratings, bins=100, range=(0.0, 10.0))
    plt.bar(_hist[1][:-1], _hist[0]/N)
    plt.xlabel('IMDb rating')
    plt.xticks([i for i in range(11)])
    plt.ylabel('Occurrence Freq.')
    plt.title('Ratings of top and bottom 1000 movies on IMDb')
    plt.show()


if __name__ == '__main__':
    # trailer_data_path =  os.path.join(data_root, trailer_video_dir)
    # create_rating_list(trailer_data_path)
    trailer_rating_file = os.path.join(data_root, rating_file_name)
    histogram_ratings(trailer_rating_file)
