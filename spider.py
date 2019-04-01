import json
import re
import requests
from requests.exceptions import RequestException


def get_one_page(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


def parse_one_page(html):
    pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name"><a'
                         '.*?href="/films/(.*?)".*?>(.*?)</a>.*?"star">(.*?)</p>.*?releasetime">(.*?)</p>.*?integer"'
                         '>(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)
    items = re.findall(pattern, html)
    # print(items)
    for item in items:
        yield {
            'index': item[0],
            'image': item[1],
            'inweb': item[2],
            'title': item[3],
            'actor': item[4].strip()[3:],
            'time': item[5].strip()[5:],
            'score': item[6] + item[7]
        }


# 获取评论
def get_comments(num):
    i = 1
    url = "https://maoyan.com/films/" + num
    web = get_one_page(url)
    pattern = re.compile('score-star clearfix" data-score="(.*?)">.*?comment-content">(.*?)</div>', re.S)
    items = re.findall(pattern, web)
    for item in items:
        yield {
            'index': i,
            'score': item[0],
            'comment': item[1]
        }
        i += 1


def write_to_file(content):
    with open('./results/result.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
        f.close()


def save_imgs(item):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.162 Safari/537.36 '
    }
    response = requests.get(item['image'], headers=headers).content
    with open('./results/imgs/' + item['index'] + '_' + item['title'] + '.jpg', 'wb') as f:
        f.write(response)


def main(offset):
    url = "http://maoyan.com/board/4?offset=" + str(offset)
    html = get_one_page(url)
    # print(html)
    for item in parse_one_page(html):
        # print(item)
        write_to_file(item)
        # save_imgs(item)
        for comment in get_comments(item['inweb']):
            # print(comment)
            write_to_file(comment)


if __name__ == '__main__':
    for i in range(10):
        main(i)
