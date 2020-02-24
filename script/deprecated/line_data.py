import requests
import bs4

city = 'wuhan'
city_CN = "武汉"
ak = ''
sk = ''
part1 = 0
part2 = 0
part3 = 0

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
url = 'http://%s.8684.cn' % city
html = requests.get(url, headers=headers)
# print (main_html.text)
soup = bs4.BeautifulSoup(html.text, 'lxml')
links_number = soup.find('div', class_='bus_kt_r1').find_all('a')
links_letter = soup.find('div', class_='bus_kt_r2').find_all('a')
links = links_number + links_letter
# print(links)
# 1, 2, 3, 4, B, D
lines_stations = {}
for link in links:
    link_href = link['href']
    link_html = requests.get(url + link_href, headers=headers)
    link_soup = bs4.BeautifulSoup(link_html.text, 'lxml')
    lines = link_soup.find('div', class_='stie_list').find_all('a')
    for line in lines:
        line_href = line['href']
        line_name = line.get_text()
        try:
            line_html = requests.get(url + line_href, headers=headers)

            line_info = {}
            line_soup = bs4.BeautifulSoup(line_html.text, 'lxml')
            bus_lines = line_soup.find_all('div', class_='bus_line_site')
            for bus_line in bus_lines:
                stations = []
                bus_stations = bus_line.find_all('a')
                for bus_station in bus_stations:
                    stations.append(bus_station.get_text())
                if bus_lines.index(bus_line) == 0:
                    line_info[line_name] = stations

            lines_stations.update(line_info)
        except Exception as e:
            print("[info] some error occur")
            continue
        # all_lines.append(line_name)
        print("[info] get the info of line %s, total: %s" % (line_name, len(lines_stations)))
    with open("../data/lines_stations_%s.json" % city, "w", encoding='utf-8') as f:
        part1 = len(lines_stations)
        f.write(str(lines_stations))

del lines_stations

from urllib import parse
import hashlib


def get_poi_position(address):
    queryStr = '/place/v2/search?query=%s&tag=公交车站&city_limit=true&region=%s&output=json&ak=%s' % (address, city_CN, ak)
    encodedStr = parse.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")
    rawStr = encodedStr + sk
    sn = (hashlib.md5(parse.quote_plus(rawStr).encode("utf-8")).hexdigest())
    url = parse.quote("http://api.map.baidu.com" + queryStr + "&sn=" + sn, safe="/:=&?#+!$,;'@()*[]")
    try:
        response = requests.get(url)
        content = eval(response.content)
        lng = content['results'][0]['location']['lng']
        lat = content['results'][0]['location']['lat']
        return lng, lat
    # location = content['location']
    # print(location)
    except Exception as e:
        return None, None


lines_geometry = []

with open('../data/lines_stations_%s.json' % city, "r", encoding='utf-8') as f:
    lines = dict(eval(f.read()))
    for name, stations in lines.items():
        line = []
        lng_1, lat_1 = get_poi_position(stations[0])
        lng_2, lat_2 = get_poi_position(stations[-1])
        if lng_1 != None and lng_2 != None:
            line.append(lng_1)
            line.append(lat_1)
            line.append(lng_2)
            line.append(lat_2)
        if len(line):
            lines_geometry.append(line)
            print("[info] process line %s, total: %d" % (name, len(lines_geometry)))

with open('../data/lines_geometry_%s.json' % city, 'w', encoding='utf-8') as f:
    part2 = len(lines_geometry)
    f.write(str(lines_geometry))

del lines_geometry

def get_bus_info_baidu(start_lng, start_lat, end_lng, end_lat):
    global null
    null = ''
    queryStr = '/direction/v2/transit?origin=%f,%f&destination=%f,%f&ak=%s' % (
        start_lat, start_lng, end_lat, end_lng, ak)
    encodedStr = parse.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")
    rawStr = encodedStr + sk
    sn = (hashlib.md5(parse.quote_plus(rawStr).encode("utf-8")).hexdigest())
    url = parse.quote("http://api.map.baidu.com" + queryStr + "&sn=" + sn, safe="/:=&?#+!$,;'@()*[]")
    try:
        response = requests.get(url)
        content = response.content
        content = dict(eval(content))
        steps = content['result']['routes'][0]['steps']
        route = []
        for step in steps:
            path = step[0]['path']
            polylines = path.split(';')
            for polyline in polylines:
                lng = float(polyline.split(',')[0])
                lat = float(polyline.split(',')[1])
                route.append(lng)
                route.append(lat)
        for i in range(-2, -len(route), -2):
            route[i] = int(1e4 * (route[i] - route[i - 2]))
            route[i + 1] = int(1e4 * (route[i + 1] - route[i - 1]))
        route[0] = int(1e4 * route[0])
        route[1] = int(1e4 * route[1])
        filter_route = []
        for i in range(0, len(route), 2):
            if route[i] != 0 or route[i + 1] != 0:
                filter_route.append(route[i])
                filter_route.append(route[i + 1])
        return filter_route
    except Exception as e:
        return None


with open('../data/lines_geometry_%s.json' % city) as f:
    lines = list(eval(f.read()))
lines_data = []
for line in lines:
    start_lng, start_lat = line[0], line[1]
    end_lng, end_lat = line[2], line[3]
    route = get_bus_info_baidu(start_lng, start_lat, end_lng, end_lat)
    print("[info] process data [%f, %f]-[%f, %f], total: %d" % (start_lng, start_lat, end_lng, end_lat, len(lines_data)))
    if route != None and len(route) > 2:
        lines_data.append(route)

with open('../data/lines_data_%s.json' % city, 'w') as f:
    part3 = len(lines_data)
    f.write(str(lines_data))

print('[info] part1-part2: %f' % (part2 / part1))
print('[info] part2-part3: %f' % (part3 / part2))
