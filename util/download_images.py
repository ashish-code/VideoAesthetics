"""
Download images from imgur using concurrency
Client ID:
030b807d79a90c2
Client secret:
cb63fea40373f9b1d7e8ebd2c4d43c1c1dc1cb15
"""

import json
import logging
import os
from pathlib import Path
from urllib.request import urlopen, Request 
from time import time
from functools import partial
from multiprocessing.pool import Pool

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('requests').setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)


IMGUR_CLIENT_ID = '030b807d79a90c2'
IMGUR_CLIENT_SECRET = 'cb63fea40373f9b1d7e8ebd2c4d43c1c1dc1cb15'

types = {'image/jpeg', 'image/png'}


def get_links(client_id):
    headers = {'Authorization': 'Client-ID {}'.format(client_id)}
    req = Request('https://api.imgur.com/3/gallery/random/random/', headers=headers, method='GET')
    with urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    return [item['link'] for item in data['data'] if 'type' in item and item['type'] in types]


def download_link(directory, link):
    logger.info('Downloading %s', link)
    download_path = directory / os.path.basename(link)
    with urlopen(link) as image, download_path.open('wb') as f:
        f.write(image.read())
    logger.info('Downloaded %s', link)


def setup_download_dir():
    download_dir = Path('images')
    if not download_dir.exists():
        download_dir.mkdir()
    return download_dir


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('requests').setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)


def get_single():
    ts = time()
    client_id = IMGUR_CLIENT_ID
    if not client_id:
        raise Exception('valid Imgur client id not found.')
    download_dir = setup_download_dir()
    links = [l for l in get_links(client_id) if l.endswith('.jpg')]
    for link in links:
        download_link(download_dir, link)
    print('Took {}s'.format(time()-ts))


def get_multiple():
    ts = time()
    client_id = IMGUR_CLIENT_ID
    if not client_id:
        raise Exception('valid client id not provided.')
    download_dir = setup_download_dir()
    links = get_links(client_id)
    download = partial(download_link, download_dir)
    with Pool(4) as p:
        p.map(download, links)
    logging.info('Took %s seconds', time()-ts)


if __name__ == '__main__':
    get_multiple()
