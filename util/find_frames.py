"""
Find and save scene-exemplar frames from video of movie trailer
"""

import os 
import sys
import subprocess
import threading
import time
from random import shuffle

import cv2
import scenedetect
import pims
import matplotlib.pyplot as plt
from PIL import Image


# global variables
data_root = '/home/ashish/Data/VideoAesthetics/'
trailer_video_dir = 'trailer_video'
video_file_type = 'mp4'
frame_file_type = 'png'
rating_file_name = 'trailer_ratings.txt'
scene_list_file_name = 'scene_list.csv'
scene_frame_dir = 'scene_frame_images/'
scene_frame_list_dir = 'scene_frame_list/'


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


def get_trailer_video_path(trailer_id):
    return os.path.join(data_root, trailer_video_dir, trailer_id + '.' + video_file_type)


def get_trailer_frame_path(trailer_id):
    return os.path.join(data_root, scene_frame_dir, trailer_id)


def get_frame_list_path(trailer_id):
    return os.path.join(data_root, scene_frame_list_dir, trailer_id + '.csv')


def find_exemplar_frames(video_file_path):
    time_stamp = ''.join([x for x in str(time.time()).split('.')])
    scene_list_file_path = data_root + time_stamp + '_' + scene_list_file_name
    sd_cmd = 'scenedetect -q -l -d content -t 30 -co {} -i {}'.format(scene_list_file_path, video_file_path)
    subprocess.call([item for item in sd_cmd.split(' ')])
    frame_start_list = []
    with open(scene_list_file_path, 'r') as slf:
        line = slf.readline()
        line = slf.readline()
        lines = slf.readlines()
        for line in lines:
            frame_start_list.append(int(line.split(',')[1]))

    exemplar_frame_list = []
    for i in range(len(frame_start_list)-1):
        exemplar_frame_list.append(int(sum(frame_start_list[i:i+2])/2))
    os.remove(scene_list_file_path)
    return exemplar_frame_list


@timelimit(240)
def extract_scene_frames(trailer_id):
    video_file_path = get_trailer_video_path(trailer_id)
    efl = find_exemplar_frames(video_file_path)

    vid = pims.Video(video_file_path)
    if efl == []:
        raise Exception('Empty list of scene exemplar frame numbers!')
    
    exemplar_frame_path = get_trailer_frame_path(trailer_id)
    
    if os.path.exists(exemplar_frame_path):
        print('{} already exists!'.format(trailer_id))
        return
    else:
        os.mkdir(exemplar_frame_path)
    # extract the exemplar numbered frames from the trailer video
    exemplar_frames = vid[efl]

    for i, exemplar_frame in enumerate(exemplar_frames):
        frame_file_name = '%03d.png'%(i)
        frame_file_path = os.path.join(exemplar_frame_path, frame_file_name)
        im = Image.fromarray(exemplar_frame)
        im.save(frame_file_path)
        # print(frame_file_path)

    efl_file_path = get_frame_list_path(trailer_id)
    with open(efl_file_path, 'w+') as f:
        for i,fm in enumerate(efl):
            f.write('{},{}\n'.format(i,fm))


def process_trailer_list(trailer_rating_file_path):
    with open(trailer_rating_file_path, 'r') as f:
        lines = f.readlines()
        trailer_id_list = []
        for line in lines:
            trailer_id = line.split(',')[0]
            trailer_id_list.append(trailer_id)
    
    # towards running multiple clone jobs and minimising collisions
    shuffle(trailer_id_list)

    for i_id, trailer_id in enumerate(trailer_id_list):
        print('{}: processing {}'.format(i_id, trailer_id))
        exemplar_frame_path = get_trailer_frame_path(trailer_id)
        if os.path.exists(exemplar_frame_path):
            print('{} already exists!'.format(trailer_id))
            continue
        try:
            to = time.time()
            extract_scene_frames(trailer_id)
            print('{}s'.format(time.time()-to))
        except Exception as err:
            print(repr(err))


if __name__ == '__main__':
    trailer_rating_file_path = os.path.join(data_root, rating_file_name)
    if not os.path.exists(trailer_rating_file_path):
        print('Trailer rating file not found!')
        exit
    process_trailer_list(trailer_rating_file_path)
