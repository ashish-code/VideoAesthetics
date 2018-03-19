"""
Get list of movie references from IMDb. An IMDb id for each movie.
we are focusing specifically on top and bottom 1000 rated movies on IMDb

author: ashish gupta
email: ashishagupta@gmail.com
date: March, 15, 2018
"""

import requests
import re

data_root = '../data/'


def imdb_id_search(search_page_url):
    r = requests.get(search_page_url)
    html = r.text.split('\n')
    result = []
    for line in html:
        line = line.rstrip('\n')
        m = re.search(r'data-tconst="tt(\d+?)">', line)
        if m:
            _id = m.group(1)
            result.append(_id)
    result = list(set(result))
    return result


def get_list(url_root):
    _list = []
    for page_count in range(5):
        search_url = url_root + str(page_count+1)
        page_list = imdb_id_search(search_url)
        _list.extend(page_list)
    return _list


if __name__ == '__main__':
    list_url_root = {'top' : 'https://www.imdb.com/search/title?groups=top_1000&view=simple&sort=user_rating,desc&count=250&ref_=adv_nxt&page=',
                     'bottom' : 'https://www.imdb.com/search/title?groups=bottom_1000&view=simple&sort=user_rating,asc&count=250&ref_=adv_nxt&page='}
    for _key in list_url_root.keys():
        _list = get_list(list_url_root[_key])
        imdb_id_list_file_path = data_root + _key + '_1000_list.txt'
        with open(imdb_id_list_file_path, 'w+') as f:
            for imdb_id in _list:
                f.write('{}\n'.format(imdb_id))
                # debug:
                print('{}'.format(imdb_id))