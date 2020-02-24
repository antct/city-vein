import sys
import script.coord
import time
import random
import urllib
import requests


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").content


def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
}


def getHtml(url):
    retry_count = 5
    proxy = get_proxy()
    while retry_count > 0:
        try:
            # html = requests.get(url, headers=headers)
            html = requests.get(url, headers=headers, proxies={
                                "http": "http://{}".format(proxy)})
            # if eval(html.content)['status'] == '6':
            #     delete_proxy(proxy)
            #     proxy = get_proxy()
            #     continue
            return html
        except Exception:
            retry_count -= 1
    delete_proxy(proxy)
    return None


def get_city_info(city):
    api = 'http://restapi.amap.com/v3/config/district?'
    params = {
        'key': '',
        'keywords': '%s' % city,
        'subdistrict': '0',
        'extensions': 'all'
    }
    paramMerge = urllib.parse.urlencode(params)
    url = api + paramMerge
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
        lngs.append(lng)
        lats.append(lat)
    lngs.sort()
    lats.sort()
    return adcode, center, lngs[0], lngs[-1], lats[0], lats[-1]


def extract_stations(bus_line):
    bus_name = bus_line["name"]
    stations = bus_line["stations"]
    set = []
    for station in stations:
        info = []
        station_id = station['station_id']
        station_name = station['name']
        station_lng = station["xy_coords"].split(";")[0]
        station_lat = station["xy_coords"].split(";")[1]
        wgs84cor1 = script.coord.gcj02towgs84(
            float(station_lng), float(station_lat))
        transfer_lng = wgs84cor1[0]
        transfer_lat = wgs84cor1[1]
        info.append(transfer_lng)
        info.append(transfer_lat)
        set.append(info)
    return set


def extract_line(bus_line):
    key_name = bus_line["key_name"]
    bus_name = bus_line["name"]
    front_name = bus_line["front_name"]
    terminal_name = bus_line["terminal_name"]
    set = []
    x_set = bus_line['xs'].split(',')
    y_set = bus_line['ys'].split(',')
    for i in range(len(x_set)):
        info = []
        point_lng = x_set[i]
        point_lat = y_set[i]
        wgs84cor2 = script.coord.gcj02towgs84(
            float(point_lng), float(point_lat))
        transfer_lng = wgs84cor2[0]
        transfer_lat = wgs84cor2[1]
        info.append(transfer_lng)
        info.append(transfer_lat)
        set.append(info)
    # print(set)
    return set


adcode, center, left, right, down, up = get_city_info("重庆市")


def get_geometry_info(line):
    baseUrl = "https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&is_classify=true&"
    params = {
        'keywords': '%s' % line,
        'zoom': '13',
        'city': '%s' % adcode,
        'geoobj': '%f|%f|%f|%f' % (left, down, right, up)
    }
    paramMerge = urllib.parse.urlencode(params)
    # print(paramMerge)
    targetUrl = baseUrl + paramMerge
    try:
        req = getHtml(targetUrl)
        res = req.content
        content = dict(eval(res))
        if (content["data"]["message"]) and content["data"]["busline_list"]:
            bus_lines = content["data"]["busline_list"]  # busline 列表
            bus_line = bus_lines[0]
            bus_stations = extract_stations(bus_line)
            bus_line = extract_line(bus_line)

            # print(bus_stations)
            # print(busLine)
            # 设置随机休眠
            return bus_stations

        else:
            return None
    except Exception as e:
        return None


def line_vector(line):
    vector = []
    prev_lng, prev_lat = 0, 0
    for station in line:
        if line.index(station) == 0:
            vector.append(int(1e4 * station[1]))
            vector.append(int(1e4 * station[2]))
            prev_lng = station[1]
            prev_lat = station[2]
        else:
            vector.append(int(1e4 * (station[1] - prev_lng)))
            vector.append(int(1e4 * (station[2] - prev_lat)))
            prev_lng = station[1]
            prev_lat = station[2]
    return vector


with open('../data/lines_chongqing.json', 'r', encoding='utf-8') as f:
    lines = list(eval(f.read()))

all_lines = []

for line in lines:
    # print(line)
    line_base = get_geometry_info(line)
    if line_base != None:
        tmp = []
        tmp.append(line_base[0][0])
        tmp.append(line_base[0][1])
        tmp.append(line_base[-1][0])
        tmp.append(line_base[-1][1])
        all_lines.append(tmp)
    print(len(all_lines))
    time.sleep(random.random() * random.randint(0, 7) + random.randint(0, 5))
# if line_base == None:
#     if line.find("路") != -1:
#         line = line[:line.find("路") + 1]
#     line_base = get_geometry_info(line)
# if line_base != None:
#     all_lines.append(line_vector(line_base))
#     print(len(all_lines))
with open('../data/all_lines_chongqing.json', 'w', encoding='utf-8') as f:
    f.write(str(all_lines))
