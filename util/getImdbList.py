import requests
import re

top250_url = "http://akas.imdb.com/chart/top"
bottom250_url = 'http://www.imdb.com/search/title?groups=bottom_250&production_status=released&sort=moviemeter,desc&view=simple'

top_list_file_path = '../data/top_list.txt'
bottom_list_file_path = '../data/bottom_list.txt'


def get_top250():
    r = requests.get(top250_url)
    html = r.text.split("\n")
    result = []
    for line in html:
        line = line.rstrip("\n")
        m = re.search(r'data-titleid="tt(\d+?)">', line)
        if m:
            _id = m.group(1)
            result.append(_id)
    #
    return result


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


def imdb_id_list(page_url):
    r = requests.get(page_url)
    html = r.text.split('\n')
    result = []
    for line in html:
        line = line.rstrip('\n')
        m = re.search(r'data-titleid="tt(\d+?)">', line)
        if m:
            _id = m.group(1)
            result.append(_id)
    return result


def get_bottom250():
    bottom_root_url = bottom250_url
    bottom_list = []
    for i in range(5):
        search_page_url = bottom_root_url + '&page=' + str(i+1)
        page_list = imdb_id_search(search_page_url)
        bottom_list.extend(page_list)
    return bottom_list


def write_list2file(_list, file_path):
    with open(file_path, 'w+') as f:
        for item in _list:
            f.write('{}\n'.format(item))


if __name__ == '__main__':
    # topList = get_top250()
    # topList = imdb_id_list(top250_url)
    # for i, item in enumerate(topList):
    #     print('{}:{}'.format(i,item))

    # bottomList = get_bottom250()
    # for i, item in enumerate(bottomList):
    #     print('{}:{}'.format(i, item))

    top_list = get_top250()
    bottom_list = get_bottom250()

    write_list2file(top_list, top_list_file_path)
    write_list2file(bottom_list, bottom_list_file_path)
