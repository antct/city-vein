import urllib
import requests
import hashlib
import bs4
import logging
import random
import math
import pypinyin

from tqdm import tqdm

logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
logging.root.setLevel(level=logging.INFO)
logger = logging.getLogger()

class city_vein():
    def __init__(self, city_zh, web_key, js_key, line_type=0):
        self.city_zh = city_zh
        self.city_en = ''.join(pypinyin.lazy_pinyin(self.city_zh))
        self.city_si = ''.join([i[0] for i in pypinyin.lazy_pinyin(self.city_zh)])
        self.city_en = 'hongkong' if self.city_zh == '香港' else self.city_en
        self.city_en = 'taizhou2' if self.city_zh == '台州' else self.city_en
        self.city_si = 'hk' if self.city_zh == '香港' else self.city_si
        self.web_key = web_key
        self.js_key = js_key
        if line_type not in [0, 1]:
            raise TypeError('unvalid line type')
        self.line_type = line_type
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }

    def _get_all_buses(self):
        url = 'http://%s.8684.cn' % self.city_en
        html = requests.get(url, headers=self.headers)
        soup = bs4.BeautifulSoup(html.text, 'html.parser')
        links = soup.find('div', class_='bus-layer').find_all('div', class_='pl10')[:2]
        links = [[i['href'] for i in link.find_all('a')] for link in links]
        links = sum(links, [])
        all_lines = []
        for link in tqdm(links):
            link_html = requests.get(url + link, headers=self.headers)
            link_soup = bs4.BeautifulSoup(link_html.text, 'html.parser')
            lines = link_soup.find_all('div', class_='list')
            lines = [line.find_all('a') for line in lines]
            lines = sum(lines, [])
            for line in lines:
                line_name = line.get_text()
                if self.city_en == 'hongkong':
                    all_lines.append(line_name[:line_name.find('(')].strip())
                else:
                    all_lines.append(line_name)
                # logger.info("get line: %s" % line_name)
        logger.info('get {} line'.format(len(all_lines)))
        return len(all_lines), all_lines

    def _get_all_subways(self):
        url = 'https://dt.8684.cn/{}'.format(self.city_si)
        html = requests.get(url, headers=self.headers)
        html.encoding = 'utf-8'
        soup = bs4.BeautifulSoup(html.text, 'html.parser')
        links = soup.find('div', class_='ib-box').find_all('a')
        all_lines = []
        for link in tqdm(links):
            line_name = link.get_text()
            all_lines.append(line_name)
            # logger.info("get line: %s" % line_name)
        logger.info('get {} line'.format(len(all_lines)))
        return len(all_lines), all_lines

    def _get_line_info(self, line_name):
        # https://restapi.amap.com/v3/bus/linename?
        # s=rsv3&extensions=all&key=608d75903d29ad471362f8c58c550daf&output=json&
        # pageIndex=1&city=%E5%8C%97%E4%BA%AC&offset=1&keywords=536&callback=jsonp_246759_&
        # platform=JS&logversion=2.0&appname=https%3A%2F%2Flbs.amap.com%2Fapi%2Fjavascript-api%
        # 2Fexample%2Fbus-search%2Fsearch-bus-route&csid=82FF8B4C-11F6-4370-ABA3-1A05B7108C75&sdkversion=1.4.9
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }
        base_url = "https://restapi.amap.com/v3/bus/linename?"
        params = {
            's': 'rsv3',
            'extensions': 'all',
            'key': '%s' % self.js_key,
            'output': 'json',
            'city': self.city_zh,
            'keywords': line_name,
        }
        param_merge = urllib.parse.urlencode(params).replace("%2C", ',')
        targetUrl = base_url + param_merge
        try:
            response = requests.get(targetUrl, headers=self.headers)
            content = response.content
            content = dict(eval(content))

            status = content['status']
            buslines = content['buslines']

            positive_buslines = buslines[0]
            try:
                negative_buslines = buslines[1]
                lines = positive_buslines if random.randint(
                    0, 1) == 1 else negative_buslines
            except Exception:
                lines = positive_buslines

            name = lines['name']
            try:
                start_time = int(lines['start_time'])
                end_time = int(lines['end_time'])
            except Exception:
                timedesc = lines['timedesc']
                timedesc = timedesc.replace('%22', '"').replace('%2C', ',')
                timedesc = eval(timedesc)
                time_group = timedesc['rule_group'][0]['time_group'][0]
                start_time = time_group['start_time']
                end_time = time_group['end_time']
                start_time = int('{}{}'.format(start_time[0:2], start_time[3:5]))
                end_time = int('{}{}'.format(end_time[0:2], end_time[3:5]))
            polyline = lines['polyline']
            busstops = lines['busstops']

            return start_time, end_time, polyline
        except Exception as e:
            return None, None, None

    def _transfer(self, lng, lat):
        x_pi = math.pi * 3000.0 / 180.0
        x, y = lng, lat
        z = math.sqrt(x * x + y * y) + 0.00002 * math.sin(y * x_pi)
        theta = math.atan2(y, x) + 0.000003 * math.cos(x * x_pi);
        lng = z * math.cos(theta) + 0.0065
        lat = z * math.sin(theta) + 0.006
        return lng, lat

    def _get_all_lines(self, digits=4):
        _, lines = self._get_all_buses() if self.line_type == 0 else self._get_all_subways()
        lines_info = []
        for line in tqdm(lines):
            # logger.info("get line info: %s" % line)
            start_time, end_time, polyline = self._get_line_info(line_name=line)
            if polyline != None:
                polypoints = polyline.split(';')
                polyX = []
                polyY = []
                diffX = []
                diffY = []
                for polypoint in polypoints:
                    x = float(polypoint.split(',')[0])
                    y = float(polypoint.split(',')[1])
                    x, y = self._transfer(x, y)
                    x, y = round(x, digits), round(y, digits)
                    polyX.append(x)
                    polyY.append(y)

                diffX.append(polyX[0])
                diffY.append(polyY[0])
                for i in range(0, len(polyX)-1):
                    diffX.append(polyX[i+1] - polyX[i])
                    diffY.append(polyY[i+1] - polyY[i])
                for i in range(0, len(diffX)):
                     diffX[i] = round(diffX[i], digits)
                     diffY[i] = round(diffY[i], digits)
                diff = []
                for i in range(0, len(diffX)):
                    diff.append(diffX[i])
                    diff.append(diffY[i])

                info = [start_time, end_time, ]
                info.extend(diff)
                lines_info.append(info)

        logger.info('get {} lineinfo'.format(len(lines_info)))
        logger.info("recall: %f" % float(len(lines_info) / len(lines)))
        return lines_info

    def _get_city_info(self):
        api = 'http://restapi.amap.com/v3/config/district?'
        params = {
            'key': '%s' % self.web_key,
            'keywords': '%s' % self.city_zh,
            'subdistrict': '0',
            'extensions': 'all'
        }
        param_merge = urllib.parse.urlencode(params)
        url = api + param_merge
        req = urllib.request.Request(url)
        res = urllib.request.urlopen(req)
        content = dict(eval(res.read()))
        adcode = content['districts'][0]['adcode']
        center = content['districts'][0]['center']
        polys = content['districts'][0]['polyline'].split(';')
        lngs = []
        lats = []
        for i in polys:
            if i.find('|') != -1:
                continue
            lng, lat = float(i.split(',')[0]), float(i.split(',')[1])
            lng, lat = self._transfer(lng, lat)
            lngs.append(lng)
            lats.append(lat)
        lngs.sort()
        lats.sort()
        return center.split(',')

    def generate(self):
        logger.info('get {} lines'.format(self.city_en))
        data = self._get_all_lines()
        suffix = '' if self.line_type == 0 else '_subway'

        with open('./data/{}{}.data'.format(self.city_en, suffix), 'w+') as wf:
            wf.write(str(data))

        center = self._get_city_info()
        with open('./data/{}{}.json'.format(self.city_en, suffix), 'w+') as wf:
            wf.write(str({
                "position": center,
                "scale": 11 if self.line_type == 0 else 10
            }).replace("'", '"'))
        logger.info('get {} lines done'.format(self.city_en))


if __name__ == "__main__":
    web_key = ''
    js_key = ''
    city_zh = ''
    obj = city_vein(
        city_zh=city_zh,
        web_key=web_key,
        js_key=js_key,
        line_type=0
    )
    obj.generate()
