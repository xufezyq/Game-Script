import sys
from datetime import datetime

import pymongo


def setting_devices(input_dir):
    if 'Note12T_Pro' in input_dir:
        device_name = '红米 Note 12T Pro'
    elif 'K40' in input_dir:
        device_name = 'Redmi_K40'
    else:
        print('unknown device name')
        sys.exit(1)
    return device_name


def setting_case(input_dir):
    if '成都' in input_dir:
        case_name = '定点（成都）'
    elif '楚州' in input_dir:
        case_name = '定点（楚州）'
    else:
        print('unknown case name')
        sys.exit(1)
    return case_name


def send_to_mongodb(stat_event, input_dir):
    dicc = {
        "测试机型": "Redmi_K40",
        "用例": "定点（成都）",
        "处理器": "高通骁龙870",
        "内存": "12GB",
        "date": "2024-02-19",
        "data": {
            "KPlayerClient::Breathe": "0.051",
            "KSO3World::Activate": "0.377"
        },
        "CPU Frame": "23.3"
    }
    myclient = pymongo.MongoClient("mongodb://10.11.80.122:27017/")
    mydb = myclient["vkengine"]
    mycol = mydb["engine_monitor"]

    data = {}
    for event in stat_event:
        data[event[0]] = str(event[1])

    dicc['测试机型'] = setting_devices(input_dir)
    dicc['用例'] = setting_case(input_dir)
    dicc['处理器'] = ''
    dicc['内存'] = ''
    dicc['date'] = datetime.now().strftime("%Y-%m-%d")
    dicc['data'] = data
    dicc['CPU Frame'] = str(stat_event[-1][1])

    x = mycol.insert_one(dicc)
    print(x)
