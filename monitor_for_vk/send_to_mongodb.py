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
        "测试机型": "",
        "用例": "",
        "处理器": "",
        "内存": "",
        "date": "",
        "data": {},
        "CPU Frame": ""
    }
    myclient = pymongo.MongoClient("mongodb://10.11.80.122:27017/")
    mydb = myclient["vkengine"]
    mycol = mydb["engine_monitor"]

    data = {}
    for event in stat_event:
        event_key = event[0].replace('.', '::')
        data[event_key] = str(event[1])

    dicc['测试机型'] = setting_devices(input_dir)
    dicc['用例'] = setting_case(input_dir)
    dicc['处理器'] = ''
    dicc['内存'] = ''
    dicc['date'] = datetime.now().strftime("%Y-%m-%d")
    dicc['data'] = data
    dicc['CPU Frame'] = str(stat_event[-1][1])

    # print(dicc)
    x = mycol.insert_one(dicc)
    print(x)
