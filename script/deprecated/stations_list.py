import requests
import bs4

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
url = 'http://beijing.8684.cn'
html = requests.get(url, headers=headers)
# print (main_html.text)
soup = bs4.BeautifulSoup(html.text, 'lxml')
links_number = soup.find('div', class_='bus_kt_r1').find_all('a')
links_letter = soup.find('div', class_='bus_kt_r2').find_all('a')
links = links_number + links_letter
# print(links)
# 1, 2, 3, 4, B, D
all_lines = {}
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

            all_lines.update(line_info)
        except Exception as e:
            print("[INFO] some error occur")
            continue
        # all_lines.append(line_name)
        print("[INFO] get the info of line %s" % line_name)
    with open("../data/lines_beijing.json", "w", encoding='utf-8') as f:
        f.write(str(all_lines))
