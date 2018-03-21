"""
Use video SBD (scene boundary detection) to find start of each scene.
Utilize the scene center as exemplar video-frame and save it to file.
"""

import os 
import scenedetect
import cv2
import sys
import subprocess
import pims
import matplotlib.pyplot as plt
import imageio
from PIL import Image

# global variables
data_root = '/home/ashish/Data/VideoAesthetics/'
scene_seg = 'scene_seg/'
exemplar_frame_dir = 'examplar_frames/'
scene_list_file_name = 'scene_list.csv'



def find_exemplar_frames(video_file_path, exemplar_frame_path):
    scene_list_file_path = os.path.join(data_root, scene_seg, scene_list_file_name)
    sd_cmd = 'scenedetect -q -l -d content -t 30 -co {} -i {}'.format(scene_list_file_path, video_file_path)
    subprocess.call([item for item in sd_cmd.split(' ')])
    frame_start_list = []
    with open(scene_list_file_path, 'r') as slf:
        line = slf.readline()
        line = slf.readline()
        lines = slf.readlines()
        for line in lines:
            frame_start_list.append(int(line.split(',')[1]))

    # print(frame_start_list)
    exemplar_frame_list = []
    for i in range(len(frame_start_list)-1):
        exemplar_frame_list.append(int(sum(frame_start_list[i:i+2])/2))
    # print(exemplar_frame_list)
    # print('{},{}'.format(len(frame_start_list), len(exemplar_frame_list)))
    return exemplar_frame_list


def save_frames(video_file_path, exemplar_frame_path, frame_list = []):
    vid = pims.Video(video_file_path)
    if frame_list == []:
        raise Exception('Empty list of scene exemplar frame numbers!')
    if not os.path.exists(exemplar_frame_path):
        os.mkdir(exemplar_frame_path)
    # extract the exemplar numbered frames from the trailer video
    exemplar_frames = vid[frame_list]
    for i, exemplar_frame in enumerate(exemplar_frames):
        frame_file_name = '%03d.png'%(i)
        frame_file_path = os.path.join(exemplar_frame_path, frame_file_name)
        im = Image.fromarray(exemplar_frame)
        im.save(frame_file_path)
        print(frame_file_path)
    efl_file_path = os.path.join(exemplar_frame_path, 'efl.csv')
    with open(efl_file_path, 'w+') as f:
        for i,fm in enumerate(frame_list):
            f.write('{},{}\n'.format(i,fm))


if __name__ == '__main__':
    video_file_name = '0081505.mp4'
    exemplar_frame_path = os.path.join(data_root, exemplar_frame_dir)
    if not os.path.exists(exemplar_frame_path):
        os.mkdir(exemplar_frame_path)
    video_file_path = os.path.join(data_root, scene_seg, video_file_name)
    # find the scene-exemplar frames from trailer video
    efl = find_exemplar_frames(video_file_path, exemplar_frame_path)
    exemplar_frame_dir = video_file_name.split('.')[0]
    exemplar_frame_path = os.path.join(data_root, scene_seg, exemplar_frame_dir)
    try:
        save_frames(video_file_path, exemplar_frame_path, efl)
    except Exception as err:
        print(repr(err))


