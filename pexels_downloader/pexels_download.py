#!/usr/bin/env python3

import argparse
import os
import time
import urllib.parse
from html.parser import HTMLParser

import requests

base_url = "https://www.pexels.com/search/"
end_flag = b"\\n\\n\\n\');\nrowGrid"
start_flag = b"container.insertAdjacentHTML(\'beforeend\' ,\'\\n\\n"


def download(dir, page_count, keyword):
    link_list = get_pic_url(page_count, keyword)
    for link in link_list:
        pic = requests.get(link)
        parse_result = urllib.parse.urlparse(link)
        filename = urllib.parse.parse_qs(parse_result.query)['dl'][0]
        file_path = os.path.normpath(dir + '/' + filename)
        f = open(file_path, 'wb+', buffering=1)
        f.write(pic.content)
        print("download succeed: \n\tform " + link + " to " + file_path)


class PexelsRespHTMLParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.linkList = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            if attrs[1][0] == 'download':
                self.linkList.append(attrs[0][1].strip('"\\'))

    def error(self, message):
        pass


def get_pic_url(page_count, keyword):
    download_url = base_url + urllib.parse.quote_plus(keyword)
    for page in range(page_count):
        payload = {'format': 'js',
                   'seed': time.strftime('%Y-%m-%d %H:%M:%S 0000', time.localtime()),
                   'page': page
                   }
        r = requests.get(download_url, params=payload)
        content = r.content
        start_idx = content.index(start_flag) + len(start_flag)
        end_idx = content.index(end_flag)
        content = content[start_idx: end_idx]
        parser = PexelsRespHTMLParser()
        parser.feed(str(content))
        return parser.linkList


def main():
    parser = argparse.ArgumentParser(description="download pictures form pexels.com")
    parser.add_argument('-p', '--path', help='指定存储路径,默认为当前工作路径', default=".", type=str)
    parser.add_argument('-c', '--count', help='指定下载总页数(每页15)', default=1, type=int)
    parser.add_argument('-s', '--search', help='指定搜索关键字', default='Desktop wallpaper', type=str)
    args = parser.parse_args()

    path_name = args.path
    count = args.count
    keyword = args.search

    download(path_name, count, keyword)


if __name__ == '__main__':
    main()
