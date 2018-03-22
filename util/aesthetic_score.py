"""
Computer aesthetic score of each scene-exemplar frame from trailer video.
"""

# import libraries
import numpy as np 
import os 
import sys

import subprocess
import threading
import time
from random import shuffle
import caffe

# global variables for local file/directory paths
ILGnet_root = '/home/ashish/Repos/ILGnet/'
net_file = os.path.join(ILGnet_root, 'deploy.prototxt')
caffe_model = os.path.join(ILGnet_root, 'data/AVA2/ILGnet-AVA2.caffemodel')
mean_file = os.path.join(ILGnet_root, 'mean/AVA2_mean.npy')
#
data_root = '/home/ashish/Data/VideoAesthetics/'
trailer_video_dir = 'trailer_video'
video_file_type = 'mp4'
frame_file_type = 'png'
rating_file_name = 'trailer_ratings.txt'
scene_list_file_name = 'scene_list.csv'
scene_frame_dir = 'scene_frame_images/'
scene_frame_list_dir = 'scene_frame_list/'
scene_aesthetic_score_dir = 'scene_aesthetics/'

net = caffe.Net(net_file,caffe_model,caffe.TEST)
transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
transformer.set_transpose('data', (2,0,1))
transformer.set_mean('data', np.load(mean_file).mean(1).mean(1))
transformer.set_raw_scale('data', 255) 
transformer.set_channel_swap('data', (2,1,0))


def get_aesthetic_score(image_path):
    img = caffe.io.load_image(image_path)
    net.blobs['data'].data[...] = transformer.preprocess('data',img)
    out = net.forward()
    out1 = out["loss1/loss"][0]
    return out1[1]


def get_trailer_frame_path(trailer_id):
    return os.path.join(data_root, scene_frame_dir, trailer_id)


def get_frame_list_path(trailer_id):
    return os.path.join(data_root, scene_frame_list_dir, trailer_id + '.csv')


def get_exemplar_frame_path_list(trailer_id):
    frame_list_path = get_frame_list_path(trailer_id)
    ids = []
    with open(frame_list_path, 'r') as f:
        lines = f.readlines()
    for line in lines:
        ids.append(int(line.split(',')[0]))
    frame_path_list = []
    ids = sorted(ids)
    for id in ids:
        frame_path = get_trailer_frame_path(trailer_id) + '/' + '%03d'%(id) + '.' + frame_file_type
        frame_path_list.append(frame_path)
    return frame_path_list

def computer_trailer_aesthetics(trailer_id):
    aesthetic_score_file = get_aesthetic_score_file_path(trailer_id)
    image_list = get_exemplar_frame_path_list(trailer_id)
    with open(aesthetic_score_file, 'w+') as f:
        for i, image_path in enumerate(image_list):
            aesthetic_score = get_aesthetic_score(image_path)
            f.write('{},{}\n'.format(i, aesthetic_score))
            # debug:
            print('{}:{}:{}'.format(trailer_id, i, aesthetic_score))


def get_aesthetic_score_file_path(trailer_id):
    return os.path.join(data_root, scene_aesthetic_score_dir, trailer_id + '.csv')


def process_trailer_list(trailer_rating_file_path):
    with open(trailer_rating_file_path, 'r') as f:
        lines = f.readlines()
        trailer_id_list = []
        for line in lines:
            trailer_id = line.split(',')[0]
            trailer_id_list.append(trailer_id)
    
    # towards running multiple clone jobs and minimizing collisions
    shuffle(trailer_id_list)

    for i_id, trailer_id in enumerate(trailer_id_list):
        print('{}: processing {}'.format(i_id, trailer_id))
        aesthetic_score_file = get_aesthetic_score_file_path(trailer_id)
        if os.path.exists(aesthetic_score_file):
            print('{} already exists!'.format(trailer_id))
            continue
        try:
            to = time.time()
            computer_trailer_aesthetics(trailer_id)
            print('{}s'.format(time.time()-to))
        except Exception as err:
            print(repr(err))


if __name__ == '__main__':
    trailer_rating_file_path = os.path.join(data_root, rating_file_name)
    if not os.path.exists(trailer_rating_file_path):
        print('Trailer rating file not found!')
        exit
    process_trailer_list(trailer_rating_file_path)