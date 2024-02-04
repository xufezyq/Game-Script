import os
from collections import defaultdict
from datetime import datetime
import requests
import json

target_event = [
    'CPU Frame',
    'virtual BOOL cocos2d::KMUI::Tick',
    'virtual void KRenderVK::RenderScene',
    'int KJX3RenderModule::BackgroundPresent',
    'FrameWaitTimer'
]
global_event_dict = defaultdict(dict)
# 自己测试
# global_url = 'https://xz.wps.cn/api/v1/webhook/send?key=7e60aa09abca467e00bcbe0f69ed861d'
# 每日监控群
global_url = 'https://xz.wps.cn/api/v1/webhook/send?key=700f5b7d6ec17818105a95378e4c4caf'

def send_data_robot(stat_event, input_dir):
    data = []
    for event_index, stat in stat_event.items():
        data.append(stat)

    # 确定key
    last_sep = input_dir.rfind(os.sep)
    second_last_sep = input_dir.rfind('\\', 0, last_sep)
    devices_key = input_dir[second_last_sep + 1:last_sep]
    scene_key = input_dir[last_sep + 1:]
    # 根据key添加数据
    for event_name, avg_event_elapse in data:
        if event_name in target_event:
            if devices_key not in global_event_dict:
                global_event_dict[devices_key] = {}  # 如果该键不存在，创建一个空字典
            if scene_key not in global_event_dict[devices_key]:
                global_event_dict[devices_key][scene_key] = []  # 如果该键不存在，创建一个空列表
            global_event_dict[devices_key][scene_key].append((event_name, avg_event_elapse))


# def write_data(data, sheet_name):


def create_json_data():
    current_time = datetime.now().date()
    data = {
        "msgtype": "markdown",
        "markdown": {
            "text": f"# 《剑网3无界》{current_time}性能监控数据：\n\n"
        }
    }
    for devices_key, scene_dict in global_event_dict.items():
        data['markdown']['text'] += f"## {devices_key}\n\n"
        for scene_key, stat in scene_dict.items():
            data['markdown']['text'] += f"### {scene_key}\n\n"
            for event_name, avg_event_elapse in stat:
                data['markdown']['text'] += f"- {event_name}: **<font color='green'>{avg_event_elapse}</font>**\n"
            data['markdown']['text'] += "\n\n"
    data['markdown']['text'] += "<at user_id=\"1518675131\"></at>"

    json_data = json.dumps(data)
    request_post(global_url, json_data)


def request_post(url, data):
    response = requests.post(url, data=data)
    return response
