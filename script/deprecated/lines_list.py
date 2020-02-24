from urllib import parse
import hashlib
import requests

ak = ''
sk = ''


def get_position(address):
    province = ''
    city = '北京'
    level = '公交站'
    queryStr = '/geocoder/v2/?address=%s&output=json&ak=%s' % (
        province + city + address + level, ak)
    encodedStr = parse.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")
    rawStr = encodedStr + sk
    sn = (hashlib.md5(parse.quote_plus(rawStr).encode("utf8")).hexdigest())
    url = parse.quote("http://api.map.baidu.com" + queryStr +
                      "&sn=" + sn, safe="/:=&?#+!$,;'@()*[]")
    response = requests.get(url)
    lng, lat = response.json()['result']['location']['lng'], response.json()[
        'result']['location']['lat']
    precise, confidence = response.json()['result']['precise'], response.json()[
        'result']['confidence']
    return lng, lat, precise, confidence


def get_poi_position(address):
    city = "北京"
    queryStr = '/place/v2/search?query=%s&tag=公交车站&region=%s&output=json&ak=%s' % (
        address, city, ak)
    encodedStr = parse.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")
    rawStr = encodedStr + sk
    sn = (hashlib.md5(parse.quote_plus(rawStr).encode("utf-8")).hexdigest())
    url = parse.quote("http://api.map.baidu.com" + queryStr +
                      "&sn=" + sn, safe="/:=&?#+!$,;'@()*[]")

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


# lng, lat = response.json()['result']['location']['lng'], response.json()['result']['location']['lat']
# precise, confidence = response.json()['result']['precise'], response.json()['result']['confidence']
# return lng, lat, precise, confidence


# df = pd.DataFrame(columns=['source', 'target'])
# source = []
# target = []

# for line_name, line_stations in all_lines.items():
#     print(line_name, line_stations)
#     for i in range(len(line_stations)-1):
#         source.append(get_position(line_stations[i]))
#         target.append(get_position(line_stations[i+1]))
#     break

# df['source'] = source
# df['target'] = target
# df.to_csv('./data.csv', index=False)

# print(get_position('古荡'))


data = []

with open('../data/lines_beijing.json', "r", encoding='utf-8') as f:
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
            data.append(line)
            print(line)
        print(len(data))

with open('../data/all_lines_beijing.json', 'w', encoding='utf-8') as f:
    f.write(str(data))
