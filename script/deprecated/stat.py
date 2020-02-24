import urllib
import requests
import hashlib
import bs4
import logging
import random


logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
logging.root.setLevel(level=logging.INFO)
logger = logging.getLogger()

def _get_line_info(city_name):
    # https://restapi.amap.com/v3/bus/linename?
    # s=rsv3&extensions=all&key=608d75903d29ad471362f8c58c550daf&output=json&
    # pageIndex=1&city=%E5%8C%97%E4%BA%AC&offset=1&keywords=536&callback=jsonp_246759_&
    # platform=JS&logversion=2.0&appname=https%3A%2F%2Flbs.amap.com%2Fapi%2Fjavascript-api%
    # 2Fexample%2Fbus-search%2Fsearch-bus-route&csid=82FF8B4C-11F6-4370-ABA3-1A05B7108C75&sdkversion=1.4.9
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
    }
    base_url = "https://restapi.amap.com/v3/place/text?"


    page_num = 1
    lines = []
    while True:
        params = {
            'extensions': 'all',
            'key': '',
            'keywords': '公交线路',
            'city': city_name,
            'citylimit': 'true',
            'output': 'json',
            'page': '%d' % page_num
        }
        param_merge = urllib.parse.urlencode(params).replace("%2C", ',')
        targetUrl = base_url + param_merge
        try:
            response = requests.get(targetUrl, headers=headers)
            content = response.content
            content = dict(eval(content))
            count = content['count']
            if count == '0':
                break

            pois = content['pois']
            for poi in pois:
                here_lines = poi['address'].split(';')
                lines.extend(here_lines)
        except Exception as e:
            return None
        page_num += 1

    lines = list(set(lines))
    print(lines)
_get_line_info('香港')