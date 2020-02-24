import urllib
import requests
import hashlib

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
}


def get_walk_info(start_lng, start_lat, end_lng, end_lat):
    baseUrl = "http://restapi.amap.com/v3/direction/walking?"
    params = {
        'key': '',
        'origin': '%f,%f' % (start_lng, start_lat),
        'destination': '%f,%f' % (end_lng, end_lat),
    }
    paramMerge = urllib.parse.urlencode(params).replace("%2C", ',')
    # print(paramMerge)
    targetUrl = baseUrl + paramMerge
    try:
        req = requests.get(targetUrl, headers=headers)
        res = req.content
        content = dict(eval(res))
        steps = content['route']['paths'][0]['steps']
        route = []
        for step in steps:
            polylines = step['polyline'].split(';')
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
    except Exception as e:
        return None
    return filter_route


def get_bus_info(start_lng, start_lat, end_lng, end_lat):
    baseUrl = "http://restapi.amap.com/v3/direction/transit/integrated?"
    params = {
        'key': '',
        'origin': '%f,%f' % (start_lng, start_lat),
        'destination': '%f,%f' % (end_lng, end_lat),
        'city': '北京市'
    }
    paramMerge = urllib.parse.urlencode(params).replace("%2C", ',')
    # print(paramMerge)
    targetUrl = baseUrl + paramMerge
    try:
        req = requests.get(targetUrl, headers=headers)
        res = req.content
        content = dict(eval(res))
        steps = content['route']['transits'][0]['segments'][0]['bus']
        route = []
        buslines = steps['buslines'][0]['polyline']
        polylines = buslines.split(';')
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
    except Exception as e:
        return None
    return filter_route


def get_bus_info_baidu(start_lng, start_lat, end_lng, end_lat):
    ak = ''
    sk = ''
    global null
    null = ''
    queryStr = '/direction/v2/transit?origin=%f,%f&destination=%f,%f&ak=%s' % (
        start_lat, start_lng, end_lat, end_lng, ak)
    encodedStr = urllib.parse.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")
    rawStr = encodedStr + sk
    sn = (hashlib.md5(urllib.parse.quote_plus(rawStr).encode("utf8")).hexdigest())
    url = urllib.parse.quote(
        "http://api.map.baidu.com" + queryStr + "&sn=" + sn, safe="/:=&?#+!$,;'@()*[]")
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


with open('../data/all_lines_beijing.json') as f:
    lines = list(eval(f.read()))
all_route = []
for line in lines:
    start_lng, start_lat = line[0], line[1]
    end_lng, end_lat = line[2], line[3]
    route = get_bus_info_baidu(start_lng, start_lat, end_lng, end_lat)
    print(len(all_route))
    if route != None and len(route) > 2:
        all_route.append(route)

with open('../data/all_lines_beijing_bus_baidu.json', 'w') as f:
    f.write(str(all_route))
