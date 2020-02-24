let dom = document.getElementById("container");
let myChart = echarts.init(dom);
let myData = undefined;

let city = '杭州';
let query = window.location.search.substring(1);
let param_arr = query.split("&");
for (var i = 0; i < param_arr.length; i++) {
    let pair = param_arr[i].split("=");
    if (pair[0] == 'city') {
        city = decodeURI(pair[1]);
    }
    // parse more
}

let ops = {
    city: city,
    time: '7:00',
    percent: 1.0,
    opacity: 0.1,
    step: 300,
    color: '#006EFF',
    lineWidth: 0.0,
    lineLength: 0.0,
    point: true,
    pointSpeed: 10.0,
    pointSize: 1.0
};

let zh2en = {
    "北京": "beijing",
    '上海': 'shanghai',
    "广州": "guangzhou",
    '杭州': 'hangzhou',
    "南京": "nanjing",
    "台北": "taipei",
    "武汉": "wuhan",
    "天津": "tianjin",
    "深圳": "shenzhen",
    "成都": "chengdu",
    "重庆": "chongqing",
    "香港": "hongkong",
    "澳门": "aomen",
    "西安": "xian",
    "拉萨": "lasa",
    "郑州": "zhengzhou",
    "长沙": "changsha",
    "贵阳": "guiyang",
    "西宁": "xining",
    "南宁": "nanning",
    "海口": "haikou",
    "呼和浩特": "huhehaote",
    "乌鲁木齐": "wulumuqi",
    "太原": "taiyuan",
    "石家庄": "shijiazhuang",
    "长春": "changchun",
    "合肥": "hefei",
    "哈尔滨": "haerbin",
    "兰州": "lanzhou",
    "昆明": "kunming",
    "大连": "dalian",
    "济南": "jinan",
    "开封": "kaifeng",
    "银川": "yinchuan",
    "洛阳": "luoyang",
    "南昌": "nanchang",
    "厦门": "xiamen",
    '苏州': 'suzhou',
    '沈阳': 'shenyang',
    "青岛": "qingdao",
    "常州": "changzhou",
    "东莞": "dongguan",
    "东营": "dongying",
    "佛山": "foshan",
    "福州": "fuzhou",
    "嘉兴": "jiaxing",
    "济宁": "jining",
    "临沂": "linyi",
    "南通": "nantong",
    "宁波": "ningbo",
    "泉州": "quanzhou",
    "绍兴": "shaoxing",
    "泰州": "taihzou",
    "台州": "taizhou2",
    "唐山": "tangshan",
    "潍坊": "weifang",
    "温州": "wenzhou",
    "无锡": "wuxi",
    "徐州": "xuzhou",
    "盐城": "yancheng",
    "扬州": "yangzhou",
    "烟台": "yantai",
    "淄博": "zibo",
    "亳州": "bozhou",
    "金华": "jinhua",
    "北京地铁": "beijing_subway",
    "上海地铁": "shanghai_subway",
    "广州地铁": "guangzhou_subway",
    "深圳地铁": "shenzhen_subway",
    "杭州地铁": "hangzhou_subway",
    "南京地铁": "nanjing_subway",
    "天津地铁": "tianjin_subway",
    "武汉地铁": "wuhan_subway",
    "重庆地铁": "chongqing_subway",
    "成都地铁": "chengdu_subway",
    "香港地铁": "hongkong_subway",
    "西安地铁": "xian_subway",
    "大连地铁": "dalian_subway",
    "厦门地铁": "xiamen_subway",
    "昆明地铁": "kunming_subway",
}

let zh = Object.keys(zh2en).sort(function(a, b) { return zh2en[a].localeCompare(zh2en[b]) });

let hours = Array.from({ length: 24 }, (v, k) => k);
let strHours = hours.map(x => `${x}:00`)

// progress bar setting
NProgress.configure({
    parent: '#loading',
    showSpinner: false
});

// call back function for get basic json
let setJson = (data) => {
    myChart.setOption(option = {
        bmap: {
            center: data['position'],
            zoom: data['scale'],
            roam: true,
            mapStyle: {
                'styleJson': [
                    {
                        'featureType': 'water',
                        'elementType': 'all',
                        'stylers': {
                            'color': '#031628'
                        }
                    },
                    {
                        'featureType': 'land',
                        'elementType': 'geometry',
                        'stylers': {
                            'color': '#000102'
                        }
                    },
                    {
                        'featureType': 'highway',
                        'elementType': 'all',
                        'stylers': {
                            'visibility': 'off'
                        }
                    },
                    {
                        'featureType': 'arterial',
                        'elementType': 'geometry.fill',
                        'stylers': {
                            'color': '#000000'
                        }
                    },
                    {
                        'featureType': 'arterial',
                        'elementType': 'geometry.stroke',
                        'stylers': {
                            'color': '#0b3d51'
                        }
                    },
                    {
                        'featureType': 'local',
                        'elementType': 'geometry',
                        'stylers': {
                            'color': '#000000'
                        }
                    },
                    {
                        'featureType': 'railway',
                        'elementType': 'geometry.fill',
                        'stylers': {
                            'color': '#000000'
                        }
                    },
                    {
                        'featureType': 'railway',
                        'elementType': 'geometry.stroke',
                        'stylers': {
                            'color': '#08304b'
                        }
                    },
                    {
                        'featureType': 'subway',
                        'elementType': 'geometry',
                        'stylers': {
                            'lightness': -70
                        }
                    },
                    {
                        'featureType': 'building',
                        'elementType': 'geometry.fill',
                        'stylers': {
                            'color': '#000000'
                        }
                    },
                    {
                        'featureType': 'all',
                        'elementType': 'labels.text.fill',
                        'stylers': {
                            'color': '#857f7f'
                        }
                    },
                    {
                        'featureType': 'all',
                        'elementType': 'labels.text.stroke',
                        'stylers': {
                            'color': '#000000'
                        }
                    },
                    {
                        'featureType': 'building',
                        'elementType': 'geometry',
                        'stylers': {
                            'color': '#022338'
                        }
                    },
                    {
                        'featureType': 'green',
                        'elementType': 'geometry',
                        'stylers': {
                            'color': '#062032'
                        }
                    },
                    {
                        'featureType': 'boundary',
                        'elementType': 'all',
                        'stylers': {
                            'color': '#465b6c'
                        }
                    },
                    {
                        'featureType': 'manmade',
                        'elementType': 'all',
                        'stylers': {
                            'color': '#022338'
                        }
                    },
                    {
                        'featureType': 'label',
                        'elementType': 'all',
                        'stylers': {
                            'visibility': 'off'
                        }
                    }
                ]
            }
        }
    });
}

// get random samples
let getSample = (arr, size) => {
    var shuffled = arr.slice(0), i = arr.length, temp, index;
    while (i--) {
        index = Math.floor((i + 1) * Math.random());
        temp = shuffled[index];
        shuffled[index] = shuffled[i];
        shuffled[i] = temp;
    }
    return shuffled.slice(0, size);
}

// call back function for get data
let setData = (data) => {
    let percent = ops.percent;
    let color = ops.color;
    let time = 100 * parseInt(ops.time.slice(0, ops.time.indexOf(':')))
    let sample_data = getSample(data, parseInt(percent * data.length));
    let filter_data = sample_data.filter(x => time >= x[0] && time <= x[1])
    let hStep = ops.step / (sample_data.length - 1);
    let busLines = [].concat.apply([], filter_data.map(function (busLine, idx) {
        let prevPt;
        let points = [];
        for (let i = 2; i < busLine.length; i += 2) {
            let pt = [busLine[i], busLine[i + 1]];
            if (i > 2) {
                pt = [
                    prevPt[0] + pt[0],
                    prevPt[1] + pt[1]
                ];
            }
            prevPt = pt;
            points.push([pt[0], pt[1]]);
        }
        return {
            coords: points,
            lineStyle: {
                normal: {
                    color: echarts.color.modifyHSL(color, Math.round(hStep * idx))
                }
            }
        };
    }));

    // slow change
    myChart.setOption(option = {
        bmap: myChart.getOption().bmap
    }, true)

    myChart.setOption(option = {
        series: [{
            type: 'lines',
            coordinateSystem: 'bmap',
            polyline: true,
            data: busLines,
            slient: true,
            lineStyle: {
                normal: {
                    // color: '#c23531',
                    // color: 'rgb(200, 35, 45)',
                    opacity: ops.opacity,
                    width: 1
                }
            },
            progressiveThreshold: 500,
            progressive: 200
        }, {
            type: 'lines',
            coordinateSystem: 'bmap',
            polyline: true,
            data: busLines,
            lineStyle: {
                normal: {
                    width: ops.lineWidth,
                }
            },
            effect: {
                constantSpeed: ops.pointSpeed,
                show: ops.point,
                trailLength: ops.lineLength,
                symbolSize: ops.pointSize
            },
            zlevel: 1
        }]
    });
}

// load city data
let loadCityData = (city) => {
    document.getElementById("loading").style.display = "inline";
    myChart.clear();
    $.getJSON('data/' + city + '.json', function (data) {
        setJson(data)
        $.ajax({
            xhr: function () {
                let xhr = new window.XMLHttpRequest();
                xhr.addEventListener("progress", function (evt) {
                    if (evt.lengthComputable) {
                        let percentComplete = evt.loaded / evt.total;
                        // console.log(percentComplete);
                        NProgress.set(percentComplete);
                    }
                }, false);
                return xhr;
            },
            type: 'GET',
            url: 'data/' + city + '.data',
            success: function (data) {
                let jsonData = JSON.parse(data);
                myData = jsonData;
                setData(jsonData);
                document.getElementById("loading").style.display = "none";
            }
        });
    });
}

// new gui console
gui = new dat.GUI();

gui.add(ops, 'city', zh).onChange(function (val) {
    document.getElementById("loading").style.display = "inline";
    loadCityData(zh2en[val]);
});

gui.add(ops, 'time', strHours).onChange(function (val) {
    setData(myData);
});

gui.add(ops, 'percent', 0.0, 1.0, 0.1).onChange(function (val) {
    setData(myData);
});

gui.add(ops, 'opacity', 0.0, 1.0, 0.1).onChange(function (val) {
    setData(myData);
});

gui.add(ops, 'step', 0, 600, 100).onChange(function (val) {
    setData(myData);
});

gui.add(ops, 'lineWidth', 0.0, 2.0, 0.2).onChange(function (val) {
    setData(myData);
});

gui.add(ops, 'lineLength', 0.0, 2.0, 0.2).onChange(function (val) {
    setData(myData);
});

gui.add(ops, 'point').onChange(function (val) {
    setData(myData);
});

gui.add(ops, 'pointSpeed', 0, 40, 5).onChange(function (val) {
    setData(myData);
});

gui.add(ops, 'pointSize', 0.0, 3.0, 0.5).onChange(function (val) {
    setData(myData);
});

gui.addColor(ops, 'color', '#5A94DF').onChange(function (val) {
    setData(myData);
});

gui.autoPlace = true;

loadCityData(zh2en[ops['city']]);